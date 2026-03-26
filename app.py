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
COSTO_ENVIO = 40

VENDEDORES = {
    "Mercado en Línea Culiacán": "526679771409",
    "Hector": "526679771409",
    "Silvia": "526674263892",
    "Juan": "526678962503",
    "Cristian": "526673587278",
    "Brissa": "526674283998",
    "Claudia": "526671605229",
    "Amairany": "526677469585",
    "Natalia": "526673513058",
}


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
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    nombre_seguro = secure_filename(archivo.filename)
    extension = nombre_seguro.rsplit(".", 1)[1].lower()
    nombre_final = f"{uuid.uuid4().hex}.{extension}"
    ruta_guardado = os.path.join(app.config["UPLOAD_FOLDER"], nombre_final)
    archivo.save(ruta_guardado)

    return f"uploads/{nombre_final}"


def obtener_categoria_por_id(categoria_id):
    categorias = cargar_json(CATEGORIAS_FILE)
    for categoria in categorias:
        if str(categoria.get("id")) == str(categoria_id):
            return categoria
    return None


def obtener_producto_por_id(producto_id):
    productos = cargar_json(PRODUCTOS_FILE)
    for producto in productos:
        if str(producto.get("id")) == str(producto_id):
            return producto
    return None


def obtener_productos_de_categoria(categoria_id):
    productos = cargar_json(PRODUCTOS_FILE)
    return [p for p in productos if str(p.get("categoria_id")) == str(categoria_id)]


def normalizar_precio(valor):
    try:
        texto = str(valor).replace("$", "").replace(",", "").strip()
        return float(texto) if texto else 0.0
    except Exception:
        return 0.0


def formatear_moneda(valor):
    try:
        return f"{float(valor):.2f}"
    except Exception:
        return "0.00"


def obtener_carrito():
    carrito = session.get("carrito", [])
    return carrito if isinstance(carrito, list) else []


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def total_productos_carrito():
    carrito = obtener_carrito()
    return sum(int(item.get("cantidad", 0)) for item in carrito)


def total_importe_carrito():
    carrito = obtener_carrito()
    total = 0
    for item in carrito:
        precio = normalizar_precio(item.get("precio", 0))
        cantidad = int(item.get("cantidad", 0))
        total += precio * cantidad
    return total


# ------------------------
# CONTEXTO GLOBAL
# ------------------------
@app.context_processor
def inyectar_datos_globales():
    return {
        "carrito_cantidad_total": total_productos_carrito(),
        "carrito_importe_total": total_importe_carrito(),
        "COSTO_ENVIO": COSTO_ENVIO
    }


# ------------------------
# RUTAS CLIENTE
# ------------------------
@app.route("/")
def inicio():
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:categoria_id>")
def ver_categoria(categoria_id):
    categoria = obtener_categoria_por_id(categoria_id)
    if not categoria:
        return "Categoría no encontrada", 404

    productos = obtener_productos_de_categoria(categoria_id)
    return render_template("categoria.html", categoria=categoria, productos=productos)


@app.route("/producto/<int:producto_id>")
def ver_producto(producto_id):
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return "Producto no encontrado", 404

    categoria = obtener_categoria_por_id(producto.get("categoria_id"))
    return render_template("producto.html", producto=producto, categoria=categoria)


# ------------------------
# CARRITO
# ------------------------
@app.route("/agregar_al_carrito/<int:producto_id>", methods=["POST"])
def agregar_al_carrito(producto_id):
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return redirect(url_for("inicio"))

    carrito = obtener_carrito()

    cantidad = request.form.get("cantidad", "1")
    descripcion = request.form.get("descripcion", "").strip()

    try:
        cantidad = int(cantidad)
        if cantidad < 1:
            cantidad = 1
    except Exception:
        cantidad = 1

    item_existente = None
    for item in carrito:
        if str(item.get("producto_id")) == str(producto_id) and item.get("descripcion", "") == descripcion:
            item_existente = item
            break

    if item_existente:
        item_existente["cantidad"] += cantidad
    else:
        carrito.append({
            "producto_id": producto.get("id"),
            "nombre": producto.get("nombre", ""),
            "precio": normalizar_precio(producto.get("precio", 0)),
            "foto": producto.get("foto", ""),
            "cantidad": cantidad,
            "descripcion": descripcion
        })

    guardar_carrito(carrito)

    siguiente = request.form.get("siguiente")
    if siguiente == "carrito":
        return redirect(url_for("ver_carrito"))

    return redirect(url_for("ver_categoria", categoria_id=producto.get("categoria_id")))


@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito()

    subtotal = total_importe_carrito()
    total = subtotal + COSTO_ENVIO if carrito else 0

    return render_template(
        "carrito.html",
        carrito=carrito,
        subtotal=subtotal,
        costo_envio=COSTO_ENVIO if carrito else 0,
        total=total
    )


@app.route("/carrito/actualizar/<int:indice>", methods=["POST"])
def actualizar_carrito(indice):
    carrito = obtener_carrito()

    if 0 <= indice < len(carrito):
        accion = request.form.get("accion", "").strip()

        if accion == "sumar":
            carrito[indice]["cantidad"] = int(carrito[indice].get("cantidad", 1)) + 1

        elif accion == "restar":
            nueva_cantidad = int(carrito[indice].get("cantidad", 1)) - 1
            if nueva_cantidad <= 0:
                carrito.pop(indice)
            else:
                carrito[indice]["cantidad"] = nueva_cantidad

        elif accion == "eliminar":
            carrito.pop(indice)

        else:
            cantidad = request.form.get("cantidad", "1")
            descripcion = request.form.get("descripcion", "").strip()

            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    carrito.pop(indice)
                else:
                    carrito[indice]["cantidad"] = cantidad
                    carrito[indice]["descripcion"] = descripcion
            except Exception:
                pass

    guardar_carrito(carrito)
    return redirect(url_for("ver_carrito"))


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    guardar_carrito([])
    return redirect(url_for("ver_carrito"))


# ------------------------
# PEDIDO / WHATSAPP
# ------------------------
@app.route("/datos_entrega")
def datos_entrega():
    carrito = obtener_carrito()
    if not carrito:
        return redirect(url_for("ver_carrito"))

    subtotal = total_importe_carrito()
    total = subtotal + COSTO_ENVIO

    return render_template(
        "datos_entrega.html",
        carrito=carrito,
        subtotal=subtotal,
        costo_envio=COSTO_ENVIO,
        total=total,
        vendedores=VENDEDORES
    )


@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito = obtener_carrito()
    if not carrito:
        return redirect(url_for("ver_carrito"))

    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()
    colonia = request.form.get("colonia", "").strip()
    referencias = request.form.get("referencias", "").strip()
    metodo_pago = request.form.get("metodo_pago", "").strip()
    vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()

    if vendedor not in VENDEDORES:
        vendedor = "Mercado en Línea Culiacán"

    subtotal = total_importe_carrito()
    total = subtotal + COSTO_ENVIO

    mensaje = []
    mensaje.append("🛒 *NUEVO PEDIDO*")
    mensaje.append("")
    mensaje.append(f"👤 *Nombre:* {nombre}")
    mensaje.append(f"📞 *Teléfono:* {telefono}")
    mensaje.append(f"📍 *Dirección:* {direccion}")
    mensaje.append(f"🏘️ *Colonia:* {colonia}")
    mensaje.append(f"📝 *Referencias:* {referencias}")
    mensaje.append(f"💳 *Método de pago:* {metodo_pago}")
    mensaje.append(f"👨‍💼 *Vendedor:* {vendedor}")
    mensaje.append("")
    mensaje.append("*Productos:*")

    for item in carrito:
        nombre_producto = item.get("nombre", "")
        cantidad = int(item.get("cantidad", 0))
        precio = normalizar_precio(item.get("precio", 0))
        descripcion = item.get("descripcion", "").strip()
        importe = precio * cantidad

        linea = f"- {cantidad} x {nombre_producto} - ${formatear_moneda(importe)}"
        if descripcion:
            linea += f" ({descripcion})"
        mensaje.append(linea)

    mensaje.append("")
    mensaje.append(f"Subtotal: ${formatear_moneda(subtotal)}")
    mensaje.append(f"Envío: ${formatear_moneda(COSTO_ENVIO)}")
    mensaje.append(f"Total: ${formatear_moneda(total)}")

    texto = "\n".join(mensaje)
    telefono_vendedor = VENDEDORES.get(vendedor, VENDEDORES["Mercado en Línea Culiacán"])
    enlace_whatsapp = f"https://wa.me/{telefono_vendedor}?text={quote(texto)}"

    guardar_carrito([])
    return redirect(enlace_whatsapp)


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)
    return render_template("admin.html", categorias=categorias, productos=productos, vendedores=VENDEDORES)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre", "").strip()
    foto = request.files.get("foto_categoria")

    if not nombre:
        return redirect(url_for("admin"))

    categorias = cargar_json(CATEGORIAS_FILE)
    nueva_categoria = {
        "id": obtener_siguiente_id(categorias),
        "nombre": nombre,
        "foto": guardar_imagen(foto)
    }

    categorias.append(nueva_categoria)
    guardar_json(CATEGORIAS_FILE, categorias)

    return redirect(url_for("admin"))


@app.route("/editar_categoria/<int:categoria_id>", methods=["GET", "POST"])
def editar_categoria(categoria_id):
    categorias = cargar_json(CATEGORIAS_FILE)
    categoria = None

    for c in categorias:
        if str(c.get("id")) == str(categoria_id):
            categoria = c
            break

    if not categoria:
        return "Categoría no encontrada", 404

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        foto = request.files.get("foto_categoria")

        if nombre:
            categoria["nombre"] = nombre

        nueva_foto = guardar_imagen(foto)
        if nueva_foto:
            categoria["foto"] = nueva_foto

        guardar_json(CATEGORIAS_FILE, categorias)
        return redirect(url_for("admin"))

    return render_template("editar_categoria.html", categoria=categoria)


@app.route("/eliminar_categoria/<int:categoria_id>", methods=["POST"])
def eliminar_categoria(categoria_id):
    categorias = cargar_json(CATEGORIAS_FILE)
    productos = cargar_json(PRODUCTOS_FILE)

    categorias = [c for c in categorias if str(c.get("id")) != str(categoria_id)]
    productos = [p for p in productos if str(p.get("categoria_id")) != str(categoria_id)]

    guardar_json(CATEGORIAS_FILE, categorias)
    guardar_json(PRODUCTOS_FILE, productos)

    return redirect(url_for("admin"))


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()
    foto = request.files.get("foto_producto")

    if not nombre or not categoria_id:
        return redirect(url_for("admin"))

    if vendedor not in VENDEDORES:
        vendedor = "Mercado en Línea Culiacán"

    productos = cargar_json(PRODUCTOS_FILE)

    nuevo_producto = {
        "id": obtener_siguiente_id(productos),
        "nombre": nombre,
        "precio": normalizar_precio(precio),
        "descripcion": descripcion,
        "categoria_id": int(categoria_id),
        "foto": guardar_imagen(foto),
        "vendedor": vendedor
    }

    productos.append(nuevo_producto)
    guardar_json(PRODUCTOS_FILE, productos)

    return redirect(url_for("admin"))


@app.route("/editar_producto/<int:producto_id>", methods=["GET", "POST"])
def editar_producto(producto_id):
    productos = cargar_json(PRODUCTOS_FILE)
    categorias = cargar_json(CATEGORIAS_FILE)
    producto = None

    for p in productos:
        if str(p.get("id")) == str(producto_id):
            producto = p
            break

    if not producto:
        return "Producto no encontrado", 404

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria_id = request.form.get("categoria_id", "").strip()
        vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()
        foto = request.files.get("foto_producto")

        if nombre:
            producto["nombre"] = nombre

        producto["precio"] = normalizar_precio(precio)
        producto["descripcion"] = descripcion

        if categoria_id:
            try:
                producto["categoria_id"] = int(categoria_id)
            except Exception:
                pass

        if vendedor in VENDEDORES:
            producto["vendedor"] = vendedor
        else:
            producto["vendedor"] = "Mercado en Línea Culiacán"

        nueva_foto = guardar_imagen(foto)
        if nueva_foto:
            producto["foto"] = nueva_foto

        guardar_json(PRODUCTOS_FILE, productos)
        return redirect(url_for("admin"))

    return render_template(
        "editar_producto.html",
        producto=producto,
        categorias=categorias,
        vendedores=VENDEDORES
    )


@app.route("/eliminar_producto/<int:producto_id>", methods=["POST"])
def eliminar_producto(producto_id):
    productos = cargar_json(PRODUCTOS_FILE)
    productos = [p for p in productos if str(p.get("id")) != str(producto_id)]
    guardar_json(PRODUCTOS_FILE, productos)
    return redirect(url_for("admin"))


# ------------------------
# INICIO
# ------------------------
init_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
