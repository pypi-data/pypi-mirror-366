import setuptools

with open("README.md", "r") as readme:
    long_description = readme.read()

setuptools.setup(
    name="arma3query",
    version="1.1",
    author="Jishnu Karri",
    author_email="me@jishnukarri.me",
    description="Small module to decode the Arma 3 rules binary response.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jishnukarri/arma3-a2s",
    py_modules=["arma3query"],
    install_requires=["python-a2s"],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
    python_requires=">=3.10"
)