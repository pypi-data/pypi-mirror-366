from setuptools import setup, find_packages

# Read the README.md content for PyPI description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="findpkg",
    version="0.1.1",
    description="CLI tool to locate in which virtual environment a Python package is installed.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Arslaan Darwajkar",
    url="https://github.com/Pro-Ace-grammer/findpkg",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'findpkg=findpkg.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)