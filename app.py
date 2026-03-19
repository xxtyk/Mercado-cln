from flask import Flask, render_template
# Asegúrate de importar tus modelos si los usas, por ejemplo:
# from models import Categorias 

app = Flask(__name__)

@app.route('/')
def index():
    # Aquí corregimos los 4 espacios exactos para que Render no falle
    # Si no tienes base de datos aún, puedes comentar la línea de abajo con un #
    # categorias = Categorias.query.all() 
    
    # Lista de categorías de prueba para que la app cargue hoy mismo:
    categorias = [
        {'nombre': 'Cuidado del cabello', 'color': 'white'},
        {'nombre': 'Cocina', 'color': 'orange'},
        {'nombre': 'Mascotas', 'color': 'green'},
        {'nombre': 'Música y sonido', 'color': 'blue'}
    ]
    
    return render_template('index.html', categorias=categorias)

if __name__ == "__main__":
    import os
    # Esto es vital para que Render asigne el puerto correctamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
