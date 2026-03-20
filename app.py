import os
from flask import Flask, request, redirect, url_for

app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE CARPETAS ---
UPLOAD_FOLDER = 'static/img'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- VISTA DEL CLIENTE (SOADI HICA) ---
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Soadi hica</title>
        <style>
            body { font-family: sans-serif; margin: 0; background: #000; color: #fff; text-align: center; }
            .logo-inicio { width: 200px; height: 200px; margin-top: 60px; cursor: pointer; border-radius: 50%; border: 4px solid #00f2ff; object-fit: cover; }
            .header-titulo { color: #00f2ff; font-size: 28px; margin-top: 20px; }
            .btn-entrar { background: #00f2ff; color: #000; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 20px; }
        </style>
    </head>
    <body>
        <img src="/static/img/logo.jpg" class="logo-inicio" onerror="this.src='https://via.placeholder.com/200?text=LOGO+AQUÍ'">
        <h1 class="header-titulo">Soadi hica</h1>
        <p>Culiacán • Pago Contra Entrega</p>
        <a href="/config" style="display:block; margin-top:100px; color:#333; text-decoration:none;">Acceso Panel</a>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL PROFESIONAL ---
@app.route('/config', methods=['GET', 'POST'])
def config():
    msg = ""
    if request.method == 'POST':
        file = request.files.get('foto')
        nombre = request.form.get('nombre_archivo')
        if file and nombre:
            # Aseguramos que termine en .jpg para que el código lo encuentre
            if not nombre.lower().endswith('.jpg'):
                nombre = nombre + '.jpg'
            file.save(os.path.join(UPLOAD_FOLDER, nombre.lower()))
            msg = f"<div style='background:#d4edda; color:#155724; padding:10px; border-radius:5px;'>¡Archivo '{nombre}' actualizado con éxito!</div>"

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Control - Soadi hica</title>
        <style>
            body {{ font-family: sans-serif; background: #f4f4f4; padding: 20px; color: #333; }}
            .container {{ max-width: 500px; margin: auto; background: #fff; padding: 25px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
            h2 {{ text-align: center; color: #000; margin-bottom: 30px; border-bottom: 2px solid #00f2ff; padding-bottom: 10px; }}
            .btn {{ display: block; width: 100%; padding: 15px; margin: 10px 0; border: none; border-radius: 10px; font-weight: bold; text-decoration: none; cursor: pointer; text-align: center; font-size: 16px; box-sizing: border-box; }}
            .btn-view {{ background: #f8f9fa; border: 2px solid #000; color: #000; }}
            .btn-cat {{ background: #00f2ff; color: #000; }}
            .btn-prod {{ background: #000; color: #fff; }}
            .seccion {{ margin-top: 30px; padding-top: 20px; border-top: 1px dashed #ccc; }}
            label {{ font-weight: bold; display: block; margin-bottom: 5px; }}
            input[type="text"], select {{ width: 100%; padding: 12px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>PANEL DE CONTROL</h2>
            {msg}

            <label>Paso 1: Revisar tienda</label>
            <a href="/" class="btn btn-view">👁️ VER MI CATÁLOGO</a>

            <div class="seccion">
                <label>Paso 2: Configurar Categorías</label>
                <form method="post" enctype="multipart/form-data">
                    <select name="nombre_archivo">
                        <option value="logo.jpg">Cambiar LOGO Principal</option>
                        <option value="cabello.jpg">Imagen Cuidado del Cabello</option>
                        <option value="cocina.jpg">Imagen Cocina / Hogar</option>
                        <option value="mascotas.jpg">Imagen Mascotas</option>
                        <option value="electro.jpg">Imagen Electrodomésticos</option>
                    </select>
                    <input type="file" name="foto" required>
                    <button type="submit" class="btn btn-cat">ACTUALIZAR CATEGORÍA</button>
                </form>
            </div>

            <div class="seccion">
                <label>Paso 3: Configurar Productos Individuales</label>
                <form method="post" enctype="multipart/form-data">
                    <input type="text" name="nombre_archivo" placeholder="Ejemplo: botox o minisplit" required>
                    <input type="file" name="foto" required>
                    <button type="submit" class="btn btn-prod">SUBIR NUEVO PRODUCTO</button>
                </form>
            </div>
        </div>
        <p style="text-align:center; font-size:12px; color:#998; margin-top:20px;">Soadi hica Sistema v3.0</p>
    </body>
    </html>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
