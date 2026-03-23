import os
import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "productos.json")

# ---------- FUNCIONES ----------
def cargar_productos():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_productos(productos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, ensure_ascii=False, indent=4)

# ---------- RUTAS ----------

@app.route('/')
def index():
    productos = cargar_productos()
    return render_template('index.html', productos=productos)

@app.route('/admin')
def admin():
    productos = cargar_productos()
    return render_template('admin.html', productos=productos)

@app.route('/vendedor/<vendedor_id>')
def vendedor(vendedor_id):
    productos = cargar_productos()
    return render_template('vendedor.html', vendedor_id=vendedor_id, productos=productos)

# 🔥 ESTA ES LA QUE TE FALTABA
@app.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    productos = cargar_productos()

    nombre = request.form.get('nombre')
    precio = request.form.get('precio')
    categoria = request.form.get('categoria')
    foto = request.form.get('foto')

    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "categoria": categoria,
        "foto": foto
    }

    productos.append(nuevo)
    guardar_productos(productos)

    return redirect(url_for('admin'))

# ---------- RUN ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
