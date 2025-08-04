import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def generar_resumen_rendimiento(excel_path=None, hoja="Sheet1"):
    if excel_path is None:
        excel_path = os.path.join(os.path.dirname(__file__), "precios_cierre.xlsx")

    df = pd.read_excel(excel_path, index_col=0, parse_dates=True)
    df_ret = df.pct_change().dropna()
    media = df_ret.mean()
    cov = df_ret.cov()

    rendimientos = np.arange(0.0001, 1.0001, 0.0001)
    resultados = []
    for r in rendimientos:
        pesos = media * 0
        pesos[0] = 1
        w = np.array([r] + [((1 - r) / (len(media) - 1))] * (len(media) - 1))
        w /= w.sum()
        rendimiento_esp = np.dot(w, media)
        volatilidad = np.sqrt(np.dot(w.T, np.dot(cov, w)))
        resultados.append((r*100, rendimiento_esp*100, volatilidad*100))

    df_result = pd.DataFrame(resultados, columns=["% R", "Rend Esperado", "Desv Std"])
    min_std_idx = df_result["Desv Std"].idxmin()
    min_std_row = df_result.loc[min_std_idx]

    df_result.to_excel(os.path.join(os.path.dirname(__file__), "resumen_rendimiento.xlsx"), index=False)

    plt.figure(figsize=(10,6))
    plt.plot(df_result["% R"], df_result["Desv Std"], label="Desviación Estándar (%)")
    plt.axvline(min_std_row["% R"], color="red", linestyle="--", label=f"Mínima Std: {min_std_row['% R']:.2f}%")
    plt.xlabel("Rendimiento Simulado (%)")
    plt.ylabel("Desviación Estándar (%)")
    plt.title("Desviación Estándar vs. Rendimiento Simulado")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(os.path.dirname(__file__), "grafico_std.png"))
    plt.close()

    return df_result
