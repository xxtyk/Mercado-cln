import os
import uuid
import requests

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient, DESCENDING

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ------------------------
# CLOUDINARY
# ------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip(),
    api_key=os.environ.get("CLOUDINARY_API_KEY", "").strip(),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "").strip(),
    secure=True
)

# ------------------------
# MONGODB
# ------------------------
MONGO_URI = os.environ.get("MONGO_URI", "").strip()

mongo_client = None
mongo_db = None
productos_col = None
categorias_col = None

if MONGO_URI:
    try:
        mongo_client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            tls=True,
            retryWrites=True
        )

        mongo_client.admin.command("ping")

        mongo_db = mongo_client["mercado_cln"]
        productos_col = mongo_db["productos"]
        categorias_col = mongo_db["categorias"]

        productos_col.create_index("id", unique=True)
        categorias_col.create_index("id", unique=True)
        productos_col.create_index("categoria_id")

        print("✅ MongoDB conectado correctamente")

    except Exception as e:
        print("❌ Error conectando MongoDB:", e)
else:
    print("❌ Falta MONGO_URI")

# ------------------------
# CONFIG
# ------------------------
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
COSTO_ENVIO = 40

GREEN_API_INSTANCE = os.environ.get("GREEN_API_INSTANCE", "").strip()
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN", "").strip()
GREEN_API_CHAT_ID = os.environ.get("GREEN_API_CHAT_ID", "").strip()

VENDEDORES = {
    "Mercado en Línea Culiacán": "526679771409",
}

# ------------------------
# UTILIDADES
# ------------------------
def extension_permitida(nombre_archivo):
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in EXTENSIONES_PERMITIDAS


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    try:
        resultado = cloudinary.uploader.upload(
            archivo,
            folder="mercado_cln",
            public_id=f"{uuid.uuid4().hex}",
            resource_type="image"
        )
        return resultado.get("secure_url", "")
    except Exception as e:
        print("❌ Error Cloudinary:", e)
        return ""


def obtener_siguiente_id(coleccion):
    if coleccion is None:
        return 1

    ultimo = coleccion.find_one({}, {"id": 1}, sort=[("id", DESCENDING)])
    return int(ultimo.get("id", 0)) + 1 if ultimo else 1


def convertir_float(valor, default=0):
    try:
        if valor is None or valor == "":
            return float(default)
        return float(valor)
    except Exception:
        return float(default)


def obtener_carrito_desde_session():
    carrito = session.get("carrito", [])

    if isinstance(carrito, dict):
        carrito = list(carrito.values())

    if not isinstance(carrito, list):
        carrito = []

    return carrito


def obtener_datos_entrega():
    datos_session = session.get("datos_entrega", {})
    if not isinstance(datos_session, dict):
        datos_session = {}

    datos = {
        "nombre": (
            request.form.get("nombre")
            or datos_session.get("nombre")
            or session.get("nombre_cliente")
            or session.get("nombre")
            or ""
        ),
        "telefono": (
            request.form.get("telefono")
            or datos_session.get("telefono")
            or session.get("telefono_cliente")
            or session.get("telefono")
            or ""
        ),
        "direccion": (
            request.form.get("direccion")
            or datos_session.get("direccion")
            or session.get("direccion")
            or ""
        ),
        "colonia": (
            request.form.get("colonia")
            or datos_session.get("colonia")
            or session.get("colonia")
            or ""
        ),
        "referencia": (
            request.form.get("referencia")
            or datos_session.get("referencia")
            or session.get("referencia")
            or ""
        ),
        "metodo_pago": (
            request.form.get("metodo_pago")
            or datos_session.get("metodo_pago")
            or session.get("metodo_pago")
            or ""
        ),
        "tipo_entrega": (
            request.form.get("tipo_entrega")
            or datos_session.get("tipo_entrega")
            or session.get("tipo_entrega")
            or ""
        ),
        "comentarios": (
            request.form.get("comentarios")
            or datos_session.get("comentarios")
            or session.get("comentarios")
            or ""
        ),
    }

    return datos


def construir_mensaje_pedido():
    carrito = obtener_carrito_desde_session()
    datos = obtener_datos_entrega()

    lineas = []
    lineas.append("🛒 *NUEVO PEDIDO DESDE LA APP*")
    lineas.append("")

    if carrito:
        lineas.append("*Productos:*")
        subtotal = 0

        for i, item in enumerate(carrito, start=1):
            nombre = str(item.get("nombre", "Producto")).strip()
            cantidad = int(item.get("cantidad", 1) or 1)
            precio = convertir_float(item.get("precio", 0))
            descripcion = str(item.get("descripcion", "") or "").strip()

            total_item = precio * cantidad
            subtotal += total_item

            lineas.append(f"{i}. {nombre}")
            lineas.append(f"   Cantidad: {cantidad}")
            lineas.append(f"   Precio: ${precio:.2f}")
            lineas.append(f"   Total: ${total_item:.2f}")

            if descripcion:
                lineas.append(f"   Nota: {descripcion}")

        envio = 0
        tipo_entrega = datos.get("tipo_entrega", "").lower()

        if "domicilio" in tipo_entrega or "envio" in tipo_entrega:
            envio = COSTO_ENVIO

        total_general = subtotal + envio

        lineas.append("")
        lineas.append(f"*Subtotal:* ${subtotal:.2f}")
        lineas.append(f"*Envío:* ${envio:.2f}")
        lineas.append(f"*Total:* ${total_general:.2f}")
    else:
        lineas.append("No se encontraron productos en el carrito.")
        lineas.append("")

    lineas.append("")
    lineas.append("*Datos de entrega:*")
    lineas.append(f"Nombre: {datos.get('nombre', '') or 'No capturado'}")
    lineas.append(f"Teléfono: {datos.get('telefono', '') or 'No capturado'}")
    lineas.append(f"Tipo de entrega: {datos.get('tipo_entrega', '') or 'No capturado'}")
    lineas.append(f"Dirección: {datos.get('direccion', '') or 'No capturada'}")
    lineas.append(f"Colonia: {datos.get('colonia', '') or 'No capturada'}")
    lineas.append(f"Referencia: {datos.get('referencia', '') or 'No capturada'}")
    lineas.append(f"Método de pago: {datos.get('metodo_pago', '') or 'No capturado'}")

    comentarios = datos.get("comentarios", "")
    if comentarios:
        lineas.append(f"Comentarios: {comentarios}")

    return "\n".join(lineas)


def enviar_whatsapp_green_api(texto):
    if not GREEN_API_INSTANCE or not GREEN_API_TOKEN or not GREEN_API_CHAT_ID:
        print("❌ Faltan variables de Green API")
        return False

    chat_id = GREEN_API_CHAT_ID.strip()
    if not chat_id.endswith("@g.us") and not chat_id.endswith("@c.us"):
        chat_id = f"{chat_id}@g.us"

    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

    payload = {
        "chatId": chat_id,
        "message": texto
    }

    try:
        respuesta = requests.post(url, json=payload, timeout=30)
        print("✅ Respuesta Green API:", respuesta.status_code, respuesta.text)
        return respuesta.ok
    except Exception as e:
        print("❌ Error WhatsApp:", e)
        return False


# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    categorias = list(categorias_col.find({}, {"_id": 0})) if categorias_col else []
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:id>")
def categoria(id):
    productos = list(productos_col.find({"categoria_id": id}, {"_id": 0})) if productos_col else []
    return render_template("categoria.html", productos=productos)


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = list(categorias_col.find({}, {"_id": 0})) if categorias_col else []
    productos = list(productos_col.find({}, {"_id": 0})) if productos_col else []
    return render_template("admin.html", categorias=categorias, productos=productos)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    try:
        if categorias_col is None:
            print("❌ No hay conexión con categorias_col")
            return redirect("/admin")

        nombre = (request.form.get("nombre") or "").strip()
        foto = request.files.get("foto_categoria")

        print("📌 Nombre recibido:", nombre)
        print("📌 Trae foto:", bool(foto and foto.filename))

        if not nombre:
            print("❌ Nombre vacío")
            return redirect("/admin")

        foto_url = guardar_imagen(foto) if foto and foto.filename else ""

        nuevo_id = obtener_siguiente_id(categorias_col)
        print("📌 Siguiente id:", nuevo_id)
        print("📌 Foto URL:", foto_url)

        categorias_col.insert_one({
            "id": nuevo_id,
            "nombre": nombre,
            "foto": foto_url
        })

        print("✅ Categoría guardada correctamente")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error en agregar_categoria:", e)
        return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    if productos_col is None:
        print("❌ No hay conexión con productos_col")
        return redirect("/admin")

    nombre = (request.form.get("nombre") or "").strip()
    precio = request.form.get("precio")
    categoria_id = request.form.get("categoria_id")
    descripcion = (request.form.get("descripcion") or "").strip()
    foto = request.files.get("foto_producto")

    if not nombre or not categoria_id:
        return redirect("/admin")

    productos_col.insert_one({
        "id": obtener_siguiente_id(productos_col),
        "nombre": nombre,
        "precio": convertir_float(precio, 0),
        "categoria_id": int(categoria_id),
        "descripcion": descripcion,
        "foto": guardar_imagen(foto)
    })

    return redirect("/admin")


# ------------------------
# WHATSAPP
# ------------------------
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    texto = construir_mensaje_pedido()
    enviado = enviar_whatsapp_green_api(texto)

    if enviado:
        session.pop("carrito", None)

    return redirect("/")


# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
