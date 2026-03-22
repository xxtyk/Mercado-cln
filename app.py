import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "12345"

USUARIO = "admin"
PASSWORD = "1234"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "productos.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GREEN_API_URL = os.getenv("GREEN_API_URL")
GREEN_API_INSTANCE = os.getenv("GREEN_API_INSTANCE")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")
GREEN_API_CHAT_ID = os.getenv("GREEN_API_CHAT_ID")

VENDEDORES = [
    "Mercado en Línea Culiacán",
    "Silvia",
    "Hector",
    "Juan",
    "Cristian",
    "Amayrani",
    "Brisa",
    "Natalia",
    "Claudia"
]

# =========================
# INICIO
# =========================

def init_app():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

# =========================
# PRODUCTOS
# =========================

def cargar_productos():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except:
        return []

def guardar_productos(productos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, indent=4)

# =========================
# CATEGORÍAS
# =========================

def obtener_categorias():
    productos = cargar_productos()
    categorias = {}

    for p in productos:
        if not isinstance(p, dict):
            continue

        nombre = str(p.get("categoria", "")).strip()
        if nombre and nombre not in categorias:
            categorias[nombre] = p.get("foto", "")

    return [{"nombre": k, "foto": v} for k, v in categorias.items()]

def obtener_categorias_admin():
    productos = cargar_productos()
    categorias = {}

    for p in productos:
        if not isinstance(p, dict):
            continue

        nombre = str(p.get("categoria", "")).strip()
        if nombre and nombre not in categorias:
            categorias[nombre] = p.get("foto", "")

    return categorias

# =========================
# CARRITO
# =========================

def obtener_carrito():
    if "carrito" not in session:
        session["carrito"] = []
    return session["carrito"]

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    producto = request.form.get("producto")
    precio = float(request.form.get("precio", 0))
    foto = request.form.get("foto")

    carrito = obtener_carrito()

    carrito.append({
        "producto": producto,
        "precio": precio,
        "foto": foto,
        "cantidad": 1,
        "total": precio
    })

    session["carrito"] = carrito
    session.modified = True

    return redirect(url_for("carrito"))

@app.route("/carrito")
def carrito():
    carrito = obtener_carrito()
    subtotal = sum(p["total"] for p in carrito)
    return render_template("carrito.html", carrito=carrito, subtotal=subtotal)

@app.route("/vaciar_carrito")
def vaciar_carrito():
    session["carrito"] = []
    return redirect(url_for("carrito"))

# =========================
# TIENDA
# =========================

@app.route("/")
def index():
    categorias = obtener_categorias()
    return render_template("index.html", categorias=categorias)

@app.route("/categoria/<nombre>")
def categoria(nombre):
    productos = cargar_productos()
    filtrados = [p for p in productos if p.get("categoria") == nombre]
    return render_template("categoria.html", productos=filtrados, nombre_categoria=nombre)

@app.route("/checkout")
def checkout():
    carrito = obtener_carrito()

    if not carrito:
        return redirect(url_for("carrito"))

    subtotal = sum(p["total"] for p in carrito)

    return render_template(
        "checkout.html",
        carrito=carrito,
        subtotal=subtotal,
        vendedores=VENDEDORES
    )

# =========================
# FINALIZAR PEDIDO
# =========================

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    nombre = request.form.get("nombre")
    colonia = request.form.get("colonia")
    calle = request.form.get("calle")
    celular = request.form.get("celular")
    entrega = request.form.get("entrega")
    vendedor = request.form.get("vendedor")

    carrito = obtener_carrito()

    subtotal = sum(p["total"] for p in carrito)
    envio = 40 if entrega == "domicilio" else 0
    total = subtotal + envio

    mensaje = f"Pedido de {nombre}\nTotal: ${total}"

    try:
        url = f"{GREEN_API_URL}/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
        requests.post(url, json={
            "chatId": GREEN_API_CHAT_ID,
            "message": mensaje
        })
    except:
        pass

    session["carrito"] = []
    return redirect(url_for("index"))

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["usuario"] == USUARIO and request.form["password"] == PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            flash("Usuario o contraseña incorrectos")

    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    productos = cargar_productos()
    categorias = obtener_categorias_admin()

    return render_template("admin.html", productos=productos, categorias=categorias)

# =========================
# AGREGAR CATEGORIA
# =========================

@app.route("/editar_categoria", methods=["GET", "POST"])
def editar_categoria():
    if request.method == "POST":
        nombre = request.form.get("nombre_categoria")

        productos = cargar_productos()

        productos.append({
            "nombre": nombre,
            "precio": "0",
            "descripcion": "",
            "categoria": nombre,
            "foto": ""
        })

        guardar_productos(productos)

        return redirect(url_for("admin"))

    categorias = obtener_categorias_admin()
    return render_template("producto.html", categorias=categorias)

# =========================
# AGREGAR PRODUCTO
# =========================

@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    descripcion = request.form.get("descripcion")
    categoria = request.form.get("categoria")

    productos = cargar_productos()

    productos.append({
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "categoria": categoria,
        "foto": ""
    })

    guardar_productos(productos)

    return redirect(url_for("admin"))

# =========================
# RUN
# =========================

init_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
