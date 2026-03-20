from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def index():
    categorias = [
        {"nombre": "Abarrotes", "emoji": "🛒", "color": "#27ae60"},
        {"nombre": "Limpieza", "emoji": "🧼", "color": "#3498db"},
        {"nombre": "Frutas", "emoji": "🍎", "color": "#e67e22"},
        {"nombre": "Mascotas", "emoji": "🐶", "color": "#d35400"}
    ]
    return render_template('index.html', categorias=categorias)

@app.route('/admin')
def admin():
    # Esta línea es la que hace que funcione el archivo admin.html que creamos
    return render_template('admin.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
