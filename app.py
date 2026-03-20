import os
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDINARY ---
# Lee las llaves que pusiste en el Panel de Render
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

# Lista temporal para guardar productos (En Render se borra al reiniciar, 
# luego podemos conectar una base de datos)
productos = []

@app.route('/')
def index():
    # Esta es tu página principal donde se verán los productos
    return render_template('index.html', productos=productos)

@app.route('/admin')
def admin():
    # Tu panel para subir cosas
    return render_template('admin.html')

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    nombre = request.form.get('producto')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')
    archivo = request.files.get('archivo')

    if archivo:
        # 1. Sube la imagen a Cloudinary
        upload_result = cloudinary.uploader.upload(archivo)
        url_imagen = upload_result['secure_url']
        
        # 2. Guarda la info del producto en la lista
        nuevo_prod = {
            'nombre': nombre,
            'precio': precio,
            'categoria': categoria,
            'imagen': url_imagen
        }
        productos.append(nuevo_prod)
        
    return redirect(url_for('index'))

# --- BLOQUE FINAL PARA RENDER ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
