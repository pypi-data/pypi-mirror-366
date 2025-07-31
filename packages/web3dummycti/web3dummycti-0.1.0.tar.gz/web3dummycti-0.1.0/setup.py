from setuptools import setup, find_packages

setup(
    name="web3dummycti",
    version="0.1.0",
    description="web3dummycti",
    author="brojafox",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
    ],
    python_requires=">=3.6",
)