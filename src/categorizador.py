import re

_REGLAS_RAW = {
    # Servicios y Telecomunicaciones
    "tullave": "Transporte",
    "claro": "Servicios",
    "movistar": "Servicios",
    "tigo": "Servicios",
    "acueducto": "Servicios",
    "servicio": "Servicios",
    "caja colombiana": "Servicios",  # Colsubsidio
    # Mercado y Restaurantes
    "exito": "Mercado",
    "carulla": "Mercado",
    "d1": "Mercado",
    "oxxo": "Mercado",
    "DOLLARCITY": "Mercado",
    "kfc": "Restaurantes",
    # Transporte
    "uber": "Transporte",
    "didi": "Transporte",
    # Entretenimiento
    "netflix": "Entretenimiento",
    "spotify": "Entretenimiento",
    # Deudas, Tarjetas y Financiero
    "tarjeta de crédito": "Deudas / Tarjetas",
    "fondo rotatorio": "Deudas / Tarjetas",
    "fxa": "Compras",
    "addi": "Deudas / Tarjetas",
}

# Normalizamos las llaves a minúsculas
REGLAS = {clave.lower(): valor for clave, valor in _REGLAS_RAW.items()}

# Patrón para detectar secuencias de 7 a 10 dígitos (números de cuenta o teléfonos en la cadena)
PATRON_NUMERO_CUENTA = re.compile(r"\b\d{7,10}\b")


def categorizar(comercio: str | None, tipo: str) -> str:
    # 1. El tipo manda
    if tipo == "ingreso":
        return "Ingresos"

    if not comercio:
        return "Sin categorizar"

    comercio_lower = comercio.lower()

    # 2. Regla para Transferencias (Llaves, Nequi/Daviplata por teléfono o Cuenta *XXXXX)
    if (
        "llave" in comercio_lower
        or "cuenta" in comercio_lower
        or PATRON_NUMERO_CUENTA.search(comercio_lower)
    ):
        return "Transferencias"

    # 3. Reglas por palabras clave de comercios
    for palabra_clave, categoria in REGLAS.items():
        if palabra_clave in comercio_lower:
            return categoria

    return "Sin categorizar"