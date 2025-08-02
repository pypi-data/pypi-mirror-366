from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textstatslite",
    version="0.2.1",
    description="Lightweight text statistics tool with CLI and readability scoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Khangesh Matte",
    packages=find_packages(),
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'textstats=textstatslite.__main__:main'
        ]
    },
    include_package_data=True,  # Optional: in case you include non-Python files
)
