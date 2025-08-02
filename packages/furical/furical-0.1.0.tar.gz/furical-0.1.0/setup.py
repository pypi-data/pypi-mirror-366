from setuptools import setup, find_packages

setup(
    name="furical",
    version="0.1.0",
    author="MD ARIF AZIZ",
    author_email="arifaziz0125@gmail.com",
    description="A simple calculator package",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_point={
        "console_scripts": [
            "furical=furical.calculator:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)