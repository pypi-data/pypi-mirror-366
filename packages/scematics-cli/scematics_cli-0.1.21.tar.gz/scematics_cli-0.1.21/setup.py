from setuptools import setup, find_packages

# Read the README for long_description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A CLI tool for managing file uploads"

setup(
    name="scematics-cli",
    version="0.1.21",
    packages=find_packages(),
    install_requires=[
        "typer",
        "requests",
        "rich",
        "pillow",
        "opencv-python",
        "pathlib",
        "websocket-client", 
        "websockets",
        "tqdm",
        "boto3", 
        "azure-storage-blob",
        "google-cloud-storage" 
    ],
    entry_points={
        'console_scripts': [
            'scematics-cli=scematics_cli.cli:main',  # Changed from hyphen to underscore
        ],
    },
    author="scematics.io",
    author_email="karthickeyan@scematics.xyz",
    description="A CLI tool for managing file uploads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0karthickm/scematics-cli",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Changed to be more flexible with versions
)
