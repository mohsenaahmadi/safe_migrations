# Safe Migrations

A Django package to safely generate and apply migrations from historical commits.

## Installation

Install the package via pip:

```bash
pip install safe-migrations
```

add `safe_migrations` to `INSTALLED_APPS` in settings.py of your django project.

## Usage

```bash
python manage.py safe_migrations --hash GIT_COMMIT_HASH --git GIT_DIRECTORY
```

## Features

Automatically identifies model changes across commits.
Generates and applies all missing migrations safely.
