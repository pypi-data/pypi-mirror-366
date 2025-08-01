from setuptools import setup, find_packages

# Read the long description from README.md
def read_long_description():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(
    name="geolapis-core",
     version="0.1.1",
    author="NI Ezema / Geolapis Ltd",
    author_email="contact@geolapis.com",
    description="Fast LAS file sanity checks for petrophysicists",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://www.geolapis.com",
    project_urls={
        "Documentation": "https://www.geolapis.com/docs",
        "Source": "https://github.com/GeolapisLtd/GeolapisCore",
        "Issues": "https://github.com/GeolapisLtd/GeolapisCore/issues",
    },
    packages=find_packages(
        include=["core*", "products*", "services*", "ops*", "labs*"],
        exclude=["tests*", "tools*", "test_data*", "logs*"]
    ),
    install_requires=[
        "lasio>=0.27.0",
        "rich>=13.0.0"
    ],
    entry_points={
        "console_scripts": [
            "geolapis-core=products.las_validator_pro.cli:main"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: GIS",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False
)
