import os
import uuid
import requests

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ------------------------
# CLOUDINARY
# ------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# ------------------------
# MONGODB
# ------------------------
MONGO_URI = os.environ.get("MONGO_URI", "").strip()
mongo_client = MongoClient(MONGO_URI) if MONGO_URI else None
mongo_db = mongo_client["mercado_cln"] if mongo_client is not None else None

productos_col = mongo_db["productos"] if mongo_db is not None else None
categorias_col = mongo_db["categorias"] if mongo_db is not None else None

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


def resolver_imagen(imagen):
    if not imagen:
        return url_for("static", filename="logo.png")

    imagen = str(imagen).strip()

    if imagen.startswith("http://") or imagen.startswith("https://"):
        return imagen

    return url_for("static", filename=imagen)


def obtener_siguiente_id(coleccion):
    if coleccion is None:
        return 1

    ultimo = coleccion.find_one(sort=[("id", -1)])
    return int(ultimo.get("id", 0)) + 1 if ultimo else 1


def guardar_imagen(archivo):
    if not archivo or archivo.filename == "":
        return ""

    if not extension_permitida(archivo.filename):
        return ""

    try:
        nombre_seguro = secure_filename(archivo.filename)
        resultado = cloudinary.uploader.upload(
            archivo,
            folder="mercado_cln",
            public_id=f"{uuid.uuid4().hex}_{nombre_seguro}",
            resource_type="image"
        )
        return resultado.get("secure_url", "")
    except Exception as e:
        print("Error Cloudinary:", e)
        return ""


def obtener_carrito():
    carrito = session.get("carrito", [])
    return carrito if isinstance(carrito, list) else []


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def total_importe_carrito():
    total = 0
    for item in obtener_carrito():
        try:
            total += float(item.get("precio", 0)) * int(item.get("cantidad", 0))
        except Exception:
            pass
    return total


def total_items_carrito():
    return sum(int(i.get("cantidad", 0)) for i in obtener_carrito())


def calcular_totales(tipo_entrega="recoger"):
    subtotal = total_importe_carrito()
    costo_envio = COSTO_ENVIO if str(tipo_entrega).strip().lower() == "domicilio" else 0
    total = subtotal + costo_envio
    return subtotal, costo_envio, total


@app.context_processor
def ctx():
    return {
        "carrito_cantidad_total": total_items_carrito(),
        "carrito_importe_total": total_importe_carrito(),
        "resolver_imagen": resolver_imagen,
        "COSTO_ENVIO": COSTO_ENVIO
    }


def listar_categorias():
    if categorias_col is None:
        return []
    return list(categorias_col.find({}, {"_id": 0}).sort("id", 1))


def listar_productos():
    if productos_col is None:
        return []
    return list(productos_col.find({}, {"_id": 0}).sort("id", 1))


def obtener_categoria_por_id(categoria_id):
    if categorias_col is None:
        return None
    return categorias_col.find_one({"id": int(categoria_id)}, {"_id": 0})


def obtener_producto_por_id(producto_id):
    if productos_col is None:
        return None
    return productos_col.find_one({"id": int(producto_id)}, {"_id": 0})


# ------------------------
# RUTAS CLIENTE
# ------------------------
@app.route("/")
def inicio():
    return render_template("portada.html")


@app.route("/catalogo")
def catalogo():
    categorias = listar_categorias()
    return render_template("index.html", categorias=categorias)


@app.route("/categoria/<int:categoria_id>")
def ver_categoria(categoria_id):
    categoria = obtener_categoria_por_id(categoria_id)
    if not categoria:
        return "Categoría no encontrada", 404

    productos = []
    if productos_col is not None:
        productos = list(productos_col.find({"categoria_id": int(categoria_id)}, {"_id": 0}).sort("id", 1))

    return render_template("categoria.html", categoria=categoria, productos=productos)


# ------------------------
# CARRITO
# ------------------------
@app.route("/agregar_al_carrito/<int:producto_id>", methods=["POST"])
def agregar_al_carrito(producto_id):
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return redirect(url_for("catalogo"))

    carrito = obtener_carrito()

    try:
        cantidad = int(request.form.get("cantidad", "1"))
        if cantidad < 1:
            cantidad = 1
    except Exception:
        cantidad = 1

    descripcion = request.form.get("descripcion", "").strip()

    item_existente = None
    for item in carrito:
        if int(item.get("producto_id", 0)) == producto_id and item.get("descripcion", "") == descripcion:
            item_existente = item
            break

    if item_existente:
        item_existente["cantidad"] = int(item_existente.get("cantidad", 0)) + cantidad
    else:
        carrito.append({
            "producto_id": producto_id,
            "nombre": producto.get("nombre", ""),
            "precio": float(producto.get("precio", 0)),
            "cantidad": cantidad,
            "foto": producto.get("foto", ""),
            "descripcion": descripcion
        })

    guardar_carrito(carrito)
    return redirect(request.referrer or url_for("ver_categoria", categoria_id=producto.get("categoria_id")))


@app.route("/carrito")
def ver_carrito():
    carrito = obtener_carrito()
    subtotal, costo_envio, total = calcular_totales("recoger")
    return render_template(
        "carrito.html",
        carrito=carrito,
        subtotal=subtotal,
        costo_envio=costo_envio,
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

    if len(carrito) == 0:
        session.pop("carrito", None)
    else:
        guardar_carrito(carrito)

    session.modified = True
    return redirect(url_for("ver_carrito"))


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("ver_carrito"))


# ------------------------
# PEDIDO / DATOS ENTREGA
# ------------------------
@app.route("/datos_entrega", methods=["GET", "POST"])
def datos_entrega():
    carrito = obtener_carrito()
    if not carrito:
        return redirect(url_for("ver_carrito"))

    tipo_entrega = request.values.get("tipo_entrega", "recoger").strip().lower()
    subtotal, costo_envio, total = calcular_totales(tipo_entrega)

    return render_template(
        "datos_entrega.html",
        carrito=carrito,
        subtotal=subtotal,
        costo_envio=costo_envio,
        total=total,
        tipo_entrega=tipo_entrega,
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
    nota = request.form.get("nota", "").strip()
    tipo_entrega = request.form.get("tipo_entrega", "recoger").strip().lower()
    vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()

    if vendedor not in VENDEDORES:
        vendedor = "Mercado en Línea Culiacán"

    subtotal, costo_envio, total = calcular_totales(tipo_entrega)
    texto_entrega = "Envío a domicilio en Culiacán" if tipo_entrega == "domicilio" else "Pasa a recoger a bodega"

    mensaje = []
    mensaje.append("🛒 *NUEVO PEDIDO*")
    mensaje.append("")
    mensaje.append(f"👤 *Nombre:* {nombre}")
    mensaje.append(f"📞 *Teléfono:* {telefono}")
    mensaje.append(f"🚚 *Entrega:* {texto_entrega}")
    mensaje.append(f"👨‍💼 *Vendedor:* {vendedor}")

    if direccion:
        mensaje.append(f"📍 *Dirección:* {direccion}")
    if colonia:
        mensaje.append(f"🏘️ *Colonia:* {colonia}")
    if nota:
        mensaje.append(f"📝 *Nota:* {nota}")

    mensaje.append("")
    mensaje.append("*Productos:*")

    for item in carrito:
        cantidad = int(item.get("cantidad", 0))
        nombre_producto = item.get("nombre", "")
        precio = float(item.get("precio", 0))
        descripcion = item.get("descripcion", "").strip()
        importe = int(precio * cantidad)

        linea = f"• {cantidad} x {nombre_producto} - ${importe}"
        if descripcion:
            linea += f" ({descripcion})"
        mensaje.append(linea)

    mensaje.append("")
    mensaje.append(f"Subtotal: ${int(subtotal)}")
    mensaje.append(f"Envío: ${int(costo_envio)}")
    mensaje.append(f"Total: ${int(total)}")

    texto = "\n".join(mensaje)

    try:
        if not GREEN_API_INSTANCE or not GREEN_API_TOKEN or not GREEN_API_CHAT_ID:
            print("Faltan variables de Green API")
            return redirect(url_for("datos_entrega"))

        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

        chat_id = GREEN_API_CHAT_ID.strip()
        if not chat_id.endswith("@g.us") and not chat_id.endswith("@c.us"):
            chat_id = f"{chat_id}@g.us"

        payload = {
            "chatId": chat_id,
            "message": texto
        }

        response = requests.post(url, json=payload, timeout=20)
        print("Green API:", response.status_code, response.text)

        if response.status_code not in [200, 201]:
            return redirect(url_for("datos_entrega"))

    except Exception as e:
        print("Error WhatsApp:", e)
        return redirect(url_for("datos_entrega"))

    session.pop("carrito", None)
    session.modified = True
    return redirect(url_for("inicio"))


# ------------------------
# ADMIN
# ------------------------
@app.route("/admin")
def admin():
    categorias = listar_categorias()
    productos = listar_productos()
    return render_template("admin.html", categorias=categorias, productos=productos, vendedores=VENDEDORES)


@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    if categorias_col is None:
        return redirect(url_for("admin"))

    nombre = request.form.get("nombre", "").strip()
    foto = request.files.get("foto_categoria")

    if not nombre:
        return redirect(url_for("admin"))

    nueva = {
        "id": obtener_siguiente_id(categorias_col),
        "nombre": nombre,
        "foto": guardar_imagen(foto)
    }

    categorias_col.insert_one(nueva)
    return redirect(url_for("admin"))


@app.route("/editar_categoria/<int:categoria_id>", methods=["GET", "POST"])
def editar_categoria(categoria_id):
    if categorias_col is None:
        return redirect(url_for("admin"))

    categoria = obtener_categoria_por_id(categoria_id)
    if not categoria:
        return "Categoría no encontrada", 404

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        foto = request.files.get("foto_categoria")

        cambios = {}

        if nombre:
            cambios["nombre"] = nombre

        nueva_foto = guardar_imagen(foto)
        if nueva_foto:
            cambios["foto"] = nueva_foto

        if cambios:
            categorias_col.update_one({"id": categoria_id}, {"$set": cambios})

        return redirect(url_for("admin"))

    return render_template("editar_categoria.html", categoria=categoria)


@app.route("/eliminar_categoria/<int:categoria_id>", methods=["POST"])
def eliminar_categoria(categoria_id):
    if categorias_col is None or productos_col is None:
        return redirect(url_for("admin"))

    categorias_col.delete_one({"id": categoria_id})
    productos_col.delete_many({"categoria_id": categoria_id})
    return redirect(url_for("admin"))


@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    if productos_col is None:
        return redirect(url_for("admin"))

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

    nuevo = {
        "id": obtener_siguiente_id(productos_col),
        "nombre": nombre,
        "precio": float(precio or 0),
        "descripcion": descripcion,
        "categoria_id": int(categoria_id),
        "foto": guardar_imagen(foto),
        "vendedor": vendedor
    }

    productos_col.insert_one(nuevo)
    return redirect(url_for("admin"))


@app.route("/editar_producto/<int:producto_id>", methods=["GET", "POST"])
def editar_producto(producto_id):
    if productos_col is None:
        return redirect(url_for("admin"))

    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return "Producto no encontrado", 404

    categorias = listar_categorias()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        precio = request.form.get("precio", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        categoria_id = request.form.get("categoria_id", "").strip()
        vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()
        foto = request.files.get("foto_producto")

        cambios = {}

        if nombre:
            cambios["nombre"] = nombre

        if precio != "":
            try:
                cambios["precio"] = float(precio)
            except Exception:
                pass

        cambios["descripcion"] = descripcion

        if categoria_id:
            try:
                cambios["categoria_id"] = int(categoria_id)
            except Exception:
                pass

        if vendedor in VENDEDORES:
            cambios["vendedor"] = vendedor
        else:
            cambios["vendedor"] = "Mercado en Línea Culiacán"

        nueva_foto = guardar_imagen(foto)
        if nueva_foto:
            cambios["foto"] = nueva_foto

        productos_col.update_one({"id": producto_id}, {"$set": cambios})
        return redirect(url_for("admin"))

    return render_template(
        "editar_producto.html",
        producto=producto,
        categorias=categorias,
        vendedores=VENDEDORES
    )


@app.route("/eliminar_producto/<int:producto_id>", methods=["POST"])
def eliminar_producto(producto_id):
    if productos_col is None:
        return redirect(url_for("admin"))

    productos_col.delete_one({"id": producto_id})
    return redirect(url_for("admin"))


# ------------------------
# APP
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
