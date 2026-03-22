import os
import json
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"

# ==============================
# CONFIGURACIÓN DE CARPETAS
# ==============================
def inicializar_entorno():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, 'static')
    uploads_dir = os.path.join(static_dir, 'uploads')

    if os.path.exists(static_dir) and not os.path.isdir(static_dir):
        os.remove(static_dir)
    os.makedirs(static_dir, exist_ok=True)

    if os.path.exists(uploads_dir) and not os.path.isdir(uploads_dir):
        os.remove(uploads_dir)
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir

app.config['UPLOAD_FOLDER'] = inicializar_entorno()
DB_FILE = "productos.json"

# Función auxiliar para leer el JSON sin errores
def cargar_datos():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"categorias": [], "productos": []}
    return {"categorias": [], "productos": []}

# ==============================
# RUTAS
# ==============================

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/admin')
def admin():
    datos = cargar_datos()
    categorias = datos.get("categorias", [])
    return render_template("admin.html", categorias=categorias)

@app.route('/editar_categoria', methods=['GET', 'POST'])
def editar_categoria():
    if request.method == 'POST':
        # .strip() quita espacios y .capitalize() pone la primera en Mayúscula
        nombre_categoria = request.form.get('categoria', '').strip().capitalize()
        
        if nombre_categoria:
            datos = cargar_datos()
            if "categorias" not in datos:
                datos["categorias"] = []

            if nombre_categoria not in datos["categorias"]:
                datos["categorias"].append(nombre_categoria)
                with open(DB_FILE, "w") as f:
                    json.dump(datos, f, indent=4)
                flash(f"Categoría '{nombre_categoria}' guardada.", "success")
            else:
                flash(f"La categoría '{nombre_categoria}' ya existe.", "warning")

        return redirect(url_for('admin'))
    
    return render_template("categoria.html")

# NUEVA RUTA PARA BORRAR CATEGORÍAS
@app.route('/eliminar_categoria/<nombre>')
def eliminar_categoria(nombre):
    datos = cargar_datos()
    if "categorias" in datos and nombre in datos["categorias"]:
        datos["categorias"].remove(nombre)
        with open(DB_FILE, "w") as f:
            json.dump(datos, f, indent=4)
        flash(f"Categoría '{nombre}' eliminada.", "danger")
    return redirect(url_for('admin'))

# RUTA PARA EL FORMULARIO DE PRODUCTOS (Corrigiendo el menú vacío)
@app.route('/producto')
def producto():
    datos = cargar_datos()
    categorias = datos.get("categorias", [])
    return render_template("producto.html", categorias=categorias)

# ==============================
# SERVIDOR
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
