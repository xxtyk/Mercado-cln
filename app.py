import os
import uuid
import requests
import certifi

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
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
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=15000,
            socketTimeoutMS=15000
        )

        mongo_client.admin.command("ping")

        mongo_db = mongo_client["mercado_cln"]
        productos_col = mongo_db["productos"]
        categorias_col = mongo_db["categorias"]

        print("✅ MONGO CONECTADO OK")

    except Exception as e:
        print("❌ Error conectando MongoDB:", str(e))
        mongo_client = None
        mongo_db = None
        productos_col = None
        categorias_col = None
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
        print("❌ Error Cloudinary:", str(e))
        return ""


def obtener_siguiente_id(coleccion):
    if coleccion is None:
        return 1

    ultimo = coleccion.find_one({}, {"id": 1}, sort=[("id", DESCENDING)])
    return int(ultimo.get("id", 0)) + 1 if ultimo else 1


def convertir_float(valor, default=0):
    try:
        return float(valor)
    except:
        return float(default)


# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    categorias = list(categorias_col.find({}, {"_id": 0})) if categorias_col else []
    return render_template("index.html", categorias=categorias)


@app.route("/admin")
def admin():
    categorias = list(categorias_col.find({}, {"_id": 0})) if categorias_col else []
    productos = list(productos_col.find({}, {"_id": 0})) if productos_col else []
    return render_template("admin.html", categorias=categorias, productos=productos)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    try:
        if categorias_col is None:
            print("❌ Mongo no conectado")
            return redirect("/admin")

        nombre = request.form.get("nombre")
        foto = request.files.get("foto")

        if not nombre:
            return redirect("/admin")

        foto_url = guardar_imagen(foto) if foto else ""

        categorias_col.insert_one({
            "id": obtener_siguiente_id(categorias_col),
            "nombre": nombre,
            "foto": foto_url
        })

        print("✅ Categoría guardada")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error guardando categoría:", str(e))
        return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    try:
        if productos_col is None:
            print("❌ Mongo no conectado")
            return redirect("/admin")

        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        categoria_id = request.form.get("categoria_id")
        descripcion = request.form.get("descripcion")
        foto = request.files.get("foto_producto")

        productos_col.insert_one({
            "id": obtener_siguiente_id(productos_col),
            "nombre": nombre,
            "precio": convertir_float(precio),
            "categoria_id": int(categoria_id),
            "descripcion": descripcion,
            "foto": guardar_imagen(foto)
        })

        print("✅ Producto guardado")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error producto:", str(e))
        return redirect("/admin")


@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
