from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tensi",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "torch>=1.8.0",
        "numpy>=1.19.0",
        "plotly>=5.0.0",
    ],
    python_requires=">=3.7",
    author="Dorsa Rohani",
    author_email="dorsa.rohani@gmail.com",
    description="Interactive tensor shape visualization library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DorsaRoh/tensi",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="tensor visualization pytorch numpy plotly deep-learning",
)