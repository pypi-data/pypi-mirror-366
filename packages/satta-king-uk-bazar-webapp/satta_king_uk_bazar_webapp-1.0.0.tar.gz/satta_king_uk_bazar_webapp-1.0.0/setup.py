"""
Setup script for Satta King UK Bazar package.
This file is optional since we're using pyproject.toml, but included for compatibility.
"""

from setuptools import setup, find_packages

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="satta-king-uk-bazar",
    use_scm_version=False,
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={
        "satta_king_uk_bazar": [
            "data/*.json",
            "templates/*.html",
            "static/css/*.css",
            "static/js/*.js",
            "static/*.txt",
        ],
    },
)