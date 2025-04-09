"""Setup configuration for IsopGem package."""

from setuptools import find_packages, setup

setup(
    name="isopgem",
    version="0.1.0",
    description="Sacred Geometry & Gematria Tool",
    author="IsopGem Team",
    packages=find_packages(),
    python_requires=">=3.12",
    include_package_data=True,
    install_requires=[
        "PyQt6>=6.6.0",
        "pyyaml>=6.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "numpy>=1.25.0",
        "pandas>=2.1.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "isopgem=shared.utils.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
)
