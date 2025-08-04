"""
steps.py  –  API pedagógica *con guardado automático*:

 media()   -> PASO 1  (rentab., σ, var)              → PASO_1_media.xlsx
 varcov()  -> PASO 2  (matriz var-cov)               → PASO_2_varcov.xlsx
 correl()  -> PASO 3  (correlaciones)                → PASO_3_correl.xlsx
 invvar()  -> PASO 4  (inversa var-cov)              → PASO_4_invvar.xlsx
 unos()    -> PASO 5  (matriz de 1)                  → PASO_5_unos.xlsx
 const()   -> PASO 6  (A,B,C,D,G,H)                  → PASO_6_const.xlsx
 portaf()  -> PASO 7  (pesos + riesgo)               → PASO_7_portaf.xlsx
"""

import numpy as np, pandas as pd, yfinance as yf, os, sys

TDAYS   = 252
_here   = lambda: os.path.dirname(os.path.abspath(
           sys.modules["__main__"].__file__))

# ─────────── helper para guardar ───────────────────────────────────
def _save(obj, nombre):
    ruta = os.path.join(_here(), nombre)
    with pd.ExcelWriter(ruta) as xls:
        if isinstance(obj, (pd.Series, pd.DataFrame)):
            obj.to_excel(xls, "Hoja1")
        elif isinstance(obj, tuple):
            for i, o in enumerate(obj, 1):
                if isinstance(o, (pd.Series, pd.DataFrame)):
                    o.to_excel(xls, f"Part_{i}")
    print("💾 Excel guardado:", os.path.basename(ruta))


# ─────────── PASO 0 – precios ─────────────────────────────────────
def precios(tickers, años=5):
    return yf.download(" ".join(tickers), period=f"{años}y",
                       interval="1d", auto_adjust=True,
                       progress=False)["Close"][tickers].dropna()


# ─────────── PASO 1 – rent., σ, var ───────────────────────────────
# ───────── PASO 1 – media(), dentro de steps.py ─────────
def media(p):
    r = p.pct_change().dropna()
    df = pd.concat([
        (r.mean()*100)        .rename("Rentab_dia %"),
        (r.mean()*TDAYS*100)  .rename("Rentab_año %"),
        (r.std()*100)         .rename("Std %"),
        (r.var()*100)         .rename("Var %")
    ], axis=1)
    _save(df, "PASO_1_media.xlsx")
    return df, r


# ─────────── PASO 2 – Var-Cov (frecuencia diaria) ────────────────
def varcov(r):
    """
    Matriz de varianzas y covarianzas basada en rendimientos diarios
    (no anualizada).  Se guarda en PASO_2_varcov.xlsx
    """
    Σ = r.cov()          #   ←  sin *TDAYS
    _save(Σ, "PASO_2_varcov.xlsx")
    return Σ


# ─────────── PASO 3 – Correlaciones ───────────────────────────────
def correl(r):
    C = r.corr()
    _save(C, "PASO_3_correl.xlsx")
    return C


# ─────────── PASO 4 – Inversa Var-Cov ─────────────────────────────
def invvar(Σ):
    inv = pd.DataFrame(np.linalg.inv(Σ), index=Σ.index, columns=Σ.columns)
    _save(inv, "PASO_4_invvar.xlsx")
    return inv


# ─────────── PASO 5 – Matriz de unos ──────────────────────────────
def unos(n, labels):
    U = pd.DataFrame(np.ones((n, n)), index=labels, columns=labels)
    _save(U, "PASO_5_unos.xlsx")
    return U


# ───────── PASO 6 (versión sencilla) ──────────────────────────────
# ─────────── pasos.py (fragmento relevante) ────────────
def const(mu, invΣ):
    """
    Cálculo base de las constantes A,B,C,D,G,H
    -----------------------------------------------------
    mu    : Serie  (rentabilidad en fracción, no en %)
    invΣ  : DataFrame inversa de la matriz Var-Cov
    -----------------------------------------------------
    Devuelve (const_df, G, H) y crea PASO_6_const.xlsx
    """
    one = np.ones(len(mu))
    A = one @ invΣ @ one
    B = one @ invΣ @ mu
    C = mu  @ invΣ @ mu
    D = 1/(A*C - B**2)
    G = D * (invΣ @ (C*one - B*mu))
    H = D * (invΣ @ (A*mu  - B*one))

    const_df = pd.Series(dict(A=A,B=B,C=C,D=D)).to_frame("valor")
    _save((const_df,
           pd.Series(G, name="G"),
           pd.Series(H, name="H")),
          "PASO_6_const.xlsx")
    return const_df, G, H


def const_stats(stats_df, invΣ, anual=True):
    """
    Wrapper pedagógico que llama a const(...)
      • stats_df : DataFrame de media()
      • invΣ     : inversa Var-Cov
      • anual    : True→ usa «Rentab_año %», False→ «Rentab_dia %»
    """
    col = "Rentab_año %" if anual else "Rentab_dia %"
    μ = stats_df[col] / 100          # de porcentaje a fracción
    return const(μ, invΣ)            # reutiliza la función base



# ─────────── PASO 7 – portafolios con resaltado ──────────────────
# ─────────── PASO 7 – Portafolios ±5 y Std mínima resaltada ────────────
def portaf(G, H, Σ, paso=0.0001):
    """
    ▸ Construye la frontera eficiente con ER de 0.01 % … 100 %.
    ▸ Encuentra el punto de desviación estándar mínima.
    ▸ Devuelve y guarda en Excel sólo 11 columnas:
        ❺ antes, el mínimo, ❺ después (±5).
    ▸ Resalta de amarillo la Std mínima en la hoja Part_2.
    """
    # ---- 1) frontera eficiente completa (10 000 puntos)
    er_full = np.arange(paso, 1.0001, paso)              # 0.01% … 100%
    W_full  = np.column_stack([G + H*e for e in er_full])  # pesos N×10 000

    var_full = np.einsum("ni,ij,nj->n",  # n = portafolio
                        W_full.T, Σ.values, W_full.T)
    std_full = np.sqrt(np.clip(var_full, 0, None))  # evita NaN por redondeo


    # ---- 2) ventana de ±5 alrededor de la σ mínima
    idx_min = std_full.argmin()
    l = max(0,   idx_min - 5)
    r = min(len(er_full) - 1, idx_min + 5)

    er_sel  = er_full[l:r+1]
    cols    = [f"{e*100:.2f}%" for e in er_sel]

    W = pd.DataFrame(W_full[:, l:r+1], index=Σ.index, columns=cols)
    W.loc["SUMA"] = W.sum()                     # para que vean que suma 100 %

    riesgo = pd.DataFrame({
        "Varianza": var_full[l:r+1],
        "Std":      std_full[l:r+1]
    }, index=cols)

    # ---- 3) guardar Excel con formato condicional (xlsxwriter)
    ruta = os.path.join(_here(), "PASO_7_portaf.xlsx")
    with pd.ExcelWriter(ruta, engine="xlsxwriter") as xlw:
        W.to_excel(xlw, sheet_name="Part_1")     # tabla de pesos
        riesgo.to_excel(xlw, sheet_name="Part_2")

        ws = xlw.sheets["Part_2"]
        wb = xlw.book
        yellow = wb.add_format({"bg_color": "#FFFF00"})

        first = 2                       # datos empiezan en fila 2 (1-based)
        last  = first + len(riesgo) - 1
        # columna C (índice 2 en 0-based) contiene Std
        ws.conditional_format(first-1, 2, last-1, 2,
            {"type": "formula",
             "criteria": f"=$C{first}=MIN($C${first}:$C${last})",
             "format": yellow})

    print("💾 Excel guardado: PASO_7_portaf.xlsx")
    return W, riesgo









# ─────────── Helper interno para la GUI ───────────────────────────
def _quick_markowitz(prices):
    """
    Devuelve sólo lo que la GUI necesita:
        • er  : lista con ER % (0–100)
        • std : lista con desviaciones estándar
        • idx : posición de la σ mínima
    No guarda ningún Excel.
    """
    TDAYS = 252
    R  = prices.pct_change().dropna()
    mu = R.mean()*TDAYS
    Σ  = R.cov()
    invΣ = np.linalg.inv(Σ)
    one  = np.ones(len(mu))

    A = one @ invΣ @ one
    B = one @ invΣ @ mu
    C = mu  @ invΣ @ mu
    D = 1/(A*C - B**2)
    G = D * (invΣ @ (C*one - B*mu))
    H = D * (invΣ @ (A*mu  - B*one))

    er  = np.arange(0.0001, 1.0001, 0.0001)*100          # en %
    W   = G[:,None] + H[:,None]*(er/100)
    var = np.einsum("ni,ij,nj->n", W.T, Σ.values, W.T)
    std = np.sqrt(var)
    return {"er":er, "std":std, "idx":std.argmin()}




import os
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

def descargar_precios_acciones(tickers, años=5, nombre_archivo="precios_cierre.xlsx"):
    """
    Descarga precios de cierre diarios desde Yahoo Finance y los guarda junto al script.

    Parámetros:
    - tickers: lista de símbolos (por ejemplo: ["AAPL", "GOOG"])
    - años: cantidad de años atrás desde hoy
    - nombre_archivo: nombre del archivo de salida

    Retorna:
    - DataFrame con los precios descargados
    """
    hoy = date.today()
    inicio = hoy - timedelta(days=años * 365)
    script_dir = os.path.dirname(os.path.abspath(__import__('__main__').__file__))

    all_data = []
    for ticker in tickers:
        print(f"🔄 Descargando {ticker}...")
        df = yf.download(ticker, start=inicio, end=hoy, progress=False)[["Close"]]
        df.columns = [ticker]
        all_data.append(df)

    precios = pd.concat(all_data, axis=1)
    ruta_guardado = os.path.join(script_dir, nombre_archivo)
    precios.to_excel(ruta_guardado)
    print(f"\n📁 Archivo guardado en: {ruta_guardado}")
    return precios
