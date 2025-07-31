import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="directus-py-sdk",
    version="1.1.2",
    description="Python SDK for interacting with Directus API (colletion, items, users, files)",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Dembrane/directus-py-sdk",
    author="Dembrane",
    author_email="info@dembrane.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=[
        "requests",
        "urllib3",
        "sqlparse",
    ],
    entry_points={
        "console_scripts": [
            "directus-py-sdk=directus_py_sdk.__main__:main",
        ]
    },
)