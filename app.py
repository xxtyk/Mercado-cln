import os
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Configuración de Cloudinary (Asegúrate de tener las variables en Render)
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

# Esto es temporal, se borra si Render se duerme (luego ponemos base de datos)
TABLA_PRODUCTOS = []

@app.route('/')
def tienda():
    tarjetas = ""
    for p in TABLA_PRODUCTOS:
        tarjetas += f'''
        <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-bottom:20px; text-align:left;">
            <img src="{p['foto']}" style="width:100%; border-radius:10px; margin-bottom:10px;">
            <h3 style="color:#fff; margin:0; font-size:20px;">{p['nombre']}</h3>
            <p style="color:#00f2ff; font-weight:bold; font-size:24px; margin:5px 0;">${p['precio']}</p>
            <button style="width:100%; padding:12px; background:#00f2ff; border:none; border-radius:8px; font-weight:bold;">PEDIR POR WHATSAPP</button>
        </div>'''
    
    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:10px;">
        <h1 style="color:#00f2ff; letter-spacing:2px;">MERCADO CLN</h1>
        <div style="max-width:500px; margin:auto;">{tarjetas if tarjetas else '<p>No hay productos en la tienda.</p>'}</div>
        <a href="/panel-hector" style="color:#333; text-decoration:none; display:block; margin-top:50px;">Admin</a>
    </body>
    </html>'''

@app.route('/panel-hector', methods=['GET', 'POST'])
def admin():
    global TABLA_PRODUCTOS
    mensaje = ""
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        file = request.files.get('file')
        if nombre and precio and file:
            try:
                res = cloudinary.uploader.upload(file)
                TABLA_PRODUCTOS.append({{"nombre": nombre, "precio": precio, "foto": res['secure_url']}})
                mensaje = "✅ ¡Producto guardado con éxito!"
            except Exception as e:
                mensaje = f"❌ Error al subir: {{str(e)}}"

    filas = "".join([f'''
        <div style="background:#f9f9f9; padding:10px; margin-bottom:10px; border-radius:10px; display:flex; align-items:center; border:1px solid #eee;">
            <img src="{p['foto']}" style="width:50px; height:50px; object-fit:cover; border-radius:5px; margin-right:15px;">
            <div>
                <b style="display:block;">{p['nombre']}</b>
                <span style="color:green;">${p['precio']}</span>
            </div>
        </div>''' for p in TABLA_PRODUCTOS])

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; background:#f0f0f0; padding:15px; margin:0;">
        <div style="max-width:450px; margin:auto; background:#fff; padding:25px; border-radius:25px; box-shadow:0 10px 25px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; color:#333; margin-bottom:5px;">PANEL DE CONTROL</h2>
            <p style="text-align:center; margin-bottom:20px; font-weight:bold; color:{"#28a745" if "✅" in mensaje else "#dc3545"};">{mensaje}</p>
            
            <div style="border:2px solid #00f2ff; padding:20px; border-radius:20px; margin-bottom:30px;">
                <form method="post" enctype="multipart/form-data">
                    <label style="display:block; margin-bottom:5px; font-weight:bold;">Nombre del Producto:</label>
                    <input type="text" name="nombre" placeholder="Ej. Shampo Negro" required style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #ddd; border-radius:10px; box-sizing:border-box;">
                    
                    <label style="display:block; margin-bottom:5px; font-weight:bold;">Precio ($):</label>
                    <input type="number" name="precio" placeholder="160" required style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #ddd; border-radius:10px; box-sizing:border-box;">
                    
                    <label style="display:block; margin-bottom:5px; font-weight:bold;">Foto del Producto:</label>
                    <input type="file" name="file" accept="image/*" required style="margin-bottom:20px; width:100%;">
                    
                    <button type="submit" style="width:100%; padding:18px; background:#000; color:#fff; border:none; border-radius:12px; font-weight:bold; font-size:16px; cursor:pointer;">GUARDAR PRODUCTO</button>
                </form>
            </div>

            <h3 style="border-bottom:2px solid #eee; padding-bottom:10px;">Inventario Actual</h3>
            <div style="max-height:300px; overflow-y:auto;">
                {filas if filas else '<p style="color:#999; text-align:center;">No hay productos guardados todavía.</p>'}
            </div>
            
            <hr style="margin:30px 0; border:0; border-top:1px solid #eee;">
            <a href="/" style="display:block; text-align:center; color:#00f2ff; text-decoration:none; font-weight:bold; font-size:18px;">VER TIENDA PÚBLICA</a>
        </div>
    </body>
    </html>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
