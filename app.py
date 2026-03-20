import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')

# Configuración de subida
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- VISTA DEL CLIENTE ---
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mercado en Línea Culiacán</title>
        <style>
            body { font-family: sans-serif; margin: 0; background: #f4f4f4; padding-bottom: 80px; }
            .header { background: #000; color: #fff; padding: 20px; text-align: center; font-weight: bold; font-size: 22px; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 15px; }
            .card { background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; border-bottom: 6px solid; }
            .card img { width: 100%; height: 150px; object-fit: cover; background: #eee; }
            .card h4 { margin: 10px 0; font-size: 14px; color: #333; }
            .c-cabello { border-color: #e91e63; }
            .c-cocina { border-color: #ff9800; }
            .c-mascotas { border-color: #4caf50; }
            .c-electro { border-color: #2196f3; }
            .btn-ws { position: fixed; bottom: 20px; right: 20px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="header">MERCADO EN LÍNEA CULIACÁN</div>
        <div class="grid">
            <div class="card c-cabello">
                <img src="/static/img/cabello.jpg" onerror="this.src='https://via.placeholder.com/150?text=Subir+Foto'">
                <h4>Cuidado del cabello</h4>
            </div>
            <div class="card c-cocina">
                <img src="/static/img/cocina.jpg" onerror="this.src='https://via.placeholder.com/150?text=Subir+Foto'">
                <h4>Cocina</h4>
            </div>
            <div class="card c-mascotas">
                <img src="/static/img/mascotas.jpg" onerror="this.src='https://via.placeholder.com/150?text=Subir+Foto'">
                <h4>Mascotas</h4>
            </div>
            <div class="card c-electro">
                <img src="/static/img/electro.jpg" onerror="this.src='https://via.placeholder.com/150?text=Subir+Foto'">
                <h4>Electrodomésticos</h4>
            </div>
        </div>
        <a href="https://wa.me/526671234567" class="btn-ws" target="_blank">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35">
        </a>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL ---
@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        file = request.files.get('foto')
        filename_manual = request.form.get('nombre_archivo')
        if file and filename_manual:
            filename = secure_filename(filename_manual)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return f"<h1>¡Foto {filename} subida!</h1><br><a href='/config'>Volver</a>"

    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel Control</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #eee; }
            .box { background: #fff; padding: 20px; border-radius: 10px; }
            select, input, button { width: 100%; padding: 15px; margin: 10px 0; font-size: 16px; }
            button { background: #000; color: #fff; border: none; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Subir Foto</h2>
            <form method="post" enctype="multipart/form-data">
                <select name="nombre_archivo">
                    <option value="cabello.jpg">Cabello</option>
                    <option value="cocina.jpg">Cocina</option>
                    <option value="mascotas.jpg">Mascotas</option>
                    <option value="electro.jpg">Electrodomésticos</option>
                </select>
                <input type="file" name="foto" accept="image/*" required>
                <button type="submit">ACTUALIZAR FOTO</button>
            </form>
            <br><a href="/">Ver Mercado</a>
        </div>
    </body>
    </html>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
