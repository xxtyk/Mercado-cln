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

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -----------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------
def inicializar_entorno():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if not os.path.exists(DATA_FILE):
        datos_iniciales = {
            "categorias": {},
            "productos": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos_iniciales, f, ensure_ascii=False, indent=4)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def cargar_datos():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            datos = json.load(f)
            if "categorias" not in datos:
                datos["categorias"] = {}
            if "productos" not in datos:
                datos["productos"] = []
            return datos
    except (FileNotFoundError, json.JSONDecodeError):
        return {"categorias": {}, "productos": []}


def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not allowed_file(archivo.filename):
        return ""

    nombre_seguro = secure_filename(archivo.filename)
    ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro)

    # evitar sobreescribir si ya existe
    if os.path.exists(ruta_guardado):
        nombre, extension = os.path.splitext(nombre_seguro)
        contador = 1
        while os.path.exists(ruta_guardado):
            nombre_seguro = f"{nombre}_{contador}{extension}"
            ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_seguro)
            contador += 1

    archivo.save(ruta_guardado)

    # esto es lo que se guarda para usarlo con url_for('static', filename=...)
    return f"uploads/{nombre_seguro}"


# -----------------------------------
# RUTA PRINCIPAL / TIENDA
# -----------------------------------
@app.route("/")
def inicio():
    datos = cargar_datos()

    categorias = []
    for nombre, foto in datos["categorias"].items():
        categorias.append({
            "nombre": nombre,
            "foto": foto
        })

    return render_template("index.html", categorias=categorias)


# -----------------------------------
# VER PRODUCTOS DE UNA CATEGORÍA
# -----------------------------------
@app.route("/categoria/<nombre_categoria>")
def ver_categoria(nombre_categoria):
    datos = cargar_datos()

    productos_filtrados = [
        p for p in datos["productos"]
        if p.get("categoria", "").strip().lower() == nombre_categoria.strip().lower()
    ]

    return render_template(
        "categoria_productos.html",
        nombre_categoria=nombre_categoria,
        productos=productos_filtrados
    )


# -----------------------------------
# PANEL ADMIN
# -----------------------------------
@app.route("/admin")
def admin():
    datos = cargar_datos()
    return render_template(
        "admin.html",
        categorias=datos["categorias"],
        productos=datos["productos"]
    )


# -----------------------------------
# EDITAR / AGREGAR CATEGORÍA CON FOTO
# -----------------------------------
@app.route("/editar_categoria", methods=["GET", "POST"])
def editar_categoria():
    if request.method == "POST":
        nombre_categoria = request.form.get("nombre_categoria", "").strip()
        foto = request.files.get("foto_categoria")

        if not nombre_categoria:
            flash("Debes escribir un nombre de categoría.", "error")
            return redirect(url_for("editar_categoria"))

        datos = cargar_datos()

        foto_guardada = ""
        if foto and foto.filename != "":
            foto_guardada = guardar_imagen(foto)

        # si ya existe y no suben nueva foto, conserva la anterior
        foto_anterior = datos["categorias"].get(nombre_categoria, "")
        if not foto_guardada:
            foto_guardada = foto_anterior

        datos["categorias"][nombre_categoria] = foto_guardada
        guardar_datos(datos)

        flash(f"Categoría '{nombre_categoria}' guardada correctamente.", "success")
        return redirect(url_for("admin"))

    return render_template("categoria.html")


# -----------------------------------
# AGREGAR PRODUCTO CON FOTO
# -----------------------------------
@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    datos = cargar_datos()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria = request.form.get("categoria", "").strip()
        foto = request.files.get("foto_producto")

        if not nombre or not precio or not categoria:
            flash("Nombre, precio y categoría son obligatorios.", "error")
            return redirect(url_for("agregar_producto"))

        foto_guardada = ""
        if foto and foto.filename != "":
            foto_guardada = guardar_imagen(foto)

        nuevo_producto = {
            "id": len(datos["productos"]) + 1,
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "categoria": categoria,
            "foto": foto_guardada
        }

        datos["productos"].append(nuevo_producto)
        guardar_datos(datos)

        flash("Producto guardado correctamente.", "success")
        return redirect(url_for("admin"))

    categorias = list(datos["categorias"].keys())
    return render_template("agregar_producto.html", categorias=categorias)


# -----------------------------------
# INICIALIZACIÓN
# -----------------------------------
if __name__ == "__main__":
    inicializar_entorno()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
