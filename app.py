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
EXT = {"png", "jpg", "jpeg", "webp", "gif"}


# =========================
# BASE
# =========================
def asegurar(ruta, base):
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(base, f, indent=4)


def cargar(ruta, base):
    asegurar(ruta, base)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return base


def guardar(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def subir_img(file):
    if not file or file.filename == "":
        return ""

    if "." not in file.filename:
        return ""

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in EXT:
        return ""

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    nombre = f"{uuid.uuid4().hex}.{ext}"
    ruta = os.path.join(UPLOAD_FOLDER, nombre)
    file.save(ruta)

    return f"uploads/{nombre}"


def productos():
    return cargar(PRODUCTOS_FILE, [])


def guardar_productos(data):
    guardar(PRODUCTOS_FILE, data)


def categorias():
    return cargar(CATEGORIAS_FILE, [])


def guardar_categorias(data):
    guardar(CATEGORIAS_FILE, data)


def get_producto(id):
    for p in productos():
        if str(p.get("id")) == str(id):
            return p
    return None


def get_categoria(id):
    for c in categorias():
        if str(c.get("id")) == str(id):
            return c
    return None


def get_categoria_por_nombre(nombre):
    for c in categorias():
        if c.get("nombre", "").lower().strip() == nombre.lower().strip():
            return c
    return None


# =========================
# INICIO
# =========================
@app.route("/")
def index():
    return render_template(
        "index.html",
        productos=[p for p in productos() if p.get("activo", True)],
        categorias=[c for c in categorias() if c.get("activa", True)]
    )


# =========================
# 🔥 CATEGORIA (ARREGLADO TOTAL)
# =========================
@app.route("/categoria/<id>")
def ver_categoria(id):
    lista = productos()
    filtrados = []

    id_limpio = str(id).strip().lower()

    for p in lista:
        cat_id = str(p.get("categoria_id", "")).strip()
        cat_nombre = str(p.get("categoria_nombre", "")).strip().lower()

        # 🔥 FUNCIONA CON ID Y NOMBRE (como tu URL)
        if cat_id == id or cat_nombre == id_limpio:
            filtrados.append(p)

    categoria_actual = get_categoria(id)

    # 🔥 si no encontró por ID, busca por nombre
    if not categoria_actual:
        categoria_actual = get_categoria_por_nombre(id)

    return render_template(
        "categoria.html",
        categoria=categoria_actual,
        categorias=categorias(),
        productos=filtrados
    )


# =========================
# CARRITO
# =========================
@app.route("/carrito")
def carrito():
    car = session.get("carrito", [])
    total = sum(i.get("subtotal", 0) for i in car)
    return render_template("carrito.html", carrito=car, total=total)


@app.route("/agregar_al_carrito", methods=["POST"])
def agregar_carrito():
    pid = request.form.get("producto_id")
    cant = request.form.get("cantidad", "1")
    desc = request.form.get("descripcion", "")

    try:
        cant = int(cant)
    except:
        cant = 1

    p = get_producto(pid)
    if not p:
        return redirect(url_for("index"))

    car = session.get("carrito", [])
    precio = float(p.get("precio", 0))

    encontrado = False
    for item in car:
        if item["producto_id"] == pid and item["descripcion"] == desc:
            item["cantidad"] += cant
            item["subtotal"] = item["cantidad"] * precio
            encontrado = True

    if not encontrado:
        car.append({
            "producto_id": pid,
            "nombre": p.get("nombre", ""),
            "precio": precio,
            "cantidad": cant,
            "descripcion": desc,
            "foto": p.get("foto", ""),
            "subtotal": precio * cant
        })

    session["carrito"] = car
    session.modified = True

    return redirect(url_for("carrito"))


@app.route("/actualizar_carrito", methods=["POST"])
def actualizar_carrito():
    car = session.get("carrito", [])

    for i, item in enumerate(car):
        cantidad = request.form.get(f"cantidad_{i}", item["cantidad"])
        desc = request.form.get(f"descripcion_{i}", item["descripcion"])

        try:
            cantidad = int(cantidad)
        except:
            cantidad = 1

        item["cantidad"] = cantidad
        item["descripcion"] = desc
        item["subtotal"] = cantidad * float(item["precio"])

    session["carrito"] = car
    session.modified = True

    return redirect(url_for("carrito"))


@app.route("/eliminar_del_carrito/<int:i>", methods=["POST"])
def eliminar_del_carrito(i):
    car = session.get("carrito", [])
    if i < len(car):
        car.pop(i)

    session["carrito"] = car
    session.modified = True
    return redirect(url_for("carrito"))


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar():
    session["carrito"] = []
    return redirect(url_for("car
