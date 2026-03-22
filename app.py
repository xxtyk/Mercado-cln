import os
import json
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"

# ==============================
# CONFIGURACIÓN DE CARPETAS (Mantenemos tu lógica)
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

# ==============================
# RUTAS
# ==============================

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/editar_categoria', methods=['GET', 'POST'])
def editar_categoria():
    if request.method == 'POST':
        nombre_categoria = request.form.get('categoria') # Verifica que en el HTML el name sea 'categoria'
        
        if nombre_categoria:
            try:
                if os.path.exists(DB_FILE):
                    with open(DB_FILE, "r") as f:
                        datos = json.load(f)
                else:
                    datos = {"categorias": []}
            except Exception:
                datos = {"categorias": []}

            if "categorias" not in datos:
                datos["categorias"] = []

            # Solo agregar si no existe ya
            if nombre_categoria not in datos["categorias"]:
                datos["categorias"].append(nombre_categoria)
                with open(DB_FILE, "w") as f:
                    json.dump(datos, f, indent=4)
                flash(f"Categoría '{nombre_categoria}' guardada.", "success")
            else:
                flash("La categoría ya existe.", "warning")

        return redirect(url_for('admin'))
    
    return render_template("categoria.html")

# ==============================
# SERVIDOR
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
