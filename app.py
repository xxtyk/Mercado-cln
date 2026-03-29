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
        print("✅ DB OK")
    except Exception as e:
        print("❌ DB:", str(e))

init_db()

# ------------------------
# CONFIG (Aquí ya puse tus datos de Green API)
# ------------------------
EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}
COSTO_ENVIO = 40

# TUS DATOS REALES DE GREEN API:
GREEN_API_INSTANCE = "7107547964"
GREEN_API_TOKEN = "1e6ec2470cfe4808a27cee392009c87bda99eaf03fa64a70b6"
# RECUERDA: Cambia el ID de abajo por el de tu grupo cuando lo tengas
GREEN_API_CHAT_ID = "120363321558514561@g.us" 

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
        print("❌ Cloudinary:", str(e))
        return ""

def convertir_float(v, d=0):
    try:
        return float(v) if v not in (None, "") else float(d)
    except:
        return float(d)

def convertir_int(v, d=0):
    try:
        return int(v) if v not in (None, "") else int(d)
    except:
        return int(d)

# ------------------------
# CARRITO
# ------------------------
def obtener_carrito():
    return session.get("carrito", [])

def guardar_carrito(c):
    session["carrito"] = c
    session.modified = True

def carrito_total():
    total = 0
    for i in obtener_carrito():
        total += float(i.get("precio", 0)) * int(i.get("cantidad", 1))
    return total

# ------------------------
# WHATSAPP (CONECTADO A GREEN API)
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

    envio = COSTO_ENVIO if datos.get("tipo_entrega") == "domicilio" else 0
    total += envio

    texto += f"\n💰 Total: ${total:.2f}\n\n"
    texto += f"👤 Cliente: {datos.get('nombre', 'N/A')}\n"
    texto += f"📱 Tel: {datos.get('telefono', 'N/A')}\n"
    texto += f"📍 Dir: {datos.get('direccion', 'N/A')}\n"

    return texto

def enviar_whatsapp(texto):
    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
        payload = {
            "chatId": GREEN_API_CHAT_ID,
            "message": texto
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers, timeout=10)
        if r.status_code == 200:
            print("✅ Enviado a WhatsApp correctamente")
        else:
            print(f"❌ Error API: {r.text}")
    except Exception as e:
        print("❌ WhatsApp Error:", str(e))

# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar(id):
    carrito = obtener_carrito()
    cantidad = convertir_int(request.form.get("cantidad"), 1)

    carrito.append({
        "id": id,
        "nombre": "Producto",
        "precio": 100,
        "cantidad": cantidad
    })

    guardar_carrito(carrito)
    return redirect("/")

@app.route("/datos_entrega", methods=["GET","POST"])
def datos():
    if request.method == "POST":
        session["datos_entrega"] = request.form
        return redirect("/finalizar_pedido")
    return render_template("datos_entrega.html")

# 🔥 FINALIZAR (AQUÍ ESTÁ LA CONEXIÓN)
@app.route("/finalizar_pedido", methods=["GET","POST"])
def finalizar():
    carrito = obtener_carrito()
    if not carrito:
        return redirect("/")

    # Construye el mensaje completo
    texto = construir_mensaje()

    # 🔥 ENVÍA A GREEN API DIRECTO AL GRUPO
    enviar_whatsapp(texto)

    # Limpiar carrito y datos después de enviar
    session.pop("carrito", None)
    session.pop("datos_entrega", None)

    return redirect("/")

# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
