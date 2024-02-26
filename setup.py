import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="RAMAC",
    version="0.0.1.dev1",
    author="Qian Cao, Subrata Mukherjee",
    author_email="qian.cao@fda.hhs.gov",
    description="Registration-based Automatic Matching and Correspondence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DIDSR/RAMAC",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['numpy',
                      'pandas',
                      'phantominator',
                      'SimpleITK',
                      'matplotlib']
)