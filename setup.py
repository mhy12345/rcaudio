import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rcaudio",
    version="0.0.2",
    author="mhy12345",
    author_email="maohanyang789@163.com",
    description="A real-time audio recording & analyzing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhy12345/rcaudio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
