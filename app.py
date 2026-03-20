import os
import json
from flask import Flask, request, redirect

app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'img')
DATA_FILE = os.path.join(BASE_DIR, 'productos.json')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cargar_db():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return []

def guardar_db(datos):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4)

# --- VISTA DEL CLIENTE (Solo ve los 'disponibles') ---
@app.route('/')
def home():
    productos = cargar_db()
    items_html = ""
    for p in productos:
        # SECRETO: Si el producto no está disponible, no se muestra al cliente
        if p.get('disponible', True):
            items_html += f'''
                <div style="background:#111; border-radius:12px; padding:10px; border:1px solid #333;">
                    <img src="/static/img/{p['img']}" style="width:100%; border-radius:8px; height:150px; object-fit:cover;">
                    <h3 style="margin:10px 0 5px 0;">{p['nombre']}</h3>
                    <p style="color:#00f2ff; font-weight:bold; font-size:22px; margin:0;">${p['precio']}</p>
                    <button style="width:100%; padding:12px; background:#00f2ff; border:none; border-radius:8px; margin-top:10px; font-weight:bold;">PEDIR AHORA</button>
                </div>'''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>body {{ background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:15px; }}</style>
    </head>
    <body>
        <img src="/static/img/logo.jpg" style="width:80%; max-width:250px; margin-bottom:20px;" onerror="this.src='https://via.placeholder.com/250?text=MERCADO+CLN'">
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">{items_html if items_html else '<p>Catálogo actualizándose...</p>'}</div>
        <a href="/panel-hector" style="color:#222; text-decoration:none; font-size:10px; display:block; margin-top:100px;">Admin Access</a>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL CON INTERRUPTOR ---
@app.route('/panel-hector', methods=['GET', 'POST'])
def panel():
    msg = ""
    productos = cargar_db()
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'nuevo':
            nombre = request.form.get('nombre')
            precio = request.form.get('precio')
            foto = request.files.get('foto')
            if foto and nombre:
                img_name = nombre.replace(" ", "_").lower() + ".jpg"
                foto.save(os.path.join(UPLOAD_FOLDER, img_name))
                # Guardamos como disponible por defecto
                productos.append({{"nombre": nombre, "precio": precio, "img": img_name, "disponible": True}})
                guardar_db(productos)
                msg = f"✅ '{nombre}' listo en el sistema"

        elif accion == 'switch':
            idx = int(request.form.get('id'))
            # Cambiamos de True a False o viceversa
            productos[idx]['disponible'] = not productos[idx].get('disponible', True)
            guardar_db(productos)
            estado = "ACTIVADO" if productos[idx]['disponible'] else "DESACTIVADO"
            msg = f"🔄 {productos[idx]['nombre']} ahora está {{estado}}"

    # Generar lista para el dueño con el botón de "aplastar"
    lista_admin = ""
    for i, p in enumerate(productos):
        esta_on = p.get('disponible', True)
        color_btn = "#28a745" if esta_on else "#dc3545"
        texto_btn = "DISPONIBLE (ON)" if esta_on else "AGOTADO (OFF)"
        
        lista_admin += f'''
            <div style="background:#eee; padding:15px; margin-bottom:10px; border-radius:10px; border-left: 8px solid {color_btn};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="text-align:left;">
                        <b style="font-size:18px;">{p['nombre']}</b><br>
                        <span>Precio: ${p['precio']}</span>
                    </div>
                    <form method="post" style="margin:0;">
                        <input type="hidden" name="accion" value="switch">
                        <input type="hidden" name="id" value="{i}">
                        <button type="submit" style="background:{color_btn}; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">
                            {texto_btn}
                        </button>
                    </form>
                </div>
            </div>'''

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; background:#f4f4f4; padding:15px; margin:0;">
        <div style="max-width:500px; margin:auto; background:#fff; padding:20px; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; border-bottom:3px solid #00f2ff; padding-bottom:10px;">CONTROL DE INVENTARIO</h2>
            <p style="text-align:center; color:blue; font-weight:bold;">{msg}</p>
            <a href="/" style="display:block; text-align:center; margin-bottom:20px; color:#00f2ff; font-weight:bold; text-decoration:none; border:1px solid #00f2ff; padding:10px; border-radius:20px;">👁️ VER TIENDA PÚBLICA</a>
            
            <section style="background:#fafafa; padding:15px; border-radius:10px; border:1px solid #ddd; margin-bottom:30px;">
                <h3 style="margin-top:0;">➕ Agregar Nuevo</h3>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="accion" value="nuevo">
                    <input type="text" name="nombre" placeholder="Nombre" required style="width:100%; padding:12px; margin-bottom:10px; box-sizing:border-box;">
                    <input type="number" name="precio" placeholder="Precio ($)" required style="width:100%; padding:12px; margin-bottom:10px; box-sizing:border-box;">
                    <input type="file" name="foto" required style="width:100%; margin-bottom:15px;">
                    <button type="submit" style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:10px; font-weight:bold;">GUARDAR PRODUCTO</button>
                </form>
            </section>

            <h3>📋 Tu Inventario (Aplastale para activar/desactivar)</h3>
            {lista_admin if productos else '<p>No hay productos guardados.</p>'}
        </div>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
