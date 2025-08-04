from setuptools import setup, find_packages

setup(
    name="colbertfinance",
    version="0.1.3",
    packages=find_packages(),
    install_requires=["yfinance", "pandas", "matplotlib", "openpyxl"],
    author="Jesus Colbert",
    author_email="jesus@example.com",
    description="Librería para descargar precios y analizar rendimiento proyectado con desviación estándar mínima.",
    long_description="Librería para análisis financiero con Excel export, gráficos y simulaciones.",
    long_description_content_type="text/plain",
    url="https://pypi.org/project/colbertfinance/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
