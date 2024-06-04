from setuptools import find_packages, setup
from importlib.metadata import version  # Python 3.8+

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qnnpy",
    version=version("qnnpy"),
    author="Owen Medeiros",
    author_email="omedeiro@mit.edu",
    description="The QNN library for instrument control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qnngroup/qnnpy",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
