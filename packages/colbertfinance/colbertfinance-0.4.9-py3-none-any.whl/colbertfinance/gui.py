#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
colbertfinance.gui – GUI Markowitz con TODAS las fórmulas intermedias
© 30-jul-2025 (adaptado)
"""

import os, sys, numpy as np, pandas as pd, yfinance as yf, matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")                     # evita avisos en algunos entornos

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QCompleter, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QStringListModel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# ─────────────── paths / constantes
TDAYS      = 252
BASE_DIR   = os.path.abspath(os.path.dirname(__file__))
XLSX_FILE  = os.path.join(BASE_DIR, "efficient_portfolios.xlsx")
PNG_FILE   = os.path.join(BASE_DIR, "std_vs_er.png")

# ─────────────── autocompletar ticker (consulta a Yahoo)
def yahoo_suggest(q: str, limit: int = 15):
    if not q: return []
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    try:
        j = yf.utils.get_json(url, params={"q": q, "quotesCount": limit,
                                           "newsCount": 0})
        return [d["symbol"] for d in j.get("quotes", [])
                if d.get("isYahooFinance", True)]
    except Exception:
        return []

# ─────────────── descarga de precios ajustados
def download_prices(tickers, years):
    df = yf.download(" ".join(tickers), period=f"{years}y",
                     interval="1d", auto_adjust=True,
                     progress=False, threads=True)["Close"]
    df = df[tickers].dropna()
    if df.empty:
        raise RuntimeError("No existe rango de fechas común.")
    return df

# ─────────────── núcleo Markowitz
def markowitz(prices):
    """
    σ y varianza DIARIAS  –  μ anual (μ = media diaria × 252)
    """
    R   = prices.pct_change().dropna()
    mu  = R.mean() * TDAYS              # anual
    Σ   = R.cov()                       # diaria  ← NO *TDAYS
    invΣ= np.linalg.inv(Σ)
    N   = len(mu); ones = np.ones(N)

    A = ones @ invΣ @ ones
    B = ones @ invΣ @ mu
    C = mu   @ invΣ @ mu
    D = 1/(A*C - B**2)
    G = D * (invΣ @ (C*ones - B*mu))
    H = D * (invΣ @ (A*mu  - B*ones))

    er  = np.arange(0.0001, 1.0001, 0.0001)          # 0.01 … 100 %
    W   = G[:, None] + H[:, None] * er               # N × 10 000
    var = np.einsum("ni,ij,nj->n", W.T, Σ.values, W.T)   # diaria
    std = np.sqrt(var)                               # diaria

    return dict(tickers=prices.columns, Σ=Σ, G=G, H=H,
                er=er, W=W, var=var, std=std, idx_min=std.argmin())

# ─────────────── GUI
class MarkowitzGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portafolio Markowitz – PyQt5 (cálculo completo)")
        self.resize(980, 720)

        # entrada
        self.le = QLineEdit(); self.le.setPlaceholderText("Ticker…")
        self.bt_add  = QPushButton("Añadir")
        self.spinYrs = QSpinBox(); self.spinYrs.setRange(1, 10); self.spinYrs.setValue(5)
        self.bt_calc = QPushButton("Calcular")
        self.lst = QListWidget()

        # resultados
        self.tbl    = QTableWidget()
        self.canvas = FigureCanvasQTAgg(plt.Figure())

        # autocompleter
        self._model = QStringListModel(); self._comp = QCompleter(self._model)
        self._comp.setCaseSensitivity(Qt.CaseInsensitive); self.le.setCompleter(self._comp)
        self._timer = QTimer(self, singleShot=True, interval=300)
        self._timer.timeout.connect(self._autocomplete)
        self.le.textEdited.connect(lambda _: self._timer.start())

        # layout
        top = QHBoxLayout()
        top.addWidget(self.le); top.addWidget(self.bt_add)
        top.addStretch(1)
        top.addWidget(QLabel("Años:")); top.addWidget(self.spinYrs)
        top.addWidget(self.bt_calc)

        lay = QVBoxLayout()
        lay.addLayout(top)
        lay.addWidget(QLabel("Tickers seleccionados:")); lay.addWidget(self.lst, 1)
        lay.addWidget(QLabel("Tabla ±2 ER % (σ mín resaltado):")); lay.addWidget(self.tbl, 1)
        lay.addWidget(self.canvas, 3)

        w = QWidget(); w.setLayout(lay); self.setCentralWidget(w)

        # señales
        self.bt_add .clicked.connect(self._add_ticker)
        self.bt_calc.clicked.connect(self._compute)

    # ---------- autocompletar
    def _autocomplete(self):
        self._model.setStringList(yahoo_suggest(self.le.text().strip()))
        self._comp.complete()

    # ---------- añadir ticker
    def _add_ticker(self):
        t = self.le.text().strip().upper()
        if t and t not in [self.lst.item(i).text() for i in range(self.lst.count())]:
            self.lst.addItem(t)
        self.le.clear()

    # ---------- cálculo principal
    def _compute(self):
        tks = [self.lst.item(i).text() for i in range(self.lst.count())]
        if len(tks) < 2:
            QMessageBox.warning(self, "Faltan tickers", "Añade mínimo 2."); return
        try:
            P   = download_prices(tks, self.spinYrs.value())
            res = markowitz(P)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e)); return

        self._table(res); self._plot(res); self._save(res)

    # ---------- tabla
    def _table(self, res):
        idx = res["idx_min"]
        er  = res["er"] * 100                  # en %
        std = res["std"] * 100                 # diaria en %
        W   = res["W"] * 100                   # pesos %
        tick = list(res["tickers"])

        cols = np.clip(np.arange(idx - 2, idx + 3), 0, len(er) - 1)
        headers = [f"{er[i]:.2f}%" for i in cols]

        self.tbl.setRowCount(len(tick) + 1); self.tbl.setColumnCount(5)
        self.tbl.setHorizontalHeaderLabels(headers)
        self.tbl.setVerticalHeaderLabels(tick + ["Std"])

        for r, tkr in enumerate(tick):
            for c, j in enumerate(cols):
                val = W[r, j]; txt = f"{val:+.2f}%"
                it = QTableWidgetItem(txt)
                if c == 2: it.setBackground(Qt.yellow)
                self.tbl.setItem(r, c, it)

        for c, j in enumerate(cols):
            it = QTableWidgetItem(f"{std[j]:.2f}%")
            if c == 2: it.setBackground(Qt.yellow)
            self.tbl.setItem(len(tick), c, it)

        self.tbl.resizeColumnsToContents()

    # ---------- gráfico
    def _plot(self, res):
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)
        er  = res["er"] * 100
        std = res["std"] * 100
        idx = res["idx_min"]
        L   = max(0, idx - 10); R = min(len(er) - 1, idx + 10)

        ax.scatter(std[L:R+1], er[L:R+1], color="steelblue")
        ax.scatter(std[idx], er[idx], s=160, color="magenta",
                   edgecolors="black", linewidths=1.5)
        ax.axvline(std[idx], color="magenta", ls=":", lw=1.2,
                   label=f"σ mínima = {std[idx]:.2f}%")
        ax.annotate(f"ER={er[idx]:.2f}%\nσ={std[idx]:.2f}%",
                    xy=(std[idx], er[idx]), xytext=(std[idx]*1.05, er[idx]),
                    bbox=dict(fc="yellow", ec="black", boxstyle="round,pad=0.3"),
                    fontweight="bold", arrowprops=dict(arrowstyle="->"))
        ax.set_xlabel("Desvío estándar diario (%)")
        ax.set_ylabel("ER objetivo anual (%)")
        ax.grid(True); ax.legend(); self.canvas.draw()

    # ---------- guardar Excel
    def _save(self, res):
        erc  = (res["er"] * 100).round(2)
        cols = [f"{v:.2f}%" for v in erc]
        df_W   = pd.DataFrame(res["W"] * 100, index=res["tickers"], columns=cols)
        df_var = pd.DataFrame([res["var"] * 100], index=["Var %"], columns=cols)
        df_std = pd.DataFrame([res["std"] * 100], index=["Std %"], columns=cols)

        with pd.ExcelWriter(XLSX_FILE, engine="xlsxwriter") as w:
            res["Σ"].to_excel(w, sheet_name="VarCov (diaria)")
            df_W  .to_excel(w, sheet_name="Pesos %")
            df_var.to_excel(w, sheet_name="Var %")
            df_std.to_excel(w, sheet_name="Std %")

        self.canvas.figure.savefig(PNG_FILE, dpi=120)
        QMessageBox.information(self, "Guardado",
            f"Excel y gráfico guardados en:\n{BASE_DIR}")

# ─────────────── helper público
def lanzar_gui():
    app = QApplication(sys.argv)
    gui = MarkowitzGUI(); gui.show()
    sys.exit(app.exec_())

# depuración local
if __name__ == "__main__":
    lanzar_gui()
