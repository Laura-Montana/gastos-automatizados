import os
import imaplib
import email
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargar variables de entorno desde el archivo .env
load_dotenv()

def _limpiar_html(html_str: str) -> str:
    """Convierte el HTML del correo en texto plano limpio."""
    soup = BeautifulSoup(html_str, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    return soup.get_text(separator=" ", strip=True)

def _extraer_texto_de_mensaje(msg) -> str:
    """Extrae texto plano o limpia HTML de un mensaje de correo usando imaplib/email."""
    texto_plano = ""
    texto_html = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == "multipart" or part.get("Content-Disposition"):
                continue
                
            content_type = part.get_content_type()
            try:
                cuerpo = part.get_payload(decode=True).decode(errors="ignore")
                if content_type == "text/plain":
                    texto_plano += cuerpo
                elif content_type == "text/html":
                    texto_html += _limpiar_html(cuerpo)
            except Exception:
                continue
    else:
        content_type = msg.get_content_type()
        try:
            cuerpo = msg.get_payload(decode=True).decode(errors="ignore")
            if content_type == "text/plain":
                texto_plano = cuerpo
            elif content_type == "text/html":
                texto_html = _limpiar_html(cuerpo)
        except Exception:
            pass

    return texto_plano or texto_html

def obtener_correos_recientes(remitente_filtro: str) -> list:
    """Conecta a Gmail por IMAP y retorna los correos de los últimos 90 días."""
    usuario = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if not usuario or not password:
        raise ValueError("Faltan credenciales. Revisa tu archivo .env.")

    # Conexión al servidor IMAP de Google
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(usuario, password)
    
    # 1. Seleccionamos la carpeta global 
    mail.select('"[Gmail]/All Mail"')

    # 2. Usamos X-GM-RAW con la consulta encerrada en comillas dobles
    query = f'"from:{remitente_filtro} newer_than:2d"'
    status, mensajes = mail.search(None, "X-GM-RAW", query)
    
    correos = []
    if status == "OK" and mensajes[0]:
        lista_ids = mensajes[0].split()
        for id_correo in lista_ids:
            # Obtener el mensaje completo
            res, msg_data = mail.fetch(id_correo, "(RFC822)")
            if res == "OK":
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                texto = _extraer_texto_de_mensaje(msg)
                
                # Convertir fecha del correo a epoch en milisegundos
                fecha_str = msg.get("Date")
                try:
                    dt = parsedate_to_datetime(fecha_str)
                    fecha_epoch_ms = str(int(dt.timestamp() * 1000))
                except Exception:
                    fecha_epoch_ms = "0"

                correos.append({
                    "id": id_correo.decode("utf-8"),
                    "texto": texto.strip(),
                    "fecha_epoch_ms": fecha_epoch_ms,
                })

    mail.logout()
    return correos

if __name__ == "__main__":
    from cuentas import CUENTAS
    
    todos_los_correos = []
    
    for cuenta in CUENTAS:
        remitente = cuenta.get("remitente")
        print(f"Buscando correos de: {remitente}...")
        
        # Llama a la función que ya construimos
        correos_cuenta = obtener_correos_recientes(remitente)
        todos_los_correos.extend(correos_cuenta)
        
    print(f"\n {len(todos_los_correos)} correos encontrados en total.")

    # Muestra una pequeña muestra de los primeros 3 encontrados en general
    for i, c in enumerate(todos_los_correos[:3], 1):
        print(f"\n--- Muestra Correo #{i} (ID: {c['id']}) ---")
        print(c["texto"][:300])
        print("-" * 50)