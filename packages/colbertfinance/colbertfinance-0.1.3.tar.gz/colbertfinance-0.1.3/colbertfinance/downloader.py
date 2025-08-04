import os
import pandas as pd
import yfinance as yf

def here():
    return os.path.dirname(os.path.abspath(__file__))

def descargar_cierres(tickers, años=3):
    datos = {}
    fin = pd.Timestamp.today().date()
    inicio = fin - pd.DateOffset(years=años)
    for ticker in tickers:
        df = yf.download(ticker, start=inicio, end=fin, progress=False)
        df = df[["Close"]].rename(columns={"Close": ticker})
        datos[ticker] = df[ticker]
    df_final = pd.concat(datos.values(), axis=1)
    df_final.columns = tickers
    archivo = os.path.join(here(), "precios_cierre.xlsx")
    df_final.to_excel(archivo)
    print(f"📁 Archivo guardado en: {archivo}")
    return df_final
