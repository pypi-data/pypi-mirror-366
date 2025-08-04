import os
import pandas as pd

def generar_resumen_rendimiento(diccionario_dfs, nombre_archivo="resumen.xlsx"):
    resumen = []
    for ticker, df in diccionario_dfs.items():
        df = df.dropna()
        if df.empty: continue
        precio_inicio = df["Precio Cierre"].iloc[0]
        precio_final = df["Precio Cierre"].iloc[-1]
        rendimiento = ((precio_final - precio_inicio) / precio_inicio) * 100
        resumen.append({
            "Ticker": ticker,
            "Precio Inicial": precio_inicio,
            "Precio Final": precio_final,
            "Rendimiento (%)": rendimiento
        })
    df_resumen = pd.DataFrame(resumen)
    ruta = os.path.join(os.getcwd(), nombre_archivo)
    df_resumen.to_excel(ruta, index=False)
    print(f"✅ Archivo guardado en: {ruta}")
    return df_resumen
