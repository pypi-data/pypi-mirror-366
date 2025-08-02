from setuptools import setup, find_packages
import os
import re

# Read version from version.py
with open(os.path.join('olx_db', 'version.py'), 'r') as f:
    version_file = f.read()
    version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        raise RuntimeError("Unable to find version string in olx_db/version.py")

setup(
    name="olx-db-wonsky",
    version=version,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    description="OLX database models and migrations",
    author="Wonsky",
    author_email="vladyslav.pidborskyi@gmail.com",
)
