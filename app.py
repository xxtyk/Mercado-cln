import os
import json
from flask import Flask, render_template

app = Flask(__name__)

# ==============================
# 📁 Archivos JSON
# ==============================
PRODUCTOS_FILE = "productos.json"
CATEGORIAS_FILE = "categorias.json"
CONFIG_FILE = "config.json"

# Crear archivos si no existen
for file in [PRODUCTOS_FILE, CATEGORIAS_FILE, CONFIG_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            if file == CONFIG_FILE:
                json.dump({"logo": ""}, f)
            else:
                json.dump([], f)

# ==============================
# 📦 Cargar datos con seguridad
# ==============================
def cargar_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except:
        return [] if file_path != CONFIG_FILE else {"logo": ""}

# ==============================
# 🏠 Ruta principal
# ==============================
@app.route('/')
def inicio():
    productos = cargar_json(PRODUCTOS_FILE)
    categorias = cargar_json(CATEGORIAS_FILE)
    config = cargar_json(CONFIG_FILE)
    return render_template("index.html", productos=productos, categorias=categorias, config=config)

# ==============================
# 🚀 Servidor
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
