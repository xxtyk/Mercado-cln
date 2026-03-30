import os
import uuid
from functools import wraps

import requests
from flask import Flask, render_template, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

COSTO_ENVIO = 40

ADMIN_USER = os.environ.get("ADMIN_USER", "hector")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

API_BASE = os.environ.get("API_BASE", "https://mercado-cln-1.onrender.com/api").rstrip("/")

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


# ========================
# AYUDAS API
# ========================
def api_headers():
    return {
        "Authorization": f"Bearer {ADMIN_PASSWORD}",
        "Content-Type": "application/json"
    }


def api_get_json(url, default):
    try:
        r = requests.get(url, timeout=20)
        if r.ok:
            data = r.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return default


def obtener_categorias():
    data = api_get_json(f"{API_BASE}/categorias", [])
    salida = []

    if isinstance(data, list) and data:
        for i, c in enumerate(data, start=1):
            nombre = c.get("nombre", "")
            slug = c.get("id") or c.get("slug") or nombre.lower().replace(" ", "_")
            salida.append({
                "id": i,
                "slug": slug,
                "nombre": nombre,
                "foto": c.get("imagen") or c.get("foto"),
                "emoji": c.get("emoji", "🛍️"),
                "color": c.get("color", "#1976d2")
            })
        return salida

    salida = []
    for i, cat in enumerate(CATEGORIAS_BASE, start=1):
        salida.append({
            "id": i,
            "slug": cat["id"],
            "nombre": cat["nombre"],
            "foto": cat.get("foto"),
            "emoji": cat.get("emoji", "🛍️"),
            "color": cat.get("color", "#1976d2"),
        })
    return salida


def obtener_productos(categorias):
    data = api_get_json(f"{API_BASE}/productos", [])
    salida = []

    if not isinstance(data, list):
        return salida

    for i, p in enumerate(data, start=1):
        categoria_slug = p.get("categoria", "otro")
        categoria_id = categoria_id_por_slug(categoria_slug, categorias)

        salida.append({
            "id": int(p.get("id", i)),
            "codigo": p.get("codigo", str(p.get("id", i))),
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
    if not archivo or not getattr(archivo, "filename", ""):
        return ""

    try:
        headers = {
            "Authorization": f"Bearer {ADMIN_PASSWORD}"
        }

        files = {
            "file": (archivo.filename, archivo.stream, archivo.mimetype or "application/octet-stream")
        }

        r = requests.post(
            f"{API_BASE}/upload",
            headers=headers,
            files=files,
            timeout=60
        )

        if r.ok:
            data = r.json()
            url = data.get("url", "")
            if url.startswith("/"):
                return f"{API_BASE}{url.replace('/api', '', 1)}" if False else f"{API_BASE.rsplit('/api', 1)[0]}{url}"
            return url
    except Exception:
        pass

    return ""


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


def categoria_slug_por_id(categoria_id, categorias):
    cat = next((c for c in categorias if c["id"] == categoria_id), None)
    if not cat:
        return "otro"
    return cat.get("slug", "otro")


def categoria_id_por_slug(slug, categorias):
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
@app.route("/categoria/<int:id>")
def categoria(id):
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

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
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

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
    nombre = request.form.get("nombre", "").strip()
    foto = request.form.get("foto", "").strip()

    archivo = request.files.get("foto_archivo")
    if archivo and getattr(archivo, "filename", ""):
        subida = subir_imagen_api(archivo)
        if subida:
            foto = subida

    if nombre:
        payload = {
            "nombre": nombre,
            "imagen": foto if foto else ""
        }

        try:
            requests.post(
                f"{API_BASE}/categorias",
                headers=api_headers(),
                json=payload,
                timeout=20
            )
        except Exception:
            pass

    return redirect("/admin")


@app.route("/editar_categoria/<int:id>", methods=["GET", "POST"])
@admin_requerido
def editar_categoria(id):
    categorias = obtener_categorias()
    categoria = next((c for c in categorias if c["id"] == id), None)

    if not categoria:
        return redirect("/admin")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        foto = request.form.get("foto", "").strip()

        archivo = request.files.get("foto_archivo")
        if archivo and getattr(archivo, "filename", ""):
            subida = subir_imagen_api(archivo)
            if subida:
                foto = subida

        payload = {
            "nombre": nombre if nombre else categoria["nombre"],
            "imagen": foto if foto else categoria.get("foto", "")
        }

        try:
            requests.put(
                f"{API_BASE}/categorias/{id}",
                headers=api_headers(),
                json=payload,
                timeout=20
            )
        except Exception:
            pass

        return redirect("/admin")

    return render_template("editar_categoria.html", categoria=categoria)


@app.route("/eliminar_categoria/<int:id>")
@admin_requerido
def eliminar_categoria(id):
    try:
        requests.delete(
            f"{API_BASE}/categorias/{id}",
            headers=api_headers(),
            timeout=20
        )
    except Exception:
        pass

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

    if nombre and precio:
        categoria_id_valor = None

        if categoria_id.isdigit():
            categoria_id_valor = int(categoria_id)
        elif categorias:
            categoria_id_valor = categorias[0]["id"]

        categoria_slug = categoria_slug_por_id(categoria_id_valor, categorias)

        payload = {
            "codigo": "",
            "nombre": nombre,
            "descripcion": descripcion,
            "imagen": foto if foto else "",
            "etiqueta": "Nuevo",
            "precio": float(precio),
            "categoria": categoria_slug
        }

        try:
            requests.post(
                f"{API_BASE}/admin/producto",
                headers=api_headers(),
                json=payload,
                timeout=20
            )
        except Exception:
            pass

    return redirect("/admin")


# ========================
# API PARA REACT / REPLIT
# ========================
@app.route("/api/productos")
def api_productos():
    categorias = obtener_categorias()
    productos = obtener_productos(categorias)

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
            "categoria": p.get("categoria") or categoria_slug_por_id(p.get("categoria_id"), categorias)
        })
    return jsonify(salida)


@app.route("/api/categorias")
def api_categorias():
    categorias = obtener_categorias()

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

    archivo = request.files.get("imagen") or request.files.get("file")
    if not archivo:
        return jsonify({"ok": False, "error": "No se recibió imagen"}), 400

    url = subir_imagen_api(archivo)
    if not url:
        return jsonify({"ok": False, "error": "No se pudo subir imagen"}), 500

    filename = url.split("/")[-1]
    return jsonify({"ok": True, "filename": filename, "url": url})


@app.route("/api/uploads/<filename>")
def api_uploads(filename):
    return redirect(f"{API_BASE.rsplit('/api', 1)[0]}/api/uploads/{filename}")


@app.route("/api/admin/producto", methods=["POST"])
def api_admin_producto():
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    try:
        r = requests.post(
            f"{API_BASE}/admin/producto",
            headers=api_headers(),
            json=data,
            timeout=20
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/admin/producto/<int:id>", methods=["DELETE"])
def api_admin_eliminar_producto(id):
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    try:
        r = requests.delete(
            f"{API_BASE}/admin/producto/{id}",
            headers=api_headers(),
            timeout=20
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/admin/categoria", methods=["POST"])
def api_admin_categoria():
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    try:
        r = requests.post(
            f"{API_BASE}/categorias",
            headers=api_headers(),
            json=data,
            timeout=20
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/admin/categoria/<id>", methods=["PUT"])
def api_admin_editar_categoria(id):
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    data = request.get_json(silent=True) or {}

    try:
        r = requests.put(
            f"{API_BASE}/categorias/{id}",
            headers=api_headers(),
            json=data,
            timeout=20
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/admin/categoria/<id>", methods=["DELETE"])
def api_admin_eliminar_categoria(id):
    if not auth_api_valida():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    try:
        r = requests.delete(
            f"{API_BASE}/categorias/{id}",
            headers=api_headers(),
            timeout=20
        )
        return jsonify(r.json()), r.status_code
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


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
