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
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_productos(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

productos = cargar_productos()

# HOME
@app.route('/')
def index():
    activos = [p for p in productos if p['activo']]
    return render_template('index.html', productos=activos)

# ADMIN
@app.route('/admin')
def admin():
    return render_template('admin.html', productos=productos)

# AGREGAR PRODUCTO
@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')
    archivo = request.files.get('archivo')

    url_imagen = ""
    if archivo:
        upload = cloudinary.uploader.upload(archivo)
        url_imagen = upload['secure_url']

    nuevo = {
        "id": len(productos),
        "nombre": nombre,
        "precio": int(precio),
        "categoria": categoria,
        "imagen": url_imagen,
        "activo": True
    }

    productos.append(nuevo)
    guardar_productos(productos)
    return redirect('/admin')

# ACTIVAR / DESACTIVAR
@app.route('/toggle/<int:id>')
def toggle(id):
    for p in productos:
        if p['id'] == id:
            p['activo'] = not p['activo']
    guardar_productos(productos)
    return redirect('/admin')

# WHATSAPP
@app.route('/pedido', methods=['POST'])
def pedido():
    nombre = request.form.get('nombre')
    colonia = request.form.get('colonia')
    direccion = request.form.get('direccion')
    total = request.form.get('total')
    envio = request.form.get('envio')

    mensaje = f"""
PEDIDO:
Total: ${total}
Envío: ${envio}

Cliente:
{nombre}
Colonia: {colonia}
Dirección: {direccion}
"""

    numero = "5216670000000"  # CAMBIA TU NUMERO
    link = f"https://wa.me/{numero}?text={mensaje}"

    return redirect(link)

# RENDER
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
