import os
import json
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "12345"

# =========================
# 📁 ARCHIVOS
# =========================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "productos.json")

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
# 📦 CARGAR PRODUCTOS
# =========================

def cargar_productos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# =========================
# 🛒 CARRITO
# =========================

def obtener_carrito():
    if "carrito" not in session:
        session["carrito"] = []
    return session["carrito"]

@app.route("/agregar_carrito", methods=["POST"])
def agregar_carrito():
    producto = request.form.get("producto")
    precio = float(request.form.get("precio"))
    foto = request.form.get("foto")
    cantidad = int(request.form.get("cantidad"))

    carrito = obtener_carrito()

    encontrado = False
    for item in carrito:
        if item["producto"] == producto:
            item["cantidad"] += cantidad
            item["total"] = item["cantidad"] * item["precio"]
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "producto": producto,
            "precio": precio,
            "foto": foto,
            "cantidad": cantidad,
            "total": precio * cantidad
        })

    session["carrito"] = carrito
    session.modified = True

    return redirect(request.referrer)

@app.route("/carrito")
def carrito():
    carrito = obtener_carrito()
    subtotal = sum(item["total"] for item in carrito)
    return render_template("carrito.html", carrito=carrito, subtotal=subtotal)

@app.route("/vaciar_carrito")
def vaciar_carrito():
    session["carrito"] = []
    return redirect(url_for("carrito"))

# =========================
# 🏠 INICIO
# =========================

@app.route("/")
def index():
    productos = cargar_productos()
    return render_template("index.html", productos=productos)

# =========================
# 📂 CATEGORÍA
# =========================

@app.route("/categoria/<nombre>")
def categoria(nombre):
    productos = cargar_productos()
    filtrados = [p for p in productos if p.get("categoria") == nombre]
    return render_template("categoria.html", productos=filtrados, nombre_categoria=nombre)

# =========================
# 🚀 FINALIZAR PEDIDO
# =========================

@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    nombre = request.form.get("nombre")
    colonia = request.form.get("colonia")
    calle = request.form.get("calle")
    celular = request.form.get("celular")
    nota = request.form.get("nota")
    entrega = request.form.get("entrega")
    vendedor = request.form.get("vendedor")

    carrito = obtener_carrito()

    subtotal = sum(item["total"] for item in carrito)
    envio = 40 if entrega == "domicilio" else 0
    total = subtotal + envio

    mensaje = "🛒 *Mercado en Línea Culiacán*\n"
    mensaje += "-----------------------\n"
    mensaje += f"👤 Nombre: {nombre}\n"
    mensaje += f"📞 Celular: {celular}\n"
    mensaje += f"📍 Colonia: {colonia}\n"
    mensaje += f"🏠 Calle: {calle}\n\n"

    mensaje += "🛍 Pedido:\n"
    for item in carrito:
        mensaje += f"- {item['producto']} x{item['cantidad']} = ${item['total']}\n"

    mensaje += f"\n💰 Subtotal: ${subtotal}\n"
    mensaje += f"🚚 Envío: ${envio}\n"
    mensaje += f"🧾 Total: ${total}\n\n"

    if entrega == "domicilio":
        mensaje += "📦 Status: A domicilio\n"
    else:
        mensaje += "📦 Status: Recoger en bodega\n"

    mensaje += f"👨‍💼 Vendedor: {vendedor}\n"
    mensaje += f"📝 Nota: {nota}"

    mensaje = quote(mensaje)

    numero = "526679771409"
    link = f"https://wa.me/{numero}?text={mensaje}"

    session["carrito"] = []

    return redirect(link)

# =========================
# ▶ RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
