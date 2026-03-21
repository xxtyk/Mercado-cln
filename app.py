from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "12345"

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config(
    cloud_name="dosyi726x",
    api_key="942229587198227",
    api_secret="jHn-OlPaUEdfqvCk1DvgTeSUhyQ",
    secure=True
)

# Archivos JSON
PRODUCTOS_FILE = "productos.json"
CATEGORIAS_FILE = "categorias.json"
CONFIG_FILE = "config.json"
PEDIDOS_FILE = "pedidos.json"

# --- FUNCIONES AUXILIARES ---
def cargar_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({} if "json" in file_path else [], f)
    with open(file_path, "r") as f:
        return json.load(f)

def guardar_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# --- RUTA PRINCIPAL ---
@app.route("/")
def index():
    productos = cargar_json(PRODUCTOS_FILE)
    config = cargar_json(CONFIG_FILE)
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("index.html", productos=productos, categorias=categorias, config=config)

# --- PANEL DE CONFIGURACIÓN ---
@app.route("/configuracion")
def configuracion():
    config = cargar_json(CONFIG_FILE)
    productos = cargar_json(PRODUCTOS_FILE)
    categorias = cargar_json(CATEGORIAS_FILE)
    return render_template("configuracion.html", config=config, productos=productos, categorias=categorias)

@app.route("/guardar_configuracion", methods=["POST"])
def guardar_configuracion():
    usuario = request.form.get("usuario", "")
    notificaciones = request.form.get("notificaciones") == "on"
    logo_file = request.files.get("logo")

    config_data = {
        "usuario": usuario,
        "notificaciones": notificaciones
    }

    if logo_file and logo_file.filename != "":
        upload_result = cloudinary.uploader.upload(logo_file)
        config_data["logo"] = upload_result.get("secure_url")
    else:
        config_actual = cargar_json(CONFIG_FILE)
        if config_actual.get("logo"):
            config_data["logo"] = config_actual["logo"]

    guardar_json(CONFIG_FILE, config_data)
    flash("Configuración guardada correctamente")
    return redirect(url_for("configuracion"))

# --- AGREGAR CATEGORÍA ---
@app.route("/agregar_categoria", methods=["POST"])
def agregar_categoria():
    nombre = request.form.get("nombre_categoria")
    if not nombre:
        flash("Debes ingresar un nombre para la categoría")
        return redirect(url_for("configuracion"))
    categorias = cargar_json(CATEGORIAS_FILE)
    categoria_id = str(len(categorias) + 1)
    categorias[categoria_id] = nombre
    guardar_json(CATEGORIAS_FILE, categorias)
    flash(f"Categoría {nombre} agregada")
    return redirect(url_for("configuracion"))

# --- AGREGAR PRODUCTO ---
@app.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    categoria = request.form.get("categoria")
    imagen = request.files.get("imagen")

    if not nombre or not precio or not imagen or not categoria:
        flash("Debes ingresar nombre, precio, categoría y una imagen")
        return redirect(url_for("configuracion"))

    upload_result = cloudinary.uploader.upload(imagen)
    url_imagen = upload_result.get("secure_url")

    productos = cargar_json(PRODUCTOS_FILE)
    producto_id = str(len(productos) + 1)
    productos[producto_id] = {
        "nombre": nombre,
        "precio": float(precio),
        "categoria": categoria,
        "imagen": url_imagen,
        "disponible": True
    }
    guardar_json(PRODUCTOS_FILE, productos)
    flash(f"Producto {nombre} agregado")
    return redirect(url_for("configuracion"))

# --- CAMBIAR DISPONIBILIDAD PRODUCTO ---
@app.route("/toggle_producto/<producto_id>")
def toggle_producto(producto_id):
    productos = cargar_json(PRODUCTOS_FILE)
    if producto_id in productos:
        productos[producto_id]["disponible"] = not productos[producto_id]["disponible"]
        guardar_json(PRODUCTOS_FILE, productos)
        flash("Disponibilidad cambiada")
    return redirect(url_for("configuracion"))

# --- PEDIDO DEL CLIENTE ---
@app.route("/pedido/<producto_id>", methods=["GET", "POST"])
def pedido(producto_id):
    productos = cargar_json(PRODUCTOS_FILE)
    config = cargar_json(CONFIG_FILE)
    if producto_id not in productos or not productos[producto_id]["disponible"]:
        flash("Producto no disponible")
        return redirect(url_for("index"))

    producto = productos[producto_id]

    if request.method == "POST":
        nombre = request.form.get("nombre")
        whatsapp = request.form.get("whatsapp")
        colonia = request.form.get("colonia")
        calle_numero = request.form.get("calle_numero")
        entrega = request.form.get("entrega")
        nota = request.form.get("nota")
        costo = producto["precio"] + (40 if entrega == "Domicilio" else 0)

        pedido_data = {
            "nombre": nombre,
            "whatsapp": whatsapp,
            "colonia": colonia,
            "calle_numero": calle_numero,
            "producto": producto["nombre"],
            "entrega": entrega,
            "nota": nota,
            "costo_total": costo
        }

        pedidos = cargar_json(PEDIDOS_FILE)
        if type(pedidos) != list:
            pedidos = []
        pedidos.append(pedido_data)
        guardar_json(PEDIDOS_FILE, pedidos)
        flash(f"Pedido realizado, total: ${costo}")
        return redirect(url_for("index"))

    return render_template("pedido.html", producto=producto, config=config)
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
