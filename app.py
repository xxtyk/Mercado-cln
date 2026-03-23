import os
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# =========================
# CONFIGURACIÓN
# =========================
USUARIO = os.environ.get("ADMIN_USER", "admin")
PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PRODUCTOS_FILE = os.path.join(BASE_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(BASE_DIR, "categorias.json")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}

VENDEDORES = [
    "Mercado en Línea Culiacán",
    "Silvia",
    "Hector",
    "Juan",
    "Cristian",
    "Amayrani",
    "Brisa",
    "Natalia",
    "Claudia"
]


# =========================
# FUNCIONES AUXILIARES
# =========================
def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def asegurar_archivo_json(ruta, valor_inicial):
    if not os.path.exists(ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(valor_inicial, f, ensure_ascii=False, indent=4)


def cargar_json(ruta, valor_inicial):
    asegurar_archivo_json(ruta, valor_inicial)
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return valor_inicial


def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    nombre_seguro = secure_filename(archivo.filename)
    extension = nombre_seguro.rsplit(".", 1)[1].lower()
    nuevo_nombre = f"{uuid.uuid4().hex}.{extension}"
    ruta_completa = os.path.join(app.config["UPLOAD_FOLDER"], nuevo_nombre)

    archivo.save(ruta_completa)
    return f"uploads/{nuevo_nombre}"


def cargar_productos():
    data = cargar_json(PRODUCTOS_FILE, [])
    return data if isinstance(data, list) else []


def guardar_productos(productos):
    guardar_json(PRODUCTOS_FILE, productos)


def cargar_categorias():
    data = cargar_json(CATEGORIAS_FILE, [])
    return data if isinstance(data, list) else []


def guardar_categorias(categorias):
    guardar_json(CATEGORIAS_FILE, categorias)


def buscar_producto(producto_id):
    productos = cargar_productos()
    for producto in productos:
        if producto.get("id") == producto_id:
            return producto
    return None


def buscar_categoria(categoria_id):
    categorias = cargar_categorias()
    for categoria in categorias:
        if categoria.get("id") == categoria_id:
            return categoria
    return None


def esta_logueado():
    return session.get("admin") is True


def init_app():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    asegurar_archivo_json(PRODUCTOS_FILE, [])
    asegurar_archivo_json(CATEGORIAS_FILE, [])


init_app()


# =========================
# RUTAS PÚBLICAS
# =========================
@app.route("/")
def index():
    productos = cargar_productos()
    categorias = cargar_categorias()

    productos_activos = [p for p in productos if p.get("activo", True)]
    categorias_activas = [c for c in categorias if c.get("activa", True)]

    return render_template(
        "index.html",
        productos=productos_activos,
        categorias=categorias_activas
    )


@app.route("/categoria/<categoria_id>")
def categoria(categoria_id):
    categorias = cargar_categorias()
    categoria_actual = buscar_categoria(categoria_id)

    if not categoria_actual:
        flash("Categoría no encontrada.")
        return redirect(url_for("index"))

    productos = cargar_productos()
    productos_filtrados = [
        p for p in productos
        if p.get("activo", True) and p.get("categoria_id") == categoria_id
    ]

    return render_template(
        "categoria.html",
        categoria=categoria_actual,
        categorias=categorias,
        productos=productos_filtrados
    )


# =========================
# CARRITO
# =========================
@app.route("/carrito")
def ver_carrito():
    carrito = session.get("carrito", [])
    total = sum(float(item.get("subtotal", 0)) for item in carrito)
    return render_template("carrito.html", carrito=carrito, total=total)


@app.route("/agregar_al_carrito", methods=["POST"])
def agregar_al_carrito():
    producto_id = request.form.get("producto_id", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    cantidad_texto = request.form.get("cantidad", "1").strip()

    try:
        cantidad = int(cantidad_texto)
        if cantidad < 1:
            cantidad = 1
    except ValueError:
        cantidad = 1

    producto = buscar_producto(producto_id)
    if not producto:
        flash("Producto no encontrado.")
        return redirect(request.referrer or url_for("index"))

    carrito = session.get("carrito", [])
    precio = float(producto.get("precio", 0))

    # Si ya existe ese producto con la misma descripción, suma cantidades
    encontrado = False
    for item in carrito:
        if item.get("producto_id") == producto_id and item.get("descripcion", "") == descripcion:
            item["cantidad"] += cantidad
            item["subtotal"] = round(item["cantidad"] * float(item["precio"]), 2)
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "producto_id": producto.get("id"),
            "nombre": producto.get("nombre", ""),
            "precio": precio,
            "cantidad": cantidad,
            "descripcion": descripcion,
            "foto": producto.get("foto", ""),
            "subtotal": round(precio * cantidad, 2)
        })

    session["carrito"] = carrito
    session.modified = True
    flash("Producto agregado al carrito.")
    return redirect(url_for("ver_carrito"))


@app.route("/actualizar_carrito", methods=["POST"])
def actualizar_carrito():
    carrito = session.get("carrito", [])

    for i, item in enumerate(carrito):
        cantidad_texto = request.form.get(f"cantidad_{i}", str(item.get("cantidad", 1))).strip()
        descripcion = request.form.get(f"descripcion_{i}", item.get("descripcion", "")).strip()

        try:
            cantidad = int(cantidad_texto)
            if cantidad < 1:
                cantidad = 1
        except ValueError:
            cantidad = 1

        item["cantidad"] = cantidad
        item["descripcion"] = descripcion
        item["subtotal"] = round(float(item.get("precio", 0)) * cantidad, 2)

    session["carrito"] = carrito
    session.modified = True
    flash("Carrito actualizado.")
    return redirect(url_for("ver_carrito"))


@app.route("/eliminar_del_carrito/<int:indice>", methods=["POST"])
def eliminar_del_carrito(indice):
    carrito = session.get("carrito", [])

    if 0 <= indice < len(carrito):
        carrito.pop(indice)

    session["carrito"] = carrito
    session.modified = True
    flash("Producto eliminado del carrito.")
    return redirect(url_for("ver_carrito"))


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    session["carrito"] = []
    session.modified = True
    flash("Carrito vaciado.")
    return redirect(url_for("ver_carrito"))


# =========================
# LOGIN / LOGOUT
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()

        if usuario == USUARIO and password == PASSWORD:
            session["admin"] = True
            flash("Bienvenido al panel.")
            return redirect(url_for("admin"))
        else:
            flash("Usuario o contraseña incorrectos.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Sesión cerrada.")
    return redirect(url_for("index"))


# =========================
# PANEL ADMIN
# =========================
@app.route("/admin")
def admin():
    if not esta_logueado():
        return redirect(url_for("login"))

    productos = cargar_productos()
    categorias = cargar_categorias()

    return render_template(
        "admin.html",
        productos=productos,
        categorias=categorias,
        vendedores=VENDEDORES
    )


# =========================
# CATEGORÍAS
# =========================
@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    if not esta_logueado():
        return redirect(url_for("login"))

    nombre = request.form.get("nombre_categoria", "").strip()
    foto = request.files.get("foto_categoria")

    if not nombre:
        flash("Escribe el nombre de la categoría.")
        return redirect(url_for("admin"))

    categorias = cargar_categorias()

    for categoria in categorias:
        if categoria.get("nombre", "").strip().lower() == nombre.lower():
            flash("Esa categoría ya existe.")
            return redirect(url_for("admin"))

    foto_ruta = guardar_imagen(foto)

    nueva_categoria = {
        "id": uuid.uuid4().hex,
        "nombre": nombre,
        "foto": foto_ruta,
        "activa": True
    }

    categorias.append(nueva_categoria)
    guardar_categorias(categorias)

    flash("Categoría agregada correctamente.")
    return redirect(url_for("admin"))


@app.route("/editar_categoria/<categoria_id>", methods=["GET", "POST"])
def editar_categoria(categoria_id):
    if not esta_logueado():
        return redirect(url_for("login"))

    categorias = cargar_categorias()
    categoria_actual = None

    for c in categorias:
        if c.get("id") == categoria_id:
            categoria_actual = c
            break

    if not categoria_actual:
        flash("Categoría no encontrada.")
        return redirect(url_for("admin"))

    if request.method == "POST":
        nombre = request.form.get("nombre_categoria", "").strip()
        foto = request.files.get("foto_categoria")
        activa = request.form.get("activa") == "on"

        if nombre:
            categoria_actual["nombre"] = nombre

        if foto and foto.filename != "":
            nueva_foto = guardar_imagen(foto)
            if nueva_foto:
                categoria_actual["foto"] = nueva_foto

        categoria_actual["activa"] = activa

        guardar_categorias(categorias)
        flash("Categoría actualizada.")
        return redirect(url_for("admin"))

    return render_template("editar_categoria.html", categoria=categoria_actual)


@app.route("/eliminar_categoria/<categoria_id>", methods=["POST"])
def eliminar_categoria(categoria_id):
    if not esta_logueado():
        return redirect(url_for("login"))

    productos = cargar_productos()
    relacionadas = [p for p in productos if p.get("categoria_id") == categoria_id]

    if relacionadas:
        flash("No puedes eliminar esa categoría porque tiene productos.")
        return redirect(url_for("admin"))

    categorias = cargar_categorias()
    categorias = [c for c in categorias if c.get("id") != categoria_id]
    guardar_categorias(categorias)

    flash("Categoría eliminada.")
    return redirect(url_for("admin"))


# =========================
# PRODUCTOS
# =========================
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    if not esta_logueado():
        return redirect(url_for("login"))

    nombre = request.form.get("nombre", "").strip()
    precio_texto = request.form.get("precio", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    vendedor = request.form.get("vendedor", "").strip()
    foto = request.files.get("foto")

    if not nombre or not precio_texto or not categoria_id:
        flash("Faltan datos del producto.")
        return redirect(url_for("admin"))

    try:
        precio = float(precio_texto)
    except ValueError:
        flash("Precio inválido.")
        return redirect(url_for("admin"))

    categoria_actual = buscar_categoria(categoria_id)
    if not categoria_actual:
        flash("La categoría no existe.")
        return redirect(url_for("admin"))

    if not vendedor:
        vendedor = "Mercado en Línea Culiacán"

    foto_ruta = guardar_imagen(foto)

    productos = cargar_productos()

    nuevo_producto = {
        "id": uuid.uuid4().hex,
        "nombre": nombre,
        "precio": precio,
        "categoria_id": categoria_id,
        "categoria_nombre": categoria_actual.get("nombre", ""),
        "descripcion": descripcion,
        "vendedor": vendedor,
        "foto": foto_ruta,
        "activo": True
    }

    productos.append(nuevo_producto)
    guardar_productos(productos)

    flash("Producto agregado correctamente.")
    return redirect(url_for("admin"))


@app.route("/editar_producto/<producto_id>", methods=["GET", "POST"])
def editar_producto(producto_id):
    if not esta_logueado():
        return redirect(url_for("login"))

    productos = cargar_productos()
    categorias = cargar_categorias()
    producto_actual = None

    for p in productos:
        if p.get("id") == producto_id:
            producto_actual = p
            break

    if not producto_actual:
        flash("Producto no encontrado.")
        return redirect(url_for("admin"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio_texto = request.form.get("precio", "").strip()
        categoria_id = request.form.get("categoria_id", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        vendedor = request.form.get("vendedor", "").strip()
        foto = request.files.get("foto")
        activo = request.form.get("activo") == "on"

        if nombre:
            producto_actual["nombre"] = nombre

        if precio_texto:
            try:
                producto_actual["precio"] = float(precio_texto)
            except ValueError:
                pass

        if categoria_id:
            categoria_actual = buscar_categoria(categoria_id)
            if categoria_actual:
                producto_actual["categoria_id"] = categoria_id
                producto_actual["categoria_nombre"] = categoria_actual.get("nombre", "")

        producto_actual["descripcion"] = descripcion
        producto_actual["vendedor"] = vendedor if vendedor else "Mercado en Línea Culiacán"
        producto_actual["activo"] = activo

        if foto and foto.filename != "":
            nueva_foto = guardar_imagen(foto)
            if nueva_foto:
                producto_actual["foto"] = nueva_foto

        guardar_productos(productos)
        flash("Producto actualizado.")
        return redirect(url_for("admin"))

    return render_template(
        "editar_producto.html",
        producto=producto_actual,
        categorias=categorias,
        vendedores=VENDEDORES
    )


@app.route("/eliminar_producto/<producto_id>", methods=["POST"])
def eliminar_producto(producto_id):
    if not esta_logueado():
        return redirect(url_for("login"))

    productos = cargar_productos()
    productos = [p for p in productos if p.get("id") != producto_id]
    guardar_productos(productos)

    flash("Producto eliminado.")
    return redirect(url_for("admin"))


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    init_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
