from setuptools import setup, find_packages
setup(
    name        = "colbertfinance",
    version     = "0.3.3",
    author      = "Jesús Colbert",
    description = "Librería paso-a-paso para enseñar Markowitz",
    packages    = find_packages(),
    python_requires = ">=3.9",
    install_requires = ["pandas","numpy","yfinance","openpyxl"],
)
