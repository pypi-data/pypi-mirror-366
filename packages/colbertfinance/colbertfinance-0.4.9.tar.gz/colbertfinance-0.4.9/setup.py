from setuptools import setup, find_packages

setup(
    name="colbertfinance",
    version="0.1.0",
    author="Jesús Colbert",
    description="Librería educativa para enseñar el modelo de Markowitz paso a paso",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pandas",
        "numpy",
        "yfinance",
        "matplotlib",
        "PyQt5",
        "openpyxl"
    ],
)
