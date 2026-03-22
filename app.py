import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "12345"

# =========================
# 📁 ARCHIVOS
# =========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "productos.json")

# =========================
# 🔐 GREEN API
# =========================

GREEN_API_URL = os.getenv("GREEN_API_URL")
GREEN_API_INSTANCE = os.getenv("GREEN_API_INSTANCE")
GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")
GREEN_API_CHAT_ID = os.getenv("GREEN_API_CHAT_ID")

# =========================
# 👨‍💼 VENDEDORES
# =========================

VENDEDORES = [
    "Mercado en Línea Culiacán",
    "Silvia",
    "Hector",
    "Juan",
    "Cristian",
    "Amayrani",
    "Brisa",
    "Natalia",
    "Claudia"
]

# =========================
# 📦 PRODUCTOS
# =========================

def cargar_productos():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return []

# =========================
# 📂 CATEGORÍAS
# =========================

def obtener_categorias():
    productos = cargar_productos()
    categorias_dict = {}

    for p in productos:
        nombre_categoria = str(p.get("categoria", "")).strip()
        if nombre_categoria and nombre_categoria not in categorias_dict:
            categorias_dict[nombre_categoria] = {
                "nombre": nombre_categoria,
                "foto": p.get("foto", "")
            }

    return list(categorias_dict.values())

# =========================
# 🛒 CARRITO
# =========================

def obtener_carrito():
    if "carrito" not in session:
        session["carrito"] = []
    return session["carrito"]

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    producto = request.form.get("producto", "").strip()
    precio = float(request.form.get("precio", 0) or 0)
    foto = request.form.get("foto", "").strip()
    cantidad = int(request.form.get("cantidad", 1) or 1)

    carrito = obtener_carrito()

    for item in carrito:
        if item["producto"] == producto:
            item["cantidad"] += cantidad
            item["total"] = item["cantidad"] * item["precio"]
            break
    else:
        carrito.append({
            "producto": producto,
            "precio": precio,
            "foto": foto,
            "cantidad": cantidad,
            "total": precio * cantidad
        })

    session["carrito"] = carrito
    session.modified = True

    return redirect(request.referrer or url_for("index"))

@app.route("/carrito")
def carrito():
    carrito = obtener_carrito()
    subtotal = sum(item["total"] for item in carrito)
    return render_template("carrito.html", carrito=carrito, subtotal=subtotal)

@app.route("/vaciar_carrito")
def vaciar_carrito():
    session["carrito"] = []
    session.modified = True
    return redirect(url_for("carrito"))

# =========================
# 🏠 INICIO
# =========================

@app.route("/")
def index():
    categorias = obtener_categorias()
    return render_template("index.html", categorias=categorias)

# =========================
# 📂 CATEGORÍA
# =========================

@app.route("/categoria/<nombre>")
def categoria(nombre):
    productos = cargar_productos()
    filtrados = [p for p in productos if p.get("categoria") == nombre]
    return render_template(
        "categoria.html",
        productos=filtrados,
        nombre_categoria=nombre
    )

# =========================
# 🧾 CHECKOUT
# =========================

@app.route("/checkout")
def checkout():
    carrito = obtener_carrito()

    if not carrito:
        return redirect(url_for("carrito"))

    subtotal = sum(item["total"] for item in carrito)
    return render_template(
        "checkout.html",
        carrito=carrito,
        subtotal=subtotal,
        vendedores=VENDEDORES
    )

# =========================
# 📤 ENVIAR A GREEN API
# =========================

def enviar_green_api(mensaje):
    if not GREEN_API_URL:
        raise ValueError("Falta GREEN_API_URL")
    if not GREEN_API_INSTANCE:
        raise ValueError("Falta GREEN_API_INSTANCE")
    if not GREEN_API_TOKEN:
        raise ValueError("Falta GREEN_API_TOKEN")
    if not GREEN_API_CHAT_ID:
        raise ValueError("Falta GREEN_API_CHAT_ID")

    url = f"{GREEN_API_URL}/waInstance{GREEN_API_INSTANCE}/sendMessage/{GREEN_API_TOKEN}"

    payload = {
        "chatId": GREEN_API_CHAT_ID,
        "message": mensaje
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

# =========================
# 🚀 FINALIZAR PEDIDO
# =========================

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    nombre = request.form.get("nombre", "").strip()
    colonia = request.form.get("colonia", "").strip()
    calle = request.form.get("calle", "").strip()
    celular = request.form.get("celular", "").strip()
    nota = request.form.get("nota", "").strip()
    entrega = request.form.get("entrega", "").strip()
    vendedor = request.form.get("vendedor", "").strip()

    carrito = obtener_carrito()

    if not carrito:
        return redirect(url_for("carrito"))

    subtotal = sum(item["total"] for item in carrito)
    envio = 40 if entrega == "domicilio" else 0
    total = subtotal + envio
    status = "A domicilio" if entrega == "domicilio" else "Recoger en bodega"

    mensaje = f"""🛒 Mercado en Línea Culiacán
-----------------------
👤 Nombre: {nombre}
📞 Celular: {celular}
📍 Colonia: {colonia}
🏠 Calle: {calle}

🛍 Pedido:"""

    for item in carrito:
        mensaje += f"\n- {item['producto']} x{item['cantidad']} = ${item['total']}"

    mensaje += f"""

💰 Subtotal: ${subtotal}
🚚 Envío: ${envio}
🧾 Total: ${total}
📦 Status: {status}
👨‍💼 Vendedor: {vendedor if vendedor else 'Mercado en Línea Culiacán'}
📝 Nota: {nota if nota else '-'}"""

    try:
        enviar_green_api(mensaje)
    except Exception as e:
        return f"Error GREEN API: {e}", 500

    session["carrito"] = []
    session.modified = True

    return redirect(url_for("index"))

# =========================
# ▶ RUN
# =========================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
