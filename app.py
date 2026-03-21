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
    categorias =
