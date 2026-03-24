import os
import json
import uuid
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "uploads")
PRODUCTOS_FILE = os.path.join(BASE_DIR, "productos.json")
CATEGORIAS_FILE = os.path.join(BASE_DIR, "categorias.json")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}


# ------------------------
# UTILIDADES
# ------------------------
def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def init_app():
    os.makedirs(STATIC_FOLDER, exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    if not os.path.exists(PRODUCTOS_FILE):
        with open(PRODUCTOS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

    if not os.path.exists(CATEGORIAS_FILE):
        with open(CATEGORIAS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)


def cargar_json(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def obtener_siguiente_id(lista):
    ids = []
    for item in lista:
        try:
            ids.append(int(item.get("id", 0)))
        except Exception:
            pass
    return max(ids, default=0) + 1


def guardar_imagen(archivo):
    if not archivo or not archivo.filename:
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    nombre_seguro = secure_filename(archivo.filename)
    extension = nombre_seguro.rsplit(".", 1)[1].lower()
    nombre_final = f"{uuid.uuid4().hex}.{extension}"
    ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_final)
    archivo.save(ruta_guardado)

    return f"uploads/{nombre_final}"


init_app()


# ------------------------
# INDEX
# ------------------------
@app.route("/")
def index():
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("index.html", categorias=categorias)


# ------------------------
# PANEL ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)
    return render_template("admin.html", categorias=categorias, productos=productos)


# ------------------------
# AGREGAR CATEGORIA
# ------------------------
@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre", "").strip()
    foto_categoria = request.files.get("foto_categoria")

    if not nombre:
        return redirect(url_for("admin"))

    categorias = cargar_json(CATEGORIAS_FILE)

    existe = any(
        str(c.get("nombre", "")).strip().lower() == nombre.lower()
        for c in categorias
    )

    if existe:
        return redirect(url_for("admin"))

    ruta_foto = guardar_imagen(foto_categoria)

    categorias.append({
        "id": obtener_siguiente_id(categorias),
        "nombre": nombre,
        "foto": ruta_foto
    })

    guardar_json(CATEGORIAS_FILE, categorias)
    return redirect(url_for("admin"))


# ------------------------
# AGREGAR PRODUCTO
# ------------------------
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria = request.form.get("categoria", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    foto_archivo = request.files.get("foto")

    if not nombre or not precio or not categoria:
        return redirect(url_for("admin"))

    try:
        precio_num = float(precio)
    except Exception:
        precio_num = 0.0

    ruta_foto = guardar_imagen(foto_archivo)

    productos = cargar_json(PRODUCTOS_FILE)
    productos.append({
        "id": obtener_siguiente_id(productos),
        "nombre": nombre,
        "precio": precio_num,
        "categoria": categoria,
        "foto": ruta_foto,
        "descripcion": descripcion
    })

    guardar_json(PRODUCTOS_FILE, productos)
    return redirect(url_for("admin"))


# ------------------------
# VER CATEGORIA
# ------------------------
@app.route("/categoria/<categoria_nombre>")
def ver_categoria(categoria_nombre):
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)

    categoria = next(
        (
            c for c in categorias
            if str(c.get("nombre", "")).strip().lower() == str(categoria_nombre).strip().lower()
        ),
        None
    )

    if categoria is None:
        return redirect(url_for("index"))

    productos_filtrados = [
        p for p in productos
        if str(p.get("categoria", "")).strip().lower() == str(categoria_nombre).strip().lower()
    ]

    return render_template(
        "categoria.html",
        categoria=categoria,
        productos=productos_filtrados
    )


# ------------------------
# AGREGAR AL CARRITO
# ------------------------
@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    producto_id = request.form.get("producto_id")
    cantidad = request.form.get("cantidad", "1")
    nota = request.form.get("nota", "").strip()

    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except Exception:
        cantidad = 1

    productos = cargar_json(PRODUCTOS_FILE)
    producto_encontrado = None

    for p in productos:
        if str(p.get("id", "")) == str(producto_id):
            producto_encontrado = p
            break

    if not producto_encontrado:
        return redirect(request.referrer or url_for("index"))

    carrito_actual = session.get("carrito", [])
    if not isinstance(carrito_actual, list):
        carrito_actual = []

    encontrado = False
    for item in carrito_actual:
        mismo_id = str(item.get("id", "")) == str(producto_id)
        misma_nota = str(item.get("nota", "")).strip() == nota

        if mismo_id and misma_nota:
            item["cantidad"] = int(item.get("cantidad", 1)) + cantidad
            encontrado = True
            break

    if not encontrado:
        try:
            precio_num = float(producto_encontrado.get("precio", 0) or 0)
        except Exception:
            precio_num = 0.0

        carrito_actual.append({
            "id": producto_encontrado.get("id"),
            "nombre": producto_encontrado.get("nombre", ""),
            "precio": precio_num,
            "foto": producto_encontrado.get("foto", ""),
            "cantidad": cantidad,
            "nota": nota
        })

    session["carrito"] = carrito_actual
    session.modified = True

    return redirect(url_for("carrito"))


# ------------------------
# VER CARRITO
# ------------------------
@app.route("/carrito")
def carrito():
    carrito_items = session.get("carrito", [])

    if not isinstance(carrito_items, list):
        carrito_items = []

    total = 0

    for item in carrito_items:
        try:
            precio = float(item.get("precio", 0))
            cantidad = int(item.get("cantidad", 1))
            item["subtotal"] = precio * cantidad
            total += item["subtotal"]
        except Exception:
            item["subtotal"] = 0

    return render_template("carrito.html", carrito=carrito_items, total=total)


# ------------------------
# ELIMINAR ITEM DEL CARRITO
# ------------------------
@app.route("/eliminar_del_carrito/<int:indice>")
def eliminar_del_carrito(indice):
    carrito_items = session.get("carrito", [])

    if isinstance(carrito_items, list) and 0 <= indice < len(carrito_items):
        carrito_items.pop(indice)
        session["carrito"] = carrito_items
        session.modified = True

    return redirect(url_for("carrito"))


# ------------------------
# LIMPIAR CARRITO
# ------------------------
@app.route("/limpiar_carrito")
def limpiar_carrito():
    session["carrito"] = []
    session.modified = True
    return redirect(url_for("carrito"))


# ------------------------
# FICHA DEL CLIENTE
# ------------------------
@app.route("/ficha")
def ficha():
    carrito_items = session.get("carrito", [])

    if not isinstance(carrito_items, list):
        carrito_items = []

    total = 0
    for item in carrito_items:
        try:
            total += float(item.get("precio", 0)) * int(item.get("cantidad", 1))
        except Exception:
            pass

    return render_template("ficha.html", carrito=carrito_items, total=total)


# ------------------------
# ENVIAR PEDIDO A WHATSAPP
# ------------------------
@app.route("/enviar_pedido", methods=["POST"])
def enviar_pedido():
    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()
    referencia = request.form.get("referencia", "").strip()
    metodo_pago = request.form.get("metodo_pago", "").strip()
    comentarios = request.form.get("comentarios", "").strip()

    carrito_items = session.get("carrito", [])
    if not isinstance(carrito_items, list):
        carrito_items = []

    total = 0
    lineas = []

    for item in carrito_items:
        try:
            precio = float(item.get("precio", 0))
            cantidad = int(item.get("cantidad", 1))
            subtotal = precio * cantidad
            total += subtotal

            linea = f"- {item.get('nombre', '')} x{cantidad} = ${subtotal:.2f}"
            if item.get("nota"):
                linea += f" | Nota: {item.get('nota')}"
            lineas.append(linea)
        except Exception:
            pass

    mensaje = f"""🛒 Pedido nuevo - Mercado en Línea Culiacán

👤 Nombre: {nombre}
📞 Teléfono: {telefono}
📍 Dirección: {direccion}
📌 Referencia: {referencia}
💳 Método de pago: {metodo_pago}
📝 Comentarios: {comentarios}

📦 Productos:
{chr(10).join(lineas)}

💰 Total: ${total:.2f}
"""

    numero_whatsapp = "526674263892"
    url = f"https://wa.me/{numero_whatsapp}?text={quote(mensaje)}"
    return redirect(url)


# ------------------------
# INICIO
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
