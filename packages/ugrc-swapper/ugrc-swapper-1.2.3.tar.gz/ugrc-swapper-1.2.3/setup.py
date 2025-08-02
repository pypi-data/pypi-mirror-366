#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
setup.py
A module that installs swapper as a module
"""

from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="ugrc-swapper",
    version="1.2.3",
    license="MIT",
    description="Move data from one SDE database to another with minimal downtime",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="UGRC",
    author_email="ugrc-developers@utah.gov",
    url="https://github.com/agrc/swapper",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities",
    ],
    project_urls={
        "Issue Tracker": "https://github.com/agrc/swapper/issues",
    },
    keywords=["gis"],
    install_requires=[
        "docopt==0.*",
        "python-dotenv==1.*",
        "pyodbc==5.*",
        "xxhash==3.*",
    ],
    extras_require={
        "tests": [
            "pytest-cov>=5,<7",
            "pytest-instafail==0.5.*",
            "pytest-mock==3.*",
            "pytest-ruff==0.*",
            "pytest-watch==4.*",
            "pytest==8.*",
            "black>=24,<26",
            "ruff==0.*",
        ]
    },
    setup_requires=[
        "pytest-runner",
    ],
    entry_points={"console_scripts": ["swapper = swapper.__main__:main"]},
)
