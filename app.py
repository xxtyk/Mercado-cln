import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"  # Necesario para flash

# Carpeta para guardar archivos subidos
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            return
