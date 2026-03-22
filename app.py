import os
import json
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DATA_FILE = os.path.join(BASE_DIR, "productos.json")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def inicializar():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"categorias": {}, "productos": []}, f, ensure_ascii=False, indent=4)


def cargar():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "categorias" not in data:
                data["categorias"] = {}
            if "productos" not in data:
                data["productos"] = []
            return data
    except:
        return {"categorias": {}, "productos": []}


def guardar(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def guardar_foto(file):
    if file and file.filename and allowed(file.filename):
        nombre = secure_filename(file.filename)
        ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)

        if os.path.exists(ruta):
            base, ext = os.path.splitext(nombre)
            contador = 1
            while os.path.exists(ruta):
                nombre = f"{base}_{contador}{ext}"
                ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)
                contador += 1

        file.save(ruta)
        return f"uploads/{nombre}"
    return ""


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


@app.route("/categoria/<nombre>")
def categoria(nombre):
    data = cargar()

    productos = [
        p for p in data["productos"]
        if p.get("categoria", "").strip().lower() == nombre.strip().lower()
    ]

    return render_template(
        "producto.html",
        productos=productos,
        nombre_categoria=nombre
    )


@app.route("/admin")
def admin():
    data = cargar()
    return render_template("admin.html", categorias=data["categorias"], productos=data["productos"])


@app.route("/editar_categoria", methods=["GET", "POST"])
def editar_categoria():
    if request.method == "POST":
        nombre = request.form.get("nombre_categoria", "").strip()
        foto = request.files.get("foto_categoria")

        if not nombre:
            flash("Escribe un nombre de categoría")
            return redirect(url_for("editar_categoria"))

        data = cargar()

        ruta_foto = data["categorias"].get(nombre, "")
        if foto and foto.filename:
            nueva_foto = guardar_foto(foto)
            if nueva_foto:
                ruta_foto = nueva_foto

        data["categorias"][nombre] = ruta_foto
        guardar(data)

        flash("Categoría guardada correctamente")
        return redirect(url_for("admin"))

    return render_template("categoria.html")


@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    data = cargar()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria = request.form.get("categoria", "").strip()
        foto = request.files.get("foto_producto")

        if not nombre or not precio or not categoria:
            flash("Nombre, precio y categoría son obligatorios")
            return redirect(url_for("agregar_producto"))

        ruta_foto = ""
        if foto and foto.filename:
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

        flash("Producto guardado correctamente")
        return redirect(url_for("admin"))

    categorias = list(data["categorias"].keys())
    return render_template("admin.html", categorias=categorias, productos=data["productos"])


if __name__ == "__main__":
    inicializar()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
