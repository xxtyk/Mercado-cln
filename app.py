import os
import uuid
import requests

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ------------------------
# CLOUDINARY
# ------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# ------------------------
# MONGODB
# ------------------------
MONGO_URI = os.environ.get("MONGO_URI", "")
client = MongoClient(MONGO_URI)
db = client["mercado_cln"]

productos_col = db["productos"]
categorias_col = db["categorias"]

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


def obtener_siguiente_id(coleccion):
    doc = coleccion.find_one(sort=[("id", -1)])
    return (doc.get("id", 0) + 1) if doc else 1


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    try:
        nombre_seguro = secure_filename(archivo.filename)
        resultado = cloudinary.uploader.upload(
            archivo,
            folder="mercado_cln",
            public_id=f"{uuid.uuid4().hex}_{nombre_seguro}",
            resource_type="image"
        )
        return resultado.get("secure_url", "")
    except Exception as e:
        print("Error Cloudinary:", e)
        return ""


# ------------------------
# CARRITO
# ------------------------
def obtener_carrito():
    carrito = session.get("carrito", [])
    return carrito if isinstance(carrito, list) else []


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def total_importe_carrito():
    total = 0
    for item in obtener_carrito():
        try:
            total += float(item.get("precio", 0)) * int(item.get("cantidad", 0))
        except:
            pass
    return total


def total_items_carrito():
    return sum(int(i.get("cantidad", 0)) for i in obtener_carrito())


@app.context_processor
def ctx():
    return dict(
        carrito_cantidad_total=total_items_carrito(),
        carrito_importe_total=total_importe_carrito()
    )


# ------------------------
# RUTAS CLIENTE
# ------------------------
@app.route("/")
def inicio():
    return render_template("portada.html")


@app.route("/catalogo")
def catalogo():
    categorias = list(categorias_col.find({}, {"_id": 0}))
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:id>")
def ver_categoria(id):
    categoria = categorias_col.find_one({"id": id}, {"_id": 0})
    if not categoria:
        return "Categoría no encontrada", 404

    productos = list(productos_col.find({"categoria_id": id}, {"_id": 0}))
    return render_template("categoria.html", categoria=categoria, productos=productos)


# ------------------------
# CARRITO
# ------------------------
@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    producto = productos_col.find_one({"id": id}, {"_id": 0})
    if not producto:
        return redirect(url_for("catalogo"))

    carrito = obtener_carrito()

    existe = next((i for i in carrito if i["producto_id"] == id), None)

    if existe:
        existe["cantidad"] += 1
    else:
        carrito.append({
            "producto_id": id,
            "nombre": producto["nombre"],
            "precio": float(producto["precio"]),
            "cantidad": 1,
            "foto": producto.get("foto", "")
        })

    guardar_carrito(carrito)
    return redirect(request.referrer or url_for("catalogo"))


@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito()
    subtotal = total_importe_carrito()
    return render_template("carrito.html", carrito=carrito, subtotal=subtotal)


@app.route("/carrito/actualizar/<int:indice>", methods=["POST"])
def actualizar_carrito(indice):
    carrito = obtener_carrito()

    if 0 <= indice < len(carrito):
        accion = request.form.get("accion")

        if accion == "sumar":
            carrito[indice]["cantidad"] += 1

        elif accion == "restar":
            carrito[indice]["cantidad"] -= 1
            if carrito[indice]["cantidad"] <= 0:
                carrito.pop(indice)

        elif accion == "eliminar":
            carrito.pop(indice)

    if len(carrito) == 0:
        session.pop("carrito", None)
    else:
        guardar_carrito(carrito)

    return redirect(url_for("ver_carrito"))


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("ver_carrito"))


# ------------------------
# FINALIZAR PEDIDO (WHATSAPP)
# ------------------------
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito = obtener_carrito()
    if not carrito:
        return redirect(url_for("ver_carrito"))

    mensaje = "🛒 *NUEVO PEDIDO*\n\n"

    for item in carrito:
        mensaje += f"{item['cantidad']} x {item['nombre']} - ${int(item['precio'] * item['cantidad'])}\n"

    total = total_importe_carrito()
    mensaje += f"\nTotal: ${int(total)}"

    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

        payload = {
            "chatId": f"{GREEN_API_CHAT_ID}@g.us",
            "message": mensaje
        }

        requests.post(url, json=payload, timeout=20)

    except Exception as e:
        print("Error WhatsApp:", e)

    session.pop("carrito", None)
    session.modified = True

    return redirect(url_for("inicio"))


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = list(categorias_col.find({}, {"_id": 0}))
    productos = list(productos_col.find({}, {"_id": 0}))
    return render_template("admin.html", categorias=categorias, productos=productos)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre", "").strip()
    foto = request.files.get("foto_categoria")

    if not nombre:
        return redirect(url_for("admin"))

    nueva = {
        "id": obtener_siguiente_id(categorias_col),
        "nombre": nombre,
        "foto": guardar_imagen(foto)
    }

    categorias_col.insert_one(nueva)
    return redirect(url_for("admin"))


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    foto = request.files.get("foto_producto")

    if not nombre or not categoria_id:
        return redirect(url_for("admin"))

    nuevo = {
        "id": obtener_siguiente_id(productos_col),
        "nombre": nombre,
        "precio": float(precio or 0),
        "categoria_id": int(categoria_id),
        "foto": guardar_imagen(foto)
    }

    productos_col.insert_one(nuevo)
    return redirect(url_for("admin"))


# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
