import os
import json
from flask import Flask, render_template, request, redirect, url_for

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
# ARCHIVOS JSON
# ------------------------------
PRODUCTOS_FILE = "productos.json"
CATEGORIAS_FILE = "categorias.json"

for archivo in [PRODUCTOS_FILE, CATEGORIAS_FILE]:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)

# ------------------------------
# FUNCIONES DE CARGA / GUARDADO
# ------------------------------
def cargar_json(file_path):
    try:
        with open(file_path, "r") as f:
            contenido = f.read().strip()
            if not contenido:
                return []
            return json.loads(contenido)
    except:
        return []

def guardar_json(data, file_path):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

# ------------------------------
# RUTAS PRINCIPALES
# ------------------------------

@app.route('/')
def inicio():
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template('index.html', categorias=categorias)

@app.route('/categoria/<nombre>')
def categoria(nombre):
    productos = cargar_json(PRODUCTOS_FILE)
    filtrados = [p for p in productos if p.get("categoria") == nombre]
    return render_template('categoria.html', productos=filtrados, categoria=nombre)

# ------------------------------
# ADMIN PANEL
# ------------------------------
@app.route('/admin')
def admin():
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)
    return render_template('admin.html', categorias=categorias, productos=productos)

# ------------------------------
# AGREGAR PRODUCTO
# ------------------------------
@app.route('/agregar_producto', methods=['GET','POST'])
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        descripcion = request.form.get("descripcion")
        categoria = request.form.get("categoria")
        archivo = request.files.get("imagen")
        imagen_url = ""

        if archivo and cloudinary:
            try:
                resultado = cloudinary.uploader.upload(archivo)
                imagen_url = resultado.get("secure_url")
            except:
                imagen_url = ""

        productos = cargar_json(PRODUCTOS_FILE)
        productos.append({
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "categoria": categoria,
            "imagen": imagen_url
        })
        guardar_json(productos, PRODUCTOS_FILE)
        return redirect(url_for('admin'))
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template('cargar_producto.html', categorias=categorias)

# ------------------------------
# EDITAR CATEGORÍA
# ------------------------------
@app.route('/editar_categoria', methods=['GET','POST'])
def editar_categoria():
    if request.method == 'POST':
        nombre = request.form.get("nombre")
        categorias = cargar_json(CATEGORIAS_FILE)
        if nombre not in categorias:
            categorias.append(nombre)
        guardar_json(categorias, CATEGORIAS_FILE)
        return redirect(url_for('admin'))
    return render_template('editar_categoria.html')

# ------------------------------
# ELIMINAR PRODUCTO
# ------------------------------
@app.route('/eliminar_producto/<int:index>')
def eliminar_producto(index):
    productos = cargar_json(PRODUCTOS_FILE)
    if 0 <= index < len(productos):
        productos.pop(index)
        guardar_json(productos, PRODUCTOS_FILE)
    return redirect(url_for('admin'))

# ------------------------------
# ELIMINAR CATEGORÍA
# ------------------------------
@app.route('/eliminar_categoria/<nombre>')
def eliminar_categoria(nombre):
    categorias = cargar_json(CATEGORIAS_FILE)
    categorias = [c for c in categorias if c != nombre]
    guardar_json(categorias, CATEGORIAS_FILE)

    # También eliminar productos de esa categoría
    productos = cargar_json(PRODUCTOS_FILE)
    productos = [p for p in productos if p.get("categoria") != nombre]
    guardar_json(productos, PRODUCTOS_FILE)
    return redirect(url_for('admin'))

# ------------------------------
# SERVIDOR RENDER
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
