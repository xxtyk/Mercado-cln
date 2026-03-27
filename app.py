import os
import uuid
import requests

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from pymongo import MongoClient, DESCENDING

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
# MONGODB
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
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            tls=True,
            retryWrites=True
        )

        mongo_client.admin.command("ping")

        mongo_db = mongo_client["mercado_cln"]
        productos_col = mongo_db["productos"]
        categorias_col = mongo_db["categorias"]

        productos_col.create_index("id", unique=True)
        categorias_col.create_index("id", unique=True)
        productos_col.create_index("categoria_id")

        print("✅ MongoDB conectado correctamente")

    except Exception as e:
        print("❌ Error conectando MongoDB:", e)
else:
    print("❌ Falta MONGO_URI")

# ------------------------
# CONFIG
# ------------------------
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
COSTO_ENVIO = 40

GREEN_API_INSTANCE = os.environ.get("GREEN_API_INSTANCE", "").strip()
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN", "").strip()
GREEN_API_CHAT_ID = os.environ.get("GREEN_API_CHAT_ID", "").strip()

VENDEDORES = {
    "Mercado en Línea Culiacán": "526679771409",
}

# ------------------------
# UTILIDADES
# ------------------------
def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    try:
        resultado = cloudinary.uploader.upload(
            archivo,
            folder="mercado_cln",
            public_id=f"{uuid.uuid4().hex}",
            resource_type="image"
        )
        return resultado.get("secure_url", "")
    except Exception as e:
        print("❌ Error Cloudinary:", e)
        return ""


def obtener_siguiente_id(coleccion):
    ultimo = coleccion.find_one({}, {"id": 1}, sort=[("id", DESCENDING)])
    return int(ultimo.get("id", 0)) + 1 if ultimo else 1


# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    categorias = list(categorias_col.find({}, {"_id": 0})) if categorias_col else []
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:id>")
def categoria(id):
    productos = list(productos_col.find({"categoria_id": id}, {"_id": 0})) if productos_col else []
    return render_template("categoria.html", productos=productos)


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = list(categorias_col.find({}, {"_id": 0})) if categorias_col else []
    productos = list(productos_col.find({}, {"_id": 0})) if productos_col else []
    return render_template("admin.html", categorias=categorias, productos=productos)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre")
    foto = request.files.get("foto_categoria")

    if not nombre:
        return redirect("/admin")

    categorias_col.insert_one({
        "id": obtener_siguiente_id(categorias_col),
        "nombre": nombre,
        "foto": guardar_imagen(foto)
    })

    return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    categoria_id = request.form.get("categoria_id")
    descripcion = request.form.get("descripcion")
    foto = request.files.get("foto_producto")

    if not nombre or not categoria_id:
        return redirect("/admin")

    productos_col.insert_one({
        "id": obtener_siguiente_id(productos_col),
        "nombre": nombre,
        "precio": float(precio),
        "categoria_id": int(categoria_id),
        "descripcion": descripcion,
        "foto": guardar_imagen(foto)
    })

    return redirect("/admin")


# ------------------------
# WHATSAPP
# ------------------------
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    texto = "Nuevo pedido desde la app"

    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

    payload = {
        "chatId": f"{GREEN_API_CHAT_ID}@g.us",
        "message": texto
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error WhatsApp:", e)

    return redirect("/")


# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
