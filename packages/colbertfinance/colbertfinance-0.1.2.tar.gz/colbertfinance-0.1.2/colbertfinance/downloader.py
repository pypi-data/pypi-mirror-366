import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def here():
    """
    Retorna la ruta del directorio donde se encuentra el script que ejecuta la función.
    """
    return os.path.dirname(os.path.abspath(__import__('__main__').__file__))

def descargar_cierres(tickers, años=5, nombre_archivo="precios_cierre.xlsx"):
    """
    Descarga precios de cierre diarios desde Yahoo Finance y guarda el archivo
    en la misma carpeta desde donde se ejecuta el script principal.

    Parámetros:
    - tickers: Lista de símbolos como ["AAPL", "GOOG"]
    - años: Número de años atrás desde hoy
    - nombre_archivo: Nombre del archivo Excel de salida
    """
    fin = datetime.now()
    inicio = fin - timedelta(days=años * 365)

    datos = pd.DataFrame()
    for ticker in tickers:
        print(f"🔄 Descargando {ticker}...")
        df = yf.download(ticker, start=inicio, end=fin, progress=False)
        datos[ticker] = df["Close"]

    ruta_salida = os.path.join(here(), nombre_archivo)
    datos.to_excel(ruta_salida)
    print(f"\n📁 Archivo guardado en: {ruta_salida}")
