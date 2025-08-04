from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="robots-checker",
    version="1.2.2",
    description="A tool to filter out data from robots.txt restricted URL domains.",
    author="Dongyang Fan",
    packages=find_packages(),
    install_requires=[
        "datasets",
        "pandas",
        "protego",
    ],
    python_requires=">=3.7",
    long_description=long_description,
    long_description_content_type='text/markdown'
)