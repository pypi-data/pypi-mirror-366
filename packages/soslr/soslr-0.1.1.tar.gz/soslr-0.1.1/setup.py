from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="soslr",
    version="0.1.1",
    author="Soroush Oskouei",
    description="A semi-supervised learning library using iterative pseudo-labeling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SoroushOskouei/Semi-Supervised-sos",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
    install_requires=[      # List of dependencies
        "torch>=1.7",
        "torchvision",
        "numpy",
        "Pillow"
    ],
)
