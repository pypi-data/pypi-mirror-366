from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hello-world-package-austi",  # Replace with your desired package name
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple hello world package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hello-world-package",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "hello-world=hello_world.cli:main",
        ],
    },
)
