from setuptools import setup, find_packages

setup(
    name="sagikoza",
    version="2.3.1",
    description="A Python library for crawling and retrieving all notices published under Japan’s Furikome Sagi Relief Act, with support for both full data extraction and incremental updates.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="new-village",
    url="https://github.com/new-village/sagikoza",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "jpdatetime"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
