import os
import uuid
import json
from functools import wraps

from flask import Flask, render_template, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

COSTO_ENVIO = 40

ADMIN_USER = os.environ.get("ADMIN_USER", "hector")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

VENDEDORES = [
    "Mercado en Línea Culiacán",
    "Hector",
    "Silvia",
    "Juan",
    "Cristian",
    "Amayrani",
    "Brisa",
    "Claudia",
    "Natalia"
]

pedidos = []
uploads_memoria = {}

DATA_DIR = "data"
DATA_CATEGORIAS = os.path.join(DATA_DIR, "categorias.json")
DATA_PRODUCTOS = os.path.join(DATA_DIR, "productos.json")

CATEGORIAS_BASE = [
    {"id": "minisplit", "slug": "minisplit", "nombre": "Minisplit", "foto": None, "emoji": "❄️", "color": "#1976d2"},
    {"id": "personal", "slug": "personal", "nombre": "Cuidado personal", "foto": None, "emoji": "💄", "color": "#c62828"},
    {"id": "mascotas", "slug": "mascotas", "nombre": "Mascotas", "foto": None, "emoji": "🐾", "color": "#2e7d32"},
    {"id": "cabello", "slug": "cabello", "nombre": "Cuidado del cabello", "foto": None, "emoji": "💆", "color": "#7b1fa2"},
    {"id": "cocina", "slug": "cocina", "nombre": "Cocina", "foto": None, "emoji": "🍳", "color": "#e65100"},
    {"id": "limpieza", "slug": "limpieza", "nombre": "Limpieza", "foto": None, "emoji": "🧹", "color": "#00897b"},
    {"id": "electrodomesticos", "slug": "electrodomesticos", "nombre": "Electrodoméstico", "foto": None, "emoji": "⚡", "color": "#37474f"},
    {"id": "otro", "slug": "otro", "nombre": "Otro", "foto": None, "emoji": "🛍️", "color": "#546e7a"},
]


# ========================
# ARCHIVOS JSON
# ========================
def asegurar_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_CATEGORIAS):
        with open(DATA_CATEGORIAS, "w", encoding="utf-8") as f:
            json.dump(CATEGORIAS_BASE, f, ensure_ascii=False, indent=2)

    if not os.path.exists(DATA_PRODUCTOS):
        with open(DATA_PRODUCTOS, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def leer_json(ruta, default):
    asegurar_data()
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def guardar_json(ruta, data):
    asegurar_data()
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def slugify(texto):
    texto = (texto or "").strip().lower()
    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ñ": "n"
    }
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)

    salida = []
    for ch in texto:
        if ch.isalnum():
            salida.append(ch)
        elif ch in [" ", "-", "_"]:
            salida.append("_")

    slug = "".join(salida)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "otro"


def leer_categorias_local():
    data = leer_json(DATA_CATEGORIAS, [])
    if not isinstance(data, list):
        return []

    salida = []
    for i, c in enumerate(data, start=1):
        nombre = c.get("nombre", "")
        slug = c.get("slug") or slugify(nombre)
        salida.append({
            "id": str(c.get("id") or slug),
            "orden": i,
            "slug": slug,
            "nombre": nombre,
            "foto": c.get("imagen") or c.get("foto") or "",
            "emoji": c.get("emoji", "🛍️"),
            "color": c.get("color", "#1976d2")
        })
    return salida


def guardar_categorias_local(categorias):
    salida = []
    for c in categorias:
        salida.append({
            "id": str(c.get("id") or c.get("slug") or uuid.uuid4().hex),
            "slug": c.get("slug") or slugify(c.get("nombre", "")),
            "nombre": c.get("nombre", ""),
            "foto": c.get("foto") or c.get("imagen") or "",
            "emoji": c.get("emoji", "🛍️"),
            "color": c.get("color", "#1976d2")
        })
    guardar_json(DATA_CATEGORIAS, salida)


def leer_productos_local():
    data = leer_json(DATA_PRODUCTOS, [])
    if isinstance(data, list):
        return data
    return []


def guardar_productos_local(data):
    guardar_json(DATA_PRODUCTOS, data)


# ========================
# AYUDAS
# ========================
def resolver_imagen(valor):
    return valor or ""


def obtener_carrito():
    return session.get("carrito", [])


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def subtotal_carrito(carrito):
    return sum(float(item.get("precio", 0)) * int(item.get("cantidad", 1)) for item in carrito)


def total_items_carrito(carrito):
    return sum(int(item.get("cantidad", 1)) for item in carrito)


def admin_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logueado"):
            return redirect(url_for("login_admin"))
        return func(*args, **kwargs)
    return wrapper


def auth_api_valida():
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    return token == ADMIN_PASSWORD


def obtener_categorias():
    categorias = leer_categorias_local()
    if categorias:
        return categorias

    salida = []
    for i, cat in enumerate(CATEGORIAS_BASE, start=1):
        salida.append({
            "id": cat["id"],
            "orden": i,
            "slug": cat["slug"],
            "nombre": cat["nombre"],
            "foto": cat.get("foto", ""),
            "emoji": cat.get("emoji", "🛍️"),
            "color": cat.get("color", "#1976d2"),
        })
    return salida


def categoria_slug_por_id(categoria_id, categorias):
    categoria_id = str(categoria_id)
    cat = next((c for c in categorias if str(c["id"]) == categoria_id), None)
    if not cat:
        return "otro"
    return cat.get("slug", "otro")


def categoria_id_por_slug(slug, categorias):
    cat = next((c for c in categorias if c.get("slug") == slug), None)
    if cat:
        return c_id(cat)
    return c_id(categorias[-1]) if categorias else "otro"


def c_id(cat):
    return str(cat.get("id"))


def obtener_productos(categorias):
    data = leer_productos_local()
    salida = []

    for i, p in enumerate(data, start=1):
        categoria_slug = p.get("categoria", "otro")
        categoria_id = categoria_id_por_slug(categoria_slug, categorias)

        salida.append({
            "id": int(p.get("id_num", i)),
            "uid": str(p.get("id", uuid.uuid4().hex)),
            "codigo": p.get("codigo", str(i)),
            "nombre": p.get("nombre", ""),
            "descripcion": p.get("descripcion", ""),
            "precio": float(p.get("precio", 0)),
            "categoria": categoria_slug,
            "categoria_id": categoria_id,
            "foto": p.get("imagen") or p.get("foto") or "",
            "imagen": p.get("imagen") or p.get("foto") or "",
            "etiqueta": p.get("etiqueta", "Nuevo")
        })

    return salida


def subir_imagen_api(archivo):
    # Para que funcione ahorita sin depender de otra API:
    # si quieres usar URL manual, escribe la URL en el campo foto.
    # este helper no sube archivos externos por ahora.
    return ""


@app.context_processor
def utilidades_templates():
    carrito = obtener_carrito()
    return dict(
        resolver_imagen=resolver_imagen,
        carrito_cantidad=total_items_carrito(carrito),
        costo_envio=COSTO_ENVIO,
        admin_logueado=session.get("admin_logueado", False)
    )


# ========================
# INICIO
# ========================
@app.route("/")
def inicio():
    return redirect("/catalogo")


@app.route("/catalogo")
def catalogo():
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

    return render_template(
        "index.html",
        categorias=categorias,
        productos=productos
    )


# ========================
# LOGIN ADMIN
# ========================
@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    error = ""

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()

        if usuario == ADMIN_USER and password == ADMIN_PASSWORD:
            session["admin_logueado"] = True
            return redirect(url_for("admin"))
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login_admin.html", error=error)


@app.route("/logout_admin")
def logout_admin():
    session.pop("admin_logueado", None)
    return redirect("/catalogo")


# ========================
# VER CATEGORIA
# ========================
@app.route("/categoria/<id>")
def categoria(id):
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

    categoria_encontrada = next((c for c in categorias if str(c["id"]) == str(id)), None)

    if not categoria_encontrada:
        return redirect("/catalogo")

    productos_categoria = [
        p for p in productos
        if str(p.get("categoria_id")) == str(id)
    ]

    return render_template(
        "categoria.html",
        categoria=categoria_encontrada,
        productos=productos_categoria
    )


# ========================
# CARRITO
# ========================
@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

    producto = next((p for p in productos if int(p["id"]) == int(id)), None)

    if not producto:
        return redirect("/catalogo")

    carrito = obtener_carrito()

    encontrado = False
    for item in carrito:
        if int(item["id"]) == int(producto["id"]):
            item["cantidad"] = int(item.get("cantidad", 1)) + 1
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio": float(producto["precio"]),
            "cantidad": 1,
            "foto": producto.get("foto"),
            "categoria_id": producto.get("categoria_id")
        })

    guardar_carrito(carrito)

    regresar = request.referrer or "/catalogo"
    return redirect(regresar)


@app.route("/carrito")
def carrito():
    carrito = obtener_carrito()
    subtotal = subtotal_carrito(carrito)

    return render_template(
        "carrito.html",
        carrito=carrito,
        subtotal=subtotal
    )


@app.route("/carrito/actualizar/<int:producto_id>", methods=["POST"])
def actualizar_carrito(producto_id):
    accion = request.form.get("accion", "").strip()
    carrito = obtener_carrito()

    for item in carrito[:]:
        if int(item["id"]) == int(producto_id):
            cantidad_actual = int(item.get("cantidad", 1))

            if accion == "sumar":
                item["cantidad"] = cantidad_actual + 1
            elif accion == "restar":
                nueva_cantidad = cantidad_actual - 1
                if nueva_cantidad <= 0:
                    carrito.remove(item)
                else:
                    item["cantidad"] = nueva_cantidad
            elif accion == "eliminar":
                carrito.remove(item)

            break

    guardar_carrito(carrito)
    return redirect("/carrito")


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    guardar_carrito([])
    return redirect("/carrito")


# ========================
# DATOS DE ENTREGA
# ========================
@app.route("/datos_entrega")
def datos_entrega():
    carrito = obtener_carrito()

    if not carrito:
        return redirect("/carrito")

    subtotal = subtotal_carrito(carrito)

    return render_template(
        "datos_entrega.html",
        carrito=carrito,
        subtotal=subtotal,
        costo_envio=COSTO_ENVIO,
        vendedores=VENDEDORES
    )


# ========================
# FINALIZAR PEDIDO
# ========================
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito = obtener_carrito()

    if not carrito:
        return redirect("/carrito")

    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()
    colonia = request.form.get("colonia", "").strip()
    nota = request.form.get("nota", "").strip()
    vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()
    tipo_entrega = request.form.get("tipo_entrega", "domicilio").strip()

    subtotal = subtotal_carrito(carrito)
    envio = COSTO_ENVIO if tipo_entrega == "domicilio" else 0
    total = subtotal + envio

    pedido = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "colonia": colonia,
        "nota": nota,
        "vendedor": vendedor,
        "tipo_entrega": tipo_entrega,
        "subtotal": subtotal,
        "envio": envio,
        "total": total,
        "productos": [dict(item) for item in carrito]
    }

    pedidos.insert(0, pedido)
    guardar_carrito([])

    return render_template("pedido_recibido.html", pedido=pedido)


# ========================
# PANEL ADMIN HTML
# ========================
@app.route("/admin")
@admin_requerido
def admin():
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

    return render_template(
        "admin.html",
        pedidos=pedidos,
        productos=productos,
        categorias=categorias
    )


@app.route("/eliminar_pedido/<id>")
@admin_requerido
def eliminar_pedido(id):
    global pedidos
    pedidos = [p for p in pedidos if p["id"] != id]
    return redirect("/admin")


@app.route("/agregar_categoria", methods=["POST"])
@admin_requerido
def agregar_categoria():
    categorias = leer_categorias_local()

    nombre = request.form.get("nombre", "").strip()
    foto = request.form.get("foto", "").strip()
    emoji = request.form.get("emoji", "🛍️").strip() or "🛍️"

    archivo = request.files.get("foto_archivo")
    if archivo and getattr(archivo, "filename", ""):
        subida = subir_imagen_api(archivo)
        if subida:
            foto = subida

    if nombre:
        nueva = {
            "id": str(uuid.uuid4()),
            "slug": slugify(nombre),
            "nombre": nombre,
            "foto": foto,
            "emoji": emoji,
            "color": "#1976d2"
        }
        categorias.append(nueva)
        guardar_categorias_local(categorias)

    return redirect("/admin")


@app.route("/editar_categoria/<id>", methods=["GET", "POST"])
@admin_requerido
def editar_categoria(id):
    categorias = leer_categorias_local()
    categoria = next((c for c in categorias if str(c.get("id")) == str(id)), None)

    if not categoria:
        return redirect("/admin")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        foto = request.form.get("foto", "").strip()
        emoji = request.form.get("emoji", categoria.get("emoji", "🛍️")).strip() or "🛍️"

        archivo = request.files.get("foto_archivo")
        if archivo and getattr(archivo, "filename", ""):
            subida = subir_imagen_api(archivo)
            if subida:
                foto = subida

        categoria["nombre"] = nombre if nombre else categoria.get("nombre", "")
        categoria["slug"] = slugify(categoria["nombre"])
        categoria["foto"] = foto if foto else categoria.get("foto", "")
        categoria["emoji"] = emoji

        guardar_categorias_local(categorias)
        return redirect("/admin")

    categoria_vista = {
        "id": categoria.get("id"),
        "slug": categoria.get("slug"),
        "nombre": categoria.get("nombre"),
        "foto": categoria.get("foto", ""),
        "emoji": categoria.get("emoji", "🛍️"),
        "color": categoria.get("color", "#1976d2")
    }

    return render_template("editar_categoria.html", categoria=categoria_vista)


@app.route("/eliminar_categoria/<id>")
@admin_requerido
def eliminar_categoria(id):
    categorias = leer_categorias_local()
    categorias = [c for c in categorias if str(c.get("id")) != str(id)]
    guardar_categorias_local(categorias)
    return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
@admin_requerido
def agregar_producto():
    categorias = obtener_categorias()

    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    foto = request.form.get("foto", "").strip()
    descripcion = request.form.get("descripcion", "").strip()

    archivo = request.files.get("foto_archivo")
    if archivo and getattr(archivo, "filename", ""):
        subida = subir_imagen_api(archivo)
        if subida:
            foto = subida

    if not nombre or not precio:
        return redirect("/admin")

    categoria_slug = "otro"
    for c in categorias:
        if str(c["id"]) == str(categoria_id):
            categoria_slug = c["slug"]
            break

    productos = leer_productos_local()
    nuevo_num = len(productos) + 1

    nuevo = {
        "id": str(uuid.uuid4()),
        "id_num": nuevo_num,
        "codigo": str(nuevo_num),
        "nombre": nombre,
        "descripcion": descripcion,
        "imagen": foto,
        "precio": float(precio),
        "categoria": categoria_slug,
        "etiqueta": "Nuevo"
    }

    productos.insert(0, nuevo)
    guardar_productos_local(productos)

    return redirect("/admin")


# ========================
# API LOCAL
# ========================
@app.route("/api/productos")
def api_productos():
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

    salida = []
    for p in productos:
        salida.append({
            "id": p["uid"],
            "id_num": p["id"],
            "codigo": str(p.get("codigo", "")),
            "nombre": p.get("nombre", ""),
            "descripcion": p.get("descripcion", ""),
            "imagen": p.get("imagen") or p.get("foto") or "",
            "etiqueta": p.get("etiqueta", "Nuevo"),
            "precio": float(p.get("precio", 0)),
            "categoria": p.get("categoria") or categoria_slug_por_id(p.get("categoria_id"), categorias)
        })
    return jsonify(salida)


@app.route("/api/categorias")
def api_categorias():
    categorias = obtener_categorias()

    salida = []
    for c in categorias:
        salida.append({
            "id": c.get("id"),
            "slug": c.get("slug"),
            "nombre": c.get("nombre", ""),
            "imagen": c.get("foto"),
            "emoji": c.get("emoji", "🛍️"),
            "color": c.get("color", "#1976d2")
        })
    return jsonify(salida)


@app.route("/api/admin/auth")
def api_admin_auth():
    if auth_api_valida():
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401


@app.route("/api/webhook-pedido", methods=["POST"])
def api_webhook_pedido():
    data = request.get_json(silent=True) or {}
    pedidos.insert(0, {
        "id": str(uuid.uuid4()),
        "nombre": data.get("cliente", ""),
        "telefono": data.get("telefono", ""),
        "direccion": data.get("direccion", ""),
        "colonia": "",
        "nota": data.get("nota", ""),
        "vendedor": data.get("vendedor", ""),
        "tipo_entrega": data.get("tipo_entrega", ""),
        "subtotal": 0,
        "envio": 0,
        "total": data.get("total", 0),
        "productos": data.get("productos", [])
    })
    return jsonify({"ok": True})


# ========================
# ARRANQUE
# ========================
if __name__ == "__main__":
    asegurar_data()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
