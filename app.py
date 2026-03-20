import os
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDINARY (Usa las variables que pusimos en Render) ---
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# Base de datos en memoria
TABLA_PRODUCTOS = []

@app.route('/')
def tienda():
    tarjetas = ""
    for p in TABLA_PRODUCTOS:
        # Aquí ya incluimos la imagen que subiste
        imagen_html = f'<img src="{p["foto"]}" style="width:100%; border-radius:10px; margin-bottom:10px;">' if p.get('foto') else ""
        
        tarjetas += f'''
        <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-bottom:20px; text-align:left;">
            {imagen_html}
            <h3 style="color:#fff; margin:0; font-size:20px;">{p['nombre']}</h3>
            <p style="color:#00f2ff; font-weight:bold; font-size:24px; margin:5px 0;">${p['precio']}</p>
            <button style="width:100%; padding:12px; background:#00f2ff; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">PEDIR POR WHATSAPP</button>
        </div>'''
    
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:10px;">
        <h1 style="color:#00f2ff; letter-spacing:2px; margin-bottom:30px;">MERCADO CLN</h1>
        <div style="max-width:500px; margin:auto;">
            {tarjetas if tarjetas else '<p style="color:gray; margin-top:50px;">No hay productos disponibles por ahora.</p>'}
        </div>
        <a href="/panel-hector" style="display:block; margin-top:100px; color:#222; text-decoration:none;">Admin</a>
    </body>
    </html>'''

@app.route('/panel-hector', methods=['GET', 'POST'])
def admin():
    global TABLA_PRODUCTOS
    mensaje = ""
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        file_to_upload = request.files.get('file')
        
        if nombre and precio and file_to_upload:
            try:
                # 1. Subimos la foto a Cloudinary
                upload_result = cloudinary.uploader.upload(file_to_upload)
                url_foto = upload_result['secure_url']
                
                # 2. Guardamos en la lista con todo y foto
                TABLA_PRODUCTOS.append({{
                    "nombre": nombre, 
                    "precio": precio, 
                    "foto": url_foto,
                    "status": True
                }})
                mensaje = f"✅ ¡{nombre} guardado con éxito!"
            except Exception as e:
                mensaje = f"❌ Error al subir: {{str(e)}}"

    filas = ""
    for p in TABLA_PRODUCTOS:
        filas += f'''
        <div style="background:#eee; padding:10px; border-radius:8px; margin-bottom:5px; display:flex; align-items:center; justify-content:space-between;">
            <img src="{p['foto']}" style="width:40px; height:40px; border-radius:5px; object-fit:cover; margin-right:10px;">
            <span style="flex-grow:1;"><b>{p['nombre']}</b> (${p['precio']})</span>
            <span style="color:green; font-size:12px;">ACTIVO</span>
        </div>'''

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; background:#f0f0f0; padding:15px;">
        <div style="max-width:400px; margin:auto; background:#fff; padding:20px; border-radius:20px; box-shadow:0 10px 20px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; margin-top:0;">PANEL DE CONTROL</h2>
            <p style="text-align:center; color:blue; font-weight:bold;">{mensaje}</p>
            
            <form method="post" enctype="multipart/form-data" style="border:2px solid #00f2ff; padding:15px; border-radius:15px;">
                <label>Nombre del Producto:</label><br>
                <input type="text" name="nombre" placeholder="Ej. Shampo Negro" required style="width:100%; padding:10px; margin:8px 0; border:1px solid #ccc; border-radius:8px; box-sizing:border-box;">
                
                <label>Precio ($):</label><br>
                <input type="number" name="precio" placeholder="160" required style="width:100%; padding:10px; margin:8px 0; border:1px solid #ccc; border-radius:8px; box-sizing:border-box;">
                
                <label>Foto del Producto:</label><br>
                <input type="file" name="file" accept="image/*" required style="width:100%; margin:10px 0;">
                
                <button type="submit" style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:10px; font-weight:bold; font-size:16px; margin-top:10px; cursor:pointer;">GUARDAR PRODUCTO</button>
            </form>

            <h3 style="margin-top:25px; border-bottom:1px solid #ccc;">Inventario Actual</h3>
            {filas if filas else '<p style="color:gray;">No hay productos guardados.</p>'}
            
            <a href="/" style="display:block; text-align:center; margin-top:20px; color:#00f2ff; font-weight:bold; text-decoration:none;">VER TIENDA PÚBLICA</a>
        </div>
    </body>
    </html>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
