import os
from setuptools import setup, find_packages

# Safely attempt to import Rust extension builders
try:
    from setuptools_rust import Binding, RustExtension
    rust_extensions = [
        RustExtension("hyrandom._hyrandom_rs", binding=Binding.PyO3, optional=False)
    ]
except ImportError:
    print("WARNING: 'setuptools_rust' is missing. The Rust extension will not be compiled. Falling back to Native/NumPy engines.")
    rust_extensions = []

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hyrandom",
    version="1.0.6",
    author="Rayen",
    description="High-performance, cryptographically secure hybrid PRNG library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),
    rust_extensions=rust_extensions,
    extras_require={
        "secure": ["numpy>=1.20.0"],
        "fast": ["numpy>=1.20.0"],
        "rust": [], 
        "full": ["numpy>=1.20.0"], 
        "all": ["numpy>=1.20.0"],
    },
    entry_points={
        "console_scripts": [
            "hyrandom=hyrandom.__main__:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Rust",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)