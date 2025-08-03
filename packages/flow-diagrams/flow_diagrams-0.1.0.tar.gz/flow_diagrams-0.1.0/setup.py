"""setup.py for the Flow project"""

from setuptools import setup, find_packages

setup(
    name="flow-diagrams",
    version="0.1.0",
    description="Client library for creating Mermaid diagrams",
    packages=find_packages(exclude=["flow.app", "tests"]),
    requires=["redis"],
    python_requires=">=3.7",
)
