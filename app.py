import os
import json
from flask import Flask, request, redirect

app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE RUTAS ---
# Usamos rutas que Render entiende a la primera
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'img')
DATA_FILE = os.path.join(BASE_DIR, 'productos.json')

# Crear carpetas si no existen (con permisos totales)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cargar_db():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

# --- VISTA DE LA TIENDA ---
@app.route('/')
def home():
    productos = cargar_db()
    # Si no hay productos, mostramos un mensaje amigable en lugar de pantalla blanca
    contenido = ""
    if not productos:
        contenido = '<p style="color:#666;">Cargando catálogo... sube productos en el panel.</p>'
    else:
        for p in productos:
            contenido += f'''
                <div style="background:#111; border-radius:10px; padding:10px; border:1px solid #333;">
                    <img src="/static/img/{p['img']}" style="width:100%; border-radius:8px;">
                    <h4>{p['nombre']}</h4>
                    <p style="color:#00f2ff; font-weight:bold; font-size:20px;">${p['precio']}</p>
                </div>'''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ background:#000; color:#fff; font-family:sans-serif; text-align:center; margin:0; padding:20px; }}
            .logo {{ width:80%; max-width:300px; margin-bottom:20px; }}
            .btn-panel {{ color:#333; text-decoration:none; font-size:12px; display:block; margin-top:50px; }}
        </style>
    </head>
    <body>
        <img src="/static/img/logo.jpg" class="logo" onerror="this.src='https://via.placeholder.com/300?text=MERCADO+CLN'">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:15px;">{contenido}</div>
        <a href="/panel-hector" class="btn-panel">Acceso Panel</a>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL (NUEVA RUTA MÁS SEGURA) ---
@app.route('/panel-hector', methods=['GET', 'POST'])
def panel():
    msg = ""
    if request.method == 'POST':
        foto = request.files.get('foto')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        
        # Guardar Logo
        if foto and not nombre:
            foto.save(os.path.join(UPLOAD_FOLDER, 'logo.jpg'))
            msg = "✅ Logo actualizado"
        # Guardar Producto
        elif foto and nombre and precio:
            img_name = nombre.replace(" ", "_").lower() + ".jpg"
            foto.save(os.path.join(UPLOAD_FOLDER, img_name))
            db = cargar_db()
            db.append({{"nombre": nombre, "precio": precio, "img": img_name}})
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(db, f)
            msg = f"✅ Guardado: {nombre}"

    return f'''
    <body style="font-family:sans-serif; padding:20px; text-align:center; background:#f0f0f0;">
        <div style="max-width:400px; margin:auto; background:#fff; padding:20px; border-radius:15px; border:2px solid #00f2ff;">
            <h2>PANEL DE CONTROL</h2>
            <p style="color:green;">{msg}</p>
            <a href="/">👁️ Ver Tienda</a>
            <hr>
            <form method="post" enctype="multipart/form-data">
                <p><b>Cambiar Logo Principal:</b></p>
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:#00f2ff; border:none; border-radius:5px;">ACTUALIZAR LOGO</button>
            </form>
            <hr>
            <form method="post" enctype="multipart/form-data">
                <p><b>Nuevo Producto:</b></p>
                <input type="text" name="nombre" placeholder="Nombre" required style="width:90%; padding:10px; margin-bottom:10px;"><br>
                <input type="number" name="precio" placeholder="Precio" required style="width:90%; padding:10px; margin-bottom:10px;"><br>
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:#000; color:#fff; border:none; border-radius:5px;">GUARDAR PRODUCTO</button>
            </form>
        </div>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
