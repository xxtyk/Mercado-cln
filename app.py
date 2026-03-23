import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "productos.json")

def cargar_productos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

def guardar_productos(productos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=4)

@app.route("/")
def index():
    productos = cargar_productos()
    categorias = []

    for p in productos:
        categoria = p.get("categoria", "").strip()
        if categoria and categoria not in categorias:
            categorias.append(categoria)

    return render_template("index.html", categorias=categorias)

@app.route("/categoria/<nombre_categoria>")
def ver_categoria(nombre_categoria):
    productos = cargar_productos()

    productos_categoria = [
        p for p in productos
        if p.get("categoria", "").strip().lower() == nombre_categoria.strip().lower()
    ]

    return render_template(
        "categoria.html",
        nombre_categoria=nombre_categoria,
        productos=productos_categoria
    )

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    return redirect(request.referrer or url_for("index"))

@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    productos = cargar_productos()

    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria = request.form.get("categoria", "").strip()
    foto = request.form.get("foto", "").strip()

    nuevo_producto = {
        "nombre": nombre,
        "precio": precio,
        "categoria": categoria,
        "foto": foto
    }

    productos.append(nuevo_producto)
    guardar_productos(productos)

    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
