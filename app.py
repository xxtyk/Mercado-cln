import os
import json
from flask import Flask, request, redirect, url_for

app = Flask(__name__, static_folder='static')

# --- RUTAS QUE RENDER ENTIENDE ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Forzamos la carpeta de imagenes dentro de static
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'img')
DATA_FILE = os.path.join(BASE_DIR, 'productos.json')

# Intentar crear carpeta si no existe
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    except:
        pass

def cargar_db():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_db(datos):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4)
        return True
    except:
        return False

# --- VISTA CLIENTE ---
@app.route('/')
def home():
    productos = cargar_db()
    items_html = ""
    for p in productos:
        if p.get('disponible', True):
            # Usamos url_for para que no falle la ruta de la imagen
            img_url = url_for('static', filename=f"img/{p['img']}")
            items_html += f'''
                <div style="background:#111; border-radius:12px; padding:10px; border:1px solid #333;">
                    <img src="{img_url}" style="width:100%; border-radius:8px; height:150px; object-fit:cover;">
                    <h3 style="margin:10px 0 5px 0;">{p['nombre']}</h3>
                    <p style="color:#00f2ff; font-weight:bold; font-size:22px; margin:0;">${p['precio']}</p>
                    <button style="width:100%; padding:12px; background:#00f2ff; border:none; border-radius:8px; margin-top:10px; font-weight:bold;">PEDIR</button>
                </div>'''

    logo_url = url_for('static', filename='img/logo.jpg')
    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:15px;">
        <img src="{logo_url}" style="width:80%; max-width:250px; margin-bottom:20px;" onerror="this.src='https://via.placeholder.com/250?text=MERCADO+CLN+CULIACAN'">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">{items_html if items_html else '<p>Sube productos en el panel para empezar.</p>'}</div>
        <a href="/panel-hector" style="opacity:0.2; text-decoration:none; color:#fff; font-size:10px; display:block; margin-top:50px;">Admin</a>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL ---
@app.route('/panel-hector', methods=['GET', 'POST'])
def panel():
    msg = ""
    productos = cargar_db()
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        try:
            if accion == 'nuevo':
                nombre = request.form.get('nombre')
                precio = request.form.get('precio')
                foto = request.files.get('foto')
                if foto and nombre:
                    img_name = f"{nombre.replace(' ', '_').lower()}.jpg"
                    foto.save(os.path.join(UPLOAD_FOLDER, img_name))
                    productos.append({{"nombre": nombre, "precio": precio, "img": img_name, "disponible": True}})
                    if guardar_db(productos):
                        msg = "✅ Guardado con éxito"
                    else:
                        msg = "❌ Error al escribir en el servidor"

            elif accion == 'logo':
                foto = request.files.get('foto')
                if foto:
                    foto.save(os.path.join(UPLOAD_FOLDER, 'logo.jpg'))
                    msg = "✅ Logo actualizado"

            elif accion == 'switch':
                idx = int(request.form.get('id'))
                productos[idx]['disponible'] = not productos[idx].get('disponible', True)
                guardar_db(productos)
                msg = "🔄 Estado cambiado"
        except Exception as e:
            msg = f"❌ Error: {str(e)}"

    lista_admin = ""
    for i, p in enumerate(productos):
        color = "#28a745" if p.get('disponible', True) else "#dc3545"
        lista_admin += f'''
            <div style="background:#eee; padding:10px; margin-bottom:10px; border-radius:10px; display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:bold;">{p['nombre']}</span>
                <form method="post" style="margin:0;">
                    <input type="hidden" name="accion" value="switch">
                    <input type="hidden" name="id" value="{i}">
                    <button type="submit" style="background:{color}; color:white; border:none; padding:8px; border-radius:5px;">{ "ON" if p.get('disponible', True) else "OFF" }</button>
                </form>
            </div>'''

    return f'''
    <body style="font-family:sans-serif; padding:15px; background:#f4f4f4;">
        <div style="max-width:400px; margin:auto; background:#fff; padding:20px; border-radius:15px;">
            <h2 style="text-align:center;">CONFIGURACIÓN</h2>
            <p style="text-align:center; color:blue;">{msg}</p>
            
            <form method="post" enctype="multipart/form-data" style="background:#f9f9f9; padding:10px; border-radius:10px;">
                <b>1. Subir Logo:</b><br>
                <input type="hidden" name="accion" value="logo">
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:#00f2ff; border:none; border-radius:5px;">ACTUALIZAR LOGO</button>
            </form>
            <br>
            <form method="post" enctype="multipart/form-data" style="background:#f9f9f9; padding:10px; border-radius:10px;">
                <b>2. Nuevo Producto:</b><br>
                <input type="hidden" name="accion" value="nuevo">
                <input type="text" name="nombre" placeholder="Nombre" required style="width:95%; padding:8px; margin:5px 0;"><br>
                <input type="number" name="precio" placeholder="Precio" required style="width:95%; padding:8px; margin:5px 0;"><br>
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:#000; color:#fff; border:none; border-radius:5px;">GUARDAR PRODUCTO</button>
            </form>
            <hr>
            {lista_admin}
            <a href="/" style="display:block; text-align:center; margin-top:20px;">Ver Tienda</a>
        </div>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
