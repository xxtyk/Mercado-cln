import os
import json
import uuid
import requests

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "dosyi726x"),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
    secure=True
)

# 🔥 CAMBIO IMPORTANTE (NO SE BORREN DATOS)
DATA_DIR = os.environ.get("DATA_DIR", os.path.abspath(os.path.dirname(__file__)))

STATIC_FOLDER = os.path.join(DATA_DIR, "static")
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "uploads")
PRODUCTOS_FILE = os.path.join(DATA_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(DATA_DIR, "categorias.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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


def init_app():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    if not os.path.exists(CATEGORIAS_FILE):
        with open(CATEGORIAS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def obtener_siguiente_id(lista):
    return max([int(x.get("id", 0)) for x in lista], default=0) + 1


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    try:
        resultado = cloudinary.uploader.upload(
            archivo,
            folder="mercado_cln"
        )
        return resultado.get("secure_url", "")
    except:
        return ""


def obtener_carrito():
    return session.get("carrito", [])


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def total_importe_carrito():
    total = 0
    for item in obtener_carrito():
        total += item["precio"] * item["cantidad"]
    return total


# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    return render_template("portada.html")


@app.route("/catalogo")
def catalogo():
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:id>")
def ver_categoria(id):
    productos = cargar_json(PRODUCTOS_FILE)
    filtrados = [p for p in productos if p["categoria_id"] == id]
    return render_template("categoria.html", productos=filtrados, categoria={"nombre": "Categoría"})


@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    productos = cargar_json(PRODUCTOS_FILE)
    producto = next((p for p in productos if p["id"] == id), None)

    carrito = obtener_carrito()

    if producto:
        carrito.append({
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": 1
        })

    guardar_carrito(carrito)
    return redirect(request.referrer)


@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito()
    subtotal = total_importe_carrito()
    return render_template("carrito.html", carrito=carrito, subtotal=subtotal)


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("ver_carrito"))


# ------------------------
# FINALIZAR PEDIDO (WHATSAPP GRUPO)
# ------------------------
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito = obtener_carrito()

    mensaje = "🛒 *PEDIDO NUEVO*\n\n"

    for item in carrito:
        mensaje += f"{item['cantidad']} x {item['nombre']} - ${item['precio']}\n"

    mensaje += f"\nTotal: ${total_importe_carrito()}"

    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

        payload = {
            "chatId": f"{GREEN_API_CHAT_ID}@g.us",
            "message": mensaje
        }

        requests.post(url, json=payload)

    except Exception as e:
        print("Error:", e)

    session.pop("carrito", None)
    return redirect(url_for("inicio"))


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    productos = cargar_json(PRODUCTOS_FILE)

    foto = guardar_imagen(request.files.get("foto_producto"))

    nuevo = {
        "id": obtener_siguiente_id(productos),
        "nombre": request.form.get("nombre"),
        "precio": float(request.form.get("precio")),
        "categoria_id": int(request.form.get("categoria_id")),
        "foto": foto
    }

    productos.append(nuevo)
    guardar_json(PRODUCTOS_FILE, productos)

    return redirect(url_for("admin"))


# ------------------------
init_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
