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


def obtener_carrito():
    carrito_items = session.get("carrito", [])
    if not isinstance(carrito_items, list):
        carrito_items = []

    carrito_limpio = []
    for item in carrito_items:
        try:
            precio = float(item.get("precio", 0) or 0)
        except Exception:
            precio = 0.0

        try:
            cantidad = int(item.get("cantidad", 1) or 1)
        except Exception:
            cantidad = 1

        if cantidad < 1:
            cantidad = 1

        foto = item.get("foto", "") or item.get("imagen", "")

        carrito_limpio.append({
            "id": item.get("id"),
            "nombre": item.get("nombre", ""),
            "precio": precio,
            "foto": foto,
            "imagen": foto,
            "cantidad": cantidad,
            "nota": item.get("nota", "").strip(),
            "subtotal": precio * cantidad
        })

    return carrito_limpio


def guardar_carrito(carrito_items):
    session["carrito"] = carrito_items
    session.modified = True


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
    producto_id = request.form.get("producto_id") or request.form.get("id")
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

    carrito_actual = obtener_carrito()

    encontrado = False
    for item in carrito_actual:
        mismo_id = str(item.get("id", "")) == str(producto_id)
        misma_nota = str(item.get("nota", "")).strip() == nota

        if mismo_id and misma_nota:
            item["cantidad"] = int(item.get("cantidad", 1)) + cantidad
            item["subtotal"] = float(item.get("precio", 0)) * int(item.get("cantidad", 1))
            encontrado = True
            break

    if not encontrado:
        try:
            precio_num = float(producto_encontrado.get("precio", 0) or 0)
        except Exception:
            precio_num = 0.0

        foto = producto_encontrado.get("foto", "")

        carrito_actual.append({
            "id": producto_encontrado.get("id"),
            "nombre": producto_encontrado.get("nombre", ""),
            "precio": precio_num,
            "foto": foto,
            "imagen": foto,
            "cantidad": cantidad,
            "nota": nota,
            "subtotal": precio_num * cantidad
        })

    guardar_carrito(carrito_actual)
    return redirect(url_for("carrito"))


# ------------------------
# VER CARRITO
# ------------------------
@app.route("/carrito")
def carrito():
    carrito_items = obtener_carrito()
    subtotal = sum(item.get("subtotal", 0) for item in carrito_items)
    envio = COSTO_ENVIO if carrito_items else 0
    total = subtotal + envio

    return render_template(
        "carrito.html",
        carrito=carrito_items,
        subtotal=int(subtotal) if subtotal.is_integer() else subtotal,
        envio=envio,
        total=int(total) if float(total).is_integer() else total
    )


# ------------------------
# SUMAR AL CARRITO
# ------------------------
@app.route("/sumar_carrito/<int:producto_id>", methods=["POST"])
def sumar_carrito(producto_id):
    carrito_items = obtener_carrito()

    for item in carrito_items:
        if int(item.get("id", 0)) == producto_id:
            item["cantidad"] = int(item.get("cantidad", 1)) + 1
            item["subtotal"] = float(item.get("precio", 0)) * int(item.get("cantidad", 1))
            break

    guardar_carrito(carrito_items)
    return redirect(url_for("carrito"))


# ------------------------
# RESTAR DEL CARRITO
# ------------------------
@app.route("/restar_carrito/<int:producto_id>", methods=["POST"])
def restar_carrito(producto_id):
    carrito_items = obtener_carrito()
    nuevo_carrito = []

    for item in carrito_items:
        if int(item.get("id", 0)) == producto_id:
            nueva_cantidad = int(item.get("cantidad", 1)) - 1
            if nueva_cantidad > 0:
                item["cantidad"] = nueva_cantidad
                item["subtotal"] = float(item.get("precio", 0)) * nueva_cantidad
                nuevo_carrito.append(item)
        else:
            nuevo_carrito.append(item)

    guardar_carrito(nuevo_carrito)
    return redirect(url_for("carrito"))


# ------------------------
# ELIMINAR ITEM DEL CARRITO
# ------------------------
@app.route("/eliminar_del_carrito/<int:indice>")
def eliminar_del_carrito(indice):
    carrito_items = obtener_carrito()

    if 0 <= indice < len(carrito_items):
        carrito_items.pop(indice)

    guardar_carrito(carrito_items)
    return redirect(url_for("carrito"))


# ------------------------
# LIMPIAR CARRITO
# ------------------------
@app.route("/limpiar_carrito")
def limpiar_carrito():
    guardar_carrito([])
    return redirect(url_for("carrito"))


# ------------------------
# CHECKOUT / DATOS DE ENTREGA
# ------------------------
@app.route("/checkout", methods=["GET"])
def checkout():
    carrito_items = obtener_carrito()

    if not carrito_items:
        return redirect(url_for("carrito"))

    subtotal = sum(item.get("subtotal", 0) for item in carrito_items)

    vendedores_lista = list(VENDEDORES.keys())

    return render_template(
        "checkout.html",
        carrito=carrito_items,
        subtotal=int(subtotal) if float(subtotal).is_integer() else subtotal,
        vendedores=vendedores_lista,
        nombre="",
        direccion="",
        telefono="",
        nota="",
        vendedor_seleccionado="",
        tipo_entrega=""
    )


# ------------------------
# FINALIZAR PEDIDO
# ------------------------
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito_items = obtener_carrito()

    if not carrito_items:
        return redirect(url_for("carrito"))

    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()
    vendedor = request.form.get("vendedor", "").strip()
    tipo_entrega = request.form.get("tipo_entrega", "").strip() or request.form.get("entrega", "").strip()
    nota = request.form.get("nota", "").strip()

    subtotal = sum(item.get("subtotal", 0) for item in carrito_items)
    costo_entrega = COSTO_ENVIO if tipo_entrega == "domicilio" else 0
    total = subtotal + costo_entrega

    if not nombre or not telefono or not direccion or not vendedor or not tipo_entrega:
        vendedores_lista = list(VENDEDORES.keys())
        return render_template(
            "checkout.html",
            carrito=carrito_items,
            subtotal=int(subtotal) if float(subtotal).is_integer() else subtotal,
            vendedores=vendedores_lista,
            nombre=nombre,
            direccion=direccion,
            telefono=telefono,
            nota=nota,
            vendedor_seleccionado=vendedor,
            tipo_entrega=tipo_entrega
        )

    lineas = []
    for item in carrito_items:
        linea = f"- {item.get('nombre', '')} x{item.get('cantidad', 1)} = ${item.get('subtotal', 0):.2f}"
        if item.get("nota"):
            linea += f" | Nota: {item.get('nota')}"
        lineas.append(linea)

    entrega_texto = "Envío a domicilio" if tipo_entrega == "domicilio" else "Recoger en bodega"
    pago_texto = "Efectivo (Contra entrega)"

    mensaje = f"""🛒 Pedido nuevo - Mercado en Línea Culiacán

👤 Nombre: {nombre}
📞 WhatsApp: {telefono}
📍 Dirección: {direccion}
🧑‍💼 Vendedor: {vendedor}
🚚 Entrega: {entrega_texto}
💳 Pago: {pago_texto}
📝 Nota: {nota if nota else "Sin nota"}

📦 Productos:
{chr(10).join(lineas)}

💰 Subtotal: ${subtotal:.2f}
🚚 Envío: ${costo_entrega:.2f}
✅ Total: ${total:.2f}
"""

    numero_whatsapp = VENDEDORES.get(vendedor, VENDEDORES["Mercado en Línea Culiacán"])
    url = f"https://wa.me/{numero_whatsapp}?text={quote(mensaje)}"

    guardar_carrito([])
    return redirect(url)


# ------------------------
# FICHA DEL CLIENTE
# ------------------------
@app.route("/ficha")
def ficha():
    carrito_items = obtener_carrito()
    total = sum(item.get("subtotal", 0) for item in carrito_items)
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

    carrito_items = obtener_carrito()
    total = sum(item.get("subtotal", 0) for item in carrito_items)

    lineas = []
    for item in carrito_items:
        linea = f"- {item.get('nombre', '')} x{item.get('cantidad', 1)} = ${item.get('subtotal', 0):.2f}"
        if item.get("nota"):
            linea += f" | Nota: {item.get('nota')}"
        lineas.append(linea)

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
