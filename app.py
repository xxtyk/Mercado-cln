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
# 📁 ARCHIVOS JSON
# ==============================
PRODUCTOS_FILE = "productos.json"
CATEGORIAS_FILE = "categorias.json"
CONFIG_FILE = "config.json"

# Crear archivos si no existen
for file in [PRODUCTOS_FILE, CATEGORIAS_FILE, CONFIG_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            if file == CONFIG_FILE:
                json.dump({"logo": ""}, f)
            else:
                json.dump([], f)

# ==============================
# 📦 FUNCIONES DE CARGA/GUARDADO
# ==============================
def cargar_productos():
    try:
        with open(PRODUCTOS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def guardar_productos(productos):
    with open(PRODUCTOS_FILE, "w") as f:
        json.dump(productos, f, indent=4)

def cargar_categorias():
    try:
        with open(CATEGORIAS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def guardar_categorias(categorias):
    with open(CATEGORIAS_FILE, "w") as f:
        json.dump(categorias, f, indent=4)

def cargar_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {"logo": ""}

def guardar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# ==============================
# 🏠 RUTAS
# ==============================
@app.route('/')
def inicio():
    categorias = cargar_categorias()
    config = cargar_config()
    return render_template("index.html", categorias=categorias, config=config)

@app.route('/categoria/<nombre>')
def ver_categoria(nombre):
    productos = cargar_productos()
    categoria_productos = [p for p in productos if p.get("categoria") == nombre]
    config = cargar_config()
    return render_template("categoria.html", productos=categoria_productos, categoria=nombre, config=config)

@app.route('/admin')
def admin():
    productos = cargar_productos()
    categorias = cargar_categorias()
    config = cargar_config()
    return render_template("admin.html", productos=productos, categorias=categorias, config=config)

# ==============================
# ➕ AGREGAR PRODUCTO
# ==============================
@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    descripcion = request.form.get("descripcion")
    categoria = request.form.get("categoria")
    archivo = request.files.get("imagen")
    imagen_url = ""

    if archivo:
        resultado = cloudinary.uploader.upload(archivo)
        imagen_url = resultado.get("secure_url")

    productos = cargar_productos()
    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "descripcion": descripcion,
        "categoria": categoria,
        "imagen": imagen_url
    }
    productos.append(nuevo)
    guardar_productos(productos)
    return redirect(url_for('admin'))

# ==============================
# ➕ AGREGAR CATEGORÍA
# ==============================
@app.route('/editar_categoria', methods=['POST'])
def editar_categoria():
    nombre = request.form.get("nombre")
    categorias = cargar_categorias()
    if nombre and nombre not in categorias:
        categorias.append(nombre)
        guardar_categorias(categorias)
    return redirect(url_for('admin'))

# ==============================
# 🗑️ ELIMINAR PRODUCTO
# ==============================
@app.route('/eliminar_producto/<int:index>')
def eliminar_producto(index):
    productos = cargar_productos()
    if 0 <= index < len(productos):
        productos.pop(index)
        guardar_productos(productos)
    return redirect(url_for('admin'))

# ==============================
# 🔹 SUBIR LOGO
# ==============================
@app.route('/config_logo', methods=['POST'])
def config_logo():
    archivo = request.files.get("logo")
    if archivo:
        resultado = cloudinary.uploader.upload(archivo)
        logo_url = resultado.get("secure_url")
        config = cargar_config()
        config["logo"] = logo_url
        guardar_config(config)
    return redirect(url_for('admin'))

# ==============================
# 🚀 SERVIDOR
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
