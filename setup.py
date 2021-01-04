import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="azurestoragewrapper",
    version="0.0.1",
    author="Joe Easley",
    author_email="joeeasley@outlook.com",
    description="A wrapper on azure storage tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joe-easley/AzureStorageWrapper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)