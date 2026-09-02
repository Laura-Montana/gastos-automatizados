import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ["SUPABASE_URL"]
key = os.environ["SUPABASE_KEY"]
supabase = create_client(url, key)

def guardar_movimiento(movimiento: dict):
    return supabase.table("movimientos").insert(movimiento).execute()

