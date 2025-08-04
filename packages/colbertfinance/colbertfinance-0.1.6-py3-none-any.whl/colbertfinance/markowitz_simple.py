import numpy as np
import pandas as pd
import os

TRADING_DAYS = 252

def mu_sigma(precios):
    R = precios.pct_change().dropna()
    mu = R.mean() * TRADING_DAYS
    Sigma = R.cov()
    return mu, Sigma

def constantes_markowitz(mu, Sigma):
    invΣ = np.linalg.inv(Sigma)
    ones = np.ones(len(mu))
    A = ones @ invΣ @ ones
    B = ones @ invΣ @ mu
    C = mu @ invΣ @ mu
    D = 1 / (A*C - B**2)
    G = D * (invΣ @ (C * ones - B * mu))
    H = D * (invΣ @ (A * mu - B * ones))
    return A, B, C, D, G, H

def pesos_por_ER(G, H, er_objetivo):
    return G + H * er_objetivo

def guardar_en_excel(resultados: dict, nombre_archivo="resultados_markowitz.xlsx"):
    ruta = os.path.join(os.path.dirname(__file__), nombre_archivo)
    with pd.ExcelWriter(ruta, engine="xlsxwriter") as writer:
        for nombre, df in resultados.items():
            df.to_excel(writer, sheet_name=nombre)
