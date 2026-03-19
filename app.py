import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def cliente():
    return "<h1>Tienda Mercado en Línea Culiacán</h1><p>Vista para clientes.</p>"

@app.route('/config')
def admin():
    return "<h1>Panel de Configuración</h1><p>Aquí gestionas tus productos.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
