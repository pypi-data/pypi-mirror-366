"""
colbertfinance 0.3.3 – API paso-a-paso para enseñar Markowitz.
"""

from .steps import (
    precios,   # PASO 0
    media,     # PASO 1             → PASO_1_media.xlsx
    varcov,    # PASO 2             → PASO_2_varcov.xlsx
    correl,    # PASO 3             → PASO_3_correl.xlsx
    invvar,    # PASO 4             → PASO_4_invvar.xlsx
    unos,      # PASO 5             → PASO_5_unos.xlsx
    const,     # PASO 6             → PASO_6_const.xlsx
    portaf     # PASO 7             → PASO_7_portaf.xlsx
)

__all__ = ["precios","media","varcov","correl","invvar",
           "unos","const","portaf"]
__version__ = "0.3.3"
