import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='docVisualizer',
    version='0.1',
    author="Hongye Chen",
    author_email="mchen2608@gmail.com",
    description="Metadata visualization for pdf",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hongyec/Visoo",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
 )