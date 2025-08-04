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
def media(p):
    r   = p.pct_change().dropna()
    df  = pd.concat([
        r.mean()*100      .rename("Rentab_dia %"),
        r.mean()*TDAYS*100.rename("Rentab_año %"),
        r.std()*100       .rename("Std %"),
        r.var()*100       .rename("Var %")
    ], axis=1)
    _save(df, "PASO_1_media.xlsx")
    return df, r                   # devuelvo df y r para el paso 2


# ─────────── PASO 2 – Var-Cov ─────────────────────────────────────
def varcov(r):
    Σ = r.cov()*TDAYS
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


# ─────────── PASO 6 – constantes A,B,C,D,G,H ──────────────────────
def const(mu, invΣ):
    one = np.ones(len(mu))
    A = one @ invΣ @ one
    B = one @ invΣ @ mu
    C = mu  @ invΣ @ mu
    D = 1/(A*C - B**2)
    G = D * (invΣ @ (C*one - B*mu))
    H = D * (invΣ @ (A*mu  - B*one))
    const_df = pd.Series(dict(A=A,B=B,C=C,D=D)).to_frame("valor")
    _save((const_df, pd.Series(G,name="G"), pd.Series(H,name="H")),
          "PASO_6_const.xlsx")
    return const_df, G, H


# ─────────── PASO 7 – portafolios ─────────────────────────────────
def portaf(G, H, Σ, er_targets=(0.09,0.12,0.14,0.17,0.1925,0.22,0.25,0.30)):
    cols = [f"{e*100:.2f}%" for e in er_targets]
    W    = pd.DataFrame({c: G + H*e for c,e in zip(cols, er_targets)},
                        index=Σ.index)
    W.loc["SUMA"] = W.sum()

    var  = [(w.T @ Σ @ w) for w in W.T.values]
    std  = np.sqrt(var)
    riesgo = pd.DataFrame({"Varianza":var, "Std":std}, index=cols)

    _save((W, riesgo), "PASO_7_portaf.xlsx")
    return W, riesgo
