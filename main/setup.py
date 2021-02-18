import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="storagewrapper",
    version="0.0.2",
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
    py_modules=['storagewrapper.authenticate', 'storagewrapper.blob', 'storagewrapper.fileshare', 'storagewrapper.queue'],
    install_requires=[
        'azure-storage-queue>=12.1.4',
        'azure-storage-file-share>=12.3.0',
        'azure-storage-blob>=12.6.0',
        'azure-keyvault>=4.1.0',
        'azure-identity>=1.5.0'
    ])

