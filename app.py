import os
import json
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# CONFIG CLOUDINARY
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

DB_FILE = "productos.json"

# CARGAR PRODUCTOS
def cargar_productos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def guardar_productos(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# HOME
@app.route('/')
def index():
    productos = cargar_productos()
    activos = [p for p in productos if p.get('activo', True)]
    return render_template('index.html', productos=activos)

# RUTA DE CATEGORÍAS
@app.route('/categoria/<nombre>')
def categoria(nombre):
    productos = cargar_productos()
    filtrados = [p for p in productos if p.get('categoria') == nombre and p.get('activo', True)]
    return render_template('categoria.html', productos=filtrados, categoria=nombre)

# ADMIN
@app.route('/admin')
def admin():
    productos = cargar_productos()
    return render_template('admin.html', productos=productos)

# AGREGAR PRODUCTO
@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    productos = cargar_productos()
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria_prod = request.form.get('categoria')
    archivo = request.files.get('archivo')

    url_imagen = ""
    if archivo:
        upload = cloudinary.uploader.upload(archivo)
        url_imagen = upload['secure_url']

    nuevo = {
        "id": len(productos),
        "nombre": nombre,
        "precio": int(precio),
        "categoria": categoria_prod,
        "imagen": url_imagen,
        "activo": True
    }

    productos.append(nuevo)
    guardar_productos(productos)
    return redirect('/admin')

# ACTIVAR / DESACTIVAR
@app.route('/toggle/<int:id>')
def toggle(id):
    productos = cargar_productos()
    for p in productos:
        if p['id'] == id:
            p['activo'] = not p.get('activo', True)
    guardar_productos(productos)
    return redirect('/admin')

# WHATSAPP (PEDIDOS AL GRUPO)
@app.route('/pedido', methods=['POST'])
def pedido():
    nombre = request.form.get('nombre')
    colonia = request.form.get('colonia')
    direccion = request.form.get('direccion')
    total = request.form.get('total')
    envio = request.form.get('envio')

    mensaje = f"NUEVO PEDIDO:\n\nCliente: {nombre}\nColonia: {colonia}\nDirección: {direccion}\nTotal: ${total}\nEnvío: ${envio}"
    
    # Enlace de tu grupo de WhatsApp
    link_grupo = f"https://chat.whatsapp.com/HtBWXyZmMAxJImgPY5SRXU?text={mensaje}"

    return redirect(
