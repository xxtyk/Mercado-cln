from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Estas son las tarjetas que aparecerán en tu página
    categorias = [
        {'nombre': 'Cuidado del cabello', 'color': '#ffffff', 'icono': '🧴'},
        {'nombre': 'Cocina', 'color': '#FF6F00', 'icono': '🍳'},
        {'nombre': 'Mascotas', 'color': '#388E3C', 'icono': '🐾'},
        {'nombre': 'Música y sonido', 'color': '#1E88E5', 'icono': '🎵'}
    ]
    # Si la carpeta templates/index.html no existe, aquí dará el error 500
    return render_template('index.html', categorias=categorias)

if __name__ == "__main__":
    # Esto es OBLIGATORIO para que Render funcione
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
