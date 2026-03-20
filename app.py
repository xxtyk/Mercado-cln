import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config(secure=True)

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, precio TEXT, categoria TEXT, foto TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS categorias 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, foto TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS config 
                      (id INTEGER PRIMARY KEY, logo TEXT, nombre_tienda TEXT)''')
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO categorias (nombre, foto) VALUES (?, ?)", 
                       ("General", "https://via.placeholder.com/150"))
    cursor.execute("SELECT COUNT(*) FROM config")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config (id, logo, nombre_tienda) VALUES (1, '', 'MERCADO CLN')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def tienda():
    conn = sqlite3.connect('datos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    categorias = cursor.execute("SELECT * FROM categorias").fetchall()
    productos = cursor.execute("SELECT * FROM productos").fetchall()
    config = cursor.execute("SELECT * FROM config WHERE id=1").fetchone()
    conn.close()

    catalogo_html = ""
    for cat in categorias:
        prods_cat = [p for p in productos if p['categoria'] == cat['nombre']]
        if prods_cat:
            catalogo_html += f'''
            <div style="margin-top:40px; text-align:left; padding:0 10px;">
                <div style="display:flex; align-items:center; border-bottom:2px solid #00f2ff; padding-bottom:10px; margin-bottom:20px;">
                    <img src="{cat['foto']}" style="width:50px; height:50px; border-radius:50%; object-fit:cover; margin-right:15px; border:2px solid #00f2ff;">
                    <h2 style="color:#00f2ff; margin:0; text-transform:uppercase;">{cat['nombre']}</h2>
                </div>'''
            for p in prods_cat:
                catalogo_html += f'''
                <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-bottom:20px;">
                    <img src="{p['foto']}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                    <h3 style="color:#fff; margin:0;">{p['nombre']}</h3>
                    <p style="color:#00f2ff; font-weight:bold; font-size:24px; margin:5px 0;">${p['precio']}</p>
                    <a href="https://wa.me/521667XXXXXXX?text=Hola, quiero {p['nombre']}" style="display:block; text-align:center; background:#00f2ff; color:#000; padding:12px; border-radius:8px; font-weight:bold; text-decoration:none;">PEDIR POR WHATSAPP</a>
                </div>'''
            catalogo_html += "</div>"
    
    logo = f'<img src="{config["logo"]}" style="max-height:80px;">' if config["logo"] else f'<h1 style="color:#00f2ff;">{config["nombre_tienda"]}</h1>'

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="background:#000; color:#fff; font-family:sans-serif; text-align:center; padding:10px;">
        {logo}
        <div style="max-width:500px; margin:auto;">{catalogo_html if catalogo_html else '<p>No hay productos</p>'}</div>
    </body>
    </html>'''

@app.route('/panel-hector', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('datos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    mensaje = ""
    if request.method == 'POST':
        accion = request.form.get('accion')
        try:
            if accion == 'subir_logo':
                file = request.files.get('logo_file')
                if file:
                    res = cloudinary.uploader.upload(file)
                    cursor.execute("UPDATE config SET logo=? WHERE id=1", (res['secure_url'],))
                    mensaje = "✅ Logo actualizado"
            elif accion == 'nueva_categoria':
                nombre_cat = request.form.get('nombre_cat')
                foto_cat = request.files.get('foto_cat')
                if nombre_cat and foto_cat:
                    res = cloudinary.uploader.upload(foto_cat)
                    cursor.execute("INSERT INTO categorias (nombre, foto) VALUES (?, ?)", (nombre_cat, res['secure_url']))
                    mensaje = f"✅ Categoría {nombre_cat} creada"
            elif accion == 'guardar_producto':
                nombre, precio, categoria = request.form.get('nombre'), request.form.get('precio'), request.form.get('categoria')
                file = request.files.get('file')
                if nombre and precio and file:
                    res = cloudinary.uploader.upload(file)
                    cursor.execute("INSERT INTO productos (nombre, precio, categoria, foto) VALUES (?, ?, ?, ?)", (nombre, precio, categoria, res['secure_url']))
                    mensaje = "✅ Producto guardado"
            conn.commit()
        except Exception as e:
            mensaje = f"❌ Error: {str(e)}"
    
    categorias = cursor.execute("SELECT * FROM categorias").fetchall()
    opciones = "".join([f'<option value="{c["nombre"]}">{c["nombre"]}</option>' for c in categorias])
    conn.close()
    return f'''
    <!DOCTYPE html>
    <html>
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="font-family:sans-serif; padding:15px; background:#f4f4f4;">
        <div style="max-width:450px; margin:auto; background:#fff; padding:20px; border-radius:15px;">
            <h2>PANEL ADMIN</h2>
            <p style="color:red;">{mensaje}</p>
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="accion" value="guardar_producto">
                <input type="text" name="nombre" placeholder="Producto" required style="width:100%; margin-bottom:10px;">
                <input type="number" name="precio" placeholder="Precio" required style="width:100%; margin-bottom:10px;">
                <select name="categoria" style="width:100%; margin-bottom:10px;">{opciones}</select>
                <input type="file" name="file" required style="width:100%; margin-bottom:10px;">
                <button type="submit" style="width:100%; background:#00f2ff; padding:10px; border:none; border-radius:5px;">GUARDAR</button>
            </form>
            <hr>
            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="accion" value="nueva_categoria">
                <input type="text" name="nombre_cat" placeholder="Nueva Categoría" required style="width:100%; margin-bottom:10px;">
                <input type="file" name="foto_cat" required style="width:100%; margin-bottom:10px;">
                <button type="submit" style="width:100%; background:#ff00ea; color:#fff; padding:10px; border:none; border-radius:5px;">CREAR CATEGORÍA</button>
            </form>
        </div>
    </body>
    </html>'''

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto)
