from setuptools import setup, find_packages

setup(
    name="coffy",
    version="0.1.8",
    author="nsarathy",
    description="Lightweight local NoSQL, SQL, and Graph embedded database engine",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "networkx>=3.0",
        "pyvis>=0.3.2",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "coffy-sql=coffy.cli.sql_cli:sql_cli",
        ],
    },
)
