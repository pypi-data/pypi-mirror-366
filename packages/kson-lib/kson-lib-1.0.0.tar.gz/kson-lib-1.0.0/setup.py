from setuptools import setup, find_packages

setup(
    name="kson-lib",
    version="1.0.0",
    author="dnoxie",
    description="KSON (Kompact Structured Object Notation) - JSON with comments support",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)