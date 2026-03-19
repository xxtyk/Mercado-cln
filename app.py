from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Datos de prueba directos para evitar errores
    categorias = [
        {'nombre': 'Cuidado del cabello', 'color': '#ffffff', 'icono': '🧴'},
        {'nombre': 'Cocina', 'color': '#FF6F00', 'icono': '🍳'},
        {'nombre': 'Mascotas', 'color': '#388E3C', 'icono': '🐾'},
        {'nombre': 'Música y sonido', 'color': '#1E88E5', 'icono': '🎵'}
    ]
    return render_template('index.html', categorias=categorias)

if __name__ == "__main__":
    # Esto es lo que Render necesita para no morir
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
