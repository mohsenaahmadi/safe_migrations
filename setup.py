from setuptools import setup, find_packages
from pathlib import Path
import re


# Extract the version from the __init__.py file
def get_version():
    init_file = Path(__file__).parent / "safe_migrations" / "__init__.py"
    with open(init_file, "r") as f:
        for line in f:
            match = re.match(r"^__version__ = ['\"]([^'\"]*)['\"]", line)
            if match:
                return match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="safe_migrations",
    version=get_version(),
    author="Mohammad Mohsen Ahmadi",
    author_email="mohsenaahmadi@gmail.com",
    description="A Django package to safely generate and apply migrations from historical commits.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/safe_migrations",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "Django>=3.2",
        "gitpython>=3.1.30",
    ],
)
