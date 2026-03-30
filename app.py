import os
import uuid
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

# ========================
# DATOS EN MEMORIA
# ========================
productos = []
categorias = []
pedidos = []
uploads_memoria = {}


# ========================
# CATEGORIAS BASE
# ========================
CATEGORIAS_BASE = [
    {"id": "minisplit", "nombre": "Minisplit", "foto": None, "emoji": "❄️", "color": "#1976d2"},
    {"id": "personal", "nombre": "Cuidado personal", "foto": None, "emoji": "💄", "color": "#c62828"},
    {"id": "mascotas", "nombre": "Mascotas", "foto": None, "emoji": "🐾", "color": "#2e7d32"},
    {"id": "cabello", "nombre": "Cuidado del cabello", "foto": None, "emoji": "💆", "color": "#7b1fa2"},
    {"id": "cocina", "nombre": "Cocina", "foto": None, "emoji": "🍳", "color": "#e65100"},
    {"id": "limpieza", "nombre": "Limpieza", "foto": None, "emoji": "🧹", "color": "#00897b"},
    {"id": "electrodomesticos", "nombre": "Electrodoméstico", "foto": None, "emoji": "⚡", "color": "#37474f"},
    {"id": "otro", "nombre": "Otro", "foto": None, "emoji": "🛍️", "color": "#546e7a"},
]


def inicializar_categorias_base():
    global categorias

    if not categorias:
        categorias = []
        for i, cat in enumerate(CATEGORIAS_BASE, start=1):
            categorias.append({
                "id": i,
                "slug": cat["id"],
                "nombre": cat["nombre"],
                "foto": cat.get("foto"),
                "emoji": cat.get("emoji", "🛍️"),
                "color": cat.get("color", "#1976d2"),
            })


inicializar_categorias_base()


# ========================
# AYUDAS
# ========================
def resolver_imagen(valor):
    if valor:
        return valor
    return ""


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


def categoria_slug_por_id(categoria_id):
    cat = next((c for c in categorias if c["id"] == categoria_id), None)
    if not cat:
        return "otro"
    return cat.get("slug", "otro")


def categoria_id_por_slug(slug):
    cat = next((c for c in categorias if c.get("slug") == slug), None)
    if cat:
        return cat["id"]
    return categorias[-1]["id"] if categorias else 1


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
@app.route("/categoria/<int:id>")
def categoria(id):
    categoria_encontrada = next((c for c in categorias if c["id"] == id), None)

    if not categoria_encontrada:
        return redirect("/catalogo")

    productos_categoria = [
        p for p in productos
        if p.get("categoria_id") == id
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
    producto = next((p for p in productos if p["id"] == id), None)

    if not producto:
        return redirect("/catalogo")

    carrito = obtener_carrito()

    encontrado = False
    for item in carrito:
        if item["id"] == producto["id"]:
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
        if item["id"] == producto_id:
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
    nombre = request.form.get("nombre", "").strip()
    foto = request.form.get("foto", "").strip()

    if nombre:
        nuevo_id = max([c["id"] for c in categorias], default=0) + 1
        slug = nombre.lower().replace(" ", "_")

        categorias.append({
            "id": nuevo_id,
            "slug": slug,
            "nombre": nombre,
            "foto": foto if foto else None,
            "emoji": "🛍️",
            "color": "#1976d2"
        })

    return redirect("/admin")


@app.route("/editar_categoria/<int:id>", methods=["GET", "POST"])
@admin_requerido
def editar_categoria(id):
    categoria = next((c for c in categorias if c["id"] == id), None)

    if not categoria:
        return redirect("/admin")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        foto = request.form.get("foto", "").strip()

        if nombre:
            categoria["nombre"] = nombre

        categoria["foto"] = foto if foto else None

        return redirect("/admin")

    return render_template("editar_categoria.html", categoria=categoria)


@app.route("/eliminar_categoria/<int:id>")
@admin_requerido
def eliminar_categoria(id):
    global categorias, productos

    categorias_base_ids = list(range(1, len(CATEGORIAS_BASE) + 1))

    if id in categorias_base_ids:
        return redirect("/admin")

    categorias = [c for c in categorias if c["id"] != id]
    productos = [p for p in productos if p.get("categoria_id") != id]

    return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
@admin_requerido
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    foto = request.form.get("foto", "").strip()

    if nombre and precio:
        categoria_id_valor = None

        if categoria_id.isdigit():
            categoria_id_valor = int(categoria_id)
        elif categorias:
            categoria_id_valor = categorias[0]["id"]

        nuevo_id = max([p["id"] for p in productos], default=0) + 1

        productos.append({
            "id": nuevo_id,
            "nombre": nombre,
            "descripcion": "",
            "precio": float(precio),
            "categoria_id": categoria_id_valor,
            "categoria": categoria_slug_por_id(categoria_id_valor),
            "foto": foto if foto else None,
            "imagen": foto if foto else "",
            "etiqueta": "Nuevo"
        })

    return redirect("/admin")


# ========================
# API PARA REACT / REPLIT
# ========================
@app.route("/api/productos")
def api_productos():
    salida = []
    for p in productos:
        salida.append({
            "id": p["id"],
            "codigo": str(p.get("id", "")),
            "nombre": p.get("nombre", ""),
            "descripcion": p.get("descripcion", ""),
            "imagen": p.get("imagen") or p.get("foto") or "",
            "etiqueta": p.get("etiqueta", "Nuevo"),
            "precio": float(p.get("precio", 0)),
            "categoria": p.get("categoria") or categoria_slug_por_id(p.get("categoria_id"))
        })
    return jsonify(salida)


@app.route("/api/categorias")
def api_categorias():
    salida = []
    for c in categorias:
        salida.append({
            "id": c.get("slug") or str(c["id"]),
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


@app.route("/api/admin/upload", methods=["POST"])
def api_admin_upload():
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    archivo = request.files.get("imagen")
    if not archivo:
        return jsonify({"ok": False, "error": "No se recibió imagen"}), 400

    nombre_archivo = f"{uuid.uuid4().hex}_{archivo.filename or 'imagen.jpg'}"
    uploads_memoria[nombre_archivo] = archivo.read()

    return jsonify({"ok": True, "filename": nombre_archivo})


@app.route("/api/uploads/<filename>")
def api_uploads(filename):
    if filename not in uploads_memoria:
        return "", 404

    contenido = uploads_memoria[filename]
    ext = filename.lower()

    mimetype = "application/octet-stream"
    if ext.endswith(".png"):
        mimetype = "image/png"
    elif ext.endswith(".jpg") or ext.endswith(".jpeg"):
        mimetype = "image/jpeg"
    elif ext.endswith(".webp"):
        mimetype = "image/webp"

    return app.response_class(contenido, mimetype=mimetype)


@app.route("/api/admin/producto", methods=["POST"])
def api_admin_producto():
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    nuevo_id = max([p["id"] for p in productos], default=0) + 1
    categoria_slug = data.get("categoria", "otro")
    categoria_id = categoria_id_por_slug(categoria_slug)

    productos.append({
        "id": nuevo_id,
        "codigo": data.get("codigo", ""),
        "nombre": data.get("nombre", ""),
        "descripcion": data.get("descripcion", ""),
        "imagen": data.get("imagen", ""),
        "foto": data.get("imagen", ""),
        "etiqueta": data.get("etiqueta", "Nuevo"),
        "precio": float(data.get("precio", 0)),
        "categoria": categoria_slug,
        "categoria_id": categoria_id
    })

    return jsonify({"ok": True})


@app.route("/api/admin/producto/<int:id>", methods=["DELETE"])
def api_admin_eliminar_producto(id):
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    global productos
    productos = [p for p in productos if p["id"] != id]
    return jsonify({"ok": True})


@app.route("/api/admin/categoria", methods=["POST"])
def api_admin_categoria():
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    nuevo_id = max([c["id"] for c in categorias], default=0) + 1
    slug = data.get("id") or data.get("nombre", f"cat_{nuevo_id}").lower().replace(" ", "_")

    categorias.append({
        "id": nuevo_id,
        "slug": slug,
        "nombre": data.get("nombre", ""),
        "foto": data.get("imagen"),
        "emoji": data.get("emoji", "🛍️"),
        "color": data.get("color", "#1976d2")
    })

    return jsonify({"ok": True})


@app.route("/api/admin/categoria/<id>", methods=["PUT"])
def api_admin_editar_categoria(id):
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    for c in categorias:
        if str(c.get("slug")) == str(id) or str(c["id"]) == str(id):
            c["nombre"] = data.get("nombre", c["nombre"])
            c["foto"] = data.get("imagen", c.get("foto"))
            return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "Categoría no encontrada"}), 404


@app.route("/api/admin/categoria/<id>", methods=["DELETE"])
def api_admin_eliminar_categoria(id):
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    global categorias, productos

    categoria_obj = next((c for c in categorias if str(c.get("slug")) == str(id) or str(c["id"]) == str(id)), None)
    if not categoria_obj:
        return jsonify({"ok": False, "error": "Categoría no encontrada"}), 404

    categorias_base_slugs = [c["id"] for c in CATEGORIAS_BASE]
    if categoria_obj.get("slug") in categorias_base_slugs:
        return jsonify({"ok": False, "error": "No se puede borrar una categoría base"}), 400

    categorias = [c for c in categorias if c != categoria_obj]
    productos = [p for p in productos if p.get("categoria_id") != categoria_obj["id"]]

    return jsonify({"ok": True})


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
# ARRANQUE CORRECTO PARA RENDER
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
