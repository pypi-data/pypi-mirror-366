from setuptools import setup, find_packages

setup(
    name="axon-programmer",
    version="0.0.7",
    description="Cross-platform tool for detecting and programming Axon servos",
    long_description = open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Pranav Yerramaneni",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "hidapi",
        "ttkthemes",
        "PyQt6",
        "PyQt6-Fluent-Widgets"
    ],
    entry_points={
        "console_scripts": [
            "axon-programmer=src.gui:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)
