import re
from .base import MovimientoParseado, limitar_palabras

BANCO = "Bancolombia"

# Transferiste $22,200.00 desde tu cuenta 1111 a la cuenta *3065750988 el...
PATRON_TRANSFER_CUENTA = re.compile(
    r"Transferiste\s+\$([\d.,]+)\s+desde\s+tu\s+cuenta\s+\S+\s+a\s+la\s+cuenta\s+(\S+)",
    re.IGNORECASE,
)

# ...transferiste $45,000.00 a la llave @jua456 desde...
PATRON_TRANSFER_LLAVE = re.compile(
    r"transferiste\s+\$([\d.,]+)\s+a\s+la\s+llave\s+(@\S+)\s+desde",
    re.IGNORECASE,
)

# Compraste $3.100,00 en OXXO ESTE 53 con tu T.Deb...
PATRON_COMPRA = re.compile(
    r"Compraste\s+\$([\d.,]+)\s+en\s+(.+?)\s+con\s+tu",
    re.IGNORECASE,
)

# Recibiste un pago de Liquidez de ABB EST EMPRE por $1,100,044.00 en...
PATRON_INGRESO = re.compile(
    r"Recibiste un pago de Liquidez de\s+(.+?)\s+por\s+\$([\d.,]+)",
    re.IGNORECASE,
)

def _a_float(monto_str: str) -> float:
    monto_str = monto_str.strip()
    if "," in monto_str and "." in monto_str:
        if monto_str.rfind(",") > monto_str.rfind("."):
            # la coma está más a la derecha → es el separador decimal (formato europeo)
            monto_str = monto_str.replace(".", "").replace(",", ".")
        else:
            # el punto está más a la derecha → es el separador decimal (formato US)
            monto_str = monto_str.replace(",", "")
    elif "," in monto_str:
        # solo hay comas: si el último grupo tiene 2 dígitos, es decimal; si no, son miles
        partes = monto_str.split(",")
        monto_str = monto_str.replace(",", ".") if len(partes[-1]) == 2 else monto_str.replace(",", "")
    return float(monto_str)


def parsear(texto: str) -> MovimientoParseado | None:
    if m := PATRON_INGRESO.search(texto):
        return {
            "monto": _a_float(m.group(2)),
            "tipo": "ingreso",
            "comercio": limitar_palabras(m.group(1).strip()),
            "banco": BANCO,
        }
    if m := PATRON_COMPRA.search(texto):
        return {
            "monto": _a_float(m.group(1)),
            "tipo": "gasto",
            "comercio": limitar_palabras(m.group(2).strip()),
            "banco": BANCO,
        }
    if m := PATRON_TRANSFER_LLAVE.search(texto):
        return {
            "monto": _a_float(m.group(1)),
            "tipo": "gasto",
            "comercio": f"Llave {m.group(2)}",
            "banco": BANCO,
        }
    if m := PATRON_TRANSFER_CUENTA.search(texto):
        return {
            "monto": _a_float(m.group(1)),
            "tipo": "gasto",
            "comercio": f"Cuenta {m.group(2)}",
            "banco": BANCO,
        }
    return None