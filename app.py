from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os

app = Flask(__name__)
app.secret_key = "12345"

# --- RUTA PRINCIPAL ---
@app.route("/")
def index():
    # Cambia "index.html" por tu página principal si ya la tienes
    return render_template("index.html")

# --- PANEL DE CONFIGURACIÓN ---
@app.route("/configuracion")
def configuracion():
    return render_template("configuracion.html")

@app.route("/guardar_configuracion", methods=["POST"])
def guardar_configuracion():
    usuario = request.form.get("usuario")
    notificaciones = request.form.get("notificaciones") == "on"

    # Guardar configuración en JSON
    config_file = "config.json"
    config_data = {
        "usuario": usuario,
        "notificaciones": notificaciones
    }
    with open(config_file, "w") as f:
        json.dump(config_data, f)

    flash("Configuración guardada correctamente")
    return redirect(url_for("configuracion"))

# --- EJECUTAR APP ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
