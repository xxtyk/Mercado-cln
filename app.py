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

if DATABASE_URL:
    print("✅ DATABASE_URL detectada")
else:
    print("❌ Falta DATABASE_URL")


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


def resolver_imagen(url):
    if not url:
        return ""
    return url


app.jinja_env.globals.update(resolver_imagen=resolver_imagen)

# ------------------------
# CARRITO
# ------------------------
def obtener_carrito():
    carrito = session.get("carrito", [])
    if isinstance(carrito, dict):
        carrito = list(carrito.values())
    if not isinstance(carrito, list):
        carrito = []
    return carrito


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def carrito_cantidad_total():
    carrito = obtener_carrito()
    return sum(int(item.get("cantidad", 1)) for item in carrito)


def carrito_importe_total():
    carrito = obtener_carrito()
    total = 0
    for item in carrito:
        total += float(item.get("precio", 0)) * int(item.get("cantidad", 1))
    return total


def obtener_datos_entrega():
    datos_session = session.get("datos_entrega", {})
    if not isinstance(datos_session, dict):
        datos_session = {}

    return {
        "nombre": datos_session.get("nombre", ""),
        "telefono": datos_session.get("telefono", ""),
        "vendedor": datos_session.get("vendedor", ""),
        "tipo_entrega": datos_session.get("tipo_entrega", ""),
        "direccion": datos_session.get("direccion", ""),
        "colonia": datos_session.get("colonia", ""),
        "referencia": datos_session.get("referencia", ""),
    }

# ------------------------
# WHATSAPP
# ------------------------
def construir_mensaje_pedido():
    carrito = obtener_carrito()
    datos = obtener_datos_entrega()

    lineas = []
    lineas.append("🛒 *NUEVO PEDIDO DESDE LA APP*")
    lineas.append("")

    subtotal = 0

    if carrito:
        lineas.append("*Productos:*")

        for i, item in enumerate(carrito, start=1):
            nombre = str(item.get("nombre", "Producto")).strip()
            cantidad = int(item.get("cantidad", 1) or 1)
            precio = convertir_float(item.get("precio", 0))

            total_item = precio * cantidad
            subtotal += total_item

            lineas.append(f"{i}. {nombre}")
            lineas.append(f"   Cantidad: {cantidad}")
            lineas.append(f"   Precio: ${precio:.2f}")
            lineas.append(f"   Total: ${total_item:.2f}")
    else:
        lineas.append("No se encontraron productos en el carrito.")

    envio = COSTO_ENVIO if datos.get("tipo_entrega") == "domicilio" else 0
    total_general = subtotal + envio

    lineas.append("")
    lineas.append(f"*Subtotal:* ${subtotal:.2f}")
    lineas.append(f"*Envío:* ${envio:.2f}")
    lineas.append(f"*Total:* ${total_general:.2f}")

    lineas.append("")
    lineas.append("*Datos de entrega:*")
    lineas.append(f"Nombre: {datos.get('nombre') or 'No capturado'}")
    lineas.append(f"Teléfono: {datos.get('telefono') or 'No capturado'}")
    lineas.append(f"Vendedor: {datos.get('vendedor') or 'No capturado'}")
    lineas.append(f"Tipo de entrega: {datos.get('tipo_entrega') or 'No capturado'}")
    lineas.append(f"Dirección: {datos.get('direccion') or 'No capturada'}")
    lineas.append(f"Colonia: {datos.get('colonia') or 'No capturada'}")
    lineas.append(f"Referencia: {datos.get('referencia') or 'No capturada'}")
    lineas.append("")
    lineas.append("💵 Pago contra entrega. El cliente paga al momento que recibe su pedido.")

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

# ------------------------
# CONSULTAS
# ------------------------
def listar_categorias():
    if not DATABASE_URL:
        return []

    try:
        with get_conn() as conexion:
            with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT id, nombre, foto FROM categorias ORDER BY id ASC")
                filas = cur.fetchall()
                return [dict(x) for x in filas]
    except Exception as e:
        print("❌ Error listando categorías:", str(e))
        return []


def listar_productos():
    if not DATABASE_URL:
        return []

    try:
        with get_conn() as conexion:
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
    if not DATABASE_URL:
        return None

    try:
        with get_conn() as conexion:
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


def obtener_producto_por_id(producto_id):
    if not DATABASE_URL:
        return None

    try:
        with get_conn() as conexion:
            with conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, nombre, precio, categoria_id, descripcion, foto
                    FROM productos
                    WHERE id = %s
                """, (producto_id,))
                fila = cur.fetchone()
                if not fila:
                    return None
                item = dict(fila)
                item["precio"] = float(item["precio"] or 0)
                return item
    except Exception as e:
        print("❌ Error obteniendo producto:", str(e))
        return None


def listar_productos_por_categoria(categoria_id):
    if not DATABASE_URL:
        return []

    try:
        with get_conn() as conexion:
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
# RUTAS TIENDA
# ------------------------
@app.route("/")
def inicio():
    categorias = listar_categorias()
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:id>")
def categoria(id):
    categoria_actual = obtener_categoria_por_id(id)
    productos = listar_productos_por_categoria(id)
    return render_template(
        "categoria.html",
        categoria=categoria_actual,
        productos=productos,
        carrito_cantidad_total=carrito_cantidad_total(),
        carrito_importe_total=carrito_importe_total()
    )


@app.route("/agregar_al_carrito/<int:producto_id>", methods=["POST"])
def agregar_al_carrito(producto_id):
    try:
        cantidad = int(request.form.get("cantidad", 1))
        if cantidad < 1:
            cantidad = 1

        producto = obtener_producto_por_id(producto_id)
        if not producto:
            return redirect(request.referrer or url_for("inicio"))

        carrito = obtener_carrito()
        encontrado = False

        for item in carrito:
            if int(item.get("id")) == int(producto_id):
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

    except Exception as e:
        print("❌ Error agregando al carrito:", str(e))
        return redirect(request.referrer or url_for("inicio"))


@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito()
    subtotal = carrito_importe_total()
    return render_template("carrito.html", carrito=carrito, subtotal=subtotal)


@app.route("/carrito/actualizar/<int:producto_id>", methods=["POST"])
def actualizar_carrito(producto_id):
    accion = request.form.get("accion", "").strip()
    carrito = obtener_carrito()

    for item in carrito[:]:
        if int(item.get("id")) == int(producto_id):
            cantidad_actual = int(item.get("cantidad", 1))

            if accion == "sumar":
                item["cantidad"] = cantidad_actual + 1
            elif accion == "restar":
                item["cantidad"] = max(1, cantidad_actual - 1)
            elif accion == "eliminar":
                carrito.remove(item)

            break

    guardar_carrito(carrito)
    return redirect(url_for("ver_carrito"))


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    session["carrito"] = []
    session.modified = True
    return redirect(url_for("ver_carrito"))


@app.route("/datos_entrega", methods=["GET", "POST"])
def datos_entrega():
    carrito = obtener_carrito()
    subtotal = carrito_importe_total()

    if not carrito:
        return redirect(url_for("inicio"))

    if request.method == "POST":
        session["datos_entrega"] = {
            "nombre": (request.form.get("nombre") or "").strip(),
            "telefono": (request.form.get("telefono") or "").strip(),
            "vendedor": (request.form.get("vendedor") or "").strip(),
            "tipo_entrega": (request.form.get("tipo_entrega") or "").strip(),
            "direccion": (request.form.get("direccion") or "").strip(),
            "colonia": (request.form.get("colonia") or "").strip(),
            "referencia": (request.form.get("referencia") or "").strip(),
        }
        session.modified = True
        return redirect(url_for("confirmar_pedido"))

    datos = session.get("datos_entrega", {})
    return render_template(
        "datos_entrega.html",
        subtotal=subtotal,
        datos=datos,
        vendedores=VENDEDORES
    )


@app.route("/confirmar_pedido")
def confirmar_pedido():
    carrito = obtener_carrito()
    datos = session.get("datos_entrega", {})

    if not carrito:
        return redirect(url_for("inicio"))

    subtotal = carrito_importe_total()
    envio = COSTO_ENVIO if datos.get("tipo_entrega") == "domicilio" else 0
    total = subtotal + envio

    return render_template(
        "confirmar_pedido.html",
        carrito=carrito,
        datos=datos,
        subtotal=subtotal,
        envio=envio,
        total=total
    )


@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    texto = construir_mensaje_pedido()
    enviado = enviar_whatsapp_green_api(texto)

    if enviado:
        session.pop("carrito", None)
        session.pop("datos_entrega", None)
        session.modified = True

    return redirect(url_for("inicio"))

# ------------------------
# RUTAS ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = listar_categorias()
    productos = listar_productos()
    return render_template("admin.html", categorias=categorias, productos=productos)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    try:
        nombre = (request.form.get("nombre") or "").strip()
        foto = request.files.get("foto")

        if not nombre:
            return redirect("/admin")

        foto_url = guardar_imagen(foto) if foto and foto.filename else ""

        with get_conn() as conexion:
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


@app.route("/editar_categoria/<int:categoria_id>", methods=["GET", "POST"])
def editar_categoria(categoria_id):
    categoria = obtener_categoria_por_id(categoria_id)

    if not categoria:
        return redirect("/admin")

    if request.method == "POST":
        try:
            nombre = (request.form.get("nombre") or "").strip()
            foto = request.files.get("foto")

            nueva_foto = categoria.get("foto", "")
            if foto and foto.filename:
                nueva_foto = guardar_imagen(foto)

            with get_conn() as conexion:
                with conexion.cursor() as cur:
                    cur.execute("""
                        UPDATE categorias
                        SET nombre = %s, foto = %s
                        WHERE id = %s
                    """, (nombre, nueva_foto, categoria_id))

            print("✅ Categoría editada")
            return redirect("/admin")

        except Exception as e:
            print("❌ Error editando categoría:", str(e))
            return redirect("/admin")

    return render_template("editar_categoria.html", categoria=categoria)


@app.route("/eliminar_categoria/<int:categoria_id>", methods=["POST"])
def eliminar_categoria(categoria_id):
    try:
        with get_conn() as conexion:
            with conexion.cursor() as cur:
                cur.execute("UPDATE productos SET categoria_id = NULL WHERE categoria_id = %s", (categoria_id,))
                cur.execute("DELETE FROM categorias WHERE id = %s", (categoria_id,))

        print("✅ Categoría eliminada")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error eliminando categoría:", str(e))
        return redirect("/admin")


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    try:
        nombre = (request.form.get("nombre") or "").strip()
        precio = convertir_float(request.form.get("precio"), 0)
        categoria_id = request.form.get("categoria_id")
        descripcion = (request.form.get("descripcion") or "").strip()
        foto = request.files.get("foto_producto")

        if not nombre or not categoria_id:
            return redirect("/admin")

        foto_url = guardar_imagen(foto) if foto and foto.filename else ""

        with get_conn() as conexion:
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


@app.route("/editar_producto/<int:producto_id>", methods=["GET", "POST"])
def editar_producto(producto_id):
    producto = obtener_producto_por_id(producto_id)
    categorias = listar_categorias()

    if not producto:
        return redirect("/admin")

    if request.method == "POST":
        try:
            nombre = (request.form.get("nombre") or "").strip()
            precio = convertir_float(request.form.get("precio"), 0)
            categoria_id = request.form.get("categoria_id")
            descripcion = (request.form.get("descripcion") or "").strip()
            foto = request.files.get("foto_producto")

            nueva_foto = producto.get("foto", "")
            if foto and foto.filename:
                nueva_foto = guardar_imagen(foto)

            with get_conn() as conexion:
                with conexion.cursor() as cur:
                    cur.execute("""
                        UPDATE productos
                        SET nombre = %s, precio = %s, categoria_id = %s, descripcion = %s, foto = %s
                        WHERE id = %s
                    """, (nombre, precio, int(categoria_id), descripcion, nueva_foto, producto_id))

            print("✅ Producto editado")
            return redirect("/admin")

        except Exception as e:
            print("❌ Error editando producto:", str(e))
            return redirect("/admin")

    return render_template("editar_producto.html", producto=producto, categorias=categorias)


@app.route("/eliminar_producto/<int:producto_id>", methods=["POST"])
def eliminar_producto(producto_id):
    try:
        with get_conn() as conexion:
            with conexion.cursor() as cur:
                cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))

        print("✅ Producto eliminado")
        return redirect("/admin")

    except Exception as e:
        print("❌ Error eliminando producto:", str(e))
        return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
