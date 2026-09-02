import re
from .base import MovimientoParseado, limitar_palabras

BANCO = "Banco de Bogotá"

# --- Patrones Regex ---

# Captura el monto después de 'Monto:'
PATRON_MONTO = re.compile(r"Monto:\s*([\d.,]+)", re.IGNORECASE)

# Captura la cuenta destino o número de teléfono
PATRON_DESTINO = re.compile(
    r"Cuenta\s+Destino:\s*(\S+)", re.IGNORECASE
)

# Captura el resultado de la transacción (exitosa, fallida, etc.)
PATRON_RESULTADO = re.compile(
    r"Resultado:\s*(\w+)", re.IGNORECASE
)


def _a_float(monto_str: str) -> float:
    monto_str = monto_str.strip()
    if "," in monto_str and "." in monto_str:
        if monto_str.rfind(",") > monto_str.rfind("."):
            monto_str = monto_str.replace(".", "").replace(",", ".")
        else:
            monto_str = monto_str.replace(",", "")
    elif "," in monto_str:
        partes = monto_str.split(",")
        monto_str = (
            monto_str.replace(",", ".")
            if len(partes[-1]) == 2
            else monto_str.replace(",", "")
        )
    return float(monto_str)


def parsear(texto: str) -> MovimientoParseado | None:
    # 1. Verificar si la transacción fue exitosa
    m_resultado = PATRON_RESULTADO.search(texto)
    if not m_resultado or m_resultado.group(1).lower() != "exitosa":
        return None  # Si llegó como fallida o no especifica éxito, se descarta

    # 2. Extraer Monto y Cuenta Destino
    m_monto = PATRON_MONTO.search(texto)
    m_destino = PATRON_DESTINO.search(texto)

    if m_monto and m_destino:
        monto_num = _a_float(m_monto.group(1))
        cuenta_destino = m_destino.group(1).strip()

        return {
            "monto": monto_num,
            "tipo": "gasto",
            "comercio": f"Cuenta {cuenta_destino}",
            "banco": BANCO,
        }

    return None