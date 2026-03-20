from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    # Esta es la lista que necesita tu HTML para dibujar los botones
    categorias = [
        {"nombre": "Abarrotes", "emoji": "🛒", "color": "#27ae60"},
        {"nombre": "Limpieza", "emoji": "🧼", "color": "#2980b9"},
        {"nombre": "Frutas", "emoji": "🍎", "color": "#e67e22"},
        {"nombre": "Mascotas", "emoji": "🐶", "color": "#d35400"}
    ]
    return render_template('index.html', categorias=categorias)

if __name__ == '__main__':
    # Render usa el puerto que le asigne el sistema
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
