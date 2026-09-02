import re
from .base import MovimientoParseado, limitar_palabras

BANCO = "Nu"

# --- Patrones Regex ---

# 1. Pago de servicio (formato estructurado)
# Ejemplo: "Empresa a la cual se realizará el pago: Movistar" + "Monto: $4.240,00"
PATRON_PAGO_SERVICIO_EMPRESA = re.compile(
    r"Empresa\s+a\s+la\s+cual\s+se\s+realizar[aá]\s+el\s+pago:\s*(.+)",
    re.IGNORECASE,
)
PATRON_PAGO_SERVICIO_MONTO = re.compile(
    r"Monto:\s*\$([\d.,]+)",
    re.IGNORECASE,
)

# 2. Pago de Tarjeta de Crédito Nu
# Ejemplo: "Recibimos el pago que hiciste de tu Tarjeta de crédito Nu... Tu pago fue de $25.000,00"
PATRON_PAGO_TC = re.compile(
    r"pago\s+que\s+hiciste\s+de\s+tu\s+Tarjeta\s+de\s+cr[eé]dito\s+Nu.*?Tu\s+pago\s+fue\s+de\s*\$([\d.,]+)",
    re.IGNORECASE | re.DOTALL,
)

# 3. Compra o pago directo en comercio
# Ejemplo: "Pagaste en:\nCAJA COLOMBIANA...\nLa cantidad de:\n$26.200,00"
PATRON_PAGO_COMERCIO = re.compile(
    r"Pagaste\s+en:\s*\n?\s*(.+?)\s*\n?\s*La\s+cantidad\s+de:\s*\n?\s*\$([\d.,]+)",
    re.IGNORECASE,
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
    # Caso 1: Pagaste en [Comercio] / La cantidad de: $[Monto]
    if m := PATRON_PAGO_COMERCIO.search(texto):
        comercio = m.group(1).strip()
        monto = m.group(2)
        return {
            "monto": _a_float(monto),
            "tipo": "gasto",
            "comercio": limitar_palabras(comercio),
            "banco": BANCO,
        }

    # Caso 2: Pago de Tarjeta de Crédito Nu
    if m := PATRON_PAGO_TC.search(texto):
        monto = m.group(1)
        return {
            "monto": _a_float(monto),
            "tipo": "gasto",
            "comercio": "Pago Tarjeta de Crédito Nu",
            "banco": BANCO,
        }

    # Caso 3: Pago de servicio (Movistar, etc.)
    m_monto_serv = PATRON_PAGO_SERVICIO_MONTO.search(texto)
    m_empresa_serv = PATRON_PAGO_SERVICIO_EMPRESA.search(texto)
    if m_monto_serv and m_empresa_serv:
        comercio = m_empresa_serv.group(1).strip()
        return {
            "monto": _a_float(m_monto_serv.group(1)),
            "tipo": "gasto",
            "comercio": limitar_palabras(f"Servicio {comercio}"),
            "banco": BANCO,
        }

    return None