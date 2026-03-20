import os
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- CONFIGURACIÓN MAESTRA ---
# Solo esta línea. Render leerá la CLOUDINARY_URL que pegaste.
cloudinary.config(secure=True)

# Datos en memoria (Se reinician al desplegar en Render)
TABLA_PRODUCTOS = []
TABLA_CATEGORIAS = [{"nombre": "General", "foto": "https://via.placeholder.com/150"}]
CONFIG = {"logo": "", "nombre_tienda": "MERCADO CLN"}

@app.route('/')
def tienda():
    contenido_catalogo = ""
    for cat in TABLA_CATEGORIAS:
        prods_cat = [p for p in TABLA_PRODUCTOS if p['categoria'] == cat['nombre']]
        if prods_cat:
            contenido_catalogo += f'''
            <div style="margin-top:40px; text-align:left;">
                <div style="display:flex; align-items:center; border-bottom:2px solid #00f2ff; padding-bottom:10px; margin-bottom:20px;">
                    <img src="{cat['foto']}" style="width:50px; height:50px; border-radius:50%; object-fit:cover; margin-right:15px; border:2px solid #00f2ff;">
                    <h2 style="color:#00f2ff; margin:0; text-transform:uppercase;">{cat['nombre']}</h2>
                </div>'''
            for p in prods_cat:
                contenido_catalogo += f'''
                <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-bottom:20px;">
                    <img src="{p['foto']}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <h3 style="color:#fff; margin:0;">{p['nombre']}</h3>
                    <p style="color:#00f2ff; font-weight:bold; font-size:24px; margin:5px 0;">${p['precio']}</p>
                    <button style="width:100%; padding:12px; background:#00f2ff; border:none; border-radius:8px; font-weight:bold;">PEDIR POR WHATSAPP</button>
                </div>'''
            contenido_catalogo += "</div>"
    
    logo_html = f'<img src="{CONFIG["logo"]}" style="max-height:80px;">' if CONFIG["logo"] else f'<h1 style="color:#00f2ff;">{CONFIG["nombre_tienda"]}</h1>'

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:10px;">
        {logo_html}
        <div style="max-width:500px; margin:auto;">{contenido_catalogo if contenido_catalogo else '<p>No hay productos registrados</p>'}</div>
    </body>
    </html>'''

@app.route('/panel-hector', methods=['GET', 'POST'])
def admin():
    global TABLA_PRODUCTOS, TABLA_CATEGORIAS, CONFIG
    mensaje = ""
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        try:
            if accion == 'subir_logo':
                file = request.files.get('logo_file')
                if file:
                    res = cloudinary.uploader.upload(file)
                    CONFIG["logo"] = res['secure_url']
                    mensaje = "✅ Logo actualizado"

            elif accion == 'nueva_categoria':
                nombre_cat = request.form.get('nombre_cat')
                foto_cat = request.files.get('foto_cat')
                if nombre_cat and foto_cat:
                    res = cloudinary.uploader.upload(foto_cat)
                    TABLA_CATEGORIAS.append({"nombre": nombre_cat, "foto": res['secure_url']})
                    mensaje = f"✅ Categoría {nombre_cat} creada"

            elif accion == 'guardar_producto':
                nombre = request.form.get('nombre')
                precio = request.form.get('precio')
                categoria = request.form.get('categoria')
                file = request.files.get('file')
                if nombre and precio and file:
                    res = cloudinary.uploader.upload(file)
                    TABLA_PRODUCTOS.append({"nombre": nombre, "precio": precio, "categoria": categoria, "foto": res['secure_url']})
                    mensaje = "✅ Producto guardado"
        except Exception as e:
            mensaje = f"❌ Error de Firma: {str(e)}"

    opciones_cat = "".join([f'<option value="{c["nombre"]}">{c["nombre"]}</option>' for c in TABLA_CATEGORIAS])

    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; background:#f4f4f4; padding:15px;">
        <div style="max-width:450px; margin:auto; background:#fff; padding:20px; border-radius:20px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
            <h2 style="text-align:center;">PANEL MERCADO CLN</h2>
            <p style="text-align:center; font-weight:bold; color:red;">{mensaje}</p>
            
            <form method="post" enctype="multipart/form-data" style="background:#eee; padding:10px; border-radius:10px; margin-bottom:20px;">
                <input type="hidden" name="accion" value="subir_logo">
                <b>Cambiar Logo:</b> <input type="file" name="logo_file" required>
                <button type="submit" style="width:100%; margin-top:5px;">SUBIR LOGO</button>
            </form>

            <form method="post" enctype="multipart/form-data" style="border:2px solid #ff00ea; padding:15px; border-radius:15px; margin-bottom:20px;">
                <input type="hidden" name="accion" value="nueva_categoria">
                <h4>1. Nueva Categoría</h4>
                <input type="text" name="nombre_cat" placeholder="Nombre" required style="width:100%; margin-bottom:10px;">
