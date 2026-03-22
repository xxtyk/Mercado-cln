import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

DB_FILE = "productos.json"

# Crear archivo si no existe
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

# Cargar productos
def cargar_productos():
    with open(DB_FILE, "r") as f:
        return json.load(f)

# Guardar productos
def guardar_productos(productos):
    with open(DB_FILE, "w") as f:
        json.dump(productos, f, indent=4)

# VISTA CLIENTE
@app.route('/')
def index():
    productos = cargar_productos()
    return render_template("index.html", productos=productos)

# PANEL ADMIN
@app.route('/admin')
def admin():
    productos = cargar_productos()
    return render_template("admin.html", productos=productos)

# AGREGAR PRODUCTO
@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    imagen = request.form.get("imagen")

    productos = cargar_productos()

    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "imagen": imagen
    }

    productos.append(nuevo)
    guardar_productos(productos)

    return redirect(url_for('admin'))

# PUERTO PARA RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
