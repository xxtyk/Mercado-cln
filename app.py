import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"  # Necesario para flash

# ==============================
# CONFIGURACIÓN DE CARPETAS SEGURA
# ==============================
import shutil

def inicializar_entorno():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    static_dir = os.path.join(base_dir, 'static')
    uploads_dir = os.path.join(static_dir, 'uploads')

    # 1. Si 'static' existe pero NO es carpeta, lo borramos
    if os.path.exists(static_dir) and not os.path.isdir(static_dir):
        os.remove(static_dir)

    # 2. Si 'static' no existe, lo creamos
    os.makedirs(static_dir, exist_ok=True)

    # 3. Si 'uploads' existe pero es un archivo, lo borramos
    if os.path.exists(uploads_dir) and not os.path.isdir(uploads_dir):
        print(f"Borrando archivo estorbando: {uploads_dir}")
        os.remove(uploads_dir)

    # 4. Crear carpeta uploads
    os.makedirs(uploads_dir, exist_ok=True)
    return uploads_dir

# Guardamos la ruta en la configuración de Flask
app.config['UPLOAD_FOLDER'] = inicializar_entorno()

# ==============================
# RUTAS
# ==============================
@app.route('/', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        # ===== Subir logotipo =====
        if 'logotipo' in request.files:
            archivo = request.files['logotipo']
            if archivo.filename != '':
                ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
                archivo.save(ruta_archivo)
                flash("Logotipo subido correctamente.")
            return redirect(url_for('inicio'))

        # ===== Agregar categoría =====
        elif 'categoria' in request.form:
            categoria = request.form.get('categoria')
            if categoria:
                # Aquí puedes guardar la categoría en JSON o base de datos
                flash(f"Categoría '{categoria}' agregada correctamente.")
            return redirect(url_for('inicio'))

    # GET: solo renderiza la página
    return render_template("index.html")


@app.route('/admin')
def admin():
    return render_template("admin.html")


# ==============================
# SERVIDOR
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
