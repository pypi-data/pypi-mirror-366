import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def descargar_cierres(tickers, años=5, nombre_archivo="precios_cierre.xlsx"):
    """
    Descarga precios de cierre diarios desde Yahoo Finance y guarda el archivo
    en la misma carpeta donde se ejecuta el script principal.

    Parámetros:
    - tickers: lista de símbolos (ej. ["AAPL", "GOOG", "MSFT"])
    - años: número de años hacia atrás (default=5)
    - nombre_archivo: nombre del archivo Excel de salida
    """
    fin = datetime.now()
    inicio = fin - timedelta(days=años * 365)
    data = pd.DataFrame()

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=inicio, end=fin, progress=False)
            data[ticker] = df["Close"]
            print(f"✅ {ticker} descargado.")
        except Exception as e:
            print(f"❌ Error con {ticker}: {e}")

    script_dir = os.getcwd()
    ruta_salida = os.path.join(script_dir, nombre_archivo)

    data.to_excel(ruta_salida)
    print(f"\n📁 Archivo guardado en: {ruta_salida}")
