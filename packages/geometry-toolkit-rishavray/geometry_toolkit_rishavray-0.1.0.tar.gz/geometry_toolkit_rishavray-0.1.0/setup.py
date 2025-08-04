from setuptools import setup, find_packages

setup(
    name="geometry_toolkit_rishavray",
    version="0.1.0",
    author="Rishav Ray",
    author_email="rayrishav369@gmail.com",
    description="A toolkit for basic geometric calculations",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rishavray11/geometry_toolkit",
    packages=find_packages(),  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
