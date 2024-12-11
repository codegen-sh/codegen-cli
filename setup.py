from setuptools import setup, find_packages

setup(
    name="codegen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "requests",
        "pathlib",
    ],
    entry_points={
        "console_scripts": [
            "codegen=codegen.cli:main",
        ],
    },
)
