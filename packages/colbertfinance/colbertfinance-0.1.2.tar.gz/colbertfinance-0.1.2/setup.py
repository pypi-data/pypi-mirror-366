from setuptools import setup, find_packages

setup(
    name="colbertfinance",
    version="0.1.2",
    author="Jesús Colbert",
    author_email="tucorreo@example.com",
    description="Librería para descargar precios de cierre diarios desde Yahoo Finance",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "yfinance",
        "pandas",
        "openpyxl"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
)
