import os
import uuid
import psycopg2
import psycopg2.extras

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, session, url_for, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ------------------------
# CONFIG
# ------------------------
COSTO_ENVIO = 40
ENLACE_GRUPO_WHATSAPP = "https://chat.whatsapp.com/HtBWXyZmMAxJImgPY5SRXU?mode=gi_t"

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

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pedidos (
                        id SERIAL PRIMARY KEY,
                        codigo TEXT NOT NULL UNIQUE,
                        nombre TEXT DEFAULT '',
                        telefono TEXT DEFAULT '',
                        direccion TEXT DEFAULT '',
                        colonia TEXT DEFAULT '',
                        referencia TEXT DEFAULT '',
                        nota TEXT DEFAULT '',
                        tipo_entrega TEXT DEFAULT '',
                        vendedor TEXT DEFAULT '',
                        forma_pago TEXT DEFAULT 'EFECTIVO (CONTRA ENTREGA)',
                        subtotal NUMERIC(10,2) DEFAULT 0,
                        envio NUMERIC(10,2) DEFAULT 0,
                        total NUMERIC(10,2) DEFAULT 0,
                        mensaje TEXT DEFAULT '',
                        estado TEXT DEFAULT 'nuevo',
                        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pedido_productos (
                        id SERIAL PRIMARY KEY,
                        pedido_id INTEGER REFERENCES pedidos(id) ON DELETE CASCADE,
                        producto_id INTEGER,
                        nombre TEXT NOT NULL,
                        precio NUMERIC(10,2) DEFAULT 0,
                        cantidad INTEGER DEFAULT 1,
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

        print("✅ DB OK", flush=True)
    except Exception as e:
        print("❌ DB:", str(e), flush=True)

init_db()

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
        print("❌ Cloudinary:", str(e), flush=True)
        return ""

def resolver_imagen(url):
    if not url:
        return ""
    return url

def generar_codigo_pedido():
    return uuid.uuid4().hex[:10].upper()

app.jinja_env.globals.update(resolver_imagen=resolver_imagen)

# ------------------------
# CONSULTAS CATEGORÍAS/PRODUCTOS
# ------------------------
def listar_categorias():
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, nombre, foto FROM categorias ORDER BY id ASC")
                return cur.fetchall()
    except Exception as e:
        print("❌ categorias:", str(e), flush=True)
        return []

def listar_todos_productos():
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, nombre, precio, categoria_id, descripcion, foto
                    FROM productos
                    ORDER BY id DESC
                """)
                filas = cur.fetchall()
                productos = []
                for item in filas:
                    item = dict(item)
                    item["precio"] = float(item.get("precio") or 0)
                    productos.append(item)
                return productos
    except Exception as e:
        print("❌ listar_todos_productos:", str(e), flush=True)
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
        print("❌ categoria:", str(e), flush=True)
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
        print("❌ productos:", str(e), flush=True)
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
        print("❌ producto:", str(e), flush=True)
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
# MENSAJE PEDIDO
# ------------------------
def construir_mensaje():
    carrito = obtener_carrito()
    datos = session.get("datos_entrega", {})

    texto = "🛒 *NUEVO PEDIDO DE MERCADO EN LÍNEA CULIACÁN*\n\n"
    subtotal = 0

    for item in carrito:
        sub = float(item["precio"]) * int(item["cantidad"])
        subtotal += sub
        texto += f"• {item['nombre']} x{item['cantidad']} = ${sub:.2f}\n"

    tipo_entrega = (datos.get("tipo_entrega", "domicilio") or "domicilio").strip().lower()
    envio = COSTO_ENVIO if tipo_entrega == "domicilio" else 0
    total = subtotal + envio

    texto += f"\n💰 Subtotal: ${subtotal:.2f}\n"
    texto += f"🚚 Envío: ${envio:.2f}\n"
    texto += f"✅ Total: ${total:.2f}\n\n"
    texto += f"👤 Cliente: {datos.get('nombre', '')}\n"
    texto += f"📱 Tel: {datos.get('telefono', '')}\n"
    texto += f"📍 Dir: {datos.get('direccion', '')}\n"
    texto += f"🏘️ Colonia: {datos.get('colonia', '')}\n"
    texto += f"🏪 Entrega: {datos.get('tipo_entrega', '')}\n"
    texto += f"👨‍💼 Vendedor: {datos.get('vendedor', '')}\n"
    texto += f"📝 Nota: {datos.get('nota', '')}\n"

    return texto

# ------------------------
# PEDIDOS PANEL
# ------------------------
def guardar_pedido():
    carrito = obtener_carrito()
    datos = session.get("datos_entrega", {})

    if not carrito or not datos:
        return None

    subtotal = carrito_importe_total()
    tipo_entrega = (datos.get("tipo_entrega", "domicilio") or "domicilio").strip().lower()
    envio = COSTO_ENVIO if tipo_entrega == "domicilio" else 0
    total = subtotal + envio
    mensaje = construir_mensaje()
    codigo = generar_codigo_pedido()

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO pedidos (
                        codigo, nombre, telefono, direccion, colonia, referencia, nota,
                        tipo_entrega, vendedor, forma_pago, subtotal, envio, total, mensaje, estado
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'nuevo')
                    RETURNING id
                """, (
                    codigo,
                    datos.get("nombre", ""),
                    datos.get("telefono", ""),
                    datos.get("direccion", ""),
                    datos.get("colonia", ""),
                    datos.get("referencia", ""),
                    datos.get("nota", ""),
                    datos.get("tipo_entrega", ""),
                    datos.get("vendedor", ""),
                    "EFECTIVO (CONTRA ENTREGA)",
                    subtotal,
                    envio,
                    total,
                    mensaje
                ))

                fila = cur.fetchone()
                if not fila:
                    return None

                pedido_id = fila["id"]

                for item in carrito:
                    cur.execute("""
                        INSERT INTO pedido_productos (
                            pedido_id, producto_id, nombre, precio, cantidad, foto
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        pedido_id,
                        item.get("id"),
                        item.get("nombre", ""),
                        float(item.get("precio", 0)),
                        int(item.get("cantidad", 1)),
                        item.get("foto", "")
                    ))

                return pedido_id

    except Exception as e:
        print("❌ guardar_pedido:", str(e), flush=True)
        return None

def contar_pedidos_nuevos():
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM pedidos WHERE estado='nuevo'")
                return int(cur.fetchone()[0] or 0)
    except Exception as e:
        print("❌ contar_pedidos_nuevos:", str(e), flush=True)
        return 0

def listar_pedidos_pendientes():
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, codigo, nombre, telefono, direccion, colonia, referencia, nota,
                           tipo_entrega, vendedor, forma_pago, subtotal, envio, total, mensaje,
                           estado, creado_en
                    FROM pedidos
                    WHERE estado <> 'reenviado'
                    ORDER BY id DESC
                """)
                filas = cur.fetchall()
                pedidos = []
                for item in filas:
                    item = dict(item)
                    item["subtotal"] = float(item.get("subtotal") or 0)
                    item["envio"] = float(item.get("envio") or 0)
                    item["total"] = float(item.get("total") or 0)
                    pedidos.append(item)
                return pedidos
    except Exception as e:
        print("❌ listar_pedidos_pendientes:", str(e), flush=True)
        return []

def obtener_pedido_por_id(pedido_id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, codigo, nombre, telefono, direccion, colonia, referencia, nota,
                           tipo_entrega, vendedor, forma_pago, subtotal, envio, total, mensaje,
                           estado, creado_en
                    FROM pedidos
                    WHERE id=%s
                """, (pedido_id,))
                item = cur.fetchone()
                if not item:
                    return None
                item = dict(item)
                item["subtotal"] = float(item.get("subtotal") or 0)
                item["envio"] = float(item.get("envio") or 0)
                item["total"] = float(item.get("total") or 0)
                return item
    except Exception as e:
        print("❌ obtener_pedido_por_id:", str(e), flush=True)
        return None

def listar_productos_de_pedido(pedido_id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, nombre, precio, cantidad, foto
                    FROM pedido_productos
                    WHERE pedido_id=%s
                    ORDER BY id ASC
                """, (pedido_id,))
                filas = cur.fetchall()
                productos = []
                for item in filas:
                    item = dict(item)
                    item["precio"] = float(item.get("precio") or 0)
                    item["cantidad"] = int(item.get("cantidad") or 0)
                    productos.append(item)
                return productos
    except Exception as e:
        print("❌ listar_productos_de_pedido:", str(e), flush=True)
        return []

def cambiar_estado_pedido(pedido_id, estado):
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE pedidos SET estado=%s WHERE id=%s", (estado, pedido_id))
        return True
    except Exception as e:
        print("❌ cambiar_estado_pedido:", str(e), flush=True)
        return False

# ------------------------
# RUTAS TIENDA
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

    try:
        cantidad = int(request.form.get("cantidad", 1) or 1)
    except Exception:
        cantidad = 1

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
        datos=session.get("datos_entrega", {}),
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )

@app.route("/finalizar_pedido", methods=["GET", "POST"])
def finalizar_pedido():
    carrito = obtener_carrito()
    if not carrito:
        return "El carrito está vacío"

    datos = session.get("datos_entrega", {})
    if not datos:
        return "Faltan los datos de entrega"

    pedido_id = guardar_pedido()
    if not pedido_id:
        return "No se pudo guardar el pedido"

    session.pop("carrito", None)
    session.pop("datos_entrega", None)
    session.pop("ultimo_producto_id", None)
    session.modified = True

    return render_template("pedido_recibido.html")

# ------------------------
# RUTAS PANEL
# ------------------------
@app.route("/admin")
def admin():
    categorias = listar_categorias()
    productos = listar_todos_productos()
    pedidos_nuevos = contar_pedidos_nuevos()

    return render_template(
        "admin.html",
        categorias=categorias,
        productos=productos,
        pedidos_nuevos=pedidos_nuevos
    )

@app.route("/pedidos")
def ver_pedidos():
    pedidos = listar_pedidos_pendientes()
    pedidos_nuevos = contar_pedidos_nuevos()

    return render_template(
        "pedidos.html",
        pedidos=pedidos,
        pedidos_nuevos=pedidos_nuevos
    )

@app.route("/pedido/<int:id>")
def ver_pedido(id):
    pedido = obtener_pedido_por_id(id)
    if not pedido:
        return redirect(url_for("ver_pedidos"))

    if pedido.get("estado") == "nuevo":
        cambiar_estado_pedido(id, "pendiente_reenvio")
        pedido["estado"] = "pendiente_reenvio"

    productos = listar_productos_de_pedido(id)

    return render_template(
        "pedido_detalle.html",
        pedido=pedido,
        productos=productos,
        enlace_grupo=ENLACE_GRUPO_WHATSAPP
    )

@app.route("/pedido/<int:id>/reenviar", methods=["POST"])
def reenviar_pedido(id):
    pedido = obtener_pedido_por_id(id)
    if not pedido:
        return jsonify({"ok": False})

    cambiar_estado_pedido(id, "reenviado")
    return jsonify({"ok": True, "grupo": ENLACE_GRUPO_WHATSAPP})

# ------------------------
if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)
