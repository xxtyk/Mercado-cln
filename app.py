import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "12345"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTOS_FILE = os.path.join(BASE_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(BASE_DIR, "categorias.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------------
# INICIALIZAR ARCHIVOS
# ------------------------
def init_app():
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
        json.dump(data, f, ensure_ascii=False, indent=4)

# ------------------------
# INDEX (CLIENTE)
# ------------------------
@app.route("/")
def index():
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("index.html", categorias=categorias)

# ------------------------
# VER CATEGORIA
# ------------------------
@app.route("/categoria/<categoria_nombre>")
def ver_categoria(categoria_nombre):
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)

    categoria = next((c for c in categorias if c["nombre"] == categoria_nombre), None)

    productos_filtrados = [p for p in productos if p.get("categoria") == categoria_nombre]

    return render_template("categoria.html", categoria=categoria, productos=productos_filtrados)

# ------------------------
# AGREGAR AL CARRITO (ARREGLADO)
# ------------------------
@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    producto_id = request.form.get("producto_id")
    cantidad = request.form.get("cantidad", "1")

    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except:
        cantidad = 1

    productos = cargar_json(PRODUCTOS_FILE)
    producto_encontrado = None

    for p in productos:
        if str(p.get("id")) == str(producto_id):
            producto_encontrado = p
            break

    if not producto_encontrado:
        return redirect(request.referrer or url_for("index"))

    carrito = session.get("carrito", [])

    encontrado = False
    for item in carrito:
        if str(item.get("id")) == str(producto_id):
            item["cantidad"] += cantidad
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "id": producto_encontrado.get("id"),
            "nombre": producto_encontrado.get("nombre"),
            "precio": float(producto_encontrado.get("precio", 0)),
            "foto": producto_encontrado.get("foto", ""),
            "cantidad": cantidad
        })

    session["carrito"] = carrito
    session.modified = True

    return redirect(request.referrer or url_for("carrito"))

# ------------------------
# VER CARRITO
# ------------------------
@app.route("/carrito")
def carrito():
    carrito = session.get("carrito", [])

    total = 0
    for item in carrito:
        total += float(item["precio"]) * int(item["cantidad"])

    return render_template("carrito.html", carrito=carrito, total=total)

# ------------------------
# LIMPIAR CARRITO
# ------------------------
@app.route("/limpiar_carrito")
def limpiar_carrito():
    session["carrito"] = []
    return redirect(url_for("carrito"))

# ------------------------
# INICIO
# ------------------------
if __name__ == "__main__":
    init_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
