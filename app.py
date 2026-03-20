import os
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Configuración de Cloudinary
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
)

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
        <div style="max-width:500px; margin:auto;">{tarjetas if tarjetas else '<p>No hay productos registrados</p>'}</div>
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
                TABLA_PRODUCTOS.append({"nombre": nombre, "precio": precio, "foto": res['secure_url']})
                mensaje = "✅ ¡Producto guardado!"
            except Exception as e:
                mensaje = f"❌ Error: {str(e)}"

    filas = "".join([f'<div style="background:#eee; padding:10px; margin-bottom:5px; border-radius:8px;"><b>{p["nombre"]}</b> - ${p["precio"]}</div>' for p in TABLA_PRODUCTOS])

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; background:#f0f0f0; padding:15px;">
        <div style="max-width:400px; margin:auto; background:#fff; padding:20px; border-radius:20px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
            <h2 style="text-align:center;">PANEL DE CONTROL</h2>
            <p style="text-align:center; font-weight:bold; color:{"green" if "✅" in mensaje else "red"};">{mensaje}</p>
            <form method="post" enctype="multipart/form-data">
                <input type="text" name="nombre" placeholder="Nombre del Producto" required style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:8px; box-sizing:border-box;">
                <input type="number" name="precio" placeholder="Precio ($)" required style="width:100%; padding:10px; margin-bottom:10px; border:1px solid #ccc; border-radius:8px; box-sizing:border-box;">
                <input type="file" name="file" accept="image/*" required style="margin-bottom:20px;">
                <button type="submit" style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">GUARDAR PRODUCTO</button>
            </form>
            <h3 style="margin-top:30px; border-top:1px solid #eee; padding-top:10px;">Inventario:</h3>
            {filas if filas else '<p style="color:#999;">No hay productos guardados.</p>'}
            <a href="/" style="display:block; text-align:center; margin-top:20px; color:#00f2ff; text-decoration:none; font-weight:bold;">VER TIENDA PÚBLICA</a>
        </div>
    </body>
    </html>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
