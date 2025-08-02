from setuptools import setup, find_packages

setup(
    name="catscan-terra",
    version="2.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
        "rich>=13.0.0",
        "keyring>=23.0.0",
    ],
    entry_points={
        "console_scripts": [
            "catscan=catscan.__main__:main",
        ],
    },
)