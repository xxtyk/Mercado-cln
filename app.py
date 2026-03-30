import os
import uuid
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

# ========================
# DATOS EN MEMORIA
# ========================
productos = []
categorias = []
pedidos = []

# ========================
# AYUDAS
# ========================
def resolver_imagen(valor):
    if valor:
        return valor
    return ""

@app.context_processor
def utilidades_templates():
    return dict(resolver_imagen=resolver_imagen)

# ========================
# INICIO
# ========================
@app.route("/")
def inicio():
    return redirect("/catalogo")

@app.route("/catalogo")
def catalogo():
    return render_template(
        "index.html",
        categorias=categorias,
        productos=productos
    )

# ========================
# VER CATEGORIA
# ========================
@app.route("/categoria/<int:id>")
def categoria(id):
    categoria_encontrada = next((c for c in categorias if c["id"] == id), None)

    if not categoria_encontrada:
        return redirect("/catalogo")

    productos_categoria = [
        p for p in productos
        if p.get("categoria_id") == id or p.get("categoria_id") is None
    ]

    return render_template(
        "categoria.html",
        categoria=categoria_encontrada,
        productos=productos_categoria
    )

# ========================
# CARRITO
# ========================
@app.route("/agregar_al_carrito/<int:id>", methods=["POST"])
def agregar_al_carrito(id):
    carrito = session.get("carrito", [])

    producto = next((p for p in productos if p["id"] == id), None)

    if producto:
        carrito.append(producto)

    session["carrito"] = carrito
    return redirect("/catalogo")

@app.route("/carrito")
def carrito():
    carrito = session.get("carrito", [])
    subtotal = sum(float(p.get("precio", 0)) for p in carrito)

    return render_template(
        "carrito.html",
        carrito=carrito,
        subtotal=subtotal
    )

# ========================
# FINALIZAR PEDIDO
# ========================
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito = session.get("carrito", [])

    if not carrito:
        return redirect("/carrito")

    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()

    pedido = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "productos": carrito
    }

    pedidos.append(pedido)
    session["carrito"] = []

    return render_template("pedido_recibido.html")

# ========================
# PANEL ADMIN
# ========================
@app.route("/admin")
def admin():
    return render_template(
        "admin.html",
        pedidos=pedidos,
        productos=productos,
        categorias=categorias
    )

# ========================
# ELIMINAR PEDIDO
# ========================
@app.route("/eliminar_pedido/<id>")
def eliminar_pedido(id):
    global pedidos
    pedidos = [p for p in pedidos if p["id"] != id]
    return redirect("/admin")

# ========================
# AGREGAR CATEGORIA
# ========================
@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre", "").strip()

    if nombre:
        categorias.append({
            "id": len(categorias) + 1,
            "nombre": nombre,
            "foto": None
        })

    return redirect("/admin")

# ========================
# AGREGAR PRODUCTO
# ========================
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()

    if nombre and precio:
        categoria_id_valor = None

        if categoria_id.isdigit():
            categoria_id_valor = int(categoria_id)
        elif categorias:
            categoria_id_valor = categorias[0]["id"]

        productos.append({
            "id": len(productos) + 1,
            "nombre": nombre,
            "precio": float(precio),
            "categoria_id": categoria_id_valor,
            "foto": None
        })

    return redirect("/admin")

# ========================
# ARRANQUE CORRECTO PARA RENDER
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
