from setuptools import setup, find_packages

setup(
    name="td_mion_orbitrap",
    version="0.1.0",
    description="Thermo Orbitrap pipeline for thermogram extraction, blank subtraction, integration, and KMD plots",
    author="Mihai Ciobanu",
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "pandas",
        "numpy",
        "matplotlib",
        "click",
        "pymzml",
    ],
    entry_points={
        "console_scripts": [
            "td-mion = td_mion_orbitrap.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
)
