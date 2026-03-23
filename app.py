import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTOS_FILE = os.path.join(BASE_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(BASE_DIR, "categorias.json")


# ---------- FUNCIONES ----------
def cargar_json(ruta, valor_inicial):
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(valor_inicial, f, ensure_ascii=False, indent=4)

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return valor_inicial


def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def cargar_productos():
    return cargar_json(PRODUCTOS_FILE, [])


def guardar_productos(productos):
    guardar_json(PRODUCTOS_FILE, productos)


def cargar_categorias():
    return cargar_json(CATEGORIAS_FILE, [])


def guardar_categorias(categorias):
    guardar_json(CATEGORIAS_FILE, categorias)


# ---------- RUTAS ----------
@app.route("/")
def index():
    productos = cargar_productos()
    categorias = cargar_categorias()
    return render_template("index.html", productos=productos, categorias=categorias)


@app.route("/admin")
def admin():
    productos = cargar_productos()
    categorias = cargar_categorias()
    return render_template("admin.html", productos=productos, categorias=categorias)


@app.route("/vendedor/<vendedor_id>")
def vendedor(vendedor_id):
    productos = cargar_productos()
    return render_template("vendedor.html", vendedor_id=vendedor_id, productos=productos)


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    productos = cargar_productos()

    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria = request.form.get("categoria", "").strip()
    foto = request.form.get("foto", "").strip()

    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "categoria": categoria,
        "foto": foto
    }

    productos.append(nuevo)
    guardar_productos(productos)

    return redirect(url_for("admin"))


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    categorias = cargar_categorias()

    nombre = request.form.get("nombre_categoria", "").strip()

    if nombre:
        existe = False
        for c in categorias:
            if isinstance(c, dict):
                if c.get("nombre", "").strip().lower() == nombre.lower():
                    existe = True
                    break
            elif isinstance(c, str):
                if c.strip().lower() == nombre.lower():
                    existe = True
                    break

        if not existe:
            categorias.append({
                "nombre": nombre
            })
            guardar_categorias(categorias)

    return redirect(url_for("admin"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
