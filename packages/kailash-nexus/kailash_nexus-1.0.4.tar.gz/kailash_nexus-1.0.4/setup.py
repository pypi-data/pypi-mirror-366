"""Setup script for Kailash Nexus."""

from setuptools import find_packages, setup

setup(
    name="kailash-nexus",
    version="1.0.4",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "kailash>=0.9.5",
    ],
    python_requires=">=3.8",
)
