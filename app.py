import os
import json
from flask import Flask, request, redirect, url_for

# --- CONFIGURACIÓN DE LA APP ---
app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE CARPETAS Y PERMISOS BLINDADOS ---
ROOT_PATH = app.root_path
UPLOAD_FOLDER = os.path.join(ROOT_PATH, 'static', 'img')
DATA_FILE = os.path.join(ROOT_PATH, 'productos.json')

# Creamos la carpeta de imágenes con permisos totales (mode=0o777)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, mode=0o777, exist_ok=True)

# Creamos el archivo JSON vacío con permisos totales si no existe
if not os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        os.chmod(DATA_FILE, 0o777)
    except Exception as e: pass

# Función segura para cargar productos
def cargar_db():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []
    return []

# --- LA TIENDA DE HÉCTOR ---
@app.route('/')
def home():
    productos = cargar_db()
    html_prods = ""
    for p in productos:
        html_prods += f'''
            <div class="card">
                <img src="/static/img/{p['img']}" onerror="this.src='https://via.placeholder.com/150?text=Mercado+CLN'">
                <div class="card-info">
                    <h4>{p['nombre']}</h4>
                    <p class="precio">${p['precio']}</p>
                    <button class="btn-pedido" onclick="alert('Pedido: {p['nombre']}')">PEDIR</button>
                </div>
            </div>
        '''

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mercado en Línea Culiacán</title>
        <style>
            body {{ font-family: sans-serif; margin: 0; background: #000; color: #fff; text-align: center; overflow-x: hidden; }}
            
            /* PORTADA DE BIENVENIDA */
            #portada {{ width: 100%; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #000; }}
            .logo-bienvenida {{ width: 85%; max-width: 400px; height: auto; margin-bottom: 20px; border: none; display: block; }}
            .btn-entrar {{ background: #00f2ff; color: #000; border: none; padding: 18px 50px; border-radius: 35px; font-weight: bold; font-size: 18px; cursor: pointer; margin-bottom: 15px; }}

            /* CATÁLOGO */
            #catalogo {{ display: none; padding: 15px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .card {{ background: #111; border-radius: 12px; border: 1px solid #333; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }}
            .card img {{ width: 100%; height: 130px; object-fit: cover; border-bottom: 1px solid #333; }}
            .card-info {{ padding: 10px; }}
            .card h4 {{ margin: 0; font-size: 15px; }}
            .precio {{ color: #00f2ff; font-weight: bold; font-size: 20px; margin: 5px 0; }}
            .btn-pedido {{ background: #00f2ff; color: #000; border: none; padding: 10px; width: 100%; border-radius: 6px; font-weight: bold; }}
            
            /* Enlace Admin oculto */
            .footer-link {{ display: block; color: #111; margin-top: 80px; text-decoration: none; font-size: 10px; }}
        </style>
    </head>
    <body>
        
        <div id="portada">
            <img src="/static/img/logo.jpg" class="logo-bienvenida" onerror="this.src='https://via.placeholder.com/350x350?text=MERCADO+CLN'">
            <button class="btn-entrar" onclick="abrirTienda()">VER PRODUCTOS</button>
            <p style="color: #666; font-size: 14px; margin-top: 15px;">Culiacán, Sinaloa</p>
        </div>

        <div id="catalogo">
            <h2 style="color:#00f2ff; margin-bottom:20px;">Catálogo Culiacán</h2>
            <div class="grid">{html_prods}</div>
            <a href="/config" class="footer-link">Admin System</a>
        </div>

        <script>
            function abrirTienda() {{
                document.getElementById('portada').style.display = 'none';
                document.getElementById('catalogo').style.display = 'grid';
                window.scrollTo(0,0);
            }}
        </script>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL A PANTALLA COMPLETA ---
@app.route('/config', methods=['GET', 'POST'])
def config():
    aviso = ""
    if request.method == 'POST':
        foto = request.files.get('foto')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        
        # CASO 1: Subir/Actualizar LOGO Principal
        if foto and not nombre and not precio:
            try:
                ruta_logo = os.path.join(UPLOAD_FOLDER, 'logo.jpg')
                foto.save(ruta_logo)
                # Forzamos permisos si Render lo permite
                try: os.chmod(ruta_logo, 0o777) 
                except: pass
                aviso = "<div style='color:green; font-weight:bold; border:2px solid green; padding:15px; border-radius:10px; background:#e1fbe1;'>¡Logo Principal actualizado! Ve a tu tienda.</div>"
            except Exception as e:
                aviso = f"<div style='color:red;'>Error al guardar logo: {{str(e)}}</div>"

        # CASO 2: Subir NUEVO PRODUCTO (con precio)
        elif foto and nombre and precio:
            try:
                img_id = nombre.replace(" ", "_").lower() + ".jpg"
                ruta_img = os.path.join(UPLOAD_FOLDER, img_id)
                foto.save(ruta_img)
                try: os.chmod(ruta_img, 0o777)
                except: pass
                
                db = cargar_db()
                db.append({{ "nombre": nombre, "precio": precio, "img": img_id }})
                with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(db, f, indent=4)
                # Intentamos forzar permisos al JSON
                try: os.chmod(DATA_FILE, 0o777)
                except: pass
                
                aviso = f"<div style='color:green; font-weight:bold; border:2px solid green; padding:15px; border-radius:10px; background:#e1fbe1;'>Producto '{{nombre}}' guardado.</div>"
            except Exception as e:
                aviso = f"<div style='color:red;'>Error al guardar producto: {{str(e)}}</div>"

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Control - Mercado CLN</title>
        <style>
            /* DISEÑO A PANTALLA COMPLETA (SPLASH SCREEN STYLE) */
            body {{ font-family: sans-serif; padding: 0; margin: 0; background: #fff; color: #000; width: 100vw; height: 100vh; overflow-x: hidden; }}
            
            /* Contenedor principal: Ocupa el 100% */
            .main-container {{ width: 100%; min-height: 100vh; display: flex; flex-direction: column; align-items: center; padding: 20px; box-sizing: border-box; }}
            
            h2 {{ text-align: center; color: #000; margin-top: 10px; margin-bottom: 25px; border-bottom: 3px solid #00f2ff; padding-bottom: 10px; font-size: 24px; width: 100%; max-width: 400px; }}
            
            .nav-link {{ display: block; text-align: center; color: #00f2ff; font-weight: bold; text-decoration: none; margin-bottom: 30px; font-size: 16px; border: 1px solid #00f2ff; padding: 10px 20px; border-radius: 20px; }}
            
            /* SECCIONES: Ocupan el 100% de su contenedor */
            .form-section {{ width: 100%; max-width: 400px; background: #f7f7f7; padding: 25px; border-radius: 15px; margin-bottom: 30px; border: 1px solid #eee; box-sizing: border-box; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
            h3 {{ color: #444; margin-top: 0; margin-bottom: 20px; font-size: 18px; border-left: 5px solid #00f2ff; padding-left: 10px; }}
            
            /* Inputs GRANDES y CÓMODOS en celular */
            label {{ font-weight: bold; display: block; margin-bottom: 8px; color: #555; font-size: 15px; }}
            input[type="text"], input[type="number"] {{ width: 100%; padding: 15px; margin-bottom: 20px; border: 1px solid #ccc; border-radius: 10px; box-sizing: border-box; font-size: 16px; background: #fff; }}
            input[type="file"] {{ margin-bottom: 25px; font-size: 15px; width: 100%; }}
            
            /* BOTONES GRANDES y LLAMATIVOS */
            .btn-submit {{ display: block; width: 100%; padding: 18px; background: #000; color: #fff; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 17px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: background 0.3s; }}
            .btn-submit-cyan {{ background: #00f2ff; color: #000; box-shadow: 0 4px 6px rgba(0,242,255,0.2); }}
            .btn-submit:active {{ transform: scale(0.98); }}
            
            /* footer */
            .admin-footer {{ text-align: center; color: #aaa; margin-top: 40px; font-size: 12px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="main-container">
            <h2>PANEL HÉCTOR CLN</h2>
            <a href="/" class="nav-link">👁️ Volver a mi Tienda</a>
            
            {aviso}

            <div class="form-section">
                <h3>1. Cambiar Logo de Portada</h3>
                <form method="post" enctype="multipart/form-data">
                    <label>Sube la foto de tu logo (JPG):</label>
                    <input type="file" name="foto" required>
                    <button type="submit" class="btn-submit btn-submit-cyan">ACTUALIZAR PORTADA</button>
                </form>
            </div>

            <div class="form-section">
                <h3>2. Subir Nuevo Producto</h3>
                <form method="post" enctype="multipart/form-data">
                    <label>Nombre del Producto:</label>
                    <input type="text" name="nombre" placeholder="Ej: Jabón Coche, Minisplit..." required>
                    <label>Precio ($):</label>
                    <input type="number" name="precio" placeholder="Ej: 150, 3200..." required>
                    <label>Foto del Producto (JPG):</label>
                    <input type="file" name="foto" required>
                    <button type="submit" class="btn-submit">GUARDAR EN CATÁLOGO</button>
                </form>
            </div>
            
            <p class="admin-footer">Mercado CLN v3.4 - Héctor System</p>
        </div>
    </body>
    </html>
    '''

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
