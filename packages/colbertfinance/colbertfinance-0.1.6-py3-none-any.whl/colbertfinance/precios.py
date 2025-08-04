import yfinance as yf
import pandas as pd

def descargar_precios(tickers, años=5):
    df = yf.download(" ".join(tickers), period=f"{años}y", interval="1d",
                     auto_adjust=True, progress=False)["Close"]
    df = df[tickers].dropna()
    if df.empty:
        raise ValueError("No hay datos comunes.")
    return df
