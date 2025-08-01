from setuptools import setup, find_packages

setup(
    name="py-qj-robots",
    version="0.1.13",
    author="QJ ROBOTS",
    author_email="github@qj-robots.com",
    description="QJ Python SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/QJ-ROBOTS/perception-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.0",
    install_requires=[
        "requests>=2.26.0",
        "python-dotenv>=0.19.0"
    ],
)