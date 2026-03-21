from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "12345"

# --- CONFIGURACIÓN CLOUDINARY ---
cloudinary.config(
    cloud_name="dosyi726x",
    api_key="942229587198227",
    api_secret="jHn-OlPaUEdfqvCk1DvgTeSUhyQ",
    secure=True
)

# --- ARCHIVOS JSON ---
PRODUCTOS_FILE = "productos.json"
CATEGORIAS_FILE = "categorias.json"
CONFIG_FILE = "config.json"
PEDIDOS_FILE = "pedidos.json"

# --- FUNCIONES AUXILIARES ---
def cargar_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({} if "json" in file_path else [], f)
    with open(file_path, "r") as f:
        return json.load(f)

def guardar_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- RUTAS PRINCIPALES ---
@app.route("/")
def index():
    productos = cargar_json(PRODUCTOS_FILE)
    categorias = cargar_json(CATEGORIAS_FILE)
    config = cargar_json(CONFIG_FILE)
    return render_template("index.html", productos=productos, categorias=categorias, config=config)

@app.route("/configuracion")
def configuracion():
    productos = cargar_json(PRODUCTOS_FILE)
    categorias = cargar_json(CATEGORIAS_FILE)
    config = cargar_json(CONFIG_FILE)
    return render_template("configuracion.html", productos=productos, categorias=categorias, config=config)

# --- GUARDAR CONFIGURACIÓN LOGO ---
@app.route("/guardar_configuracion", methods=["POST"])
def guardar_configuracion():
    usuario = request.form.get("usuario","")
    notificaciones = request.form.get("notificaciones") == "on"
    logo_file = request.files.get("logo")

    config_data = {"usuario": usuario, "notificaciones": notificaciones}

    if logo_file and logo_file.filename != "":
        upload_result = cloudinary.uploader.upload(logo_file)
        config_data["logo"] = upload_result.get("secure_url")
    else:
        config_actual = cargar_json(CONFIG_FILE)
        if config_actual.get("logo"):
            config_data["logo"] = config_actual["logo"]

    guardar_json(CONFIG_FILE, config_data)
    flash("Configuración guardada correctamente")
    return redirect(url_for("configuracion"))

# --- AGREGAR CATEGORÍA ---
@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre_categoria")
    categorias = cargar_json(CATEGORIAS_FILE)
    categoria_id = str(len(categorias)+1)

    # Subir foto categoría opcional
    foto_file = request.files.get("imagen_categoria")
    url_foto = None
    if foto_file and foto_file.filename != "":
        upload_result = cloudinary.uploader.upload(foto_file)
        url_foto = upload_result.get("secure_url")

    categorias[categoria_id] = {"nombre": nombre, "foto": url_foto}
    guardar_json(CATEGORIAS_FILE, categorias)
    flash(f"Categoría '{nombre}' agregada")
    return redirect(url_for("configuracion"))

# --- AGREGAR PRODUCTO ---
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    descripcion = request.form.get("descripcion","")
    categoria = request.form.get("categoria")
    disponible = request.form.get("disponible") == "true"
    imagen = request.files.get("imagen")

    if not nombre or not precio or not imagen or not categoria:
        flash("Debes ingresar nombre, precio, categoría y foto")
        return redirect(url_for("configuracion"))

    upload_result = cloudinary.uploader.upload(imagen)
    url_imagen = upload_result.get("secure_url")

    productos = cargar_json(PRODUCTOS_FILE)
    producto_id = str(len(productos)+1)
    productos[producto_id] = {
        "nombre": nombre
