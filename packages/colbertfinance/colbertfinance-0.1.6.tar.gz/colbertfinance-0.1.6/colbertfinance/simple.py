import yfinance as yf
import pandas as pd
import numpy as np

TRADING_DAYS = 252

def descargar_cierres(tickers, años=5):
    df = yf.download(tickers, period=f"{años}y", interval="1d", auto_adjust=True)["Close"]
    return df.dropna()

def calcular_markowitz(prices):
    R = prices.pct_change().dropna()
    mu = R.mean() * TRADING_DAYS
    cov = R.cov()
    inv_cov = np.linalg.inv(cov)

    ones = np.ones(len(mu))
    A = ones @ inv_cov @ ones
    B = ones @ inv_cov @ mu
    C = mu @ inv_cov @ mu
    D = 1 / (A * C - B**2)

    G = D * (inv_cov @ (C * ones - B * mu))
    H = D * (inv_cov @ (A * mu - B * ones))

    return mu, cov, G, H
