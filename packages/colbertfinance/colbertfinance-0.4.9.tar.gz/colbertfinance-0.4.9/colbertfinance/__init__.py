"""
colbertfinance 0.3.3 – API paso-a-paso para enseñar Markowitz.
"""

from .steps import (
    precios,   # PASO 0
    media,     # PASO 1             → PASO_1_media.xlsx
    varcov,    # PASO 2             → PASO_2_varcov.xlsx
    correl,    # PASO 3             → PASO_3_correl.xlsx
    invvar,
    const_stats,       
    descargar_precios_acciones,        # PASO 4             → PASO_4_invvar.xlsx
    unos,     # PASO 5             → PASO_5_unos.xlsx
    const,    # PASO 6             → PASO_6_const.xlsx
    portaf     # PASO 7             → PASO_7_portaf.xlsx
)

from .gui import lanzar_gui         # ← NUEVO


__all__ = ["precios","media","varcov","correl","invvar",
           "unos","const","const_stats","portaf"]
__version__ = "0.4.9"
