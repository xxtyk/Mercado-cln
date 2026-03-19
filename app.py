from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Aquí definimos tus categorías con sus colores e iconos
    categorias = [
        {'nombre': 'Cuidado del cabello', 'color': '#ffffff', 'imagen': 'https://via.placeholder.com/150'},
        {'nombre': 'Cocina', 'color': '#FF6F00', 'icono': '🍳'},
        {'nombre': 'Mascotas', 'color': '#388E3C', 'icono': '🐾'},
        {'nombre': 'Música y sonido', 'color': '#1E88E5', 'icono': '🎵'},
        {'nombre': 'Belleza', 'color': '#D32F2F', 'icono': '💄'},
        {'nombre': 'Electrónica', 'color': '#455A64', 'icono': '⚡'}
    ]
    return render_template('index.html', categorias=categorias)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
