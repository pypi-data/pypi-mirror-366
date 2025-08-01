import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biobb_adapters",
    version="5.1.0",
    author="Biobb developers",
    author_email="pau.andrio@bsc.es",
    description="Biobb_adapters is the Biobb module collection to use the building blocks with several workflow managers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="Bioinformatics Workflows BioExcel Compatibility",
    url="https://github.com/bioexcel/biobb_adapters",
    project_urls={
        "Documentation": "http://biobb_adapters.readthedocs.io/en/latest/",
        "Bioexcel": "https://bioexcel.eu/"
    },
    packages=setuptools.find_packages(exclude=['docs', 'test']),
    package_data={'biobb_adapters': ['py.typed']},
    include_package_data=True,
    zip_safe=False,
    install_requires=['cwltool'],
    python_requires='>=3.9,<=3.12',
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix"
    ),
)
