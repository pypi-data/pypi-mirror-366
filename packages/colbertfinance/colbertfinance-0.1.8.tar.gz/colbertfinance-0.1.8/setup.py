from setuptools import setup, find_packages

setup(
    name="colbertfinance",
    version="0.1.8",
    packages=find_packages(),
    install_requires=["numpy", "pandas", "yfinance", "xlsxwriter"],
    python_requires=">=3.8",
    author="Jesús Colbert",
    description="Librería educativa para análisis de portafolios (Markowitz paso a paso)",
    long_description="Funciones sencillas para descargar precios, calcular mu, Sigma y portafolio eficiente.",
    long_description_content_type="text/plain",
    url="https://pypi.org/project/colbertfinance/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Education",
    ],
)
