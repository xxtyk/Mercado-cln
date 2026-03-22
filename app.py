import os
import json
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# ==============================
# ☁️ CONFIGURACIÓN CLOUDINARY
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

# ==============================
# 🔹 FUNCIONES ÚTILES
# ==============================
def cargar_productos():
    if not os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "w") as f:
            json.dump([], f)
    with open(PRODUCTOS_FILE, "r") as f:
        try:
            productos = json.load(f)
        except:
            productos = []
    for p in productos:
        if "imagen" not in p or not p["imagen"]:
            p["imagen"] = "https://via.placeholder.com/300"
    return productos

def guardar_productos(productos):
    with open(PRODUCTOS_FILE, "w") as f:
        json.dump(productos, f, indent=4)

def cargar_categorias():
    if not os.path.exists(CATEGORIAS_FILE):
        with open(CATEGORIAS_FILE, "w") as f:
            json.dump([], f)
    with open(CATEGORIAS_FILE, "r") as f:
        try:
            categorias = json.load(f)
        except:
            categorias = []
    return categorias

def guardar_categorias(categorias):
    with open(CATEGORIAS_FILE, "w") as f:
        json.dump(categorias, f, indent=4)

# ==============================
# 🏠 RUTAS
# ==============================

# Ruta principal: lista de categorías
@app.route('/')
def inicio():
    categorias = cargar_categorias()
    return render_template("index.html", categorias=categorias)

# Página de productos por categoría
@app.route('/categoria/<nombre>')
def ver_categoria(nombre):
    productos = cargar_productos()
    productos_filtrados = [p for p in productos if p["categoria"] == nombre]
    return render_template("categoria.html", categoria=nombre, productos=productos_filtrados)

# Panel Admin
@app.route('/admin')
def admin():
    productos = cargar_productos()
    categorias = cargar_categorias()
    return render_template("admin.html", productos=productos, categorias=categorias)

# Formulario cargar producto
@app.route('/cargar_producto')
def cargar_producto():
    categorias = cargar_categorias()
    return render_template("cargar_producto.html", categorias=categorias)

# Agregar categoría
@app.route('/editar_categoria', methods=['POST'])
def editar_categoria():
    nombre = request.form.get("nombre")
    categorias = cargar_categorias()
    if nombre not in categorias:
        categorias.append(nombre)
        guardar_categorias(categorias)
    return redirect(url_for('admin'))

# Agregar producto
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

# Eliminar producto
@app.route('/eliminar_producto/<int:index>')
def eliminar_producto(index):
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
