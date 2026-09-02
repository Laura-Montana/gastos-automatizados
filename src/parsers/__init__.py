from . import nequi,bancolombia,banco_de_bogota,nu

PARSERS_POR_REMITENTE = {
    "notificaciones@nequi.com.co": nequi.parsear,
    "somos@nequi.com.co": nequi.parsear,
    "alertasynotificaciones@an.notificacionesbancolombia.com": bancolombia.parsear,  
    "nu@nu.com.co": nu.parsear,
    "NotificacionesBDB@bancodebogota.net": banco_de_bogota.parsear,
}

def obtener_parser(remitente: str):
    return PARSERS_POR_REMITENTE.get(remitente)