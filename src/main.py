from datetime import datetime, timezone
from gmail_client import obtener_correos_recientes
from parsers import obtener_parser
from categorizador import categorizar
from db import guardar_movimiento
from cuentas import CUENTAS

def procesar_cuenta(remitente: str):
    parser = obtener_parser(remitente)
    if not parser:
        print(f"Sin parser para {remitente}")
        return

    correos = obtener_correos_recientes(remitente)
    for correo in correos:
        resultado = parser(correo["texto"])
        if not resultado:
            print(f"No matcheó: {correo['id']}")
            continue

        movimiento = {
            "fecha": datetime.fromtimestamp(int(correo["fecha_epoch_ms"]) / 1000, tz=timezone.utc).date().isoformat(),
            "monto": resultado["monto"],
            "tipo": resultado["tipo"],
            "comercio": resultado["comercio"],
            "categoria": categorizar(resultado["comercio"], resultado["tipo"]),
            "banco": resultado["banco"],
            "correo_id": correo["id"],
        }
        try:
            guardar_movimiento(movimiento)
            print(f"Guardado: {movimiento}")
        except Exception as e:
            print(f"Error guardando (¿duplicado?): {e}")

if __name__ == "__main__":
    for cuenta in CUENTAS:
        procesar_cuenta(cuenta["remitente"])