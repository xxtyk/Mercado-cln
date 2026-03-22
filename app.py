import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"

# Carpeta para subir fotos dentro de 'static'
UPLOAD_FOLDER = os.path.join("static", "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DB_FILE = "productos.json"

# NO BORRES tu inicializar_entorno()
def inicializar_entorno():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

# -------------------------------------------------
# RUTA PRINCIPAL / TIENDA
# -------------------------------------------------
@app.route('/')
def inicio():
    return "<h1>Bienvenido a la Tienda</h1><p>Vista de clientes</p>"

# -------------------------------------------------
# RUTA ADMIN (ejemplo)
# -------------------------------------------------
@app.route('/admin')
def admin():
    return render_template("admin.html")

# -------------------------------------------------
# EDITAR / AGREGAR CATEGORÍA CON FOTO
# -------------------------------------------------
@app.route('/editar_categoria', methods=['GET', 'POST'])
def editar_categoria():
    if request.method == 'POST':
        nombre_categoria = request.form.get('nombre_categoria')
        foto = request.files.get('foto_categoria')

        if not nombre_categoria:
            flash("Debes escribir un nombre de categoría.", "error")
            return redirect(url_for('editar_categoria'))

        nombre_archivo = ""
        if foto:
            nombre_archivo = foto.filename
            ruta_guardado = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            foto.save(ruta_guardado)

        # Cargar JSON existente
        try:
            with open(DB_FILE, "r") as f:
                datos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            datos = {"categorias": {}}

        if "categorias" not in datos:
            datos["categorias"] = {}

        # Guardar la categoría + foto
        datos["categorias"][nombre_categoria] = nombre_archivo

        with open(DB_FILE, "w") as f:
            json.dump(datos, f, indent=4)

        flash(f"Categoría '{nombre_categoria}' guardada correctamente.", "success")
        return redirect(url_for('admin'))

    return render_template("categoria.html")

# -------------------------------------------------
# INICIALIZACIÓN
# -------------------------------------------------
if __name__ == "__main__":
    inicializar_entorno()
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
