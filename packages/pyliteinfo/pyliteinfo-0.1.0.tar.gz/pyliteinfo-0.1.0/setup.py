from setuptools import setup, find_packages

setup(
    name="pyliteinfo",
    version="0.1.0",
    description="Lightweight system and storage info utility in Python",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "psutil"
    ],
    python_requires=">=3.6",
)
