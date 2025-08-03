from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="powerplanner-lib",
    version="0.0.15",
    author="Gustaf Brahme",    
    description="Client package to access powerplanner API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gurgelx/powerplanner_lib",
    packages=find_packages(),
    install_requires=["aiohttp","aiozoneinfo","datetime"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)