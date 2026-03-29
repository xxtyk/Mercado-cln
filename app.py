import os
import uuid
import requests
import psycopg2
import psycopg2.extras

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, session

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
# DATABASE
# ------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

GREEN_API_INSTANCE = os.environ.get("GREEN_API_INSTANCE", "").strip()
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN", "").strip()
GREEN_API_CHAT_ID = os.environ.get("GREEN_API_CHAT_ID", "").strip()

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
COSTO_ENVIO = 40


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    if not DATABASE_URL:
        print("❌ Falta DATABASE_URL")
        return

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                foto TEXT DEFAULT ''
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio DOUBLE PRECISION NOT NULL DEFAULT 0,
                categoria_id INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
                descripcion TEXT DEFAULT '',
                foto TEXT DEFAULT ''
            );
        """)

        conn.commit()
        cur.close()
        conn.close()
        print("✅ POSTGRES CONECTADO OK")
    except Exception as e:
        print("❌ Error conectando PostgreSQL:", str(e))


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
            public_id=uuid.uuid4().hex,
            resource_type="image"
        )
        return resultado.get("secure_url", "")
    except Exception as e:
        print("❌ Error Cloudinary:", str(e))
        return ""


def convertir_float(valor, default=0):
    try:
        if valor is None or valor == "":
            return float(default)
        return float(valor)
    except Exception:
        return float(default)


def obtener_categorias():
    if not DATABASE_URL:
        return []

    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT id, nombre, foto FROM categorias ORDER BY id ASC;")
        filas = cur.fetchall()
        cur.close()
        conn.close()
        return list(filas)
    except Exception as e:
        print("❌ Error obteniendo categorías:", str(e))
        return []


def obtener_productos():
    if not DATABASE_URL:
        return []

    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, nombre, precio, categoria_id, descripcion, foto
            FROM productos
            ORDER BY id ASC;
        """)
        filas = cur.fetchall()
        cur.close()
        conn.close()
        return list(filas)
    except Exception as e:
        print("❌ Error obteniendo productos:", str(e))
        return []


def obtener_productos_por_categoria(categoria_id):
    if not DATABASE_URL:
        return []

    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, nombre, precio, categoria_id, descripcion, foto
            FROM productos
            WHERE categoria_id = %s
            ORDER BY id ASC;
        """, (categoria_id,))
        filas = cur.fetchall()
        cur.close()
        conn.close()
        return list(filas)
    except Exception as e:
        print("❌ Error obteniendo productos por categoría:", str(e))
        return []


def obtener_categoria(categoria_id):
    if not DATABASE_URL:
        return None

    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id, nombre, foto
            FROM categorias
            WHERE id = %s;
        """, (categoria_id,))
        fila = cur.fetchone()
        cur.close()
        conn.close()
        return fila
    except Exception as e:
        print("❌ Error obteniendo categoría:", str(e))
        return None


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

    return {
        "nombre": request.form.get("nombre") or datos_session.get("nombre") or "",
        "telefono": request.form.get("telefono") or datos_session.get("telefono") or "",
        "direccion": request.form.get("direccion") or datos_session.get("direccion") or "",
        "colonia": request.form.get("colonia") or datos_session.get("colonia") or "",
        "referencia": request.form.get("referencia") or datos_session.get("referencia") or "",
        "metodo_pago": request.form.get("metodo_pago") or datos_session.get("metodo_pago") or "",
        "tipo_entrega": request.form.get("tipo_entrega") or datos_session.get("tipo_entrega") or "",
        "comentarios": request.form.get("comentarios") or datos_session.get("comentarios") or "",
    }


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
    lineas
