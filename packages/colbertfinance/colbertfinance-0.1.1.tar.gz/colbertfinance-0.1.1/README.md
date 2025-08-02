# colbertfinance

📈 Librería en Python para descargar precios de cierre diarios de acciones desde Yahoo Finance y exportarlos a Excel.

## Instalación local

```bash
pip install .
```

## Uso

```python
from colbertfinance import descargar_cierres

descargar_cierres(["AAPL", "GOOG"], años=3)
```
