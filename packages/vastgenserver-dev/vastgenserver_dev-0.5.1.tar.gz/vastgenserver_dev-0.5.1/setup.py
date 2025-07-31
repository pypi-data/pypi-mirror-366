#
# Copyright (C) 2025 Vastai-tech Company.
# All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#
import datetime
import io
import os
import sys
import subprocess
from pathlib import Path
from shutil import rmtree
from setuptools import find_packages, setup, Command

here = os.path.join(os.path.dirname(os.path.abspath(__file__)))

NAME = "vastgenserver_dev"
DESCRIPTION = "VastGenServer is a distributed server for models or others, designed to handle high concurrency and provide efficient model serving capabilities."
URL = "https://www.vastaitech.com/"
EMAIL = "AIS@vastaitech.com"
AUTHOR = "AIS"
REQUIRES_PYTHON = ">=3.7.0"

REQUIRED = [
    "ray[serve]",
    "fastapi",
    "uvicorn",
    "pydantic",
    "pyyaml",
    "python-multipart",
]

EXTRAS = {
    "embedding": [
        "transforms",
        "numpy",
    ],
    "reranker": [
        "transforms",
        "numpy",
    ],
}

try:
    with io.open(os.path.join(here, "ChangeLog")) as f:
        VERSION = f.readline().strip("\n").strip()
except FileNotFoundError:
    VERSION = "0.5.1"

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
about["__version__"] = VERSION


class UploadCommand(Command):
    description = "Build and publish the package."
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(here, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPI via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(about["__version__"]))
        os.system("git push --tags")

        sys.exit()


def get_local_version_suffix() -> str:
    if not (Path(__file__).parent / ".git").is_dir():
        # Most likely installing from a source distribution
        return ""
    date_suffix = datetime.datetime.now().strftime("%Y%m%d")
    git_hash = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"], cwd=Path(__file__).parent
    ).decode("ascii")[:-1]
    return f"+{git_hash}.d{date_suffix}"


setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION + get_local_version_suffix(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "vastgenserver=vastgenserver.main:cli",
        ],
    },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        "upload": UploadCommand,
    },
    build_with_nuitka=True,
)
