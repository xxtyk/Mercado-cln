import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTOS_FILE = os.path.join(BASE_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(BASE_DIR, "categorias.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}


def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def asegurar_archivo_json(ruta, valor_inicial):
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(valor_inicial, f, ensure_ascii=False, indent=4)


def init_app():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    asegurar_archivo_json(PRODUCTOS_FILE, [])
    asegurar_archivo_json(CATEGORIAS_FILE, [])


def cargar_json(ruta, valor_inicial):
    if not os.path.exists(ruta):
        asegurar_archivo_json(ruta, valor_inicial)

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, type(valor_inicial)):
                return data
            return valor_inicial
    except Exception:
        return valor_inicial


def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def guardar_imagen(archivo):
    if not archivo or not archivo.filename:
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    nombre_seguro = secure_filename(archivo.filename)
    nombre_base, extension = os.path.splitext(nombre_seguro)
    nombre_unico = f"{nombre_base}_{uuid.uuid4().hex[:8]}{extension}"
    ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_unico)

    archivo.save(ruta_guardado)
    return f"uploads/{nombre_unico}"


@app.route("/")
def index():
    categorias = cargar_json(CATEGORIAS_FILE, [])
    return render_template("index.html", categorias=categorias)


@app.route("/admin")
def admin():
    productos = cargar_json(PRODUCTOS_FILE, [])
    categorias = cargar_json(CATEGORIAS_FILE, [])
    return render_template("admin.html", productos=productos, categorias=categorias)


@app.route("/categoria/<nombre_categoria>")
def ver_categoria(nombre_categoria):
    productos = cargar_json(PRODUCTOS_FILE, [])
    categoria_url = str(nombre_categoria).strip().lower()

    productos_cat = []
    for p in productos:
        if isinstance(p, dict):
            categoria_producto = str(p.get("categoria", "")).strip().lower()
            activo = p.get("activo", True)

            if categoria_producto == categoria_url and activo:
                productos_cat.append(p)

    return render_template(
        "categoria.html",
        nombre_categoria=nombre_categoria,
        productos=productos_cat
    )


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    categorias = cargar_json(CATEGORIAS_FILE, [])
    nombre = request.form.get("nombre_categoria", "").strip()
    foto = request.files.get("foto_categoria")

    if not nombre:
        return redirect(url_for("admin"))

    for cat in categorias:
        if isinstance(cat, dict) and str(cat.get("nombre", "")).strip().lower() == nombre.lower():
            ruta_foto = guardar_imagen(foto)
            if ruta_foto:
                cat["foto"] = ruta_foto
            guardar_json(CATEGORIAS_FILE, categorias)
            return redirect(url_for("admin"))

    ruta_foto = guardar_imagen(foto)
    categorias.append({
        "nombre": nombre,
        "foto": ruta_foto
    })
    guardar_json(CATEGORIAS_FILE, categorias)

    return redirect(url_for("admin"))


@app.route("/editar_categoria/<int:index>", methods=["POST"])
def editar_categoria(index):
    categorias = cargar_json(CATEGORIAS_FILE, [])

    if 0 <= index < len(categorias):
        nombre = request.form.get("nombre_categoria", "").strip()
        foto = request.files.get("foto_categoria")

        if nombre:
            categorias[index]["nombre"] = nombre

        ruta_foto = guardar_imagen(foto)
        if ruta_foto:
            categorias[index]["foto"] = ruta_foto

        guardar_json(CATEGORIAS_FILE, categorias)

    return redirect(url_for("admin"))


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    productos = cargar_json(PRODUCTOS_FILE, [])
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria = request.form.get("categoria", "").strip()
    foto = request.files.get("foto")

    if not nombre or not precio or not categoria:
        return redirect(url_for("admin"))

    ruta_foto = guardar_imagen(foto)

    productos.append({
        "nombre": nombre,
        "precio": precio,
        "categoria": categoria,
        "foto": ruta_foto,
        "activo": True
    })

    guardar_json(PRODUCTOS_FILE, productos)
    return redirect(url_for("admin"))


@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    producto = request.form.get("producto", "").strip()
    precio = request.form.get("precio", "0").strip()
    foto = request.form.get("foto", "").strip()
    cantidad = request.form.get("cantidad", "1").strip()

    try:
        precio_num = float(precio)
    except Exception:
        precio_num = 0.0

    try:
        cantidad_num = int(cantidad)
    except Exception:
        cantidad_num = 1

    if cantidad_num < 1:
        cantidad_num = 1

    if "carrito" not in session:
        session["carrito"] = []

    carrito = session["carrito"]

    encontrado = False
    for item in carrito:
        if item.get("producto", "").strip().lower() == producto.lower():
            item["cantidad"] = int(item.get("cantidad", 0)) + cantidad_num
            item["total"] = item["cantidad"] * float(item.get("precio", 0))
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "producto": producto,
            "precio": precio_num,
            "foto": foto,
            "cantidad": cantidad_num,
            "total": precio_num * cantidad_num
        })

    session["carrito"] = carrito
    session.modified = True

    return redirect(url_for("ver_carrito"))


@app.route("/carrito")
def ver_carrito():
    carrito = session.get("carrito", [])
    total = sum(float(item.get("total", 0)) for item in carrito)
    return render_template("carrito.html", carrito=carrito, total=total)


@app.route("/sumar_carrito/<int:index>")
def sumar_carrito(index):
    carrito = session.get("carrito", [])

    if 0 <= index < len(carrito):
        carrito[index]["cantidad"] = int(carrito[index].get("cantidad", 0)) + 1
        carrito[index]["total"] = carrito[index]["cantidad"] * float(carrito[index].get("precio", 0))
        session["carrito"] = carrito
        session.modified = True

    return redirect(url_for("ver_carrito"))


@app.route("/restar_carrito/<int:index>")
def restar_carrito(index):
    carrito = session.get("carrito", [])

    if 0 <= index < len(carrito):
        carrito[index]["cantidad"] = int(carrito[index].get("cantidad", 0)) - 1

        if carrito[index]["cantidad"] <= 0:
            carrito.pop(index)
        else:
            carrito[index]["total"] = carrito[index]["cantidad"] * float(carrito[index].get("precio", 0))

        session["carrito"] = carrito
        session.modified = True

    return redirect(url_for("ver_carrito"))


@app.route("/eliminar_carrito/<int:index>")
def eliminar_carrito(index):
    carrito = session.get("carrito", [])

    if 0 <= index < len(carrito):
        carrito.pop(index)
        session["carrito"] = carrito
        session.modified = True

    return redirect(url_for("ver_carrito"))


@app.route("/vaciar_carrito")
def vaciar_carrito():
    session["carrito"] = []
    session.modified = True
    return redirect(url_for("ver_carrito"))


if __name__ == "__main__":
    init_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
