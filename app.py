import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "12345")

COSTO_ENVIO = 40

ADMIN_USER = os.environ.get("ADMIN_USER", "hector")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

VENDEDORES = [
    "Mercado en Línea Culiacán",
    "Hector",
    "Silvia",
    "Juan",
    "Cristian",
    "Amayrani",
    "Brisa",
    "Claudia",
    "Natalia"
]

# ========================
# CATEGORIAS FIJAS
# ========================
categorias = [
    {"id": 1, "nombre": "Minisplit", "foto": None},
    {"id": 2, "nombre": "Cuidado personal", "foto": None},
    {"id": 3, "nombre": "Mascotas", "foto": None},
    {"id": 4, "nombre": "Cuidado del cabello", "foto": None},
    {"id": 5, "nombre": "Cocina", "foto": None},
    {"id": 6, "nombre": "Limpieza", "foto": None},
    {"id": 7, "nombre": "Electrodoméstico", "foto": None},
    {"id": 8, "nombre": "Otro", "foto": None},
]

# ========================
# DATOS EN MEMORIA
# ========================
productos = []
pedidos = []


# ========================
# AYUDAS
# ========================
def resolver_imagen(valor):
    if valor:
        return valor
    return ""


def obtener_carrito():
    return session.get("carrito", [])


def guardar_carrito(carrito):
    session["carrito"] = carrito
    session.modified = True


def subtotal_carrito(carrito):
    return sum(float(item.get("precio", 0)) * int(item.get("cantidad", 1)) for item in carrito)


def total_items_carrito(carrito):
    return sum(int(item.get("cantidad", 1)) for item in carrito)


def admin_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logueado"):
            return redirect(url_for("login_admin"))
        return func(*args, **kwargs)
    return wrapper


@app.context_processor
def utilidades_templates():
    carrito = obtener_carrito()
    return dict(
        resolver_imagen=resolver_imagen,
        carrito_cantidad=total_items_carrito(carrito),
        costo_envio=COSTO_ENVIO,
        admin_logueado=session.get("admin_logueado", False)
    )


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
# LOGIN ADMIN
# ========================
@app.route("/login_admin", methods=["GET", "POST"])
def login_admin():
    error = ""

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "").strip()

        if usuario == ADMIN_USER and password == ADMIN_PASSWORD:
            session["admin_logueado"] = True
            return redirect(url_for("admin"))
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login_admin.html", error=error)


@app.route("/logout_admin")
def logout_admin():
    session.pop("admin_logueado", None)
    return redirect("/catalogo")


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
        if p.get("categoria_id") == id
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
    producto = next((p for p in productos if p["id"] == id), None)

    if not producto:
        return redirect("/catalogo")

    carrito = obtener_carrito()

    encontrado = False
    for item in carrito:
        if item["id"] == producto["id"]:
            item["cantidad"] = int(item.get("cantidad", 1)) + 1
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio": float(producto["precio"]),
            "cantidad": 1,
            "foto": producto.get("foto"),
            "categoria_id": producto.get("categoria_id")
        })

    guardar_carrito(carrito)

    regresar = request.referrer or "/catalogo"
    return redirect(regresar)


@app.route("/carrito")
def carrito():
    carrito = obtener_carrito()
    subtotal = subtotal_carrito(carrito)

    return render_template(
        "carrito.html",
        carrito=carrito,
        subtotal=subtotal
    )


@app.route("/carrito/actualizar/<int:producto_id>", methods=["POST"])
def actualizar_carrito(producto_id):
    accion = request.form.get("accion", "").strip()
    carrito = obtener_carrito()

    for item in carrito[:]:
        if item["id"] == producto_id:
            cantidad_actual = int(item.get("cantidad", 1))

            if accion == "sumar":
                item["cantidad"] = cantidad_actual + 1

            elif accion == "restar":
                nueva_cantidad = cantidad_actual - 1
                if nueva_cantidad <= 0:
                    carrito.remove(item)
                else:
                    item["cantidad"] = nueva_cantidad

            elif accion == "eliminar":
                carrito.remove(item)

            break

    guardar_carrito(carrito)
    return redirect("/carrito")


@app.route("/vaciar_carrito", methods=["POST"])
def vaciar_carrito():
    guardar_carrito([])
    return redirect("/carrito")


# ========================
# DATOS DE ENTREGA
# ========================
@app.route("/datos_entrega")
def datos_entrega():
    carrito = obtener_carrito()

    if not carrito:
        return redirect("/carrito")

    subtotal = subtotal_carrito(carrito)

    return render_template(
        "datos_entrega.html",
        carrito=carrito,
        subtotal=subtotal,
        costo_envio=COSTO_ENVIO,
        vendedores=VENDEDORES
    )


# ========================
# FINALIZAR PEDIDO
# ========================
@app.route("/finalizar_pedido", methods=["POST"])
def finalizar_pedido():
    carrito = obtener_carrito()

    if not carrito:
        return redirect("/carrito")

    nombre = request.form.get("nombre", "").strip()
    telefono = request.form.get("telefono", "").strip()
    direccion = request.form.get("direccion", "").strip()
    colonia = request.form.get("colonia", "").strip()
    nota = request.form.get("nota", "").strip()
    vendedor = request.form.get("vendedor", "Mercado en Línea Culiacán").strip()
    tipo_entrega = request.form.get("tipo_entrega", "domicilio").strip()

    subtotal = subtotal_carrito(carrito)
    envio = COSTO_ENVIO if tipo_entrega == "domicilio" else 0
    total = subtotal + envio

    pedido = {
        "id": str(uuid.uuid4()),
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "colonia": colonia,
        "nota": nota,
        "vendedor": vendedor,
        "tipo_entrega": tipo_entrega,
        "subtotal": subtotal,
        "envio": envio,
        "total": total,
        "productos": [dict(item) for item in carrito]
    }

    pedidos.insert(0, pedido)
    guardar_carrito([])

    return render_template("pedido_recibido.html", pedido=pedido)


# ========================
# PANEL ADMIN
# ========================
@app.route("/admin")
@admin_requerido
def admin():
    return render_template(
        "admin.html",
        pedidos=pedidos,
        productos=productos,
        categorias=categorias
    )


@app.route("/eliminar_pedido/<id>")
@admin_requerido
def eliminar_pedido(id):
    global pedidos
    pedidos = [p for p in pedidos if p["id"] != id]
    return redirect("/admin")


# ========================
# CATEGORIAS BLOQUEADAS
# ========================
@app.route("/agregar_categoria", methods=["POST"])
@admin_requerido
def agregar_categoria():
    return redirect("/admin")


# ========================
# AGREGAR PRODUCTO
# ========================
@app.route("/agregar_producto", methods=["POST"])
@admin_requerido
def agregar_producto():
    nombre = request.form.get("nombre", "").strip()
    precio = request.form.get("precio", "").strip()
    categoria_id = request.form.get("categoria_id", "").strip()
    foto = request.form.get("foto", "").strip()

    if nombre and precio:
        categoria_id_valor = 8

        if categoria_id.isdigit():
            categoria_id_valor = int(categoria_id)

        nuevo_id = max([p["id"] for p in productos], default=0) + 1

        productos.append({
            "id": nuevo_id,
            "nombre": nombre,
            "precio": float(precio),
            "categoria_id": categoria_id_valor,
            "foto": foto if foto else None
        })

    return redirect("/admin")


# ========================
# ARRANQUE CORRECTO PARA RENDER
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
