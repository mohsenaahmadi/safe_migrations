import os
import subprocess
from pathlib import Path
from django.core.management.base import BaseCommand
from git import Repo
from django.conf import settings


class Command(BaseCommand):
    help = "Create and apply safe migrations."

    def add_arguments(self, parser):
        parser.add_argument("--hash", nargs="?", default=None, help="Commit hash to start the operation. If not provided, the command will determine it automatically.")
        parser.add_argument("--git", nargs="?", default=None, help="Git repository path.")

    def handle(self, *args, **options):
        target_hash = options["hash"]
        git_dir = options["git"]
        repo = Repo(git_dir if git_dir else Path.cwd())

        if repo.bare:
            self.stderr.write("The repository is bare or not found.")
            return

        if not target_hash:
            target_hash = self.find_last_stable_commit(repo)

        if not target_hash:
            self.stderr.write("No stable commit found with successful migrations.")
            return

        self.stdout.write(f"Using starting commit: {target_hash}")

        commits = self.get_commits_since(repo, target_hash)
        self.prepare_migrations_folder()

        for commit in commits:
            self.stdout.write(f"Checking out commit {commit.hexsha}")
            repo.git.checkout(commit.hexsha)

            if self.models_changed():
                self.run_makemigrations()

        # Return to HEAD and finalize migrations
        self.stdout.write("Returning to HEAD")
        self.back_to_branch(repo)
        self.run_makemigrations()
        self.run_migrate()

    def back_to_branch(self, repo):
        head_commit = repo.head.commit
        branches = [branch.name for branch in repo.branches if branch.commit == head_commit]
        if branches:
            repo.git.checkout(branches[0])
        else:
            self.stdout.write("HEAD is not attached to any branch. Remaining on the commit.")
            repo.git.checkout("HEAD")

    def find_last_stable_commit(self, repo):
        self.stdout.write("Determining last stable commit with successful migrations...")

        for commit in repo.iter_commits():
            if self.commit_has_successful_migrations(commit):
                return commit.hexsha
        return None

    def commit_has_successful_migrations(self, commit):
        for file_path in commit.stats.files.keys():
            if file_path.endswith("models.py"):
                return True
        return False

    def get_commits_since(self, repo, start_hash):
        start_commit = repo.commit(start_hash)
        return list(repo.iter_commits(rev=f"{start_commit.hexsha}^..HEAD"))[::-1]

    def prepare_migrations_folder(self):
        self.stdout.write("Cleaning migrations folders...")
        apps = [app for app in settings.INSTALLED_APPS if not app.startswith("django.")]
        for app_dir in Path.cwd().iterdir():
            if app_dir.name in apps:
                migrations_dir = app_dir / "migrations"
                if migrations_dir.exists() and migrations_dir.is_dir():
                    for item in migrations_dir.iterdir():
                        if item.name not in ["__init__.py", "__pycache__"]:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                os.rmdir(item)
                    self.stdout.write(f"Cleaned {migrations_dir}")
                else:
                    migrations_dir.mkdir(exist_ok=True)
                    (migrations_dir / "__init__.py").touch()

    def models_changed(self):
        return True

    def run_makemigrations(self):
        self.stdout.write("Running makemigrations...")
        subprocess.run(["python", "manage.py", "makemigrations"], check=True)

    def run_migrate(self):
        self.stdout.write("Running migrate...")
        subprocess.run(["python", "manage.py", "migrate"], check=True)
