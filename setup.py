import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MetaChem",
    version="0.0.1",
    author="Penelope Faulkner Rainford",
    author_email="pf550@york.ac.uk",
    description="The implemented MetaChem framework",
    long_description= long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/faulknerrainford/MetaChem",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
