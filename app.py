import os
import uuid
import requests
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ------------------------
# DB
# ------------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
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
                    foto TEXT
                );
            """)

            # 🔥 AUTOCREAR CATEGORÍAS
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

init_db()

# ------------------------
# GREEN API
# ------------------------
GREEN_API_INSTANCE = os.environ.get("GREEN_API_INSTANCE")
GREEN_API_TOKEN = os.environ.get("GREEN_API_TOKEN")
GREEN_API_CHAT_ID = os.environ.get("GREEN_API_CHAT_ID")

def enviar_whatsapp(texto):
    try:
        url = f"https://api.green-api.com/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"
        payload = {
            "chatId": GREEN_API_CHAT_ID,
            "message": texto
        }
        requests.post(url, json=payload)
        print("✅ enviado a WhatsApp")
    except Exception as e:
        print("❌ WhatsApp:", e)

# ------------------------
# CONSULTAS
# ------------------------
def listar_categorias():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM categorias ORDER BY id")
            return cur.fetchall()

def listar_productos(cat_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM productos WHERE categoria_id=%s", (cat_id,))
            return cur.fetchall()

def obtener_producto(id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM productos WHERE id=%s", (id,))
            return cur.fetchone()

# ------------------------
# CARRITO
# ------------------------
def obtener_carrito():
    return session.get("carrito", [])

def guardar_carrito(c):
    session["carrito"] = c
    session.modified = True

# ------------------------
# RUTAS
# ------------------------
@app.route("/")
def inicio():
    categorias = listar_categorias()
    return render_template("index.html", categorias=categorias)

@app.route("/categoria/<int:id>")
def categoria(id):
    productos = listar_productos(id)
    return render_template("categoria.html", productos=productos)

@app.route("/agregar/<int:id>", methods=["POST"])
def agregar(id):
    producto = obtener_producto(id)
    carrito = obtener_carrito()

    carrito.append({
        "nombre": producto["nombre"],
        "precio": float(producto["precio"]),
        "cantidad": int(request.form.get("cantidad", 1))
    })

    guardar_carrito(carrito)
    return redirect("/")

@app.route("/datos", methods=["GET","POST"])
def datos():
    if request.method == "POST":
        session["datos"] = request.form
        return redirect("/finalizar")
    return render_template("datos_entrega.html")

# 🔥 FINALIZAR
@app.route("/finalizar")
def finalizar():
    carrito = obtener_carrito()
    datos = session.get("datos", {})

    mensaje = "🛒 PEDIDO\n\n"
    total = 0

    for item in carrito:
        subtotal = item["precio"] * item["cantidad"]
        total += subtotal
        mensaje += f"{item['nombre']} x{item['cantidad']} = ${subtotal}\n"

    mensaje += f"\nTOTAL: ${total}\n"
    mensaje += f"\n👤 {datos.get('nombre')}\n📱 {datos.get('telefono')}"

    enviar_whatsapp(mensaje)

    session["carrito"] = []
    session.pop("datos", None)

    return redirect("/")

# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
