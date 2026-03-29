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
# POSTGRESQL
# ------------------------
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

conn = None

if DATABASE_URL:
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        conn.autocommit = True
        print("✅ POSTGRES CONECTADO OK")
    except Exception as e:
        conn = None
        print("❌ Error conectando Postgres:", str(e))
else:
    print("❌ Falta DATABASE_URL")


def get_conn():
    global conn
    if conn is None:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        conn.autocommit = True
    return conn


def init_db():
    if not DATABASE_URL:
        return

    try:
        conexion = get_conn()
        with conexion.cursor() as cur:
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
                    precio NUMERIC(10,2) DEFAULT 0,
                    categoria_id INTEGER REFERENCES categorias(id) ON DELETE SET NULL,
                    descripcion TEXT DEFAULT '',
                    foto TEXT DEFAULT ''
                );
            """)
        print("✅ TABLAS LISTAS")
    except Exception as e:
        print("❌ Error creando tablas:", str(e))


init_db()

# ------------------------
# CONFIG
# ------------------------
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
COSTO_ENVIO = 40

GREEN_API_INSTANCE = os.environ.get("GREEN_API_INSTANCE", "").strip()
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN", "").strip()
GREEN_API_CHAT_ID = os.environ.get("GREEN_API_CHAT_ID", "").strip()

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
        print("❌ Error Cloudinary:", str(e))
        return ""


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
        print("❌ Error WhatsApp:", str(e))
        return False


def resolver_imagen(url):
    if not url:
        return ""
    return url


app.jinja_env.globals.update(resolver_imagen=resolver_imagen)

# ------------------------
# CONSULTAS
# ------------------------
def listar_categorias():
    if conn is None:
        return []

    try:
        conexion = get_conn()
        with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, nombre, foto FROM categorias ORDER BY id ASC")
            return [dict(x) for x in cur.fetchall()]
    except Exception as e:
        print("❌ Error listando categorías:", str(e))
        return []


def listar_productos():
    if conn is None:
        return []

    try:
        conexion = get_conn()
        with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, nombre, precio, categoria_id, descripcion, foto
                FROM productos
                ORDER BY id ASC
            """)
            filas = cur.fetchall()
            productos = []
            for x in filas:
                item = dict(x)
                item["precio"] = float(item["precio"] or 0)
                productos.append(item)
            return productos
    except Exception as e:
        print("❌ Error listando productos:", str(e))
        return []


def obtener_categoria_por_id(categoria_id):
    if conn is None:
        return None

    try:
        conexion = get_conn()
        with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, nombre, foto FROM categorias WHERE id = %s",
                (categoria_id,)
            )
            fila = cur.fetchone()
            return dict(fila) if fila else None
    except Exception as e:
        print("❌ Error obteniendo categoría:", str(e))
        return None


def listar_productos_por_categoria(categoria_id):
    if conn is None:
        return []

    try:
        conexion = get_conn()
        with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, nombre, precio, categoria_id, descripcion, foto
                FROM productos
                WHERE categoria_id = %s
                ORDER BY id ASC
            """, (categoria_id,))
            filas = cur.fetchall()
            productos = []
            for x in filas:
                item = dict(x)
                item["precio"] = float(item["precio"] or 0)
                productos.append(item)
            return productos
    except Exception as e:
        print("❌ Error productos por categoría:", str(e))
        return []

# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    categorias = listar_categorias()
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:id>")
def categoria(id):
    categoria_actual = obtener_categoria_por_id(id)
    productos = listar_productos_por_categoria(id)
    return render_template("categoria.html", categoria=categoria_actual, productos=productos)


@app.route("/admin")
def admin():
    categorias = listar_categorias()
    productos = listar_productos()
    return render_template("admin.html", categorias=categorias, productos=productos)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    try:
        if conn is None:
            print("❌ Postgres no conectado")
            return redirect("/admin")

        nombre = (request.form.get("nombre") or "").strip()
        foto = request.files.get("foto")

        if not nombre:
            print("❌ Nombre vacío")
            return redirect("/admin")

        foto_url = guardar_imagen(foto) if foto and foto.filename else ""

        conexion = get_conn()
        with conexion.cursor() as cur:
            cur.execute(
                "INSERT INTO categorias (nombre, foto) VALUES (%s, %s)",
                (nombre, foto_url)
            )

        print("✅ Categoría guardada")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error guardando categoría:", str(e))
        return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    try:
        if conn is None:
            print("❌ Postgres no conectado")
            return redirect("/admin")

        nombre = (request.form.get("nombre") or "").strip()
        precio = convertir_float(request.form.get("precio"), 0)
        categoria_id = request.form.get("categoria_id")
        descripcion = (request.form.get("descripcion") or "").strip()
        foto = request.files.get("foto_producto")

        if not nombre or not categoria_id:
            print("❌ Faltan datos del producto")
            return redirect("/admin")

        foto_url = guardar_imagen(foto) if foto and foto.filename else ""

        conexion = get_conn()
        with conexion.cursor() as cur:
            cur.execute("""
                INSERT INTO productos (nombre, precio, categoria_id, descripcion, foto)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, precio, int(categoria_id), descripcion, foto_url))

        print("✅ Producto guardado")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error guardando producto:", str(e))
        return redirect("/admin")


@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    texto = construir_mensaje_pedido()
    enviado = enviar_whatsapp_green_api(texto)

    if enviado:
        session.pop("carrito", None)

    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
