"""
Setup script for CryptoPIX - Revolutionary Post-Quantum Cryptographic Library
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cryptopix",
    version="8.0.0",
    author="CryptoPIX Team",
    author_email="founder@cryptopix.in",
    description="Revolutionary Post-Quantum Cryptographic Library using Color Lattice Learning with Errors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.cryptopix.in",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "Pillow>=8.0.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "fast": [
            "numba>=0.53.0",  # For JIT compilation of hot paths
        ],
    },
    entry_points={
        "console_scripts": [
            "cryptopix=cryptopix.cli:main",
        ],
    },
    package_data={
        "cryptopix": ["*.md", "examples/*.py"],
    },
    keywords="cryptography post-quantum lattice color-based encryption signatures",
    project_urls={
        "Homepage": "https://www.cryptopix.in",
        "Bug Reports": "https://github.com/cryptopix-official/cryptopix/issues",
        "Source": "https://github.com/cryptopix-official/cryptopix",
        "Documentation": "https://www.cryptopix.in/docs",
        "Support": "https://www.cryptopix.in/support",
    },
)