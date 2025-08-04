from setuptools import setup, find_packages

setup(
    name="findpkg",
    version="0.1.0",
    description="CLI tool to locate in which virtual environment a Python package is installed.",
    author="Arslaan Darwajkar",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'findpkg=findpkg.__main__:search_package',
        ],
    },
    python_requires='>=3.6',
)

entry_points={
    'console_scripts': [
        'findpkg=findpkg.__main__:main',
    ],
},