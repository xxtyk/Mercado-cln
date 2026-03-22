import os
import json
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"

# -----------------------------------
# CONFIGURACIÓN
# -----------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DATA_FILE = os.path.join(BASE_DIR, "productos.json")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -----------------------------------
# INICIALIZAR
# -----------------------------------
def inicializar():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "categorias": {},
                "productos": []
            }, f, indent=4)

# -----------------------------------
# FUNCIONES
# -----------------------------------
def cargar():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"categorias": {}, "productos": []}

def guardar(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def guardar_foto(file):
    if file and allowed(file.filename):
        nombre = secure_filename(file.filename)
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)
        file.save(ruta)
        return f"uploads/{nombre}"
    return ""

# -----------------------------------
# INICIO (CLIENTES)
# -----------------------------------
@app.route("/")
def index():
    data = cargar()

    categorias = []
    for nombre, foto in data["categorias"].items():
        categorias.append({
            "nombre": nombre,
            "foto": foto
        })

    return render_template("index.html", categorias=categorias)

# -----------------------------------
# VER PRODUCTOS POR CATEGORÍA
# -----------------------------------
@app.route("/categoria/<nombre>")
def categoria(nombre):
    data = cargar()

    productos = [
        p for p in data["productos"]
        if p["categoria"] == nombre
    ]

    return render_template(
        "producto.html",
        productos=productos,
        nombre_categoria=nombre
    )

# -----------------------------------
# PANEL ADMIN
# -----------------------------------
@app.route("/admin")
def admin():
    data = cargar()
    return render_template(
        "admin.html",
        categorias=data["categorias"]
    )

# -----------------------------------
# AGREGAR CATEGORÍA
# -----------------------------------
@app.route("/editar_categoria", methods=["GET", "POST"])
def editar_categoria():
    if request.method == "POST":
        nombre = request.form.get("nombre_categoria")
        foto = request.files.get("foto_categoria")

        if not nombre:
            flash("Escribe un nombre")
            return redirect(url_for("editar_categoria"))

        data = cargar()

        ruta_foto = ""
        if foto:
            ruta_foto = guardar_foto(foto)

        data["categorias"][nombre] = ruta_foto
        guardar(data)

        return redirect(url_for("admin"))

    return render_template("categoria.html")

# -----------------------------------
# AGREGAR PRODUCTO
# -----------------------------------
@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    data = cargar()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        descripcion = request.form.get("descripcion")
        categoria = request.form.get("categoria")
        foto = request.files.get("foto_producto")

        ruta_foto = ""
        if foto:
            ruta_foto = guardar_foto(foto)

        nuevo = {
            "id": len(data["productos"]) + 1,
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "categoria": categoria,
            "foto": ruta_foto
        }

        data["productos"].append(nuevo)
        guardar(data)

        return redirect(url_for("admin"))

    categorias = list(data["categorias"].keys())
    return render_template("agregar_producto.html", categorias=categorias)

# -----------------------------------
# RUN
# -----------------------------------
if __name__ == "__main__":
    inicializar()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
