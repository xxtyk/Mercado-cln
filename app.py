import os
from flask import Flask, render_template

app = Flask(__name__)

# Aquí es donde van tus categorías de Culiacán
@app.route('/')
def inicio():
    categorias = [
        "Cuidado del cabello", 
        "Cocina", 
        "Mascotas", 
        "Música y sonido", 
        "Cuidado personal", 
        "Electrodomésticos"
    ]
    return render_template('index.html', categorias=categorias)

if __name__ == "__main__":
    # Este es el ajuste para que Render no falle
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
