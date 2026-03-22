import os
import json
from flask import Flask, render_template, request, redirect, url_for

# Cloudinary
try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    cloudinary = None
    print("⚠️ Cloudinary no instalado")

app = Flask(__name__)

# ------------------------------
# ☁️ CONFIGURACIÓN CLOUDINARY
# ------------------------------
if cloudinary:
    cloudinary.config(
        cloud_name="dosyi726x",
        api_key="942229587198227",
        api_secret="JHn-OlPaUEdfqvCk1DvgTeSUhyQ"
    )

# ------------------------------
# 📁 ARCHIVO DE PRODUCTOS
# ------------------------------
DB_FILE = "productos.json"

# Crear productos.json automáticamente si no existe
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f:
        f.write("[]")  # JSON vacío válido

# ------------------------------
# CARGAR PRODUCTOS
# ------------------------------
def cargar_productos():
    try:
        with open(DB_FILE, "r") as f:
            contenido = f.read().strip()
            if not contenido:
                return []
            productos = json.loads(contenido)
            # asegurar que siempre haya imagen
            for p in productos:
                if not p.get("imagen"):
                    p["imagen"] = "https://via.placeholder.com/300"
            return productos
    except Exception as e:
        print("ERROR PRODUCTOS:", e)
        return []

# ------------------------------
# GUARDAR PRODUCTOS
# ------------------------------
def guardar_productos(productos):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(productos, f, indent=4)
    except Exception as e:
        print("ERROR GUARDAR:", e)

# ------------------------------
# RUTA PRINCIPAL / CATÁLOGO
# ------------------------------
@app.route('/')
def inicio():
    productos = cargar_productos()
    # Asegúrate que el archivo HTML se llame exactamente index.html en /templates
    return render_template("index.html", productos=productos)

# ------------------------------
# ADMIN
# ------------------------------
@app.route('/admin')
def admin():
    productos = cargar_productos()
    return render_template("admin.html", productos=productos)

# ------------------------------
# AGREGAR PRODUCTO
# ------------------------------
@app.route('/agregar', methods=['POST'])
def agregar():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    archivo = request.files.get("imagen")

    imagen_url = ""

    if archivo and cloudinary:
        try:
            resultado = cloudinary.uploader.upload(archivo)
            imagen_url = resultado.get("secure_url")
        except Exception as e:
            print("ERROR SUBIDA CLOUDINARY:", e)

    productos = cargar_productos()
    nuevo = {"nombre": nombre, "precio": precio, "imagen": imagen_url}
    productos.append(nuevo)
    guardar_productos(productos)

    return redirect(url_for('admin'))

# ------------------------------
# ELIMINAR PRODUCTO
# ------------------------------
@app.route('/eliminar/<int:index>')
def eliminar(index):
    productos = cargar_productos()
    if 0 <= index < len(productos):
        productos.pop(index)
        guardar_productos(productos)
    return redirect(url_for('admin'))

# ------------------------------
# SERVIDOR (RENDER)
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
