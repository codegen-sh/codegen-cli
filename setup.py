from setuptools import find_packages, setup

setup(
    name="codegen",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["click", "requests>=2.25.0", "pathlib", "algoliasearch", "rich", "pyjwt", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "codegen=codegen.cli:main",
        ],
    },
)
