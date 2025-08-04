import os
import pandas as pd
import yfinance as yf

def here():
    return os.path.dirname(os.path.abspath(__file__))

def descargar_cierres(tickers, inicio, fin):
    if isinstance(tickers, str):
        tickers = [tickers]
    data = yf.download(tickers, start=inicio, end=fin, group_by='ticker', auto_adjust=True)
    resultado = {}
    for ticker in tickers:
        df = data[ticker] if len(tickers) > 1 else data
        df = df[["Close"]].rename(columns={"Close": "Precio Cierre"})
        df.index.name = "Fecha"
        resultado[ticker] = df
    return resultado
