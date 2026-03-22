import os
import json
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ==============================
# ☁️ CLOUDINARY
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
        f.write("[]")

# ==============================
# 📦 CARGAR PRODUCTOS (MEJORADO)
# ==============================
def cargar_productos():
    try:
        with open(DB_FILE, "r") as f:
            contenido = f.read().strip()

            if not contenido:
                return []

            productos = json.loads(contenido)

            # asegurar imagen válida
            for p in productos:
                if not p.get("imagen"):
                    p["imagen"] = "https://via.placeholder.com/300"

            return productos

    except Exception as e:
        print("ERROR PRODUCTOS:", e)
        return []

# ==============================
# 💾 GUARDAR PRODUCTOS
# ==============================
def guardar_productos(productos):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(productos, f, indent=4)
    except Exception as e:
        print("ERROR GUARDAR:", e)

# ==============================
# 🏠 CATÁLOGO
# ==============================
@app.route('/')
def inicio():
    productos = cargar_productos()
    return render_template("index.html", productos=productos)

# ==============================
# ⚙️ ADMIN (PROTEGIDO)
# ==============================
@app.route('/admin')
def admin():
    try:
        productos = cargar_productos()
        return render_template("admin.html", productos=productos)
    except Exception as e:
        return f"ERROR ADMIN: {e}"

# ==============================
# ➕ AGREGAR PRODUCTO
# ==============================
@app.route('/agregar', methods=['POST'])
def agregar():
    try:
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        archivo = request.files.get("imagen")

        imagen_url = ""

        if archivo and archivo.filename != "":
            resultado = cloudinary.uploader.upload(archivo)
            imagen_url = resultado.get("secure_url")

        productos = cargar_productos()
