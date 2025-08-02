from setuptools import setup
import pathlib

this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="simple-media-sorter",
    version="0.9",
    author="Abdul Rahim",
    author_email="a.rahim29@yahoo.com",
    description="A set of python modules to sort and clean media files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["simple_media_sorter"],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
