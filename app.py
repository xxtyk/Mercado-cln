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

# Datos temporales (Se borran si Render se duerme)
TABLA_PRODUCTOS = []
CONFIG = {"logo": "", "nombre_tienda": "MERCADO CLN"}

@app.route('/')
def tienda():
    # Agrupar por categorías para la vista de catálogo
    categorias = {}
    for p in TABLA_PRODUCTOS:
        cat = p.get('categoria', 'General')
        if cat not in categorias: categorias[cat] = []
        categorias[cat].append(p)

    contenido_catalogo = ""
    for cat, prods in categorias.items():
        contenido_catalogo += f'<h2 style="color:#00f2ff; text-align:left; margin-top:30px; border-bottom:1px solid #333;">{cat}</h2>'
        for p in prods:
            contenido_catalogo += f'''
            <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-bottom:20px; text-align:left;">
                <img src="{p['foto']}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                <h3 style="color:#fff; margin:0; font-size:20px;">{p['nombre']}</h3>
                <p style="color:#00f2ff; font-weight:bold; font-size:24px; margin:5px 0;">${p['precio']}</p>
                <button style="width:100%; padding:12px; background:#00f2ff; border:none; border-radius:8px; font-weight:bold;">PEDIR POR WHATSAPP</button>
            </div>'''
    
    logo_html = f'<img src="{CONFIG["logo"]}" style="max-height:80px; margin-bottom:10px;">' if CONFIG["logo"] else f'<h1 style="color:#00f2ff; letter-spacing:2px;">{CONFIG["nombre_tienda"]}</h1>'

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:10px;">
        {logo_html}
        <div style="max-width:500px; margin:auto;">{contenido_catalogo if contenido_catalogo else '<p>No hay productos registrados</p>'}</div>
        <a href="/panel-hector" style="color:#222; text-decoration:none; display:block; margin-top:50px;">Admin</a>
    </body>
    </html>'''

@app.route('/panel-hector', methods=['GET', 'POST'])
def admin():
    global TABLA_PRODUCTOS, CONFIG
    mensaje = ""
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        # Lógica para subir LOGOTIPO
        if accion == 'subir_logo':
            file = request.files.get('logo_file')
            if file:
                res = cloudinary.uploader.upload(file)
                CONFIG["logo"] = res['secure_url']
                mensaje = "✅ Logotipo actualizado"
        
        # Lógica para GUARDAR PRODUCTO
        elif accion == 'guardar_producto':
            nombre = request.form.get('nombre')
            precio = request.form.get('precio')
            categoria = request.form.get('categoria')
            file = request.files.get('file')
            if nombre and precio and file:
                try:
                    res = cloudinary.uploader.upload(file)
                    TABLA_PRODUCTOS.append({"nombre": nombre, "precio": precio, "categoria": categoria, "foto": res['secure_url']})
                    mensaje = "✅ Producto guardado"
                except Exception as e:
                    mensaje = f"❌ Error: {str(e)}"

    filas = "".join([f'<div style="background:#eee; padding:10px; margin-bottom:5px; border-radius:8px;"><b>{p["nombre"]}</b> ({p["categoria"]}) - ${p["precio"]}</div>' for p in TABLA_PRODUCTOS])

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; background:#f4f4f4; padding:15px;">
        <div style="max-width:450px; margin:auto; background:#fff; padding:20px; border-radius:20px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
            <h2 style="text-align:center;">PANEL DE CONTROL</h2>
            <p style="text-align:center; font-weight:bold; color:green;">{mensaje}</p>
            
            <div style="background:#f9f9f9; padding:15px; border-radius:15px; margin-bottom:20px; border:1px solid #ddd;">
                <h4>Insertar Logotipo</h4>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="accion" value="subir_logo">
                    <input type="file" name="logo_file" accept="image/*" required style="width:100%; margin-bottom:10px;">
                    <button type="submit" style="width:100%; padding:10px; background:#444; color:white; border:none; border-radius:8px;">SUBIR LOGO</button>
                </form>
            </div>

            <div style="border:2px solid #00f2ff; padding:15px; border-radius:15px;">
                <h4>Agregar a Catálogo</h4>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="accion" value="guardar_producto">
                    <input type="text" name="nombre" placeholder="Nombre" required style="width:100%; padding:10px; margin-bottom:10px; border-radius:8px; border:1px solid #ccc; box-sizing:border-box;">
                    <input type="number" name="precio" placeholder="Precio" required style="width:100%; padding:10px; margin-bottom:10px; border-radius:8px; border:1px solid #ccc; box-sizing:border-box;">
                    <select name="categoria" style="width:100%; padding:10px; margin-bottom:10px; border-radius:8px; border:1px solid #ccc;">
                        <option value="General">Categoría: General</option>
                        <option value="Shampoo">Shampoo y Cremas</option>
                        <option value="Electronica">Electrónica</option>
                        <option value="Aires">Aires Acondicionados</option>
                    </select>
                    <input type="file" name="file" accept="image/*" required style="width:100%; margin-bottom:15px;">
                    <button type="submit" style="width:100%; padding:15px; background:#000; color:#fff; border:none; border-radius:10px; font-weight:bold;">GUARDAR PRODUCTO</button>
                </form>
            </div>

            <h3 style="margin-top:20px;">Inventario:</h3>
            {filas if filas else '<p>No hay productos.</p>'}
            <a href="/" style="display:block; text-align:center; margin-top:20px; color:#00f2ff; text-decoration:none; font-weight:bold;">VER TIENDA</a>
        </div>
    </body>
    </html>'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
