from setuptools import setup, find_packages

setup(
    name="baekbox",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hek = baekbox:hel"
        ]
    }
)