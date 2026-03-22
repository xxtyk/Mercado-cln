import os
import json
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ==========================================
# 🔥 CONFIGURACIÓN CLOUDINARY (LLAVES LISTAS)
# ==========================================
cloudinary.config(
    cloud_name = "dosyi726x", 
    api_key = "942229587198227", 
    api_secret = "JHn-OlPaUEdfqvCk1DvgTeSUhyQ"
)

DB_FILE = "productos.json"

# Crear el archivo de base de datos si no existe
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        json.dump([], f)

def cargar_productos():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                return json.load(f)
        return []
    except:
        return []

def guardar_productos(productos):
    with open(DB_FILE, "w") as f:
        json.dump(productos, f, indent=4)

# ==========================================
# 🏠 RUTAS DE MERCADO CLN
# ==========================================

@app.route('/')
def inicio():
    productos = cargar_productos()
    return render_template("index.html", productos=productos)

@app.route('/admin')
def admin():
    productos = cargar_productos()
    return render_template("admin.html", productos=productos)

@app.route('/admin/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    file = request.files.get('imagen')

    # Subida automática a la nube de Cloudinary
    if file:
        try:
            resultado = cloudinary.uploader.upload(file)
            url_imagen = resultado['secure_url']
        except Exception as e:
            print(f"Error subiendo a Cloudinary: {e}")
            url_imagen = "https://via.placeholder.com/300"
    else:
        url_imagen = "https://via.placeholder.com/300"

    productos = cargar_productos()
    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "imagen": url_imagen
    }
    productos.append(nuevo)
    guardar_productos(productos)

    return redirect(url_for('admin'))

@app.route('/eliminar/<int:index>')
def eliminar(index):
    productos = cargar_productos()
    if 0 <= index < len(productos):
        productos.pop(index)
        guardar_productos(productos)
    return redirect(url_for('admin'))

# ==========================================
# 🚀 ARRANQUE PARA RENDER
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
