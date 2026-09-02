import re
from .base import MovimientoParseado, limitar_palabras

BANCO = "Nequi"

# Listo tu pago en Claro Móvil
# Pagaste con Nequi tu factura por $34.541.
PATRON_PAGO_TITULO = re.compile(
    r"Listo tu pago en\s+(.+?)\s+Pagaste", re.IGNORECASE
)
PATRON_PAGO_FACTURA = re.compile(
    r"Pagaste con Nequi tu factura por\s+\$([\d.,]+)", re.IGNORECASE
)

# Recibiste 43.000 de *** el 33 de julio de 2026 a las 2:40 p.m...
PATRON_RECIBIDO = re.compile(
    r"Recibiste\s+\$?([\d.,]+)\s+de\s+(.+?)\s+el\s+\d", re.IGNORECASE
)

# Hiciste una recarga a tullave de $15.930.
PATRON_RECARGA = re.compile(
    r"Hiciste una recarga a\s+(.+?)\s+de\s+\$([\d.,]+)", re.IGNORECASE
)

# Enviaste $50.000 a Juan Pérez.
PATRON_ENVIO = re.compile(
    r"Enviaste\s+\$?([\d.,]+)\s+a\s+(.+?)(?:\.|$)", re.IGNORECASE
)
PATRON_COMPRA = re.compile(
    r"Compra(?:ste)?\s+por\s+\$?([\d.,]+)\s+en\s+(.+?)(?:\.|$)", re.IGNORECASE
)


def _a_float(monto_str: str) -> float:
    return float(monto_str.replace(".", "").replace(",", "."))


def parsear(texto: str) -> MovimientoParseado | None:
    # Pago de factura/servicio: comercio y monto vienen en frases separadas
    m_titulo = PATRON_PAGO_TITULO.search(texto)
    m_factura = PATRON_PAGO_FACTURA.search(texto)
    if m_titulo and m_factura:
        return {
            "monto": _a_float(m_factura.group(1)),
            "tipo": "gasto",
            "comercio": limitar_palabras(m_titulo.group(1).strip()),
            "banco": BANCO,
        }

    if m := PATRON_RECIBIDO.search(texto):
        return {
            "monto": _a_float(m.group(1)),
            "tipo": "ingreso",
            "comercio": limitar_palabras(m.group(2).strip()),
            "banco": BANCO,
        }
    if m := PATRON_RECARGA.search(texto):
        return {
            "monto": _a_float(m.group(2)),
            "tipo": "gasto",
            "comercio": limitar_palabras(m.group(1).strip()),
            "banco": BANCO,
        }
    if m := PATRON_ENVIO.search(texto):
        return {
            "monto": _a_float(m.group(1)),
            "tipo": "gasto",
            "comercio": limitar_palabras(m.group(2).strip()),
            "banco": BANCO,
        }
    if m := PATRON_COMPRA.search(texto):
        return {
            "monto": _a_float(m.group(1)),
            "tipo": "gasto",
            "comercio": limitar_palabras(m.group(2).strip()),
            "banco": BANCO,
        }
    return None