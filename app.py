import os
import json
import uuid
from urllib.parse import quote

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

cloudinary.config(
    cloud_name="dosyi726x",
    api_key="942229587198227",
    api_secret="jHn-OlPaUEdfqvCk1DvgTeSUhyQ",
    secure=True
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "uploads")
PRODUCTOS_FILE = os.path.join(BASE_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(BASE_DIR, "categorias.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
COSTO_ENVIO = 40

VENDEDORES = {
    "Mercado en Línea Culiacán": "526679771409",
    "Hector": "526679771409",
    "Silvia": "526674263892",
    "Juan": "526678962503",
    "Cristian": "526673587278",
    "Brissa": "526674283998",
    "Claudia": "526671605229",
    "Amairany": "526677469585",
    "Natalia": "526673513058",
}

# ------------------------
# UTILIDADES
# ------------------------
def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def init_app():
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    if not os.path.exists(CATEGORIAS_FILE):
        with open(CATEGORIAS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)


def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def obtener_siguiente_id(lista):
    ids = []
    for item in lista:
        try:
            ids.append(int(item.get("id", 0)))
        except Exception:
            pass
    return max(ids, default=0) + 1


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    try:
        nombre_seguro = secure_filename(archivo.filename)
        nombre_base = os.path.splitext(nombre_seguro)[0]

        resultado = cloudinary.uploader.upload(
            archivo,
            folder="mercado_cln",
            public_id=f"{uuid.uuid4().hex}_{nombre_base}",
            resource_type="image"
        )

        return resultado.get("secure_url", "")
    except Exception as e:
        print("Error subiendo imagen a Cloudinary:", e)
        return ""


def obtener_categoria_por_id(categoria_id):
    categorias = cargar_json(CATEGORIAS_FILE)
    for categoria in categorias:
        if str(categoria.get("id")) == str(categoria_id):
            return categoria
    return None


def obtener_producto_por_id(producto_id):
    productos = cargar_json(PRODUCTOS_FILE)
    for producto in productos:
        if str(producto.get("id")) == str(producto_id):
            return producto
    return None


def obtener_productos_de_categoria(categoria_id):
    productos = cargar_json(PRODUCTOS_FILE)
    return [p for p in productos if str(p.get("categoria_id")) == str(categoria_id)]


def normalizar_precio(valor):
    try:
        texto = str(valor).replace("$", "").replace(",", "").strip()
        return float(texto) if texto else 0.0
    except Exception:
        return 0.0


def obtener_carrito():
    carrito = session.get("carrito", [])
    return carrito if isinstance(carrito, list) else []


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def total_productos_carrito():
    carrito = obtener_carrito()
    return sum(int(item.get("cantidad", 0)) for item in carrito)


def total_importe_carrito():
    carrito = obtener_carrito()
    total = 0
    for item in carrito:
        precio = normalizar_precio(item.get("precio", 0))
        cantidad = int(item.get("cantidad", 0))
        total += precio * cantidad
    return total


# ------------------------
# CONTEXTO GLOBAL
# ------------------------
@app.context_processor
def inyectar_datos_globales():
    return {
        "carrito_cantidad_total": total_productos_carrito(),
        "carrito_importe_total": total_importe_carrito(),
        "COSTO_ENVIO": COSTO_ENVIO
    }


# ------------------------
# RUTAS CLIENTE
# ------------------------
@app.route("/")
def inicio():
    return render_template("portada.html")


@app.route("/catalogo")
def catalogo():
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:categoria_id>")
def ver_categoria(categoria_id):
    categoria = obtener_categoria_por_id(categoria_id)
    if not categoria:
        return "Categoría no encontrada", 404

    productos = obtener_productos_de_categoria(categoria_id)
    return render_template("categoria.html", categoria=categoria, productos=productos)


@app.route("/producto/<int:producto_id>")
def ver_producto(producto_id):
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return "Producto no encontrado", 404

    categoria = obtener_categoria_por_id(producto.get("categoria_id"))
    return render_template("producto.html", producto=producto, categoria=categoria)


# ------------------------
# CARRITO
# ------------------------
@app.route("/agregar_al_carrito/<int:producto_id>", methods=["POST"])
def agregar_al_carrito(producto_id):
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return redirect(url_for("catalogo"))

    carrito = obtener_carrito()

    cantidad = request.form.get("cantidad", "1")
    descripcion = request.form.get("descripcion", "").strip()

    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except Exception:
        cantidad = 1

    for item in carrito:
        if item["producto_id"] == producto_id and item["descripcion"] == descripcion:
            item["cantidad"] += cantidad
            break
    else:
        carrito.append({
            "producto_id": producto["id"],
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "foto": producto["foto"],
            "cantidad": cantidad,
            "descripcion": descripcion
        })

    guardar_carrito(carrito)
    return redirect(url_for("ver_categoria", categoria_id=producto["categoria_id"]))


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)
    return render_template("admin.html", categorias=categorias, productos=productos, vendedores=VENDEDORES)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre", "").strip()
    foto = request.files.get("foto_categoria")

    if not nombre:
        return redirect(url_for("admin"))

    categorias = cargar_json(CATEGORIAS_FILE)
    nueva_categoria = {
        "id": obtener_siguiente_id(categorias),
        "nombre": nombre,
        "foto": guardar_imagen(foto)
    }

    categorias.append(nueva_categoria)
    guardar_json(CATEGORIAS_FILE, categorias)

    return redirect(url_for("admin"))


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()
    foto = request.files.get("foto_producto")

    if not nombre or not categoria_id:
        return redirect(url_for("admin"))

    if vendedor not in VENDEDORES:
        vendedor = "Mercado en Línea Culiacán"

    productos = cargar_json(PRODUCTOS_FILE)

    nuevo_producto = {
        "id": obtener_siguiente_id(productos),
        "nombre": nombre,
        "precio": normalizar_precio(precio),
        "descripcion": descripcion,
        "categoria_id": int(categoria_id),
        "foto": guardar_imagen(foto),
        "vendedor": vendedor
    }

    productos.append(nuevo_producto)
    guardar_json(PRODUCTOS_FILE, productos)

    return redirect(url_for("admin"))


# ------------------------
# INICIO
# ------------------------
init_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
