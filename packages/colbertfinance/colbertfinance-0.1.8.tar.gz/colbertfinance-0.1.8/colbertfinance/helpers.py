import os, sys

def here(filename: str = "") -> str:
    """
    Devuelve la ruta de la carpeta donde se ejecuta el script principal.
    Si se pasa `filename`, combina la ruta con ese nombre de archivo.
    """
    base = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
    return os.path.join(base, filename) if filename else base
