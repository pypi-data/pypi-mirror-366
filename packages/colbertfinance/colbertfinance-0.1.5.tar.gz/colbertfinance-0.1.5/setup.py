from setuptools import setup, find_packages

setup(
    name="colbertfinance",
    version="0.1.5",
    description="Librería para descargar y resumir precios de cierre desde Yahoo Finance.",
    author="Jesús Colbert",
    author_email="jesus@example.com",
    packages=find_packages(),
    install_requires=["yfinance", "pandas", "openpyxl"],
    python_requires=">=3.7"
)
