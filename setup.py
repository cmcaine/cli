import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cmcaine-cli",
    version="0.0.2",
    author="Colin Caine",
    description="Easy CLIs from function inspection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmcaine/cli",
    py_modules=['cli'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
