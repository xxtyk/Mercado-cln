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

                # 🔥 CREA CATEGORÍAS SI NO EXISTEN
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
        print("❌ WhatsApp:", str(e))

# ------------------------
# CONSULTAS
# ------------------------
def listar_categorias():
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM categorias ORDER BY id")
                return cur.fetchall()
    except:
        return []

def listar_productos(cat_id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM productos WHERE categoria_id=%s", (cat_id,))
                return cur.fetchall()
    except:
        return []

def obtener_producto(id):
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM productos WHERE id=%s", (id,))
                return cur.fetchone()
    except:
        return None

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
def construir_mensaje():
    carrito = obtener_carrito()
    datos = session.get("datos_entrega", {})

    texto = "🛒 *NUEVO PEDIDO*\n\n"
    total = 0

    for item in carrito:
        sub = float(item["precio"]) * int(item["cantidad"])
        total += sub
        texto += f"• {item['nombre']} x{item['cantidad']} = ${sub:.2f}\n"

    texto += f"\n💰 Total: ${total:.2f}\n\n"
    texto += f"👤 {datos.get('nombre','')}\n"
    texto += f"📱 {datos.get('telefono','')}\n"
    texto += f"📍 {datos.get('direccion','')}"

    return texto

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

@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar(id):
    producto = obtener_producto(id)
    if not producto:
        return redirect("/")

    carrito = obtener_carrito()
    cantidad = int(request.form.get("cantidad", 1))

    carrito.append({
        "id": producto["id"],
        "nombre": producto["nombre"],
        "precio": float(producto["precio"]),
        "cantidad": cantidad
    })

    guardar_carrito(carrito)
    return redirect(request.referrer or "/")

@app.route("/datos_entrega", methods=["GET","POST"])
def datos():
    if request.method == "POST":
        session["datos_entrega"] = request.form
        return redirect("/finalizar_pedido")
    return render_template("datos_entrega.html")

@app.route("/finalizar_pedido", methods=["GET","POST"])
def finalizar():
    carrito = obtener_carrito()
    if not carrito:
        return redirect("/")

    texto = construir_mensaje()
    enviar_whatsapp(texto)

    session.pop("carrito", None)
    session.pop("datos_entrega", None)

    return redirect("/")

# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
