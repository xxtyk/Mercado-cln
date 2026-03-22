import os, json
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "12345"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DATA_FILE = os.path.join(BASE_DIR, "productos.json")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def init_app():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

def guardar_foto(file):
    if not file or not file.filename:
        return ""
    nombre = secure_filename(file.filename)
    ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre)
    file.save(ruta)
    return "uploads/" + nombre

@app.route("/")
def index():
    data = cargar()
    categorias = []
    for nombre, foto in data["categorias"].items():
        categorias.append({"nombre": nombre, "foto": foto})
    return render_template("index.html", categorias=categorias)

@app.route("/categoria/<nombre>")
def categoria(nombre):
    data = cargar()
    productos = [p for p in data["productos"] if p.get("categoria", "").lower() == nombre.lower()]
    return render_template("producto.html", productos=productos, nombre_categoria=nombre)

@app.route("/admin")
def admin():
    data = cargar()
    return render_template("admin.html", categorias=data["categorias"], productos=data["productos"])

@app.route("/editar_categoria", methods=["GET", "POST"])
def editar_categoria():
    if request.method == "POST":
        nombre = request.form.get("nombre_categoria", "").strip()
        foto
foto = request.files.get("foto_categoria")

        if not nombre:
            flash("Escribe un nombre de categoría")
            return redirect(url_for("editar_categoria"))

        data = cargar()

        ruta_foto = data["categorias"].get(nombre, "")
        nueva = guardar_foto(foto)

        if nueva:
            ruta_foto = nueva

        data["categorias"][nombre] = ruta_foto
        guardar(data)

        return redirect(url_for("admin"))

    return render_template("categoria.html")


@app.route("/agregar_producto", methods=["GET", "POST"])
def agregar_producto():
    data = cargar()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        precio = request.form.get("precio")
        descripcion = request.form.get("descripcion")
        categoria = request.form.get("categoria")
        foto = request.files.get("foto_producto")

        nuevo = {
            "id": len(data["productos"]) + 1,
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "categoria": categoria,
            "foto": guardar_foto(foto)
        }

        data["productos"].append(nuevo)
        guardar(data)
        return redirect(url_for("admin"))

    return render_template(
        "admin.html",
        categorias=list(data["categorias"].keys()),
        productos=data["productos"]
    )


if __name__ == "__main__":
    init_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
