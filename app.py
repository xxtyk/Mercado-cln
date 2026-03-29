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
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    try:
        with get_conn() as conexion:
            with conexion.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS categorias (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT,
                        foto TEXT
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS productos (
                        id SERIAL PRIMARY KEY,
                        nombre TEXT,
                        precio NUMERIC,
                        categoria_id INTEGER,
                        descripcion TEXT,
                        foto TEXT
                    );
                """)
    except Exception as e:
        print("❌ DB:", str(e))

init_db()

# ------------------------
# GREEN API
# ------------------------
GREEN_API_INSTANCE = os.environ.get("GREEN_API_INSTANCE", "")
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN", "")
GREEN_API_CHAT_ID = os.environ.get("GREEN_API_CHAT_ID", "")

def enviar_whatsapp_green_api(texto):
    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
        payload = {
            "chatId": GREEN_API_CHAT_ID,
            "message": texto
        }
        requests.post(url, json=payload)
    except Exception as e:
        print("❌ WhatsApp:", str(e))

# ------------------------
# CARRITO
# ------------------------
def obtener_carrito():
    return session.get("carrito", [])

def guardar_carrito(c):
    session["carrito"] = c
    session.modified = True

# ------------------------
# MENSAJE
# ------------------------
def construir_mensaje_pedido():
    carrito = obtener_carrito()
    datos = session.get("datos_entrega", {})

    mensaje = "🛒 *NUEVO PEDIDO*\n\n"
    total = 0

    for item in carrito:
        subtotal = float(item["precio"]) * int(item["cantidad"])
        total += subtotal
        mensaje += f"• {item['nombre']} x{item['cantidad']} = ${subtotal}\n"

    mensaje += f"\n💰 Total: ${total}\n\n"
    mensaje += f"👤 {datos.get('nombre')}\n"
    mensaje += f"📱 {datos.get('telefono')}\n"
    mensaje += f"📍 {datos.get('direccion')}\n"

    return mensaje

# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    carrito = obtener_carrito()
    cantidad = int(request.form.get("cantidad", 1))

    carrito.append({
        "id": id,
        "nombre": "Producto",
        "precio": 100,
        "cantidad": cantidad
    })

    guardar_carrito(carrito)
    return redirect("/")

@app.route("/datos_entrega", methods=["GET", "POST"])
def datos_entrega():
    if request.method == "POST":
        session["datos_entrega"] = request.form
        return redirect("/finalizar_pedido")
    return render_template("datos_entrega.html")

# =========================
# FINALIZAR PEDIDO (GREEN API)
# =========================
@app.route("/finalizar_pedido", methods=["GET","POST"])
def finalizar_pedido():

    carrito = obtener_carrito()

    if not carrito:
        return redirect("/")

    texto = construir_mensaje_pedido()

    # 🔥 ENVÍA A WHATSAPP
    enviar_whatsapp_green_api(texto)

    # limpiar
    session.pop("carrito", None)
    session.pop("datos_entrega", None)

    return redirect("/")

# ------------------------
# RUN
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
