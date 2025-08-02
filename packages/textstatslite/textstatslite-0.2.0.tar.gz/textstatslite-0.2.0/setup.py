from setuptools import setup, find_packages

setup(
    name="textstatslite",
    version="0.2.0",
    description="Enhanced text statistics package with CLI and readability scoring",
    author="Khangesh Matte",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'textstats=textstatslite.__main__:main'
        ]
    }
)