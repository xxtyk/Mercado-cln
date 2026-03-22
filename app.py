import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "12345"  # Necesario para flash

# ==============================
# Crear carpetas automáticamente
# ==============================
# Carpeta estática
if not os.path.exists("static"):
    os.makedirs("static")

# Carpeta uploads dentro de static
UPLOAD_FOLDER = os.path.join("static", "uploads")
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
