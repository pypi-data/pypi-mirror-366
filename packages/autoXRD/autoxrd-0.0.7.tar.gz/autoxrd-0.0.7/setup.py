from setuptools import setup, find_packages

setup(
    name="autoXRD",
    version="0.0.7",
    author="Nathan J. Szymanski",
    author_email="nathan_szymanski@berkeley.edu",
    description="A package for automated XRD analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/njszym/XRD-AutoAnalyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "pymatgen",
        "scipy",
        "scikit-image",
        "tensorflow>=2.16",
        "pyxtal",
        "pyts",
        "tqdm",
        "asteval",
        "numexpr>=2.8.3",
    ],
    include_package_data=True,
)