import os
import uuid
import requests
import ssl
import pymongo

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient, DESCENDING

# --- BLOQUE DE DEPURACIÓN PARA SERGIO (AL PRINCIPIO) ---
print("--- DATOS DE ENTORNO PARA SERGIO ---")
print("OPENSSL:", ssl.OPENSSL_VERSION)
print("PYMONGO:", pymongo.version)
print("------------------------------------")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ------------------------
# CLOUDINARY
# ------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip(),
    api_key=os.environ.get("CLOUDINARY_API_KEY", "").strip(),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "").strip(),
    secure=True
)

# ------------------------
# MONGODB (CONFIGURACIÓN)
# ------------------------
MONGO_URI = os.environ.get("MONGO_URI", "").strip()

mongo_client = None
mongo_db = None
productos_col = None
categorias_col = None

if MONGO_URI:
    try:
        mongo_client = MongoClient(
            MONGO_URI,
            connect=True,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=10000
        )
        mongo_db = mongo_client["mercado_cln"]
        productos_col = mongo_db["productos"]
        categorias_col = mongo_db["categorias"]
    except Exception as e:
        print(f"❌ Error inicial Mongo: {e}")

# ------------------------
# RUTAS Y FUNCIONES (TU LÓGICA)
# ------------------------
# ... (Aquí va todo tu código de rutas como /, /admin, etc.) ...

# ------------------------
# LANZAMIENTO Y PRUEBA FINAL (LO QUE PIDIÓ SERGIO)
# ------------------------
if __name__ == "__main__":
    # Primero intentamos el ping que pidió Sergio
    if mongo_client:
        print("--- PROBANDO CONEXIÓN (PING) ---")
        try:
            mongo_client.admin.command('ping')
            print("✅ Conexión exitosa")
        except Exception as e:
            print("❌ Error al hacer la conexión:", e)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
