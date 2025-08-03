from setuptools import setup, find_packages

setup(
    name="robots-checker",
    version="1.2.0",
    description="A tool to filter out data from robots.txt restricted URL domains.",
    author="Dongyang Fan",
    packages=find_packages(),
    install_requires=[
        "datasets",
        "pandas",
        "protego",
    ],
    python_requires=">=3.7",
)