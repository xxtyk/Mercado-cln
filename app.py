from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "12345"

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config(
    cloud_name="dosyi726x",
    api_key="942229587198227",
    api_secret="jHn-OlPaUEdfqvCk1DvgTeSUhyQ",
    secure=True
)

# Archivos JSON
PRODUCTOS_FILE = "productos.json"
CONFIG_FILE = "config.json"

# --- FUNCIONES AUXILIARES ---
def cargar_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({}, f)
    with open(file_path, "r") as f:
        return json.load(f)

def guardar_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- RUTA PRINCIPAL ---
@app.route("/")
def index():
    productos = cargar_json(PRODUCTOS_FILE)
    return render_template("index.html", productos=productos)

# --- PANEL DE CONFIGURACIÓN ---
@app.route("/configuracion")
def configuracion():
    config = cargar_json(CONFIG_FILE)
    return render_template("configuracion.html", config=config)

@app.route("/guardar_configuracion", methods=["POST"])
def guardar_configuracion():
    usuario = request.form.get("usuario", "")
    notificaciones = request.form.get("notificaciones") == "on"

    config_data = {
        "usuario": usuario,
        "notificaciones": notificaciones
    }
    guardar_json(CONFIG_FILE, config_data)

    flash("Configuración guardada correctamente")
    return redirect(url_for("configuracion"))

# --- AGREGAR PRODUCTOS CON FOTO ---
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    imagen = request.files.get("imagen")

    if not nombre or not precio or not imagen:
        flash("Debes ingresar nombre, precio y una imagen")
        return redirect(url_for("index"))

    # Subir imagen a Cloudinary
    upload_result = cloudinary.uploader.upload(imagen)
    url_imagen = upload_result.get("secure_url")

    productos = cargar_json(PRODUCTOS_FILE)
    producto_id = str(len(productos) + 1)
    productos[producto_id] = {
        "nombre": nombre,
        "precio": precio,
        "imagen": url_imagen
    }
    guardar_json(PRODUCTOS_FILE, productos)
    flash(f"Producto {nombre} agregado")
    return redirect(url_for("index"))

# --- EJECUTAR APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
