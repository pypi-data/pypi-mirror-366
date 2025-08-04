from setuptools import find_packages, setup

setup(
    name="maxtorch",
    version="0.1.0",
    description="High-level PyTorch modules",
    author="Bosegluon",
    author_email="bosegluon@gmail.com",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    url="https://github.com/Bosegluon2/maxtorch",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["torch>=2.6.0"],
    python_requires=">=3.10",
)
