import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="my_package",
    version="0.0.1",
    author="Author Name",
    author_email="aydinabiar@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="", # Add the URL of your github repository
    packages=['financebro'],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)