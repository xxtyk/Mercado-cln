import os
import json
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

DB_FILE = "productos.json"

def cargar_productos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

@app.route('/')
def index():
    productos = cargar_productos()
    activos = [p for p in productos if p.get('activo', True)]
    return render_template('index.html', productos=activos)

@app.route('/pedido', methods=['POST'])
def pedido():
    nombre = request.form.get('nombre', 'Cliente')
    colonia = request.form.get('colonia', 'N/A')
    direccion = request.form.get('direccion', 'N/A')
    total = request.form.get('total', '0')
    envio = request.form.get('envio', '40')
    
    mensaje = f"NUEVO PEDIDO:\n\nCliente: {nombre}\nColonia: {colonia}\nDirección: {direccion}\nTotal: ${total}\nEnvío: ${envio}"
    link_whatsapp = f"https://wa.me/526671377298?text={mensaje}"
    return redirect(link_whatsapp)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
