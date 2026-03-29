import os
import uuid
import requests
import psycopg2
import psycopg2.extras

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, session, url_for

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

def get_conn():
    if not DATABASE_URL:
        raise Exception("Falta DATABASE_URL")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    if not DATABASE_URL:
        return
    try:
        with get_conn() as conexion:
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

                cur.execute("SELECT COUNT(*) FROM categorias")
                if cur.fetchone()[0] == 0:
                    cur.execute("""
                        INSERT INTO categorias (nombre) VALUES
                        ('Cuidado del cabello'),
                        ('Cocina'),
                        ('Cuidado personal'),
                        ('Aire acondicionado'),
                        ('Electrodomésticos'),
                        ('Otros');
                    """)

        print("✅ DB OK")
    except Exception as e:
        print("❌ DB:", str(e))

init_db()

# ------------------------
# GREEN API
# ------------------------
GREEN_API_INSTANCE = "7107547964"
GREEN_API_TOKEN = "1e6ec2470cfe4808a27cee392009c87bda99eaf03fa64a70b6"
GREEN_API_CHAT_ID = "120363321558514561@g.us"

VENDEDORES = [
    "Mercado en Línea Culiacán",
    "Silvia",
    "Hector",
    "Juan",
    "Cristian",
    "Amayrani",
    "Brisa",
    "Claudia",
    "Natalia"
]

def enviar_whatsapp(texto):
    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
        payload = {
            "chatId": GREEN_API_CHAT_ID,
            "message": texto
        }
        requests.post(url, json=payload, timeout=15)
        print("✅ enviado a WhatsApp")
    except Exception as e:
        print("❌ WhatsApp:", str(e))

# ------------------------
# UTILIDADES
# ------------------------
def extension_permitida(nombre_archivo):
    permitidas = {"png", "jpg", "jpeg", "webp", "gif"}
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in permitidas

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
        print("❌ Cloudinary:", str(e))
        return ""

def resolver_imagen(url):
    if not url:
        return ""
    return url

app.jinja_env.globals.update(resolver_imagen=resolver_imagen)

# ------------------------
# CONSULTAS
# ------------------------
def listar_categorias():
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, nombre, foto FROM categorias ORDER BY id ASC")
                return cur.fetchall()
    except Exception as e:
        print("❌ categorias:", str(e))
        return []

def obtener_categoria_por_id(categoria_id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, nombre, foto FROM categorias WHERE id=%s",
                    (categoria_id,)
                )
                return cur.fetchone()
    except Exception as e:
        print("❌ categoria:", str(e))
        return None

def listar_productos(cat_id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, nombre, precio, categoria_id, descripcion, foto
                    FROM productos
                    WHERE categoria_id=%s
                    ORDER BY id ASC
                """, (cat_id,))
                filas = cur.fetchall()
                productos = []
                for item in filas:
                    item = dict(item)
                    item["precio"] = float(item.get("precio") or 0)
                    productos.append(item)
                return productos
    except Exception as e:
        print("❌ productos:", str(e))
        return []

def obtener_producto(id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, nombre, precio, categoria_id, descripcion, foto
                    FROM productos
                    WHERE id=%s
                """, (id,))
                producto = cur.fetchone()
                if not producto:
                    return None
                producto = dict(producto)
                producto["precio"] = float(producto.get("precio") or 0)
                return producto
    except Exception as e:
        print("❌ producto:", str(e))
        return None

# ------------------------
# CARRITO
# ------------------------
def obtener_carrito():
    carrito = session.get("carrito", [])
    if not isinstance(carrito, list):
        carrito = []
    return carrito

def guardar_carrito(c):
    session["carrito"] = c
    session.modified = True

def carrito_cantidad_total():
    total = 0
    for item in obtener_carrito():
        total += int(item.get("cantidad", 1))
    return total

def carrito_importe_total():
    total = 0
    for item in obtener_carrito():
        total += float(item.get("precio", 0)) * int(item.get("cantidad", 1))
    return total

# ------------------------
# MENSAJE
# ------------------------
def construir_mensaje():
    carrito = obtener_carrito()
    datos = session.get("datos_entrega", {})

    texto = "🛒 *NUEVO PEDIDO DE MERCADO EN LÍNEA*\n\n"
    total = 0

    for item in carrito:
        sub = float(item["precio"]) * int(item["cantidad"])
        total += sub
        texto += f"• {item['nombre']} x{item['cantidad']} = ${sub:.2f}\n"

    tipo_entrega = datos.get("tipo_entrega", "domicilio")
    envio = 40 if tipo_entrega == "domicilio" else 0
    total += envio

    texto += f"\n💰 Total: ${total:.2f}\n\n"
    texto += f"👤 Cliente: {datos.get('nombre', '')}\n"
    texto += f"📱 Tel: {datos.get('telefono', '')}\n"
    texto += f"📍 Dir: {datos.get('direccion', '')}\n"
    texto += f"🏪 Entrega: {datos.get('tipo_entrega', '')}\n"
    texto += f"👨‍💼 Vendedor: {datos.get('vendedor', '')}\n"
    texto += f"🏠 Colonia: {datos.get('colonia', '')}\n"
    texto += f"📝 Nota: {datos.get('nota', '')}\n"

    return texto

# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    categorias = listar_categorias()
    return render_template(
        "index.html",
        categorias=categorias,
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )

@app.route("/categoria/<int:id>")
def categoria(id):
    categoria_actual = obtener_categoria_por_id(id)
    if not categoria_actual:
        return redirect(url_for("inicio"))

    productos = listar_productos(id)
    return render_template(
        "categoria.html",
        categoria=categoria_actual,
        productos=productos,
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )

@app.route("/producto/<int:id>")
def producto(id):
    producto_actual = obtener_producto(id)
    if not producto_actual:
        return redirect(url_for("inicio"))

    session["ultimo_producto_id"] = id
    session.modified = True

    categoria_actual = None
    categoria_id = producto_actual.get("categoria_id")
    if categoria_id:
        categoria_actual = obtener_categoria_por_id(categoria_id)

    return render_template(
        "producto.html",
        producto=producto_actual,
        categoria=categoria_actual,
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )

@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    producto = obtener_producto(id)
    if not producto:
        return redirect(url_for("inicio"))

    carrito = obtener_carrito()
    cantidad = int(request.form.get("cantidad", 1) or 1)

    if cantidad < 1:
        cantidad = 1

    encontrado = False
    for item in carrito:
        if int(item.get("id")) == int(id):
            item["cantidad"] = int(item.get("cantidad", 1)) + cantidad
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio": float(producto["precio"]),
            "foto": producto.get("foto", ""),
            "cantidad": cantidad
        })

    guardar_carrito(carrito)
    return redirect(request.referrer or url_for("inicio"))

@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito()
    subtotal = carrito_importe_total()

    ultimo_producto_id = session.get("ultimo_producto_id")
    if ultimo_producto_id:
        volver_url = url_for("producto", id=ultimo_producto_id)
    else:
        volver_url = url_for("inicio")

    return render_template(
        "carrito.html",
        carrito=carrito,
        subtotal=subtotal,
        volver_url=volver_url,
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )

@app.route("/carrito/sumar/<int:id>", methods=["POST"])
def carrito_sumar(id):
    carrito = obtener_carrito()

    for item in carrito:
        if int(item.get("id")) == int(id):
            item["cantidad"] = int(item.get("cantidad", 1)) + 1
            break

    guardar_carrito(carrito)
    return redirect(url_for("ver_carrito"))

@app.route("/carrito/restar/<int:id>", methods=["POST"])
def carrito_restar(id):
    carrito = obtener_carrito()
    nuevo_carrito = []

    for item in carrito:
        if int(item.get("id")) == int(id):
            cantidad_actual = int(item.get("cantidad", 1)) - 1
            if cantidad_actual > 0:
                item["cantidad"] = cantidad_actual
                nuevo_carrito.append(item)
        else:
            nuevo_carrito.append(item)

    guardar_carrito(nuevo_carrito)
    return redirect(url_for("ver_carrito"))

@app.route("/carrito/eliminar/<int:id>", methods=["POST"])
def carrito_eliminar(id):
    carrito = obtener_carrito()
    carrito = [item for item in carrito if int(item.get("id")) != int(id)]
    guardar_carrito(carrito)
    return redirect(url_for("ver_carrito"))

@app.route("/datos_entrega", methods=["GET", "POST"])
def datos_entrega():
    if request.method == "POST":
        session["datos_entrega"] = request.form.to_dict()
        session.modified = True
        return redirect(url_for("finalizar_pedido"))

    return render_template(
        "datos_entrega.html",
        carrito=obtener_carrito(),
        subtotal=carrito_importe_total(),
        vendedores=VENDEDORES,
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )

@app.route("/finalizar_pedido", methods=["GET", "POST"])
def finalizar_pedido():
    carrito = obtener_carrito()
    if not carrito:
        return redirect(url_for("inicio"))

    texto = construir_mensaje()
    enviar_whatsapp(texto)

    session.pop("carrito", None)
    session.pop("datos_entrega", None)
    session.pop("ultimo_producto_id", None)
    session.modified = True

    return redirect(url_for("inicio"))

# ------------------------
if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)
