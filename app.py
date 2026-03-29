import os
import uuid
import requests
import ssl
import pymongo

import cloudinary
import cloudinary.uploader

from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient, DESCENDING

# --- BLOQUE DE DEPURACIÓN PARA SERGIO ---
# Esto imprimirá las versiones exactas en tus logs de Render
print("--- DATOS DE ENTORNO PARA SERGIO ---")
print("OPENSSL:", ssl.OPENSSL_VERSION)
print("PYMONGO:", pymongo.version)
print("------------------------------------")

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
# MONGODB (AJUSTADO PARA RENDER)
# ------------------------
MONGO_URI = os.environ.get("MONGO_URI", "").strip()

mongo_client = None
mongo_db = None
productos_col = None
categorias_col = None

if MONGO_URI:
    try:
        # Usamos los parámetros de compatibilidad para el handshake TLS
        mongo_client = MongoClient(
            MONGO_URI,
            connect=True,
            tls=True,
            tlsAllowInvalidCertificates=True,
            retryWrites=False,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000
        )

        # Prueba de fuego: Ping a la base de datos
        mongo_client.admin.command("ping")

        mongo_db = mongo_client["mercado_cln"]
        productos_col = mongo_db["productos"]
        categorias_col = mongo_db["categorias"]

        # Índices automáticos
        if productos_col is not None:
            productos_col.create_index("id", unique=True)
            productos_col.create_index("categoria_id")
        if categorias_col is not None:
            categorias_col.create_index("id", unique=True)

        print("✅ MONGO CONECTADO OK")

    except Exception as e:
        print(f"❌ Error final en MongoDB: {e}")
        mongo_client = None
else:
    print("❌ Falta la variable MONGO_URI en el panel de Render")

# ------------------------
# CONFIGURACIÓN GENERAL
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

def obtener_siguiente_id(coleccion):
    if coleccion is None: return 1
    ultimo = coleccion.find_one({}, {"id": 1}, sort=[("id", DESCENDING)])
    return int(ultimo.get("id", 0)) + 1 if ultimo else 1

def convertir_float(valor, default=0):
    try:
        return float(valor) if valor else float(default)
    except:
        return float(default)

def obtener_carrito_desde_session():
    carrito = session.get("carrito", [])
    if isinstance(carrito, dict):
        carrito = list(carrito.values())
    return carrito if isinstance(carrito, list) else []

def obtener_datos_entrega():
    ds = session.get("datos_entrega", {})
    return {
        "nombre": request.form.get("nombre") or ds.get("nombre") or "",
        "telefono": request.form.get("telefono") or ds.get("telefono") or "",
        "direccion": request.form.get("direccion") or ds.get("direccion") or "",
        "colonia": request.form.get("colonia") or ds.get("colonia") or "",
        "referencia": request.form.get("referencia") or ds.get("referencia") or "",
        "metodo_pago": request.form.get("metodo_pago") or ds.get("metodo_pago") or "",
        "tipo_entrega": request.form.get("tipo_entrega") or ds.get("tipo_entrega") or "",
        "comentarios": request.form.get("comentarios") or ds.get("comentarios") or ""
    }

def construir_mensaje_pedido():
    carrito = obtener_carrito_desde_session()
    datos = obtener_datos_entrega()
    lineas = ["🛒 *NUEVO PEDIDO DESDE LA APP*", ""]
    
    if carrito:
        lineas.append("*Productos:*")
        subtotal = 0
        for i, item in enumerate(carrito, start=1):
            cant = int(item.get("cantidad", 1))
            pre = convertir_float(item.get("precio", 0))
            total_i = cant * pre
            subtotal += total_i
            lineas.append(f"{i}. {item.get('nombre')} x{cant} - ${total_i:.2f}")
        
        envio = COSTO_ENVIO if "domicilio" in datos.get("tipo_entrega", "").lower() else 0
        lineas.append(f"\n*Subtotal:* ${subtotal:.2f}")
        lineas.append(f"*Envío:* ${envio:.2f}")
        lineas.append(f"*Total:* ${subtotal + envio:.2f}")
    
    lineas.append("\n*Datos de entrega:*")
    for k, v in datos.items():
        if v: lineas.append(f"{k.capitalize()}: {v}")
    return "\n".join(lineas)

def enviar_whatsapp_green_api(texto):
    if not all([GREEN_API_INSTANCE, GREEN_API_TOKEN, GREEN_API_CHAT_ID]):
        return False
    url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
    chat_id = GREEN_API_CHAT_ID if "@" in GREEN_API_CHAT_ID else f"{GREEN_API_CHAT_ID}@g.us"
    try:
        requests.post(url, json={"chatId": chat_id, "message": texto}, timeout=10)
        return True
    except:
        return False

# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    cats = list(categorias_col.find({}, {"_id": 0}).sort("id", 1)) if categorias_col else []
    return render_template("index.html", categorias=cats)

@app.route("/categoria/<int:id>")
def categoria(id):
    cat = categorias_col.find_one({"id": id}, {"_id": 0}) if categorias_col else None
    prods = list(productos_col.find({"categoria_id": id}, {"_id": 0}).sort("id", 1)) if productos_col else []
    return render_template("categoria.html", categoria=cat, productos=prods)

@app.route("/admin")
def admin():
    cats = list(categorias_col.find({}, {"_id": 0}).sort("id", 1)) if categorias_col else []
    prods = list(productos_col.find({}, {"_id": 0}).sort("id", 1)) if productos_col else []
    return render_template("admin.html", categorias=cats, productos=prods)

@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = (request.form.get("nombre") or "").strip()
    foto = request.files.get("foto")
    if nombre and categorias_col:
        url = guardar_imagen(foto)
        categorias_col.insert_one({"id": obtener_siguiente_id(categorias_col), "nombre": nombre, "foto": url})
    return redirect("/admin")

@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = (request.form.get("nombre") or "").strip()
    cat_id = request.form.get("categoria_id")
    if nombre and cat_id and productos_col:
        productos_col.insert_one({
            "id": obtener_siguiente_id(productos_col),
            "nombre": nombre,
            "precio": convertir_float(request.form.get("precio")),
            "categoria_id": int(cat_id),
            "descripcion": request.form.get("descripcion", ""),
            "foto": guardar_imagen(request.files.get("foto_producto"))
        })
    return redirect("/admin")

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    if enviar_whatsapp_green_api(construir_mensaje_pedido()):
        session.pop("carrito", None)
    return redirect("/")

# ------------------------
# LANZAMIENTO
# ------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
