from setuptools import setup, find_packages

setup(
    name="compango",  # must be unique on PyPI
    version="0.0.1",
    author="Oleksandr Sorokin",
    author_email="bsorokind@gmail.com",
    description="HTMX components for django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/caullla/compango",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.10",
)
