from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Estas son las categorías que se verán en tu link de Render
    categorias = [
        {'nombre': 'Cuidado del cabello', 'color': '#ffffff', 'icono': '🧴'},
        {'nombre': 'Cocina', 'color': '#FF6F00', 'icono': '🍳'},
        {'nombre': 'Mascotas', 'color': '#388E3C', 'icono': '🐾'},
        {'nombre': 'Música y sonido', 'color': '#1E88E5', 'icono': '🎵'}
    ]
    return render_template('index.html', categorias=categorias)

if __name__ == "__main__":
    # Render necesita esto para asignar el puerto automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
