from typing import TypedDict, Optional

class MovimientoParseado(TypedDict):
    monto: float
    tipo: str          # "gasto" | "ingreso"
    comercio: Optional[str]
    banco: str

def limitar_palabras(texto: str, max_palabras: int = 2) -> str:
    """Recorta un texto a las primeras N palabras completas."""
    if not texto:
        return texto
    palabras = texto.split()
    return " ".join(palabras[:max_palabras])