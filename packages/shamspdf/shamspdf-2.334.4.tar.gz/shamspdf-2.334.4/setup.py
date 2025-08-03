import setuptools
from pathlib import Path
setuptools.setup(

    name="shamspdf",
    version="2.334.4",
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["test","data"])

)