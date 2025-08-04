import numpy as np
import pandas as pd
import os
import yfinance as yf
from .helpers import here

TRADING_DAYS = 252  # sesiones al año

# ---------------------------------------------------------------
# 1. Descargar precios ajustados
# ---------------------------------------------------------------
def descargar_cierres(tickers, años=5):
    """
    Descarga precios de cierre ajustados para `tickers` y devuelve un DataFrame.
    """
    df = yf.download(" ".join(tickers),
                     period=f"{años}y",
                     interval="1d",
                     auto_adjust=True,
                     progress=False)["Close"]
    df = df[tickers].dropna()
    if df.empty:
        raise ValueError("No hay rango común de fechas para esos tickers.")
    return df


# ---------------------------------------------------------------
# 2. Calcular μ anual y Σ (covarianza anualizada)
# ---------------------------------------------------------------
def calcular_mu_sigma(precios: pd.DataFrame):
    R     = precios.pct_change().dropna()
    mu    = R.mean() * TRADING_DAYS
    Sigma = R.cov() * TRADING_DAYS
    return mu, Sigma


# ---------------------------------------------------------------
# 3. Constantes A, B, C, D y vectores G, H
# ---------------------------------------------------------------
def constantes_markowitz(mu: pd.Series, Sigma: pd.DataFrame):
    invΣ = np.linalg.inv(Sigma)
    ones = np.ones(len(mu))

    A = ones @ invΣ @ ones
    B = ones @ invΣ @ mu
    C = mu   @ invΣ @ mu
    D = 1 / (A * C - B**2)

    G = D * (invΣ @ (C * ones - B * mu))
    H = D * (invΣ @ (A * mu   - B * ones))
    return A, B, C, D, G, H


# ---------------------------------------------------------------
# 4. Función completa de Markowitz
# ---------------------------------------------------------------
def calcular_markowitz(precios: pd.DataFrame, er_objetivo: float = 0.15):
    """
    Devuelve:
      μ, Σ, pesos óptimos, varianza, desviación estándar
    """
    mu, Sigma           = calcular_mu_sigma(precios)
    A, B, C, D, G, H    = constantes_markowitz(mu, Sigma)
    w_opt               = G + H * er_objetivo     # pesos óptimos para ER objetivo
    var_port            = w_opt.T @ Sigma @ w_opt
    std_port            = np.sqrt(var_port)
    return mu, Sigma, w_opt, std_port


# ---------------------------------------------------------------
# 5. Exportar todo a Excel junto al script
# ---------------------------------------------------------------
def exportar_excel(mu, Sigma, w, std, nombre="resultado_markowitz.xlsx"):
    ruta = os.path.join(here(), nombre)

    sheet_mu    = mu.to_frame("μ anual")
    sheet_sigma = Sigma
    sheet_w     = pd.DataFrame(w, index=mu.index, columns=["Peso óptimo"])
    sheet_std   = pd.DataFrame({"Desvío estándar": [std]})

    with pd.ExcelWriter(ruta, engine="xlsxwriter") as writer:
        sheet_mu.to_excel(writer,    sheet_name="Mu")
        sheet_sigma.to_excel(writer, sheet_name="Sigma")
        sheet_w.to_excel(writer,     sheet_name="Pesos")
        sheet_std.to_excel(writer,   sheet_name="Riesgo")

    print(f"✅ Archivo guardado en: {ruta}")
