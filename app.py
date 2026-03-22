import os
import json
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ==============================
# ☁️ CLOUDINARY (YA CONFIGURADO)
# ==============================
cloudinary.config(
    cloud_name="dosyi726x",
    api_key="942229587198227",
    api_secret="JHn-OlPaUEdfqvCk1DvgTeSUhyQ"
)

# ==============================
# 📁 BASE DE DATOS
# ==============================
DB_FILE = "productos.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

# ==============================
# 📦 CARGAR PRODUCTOS
# ==============================
def cargar_productos():
    try:
        with open(DB_FILE, "r") as f:
            productos = json.load(f)

            for p in productos:
                if "imagen" not in p or not p["imagen"]:
                    p["imagen"] = "https://via.placeholder.com/300"

            return productos
    except:
        return []

# ==============================
# 💾 GUARDAR PRODUCTOS
# ==============================
def guardar_productos(productos):
    with open(DB_FILE, "w") as f:
        json.dump(productos, f, indent=4)

# ==============================
# 🏠 CATÁLOGO
# ==============================
@app.route('/')
def inicio():
    productos = cargar_productos()
    return render_template("index.html", productos=productos)

# ==============================
# ⚙️ ADMIN
# ==============================
@app.route('/admin')
def admin():
    productos = cargar_productos()
    return render_template("admin.html", productos=productos)

# ==============================
# ➕ AGREGAR (SUBE IMAGEN DIRECTO)
# ==============================
@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    archivo = request.files.get("imagen")

    imagen_url = ""

    if archivo:
        resultado = cloudinary.uploader.upload(archivo)
        imagen_url = resultado.get("secure_url")

    productos = cargar_productos()

    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "imagen": imagen_url
    }

    productos.append(nuevo)
    guardar_productos(productos)

    return redirect(url_for('admin'))

# ==============================
# 🗑️ ELIMINAR
# ==============================
@app.route('/eliminar/<int:index>')
def eliminar(index):
    productos = cargar_productos()

    if 0 <= index < len(productos):
        productos.pop(index)
        guardar_productos(productos)

    return redirect(url_for('admin'))

# ==============================
# 🚀 SERVIDOR
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
