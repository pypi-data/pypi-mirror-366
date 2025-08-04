from setuptools import setup, find_packages

setup(
    name="colbertfinance",
    version="0.1.6",
    description="Librería educativa de análisis financiero (Markowitz simplificado)",
    author="Jesus Colbert",
    author_email="jesus.colbert@ejemplo.com",
    packages=find_packages(),
    install_requires=["yfinance", "pandas", "numpy"],
    python_requires=">=3.7",
)
