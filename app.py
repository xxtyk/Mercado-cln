from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
import cloudinary
import cloudinary.uploader
import urllib.parse

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDINARY ---
cloudinary.config( 
  cloud_name = "dosyi726x", 
  api_key = "942229587198227", 
  api_secret = "JHn-OlPaUEdfqvCk1DvgTeSUhyQ" 
)

DATABASE_URL = "postgresql://mercado_db_dcie_user:5MXf0RlYpfLs9Cjokjmttgop44auKfuV@dpg-d6v3vkk50q8c739drkd0-a/mercado_db_dcie"
MI_WHATSAPP = "526679771409"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    # Ahora traemos también la descripción
    cur.execute('SELECT nombre, precio, imagen, descripcion FROM productos ORDER BY id DESC')
    rows = cur.fetchall()
    productos = []
    for r in rows:
        desc = r[3] if r[3] else ""
        mensaje = f"Hola Héctor, me interesa: {r[0]}. Precio: ${r[1]}. {desc}"
        link_ws = f"https://wa.me/{MI_WHATSAPP}?text={urllib.parse.quote(mensaje)}"
        productos.append({"nombre": r[0], "precio": r[1], "imagen": r[2], "link_ws": link_ws, "descripcion": desc})
    cur.close()
    conn.close()
    return render_template('index.html', productos=productos)

@app.route('/admin_hector', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        descripcion = request.form['descripcion']
        
        archivo_foto = request.files['foto']
        resultado = cloudinary.uploader.upload(archivo_foto)
        url_foto = resultado['secure_url']
        
        conn = get_db_connection()
        cur = conn.cursor()
        # Guardamos también la descripción en la base de datos
        cur.execute('INSERT INTO productos (nombre, precio, imagen, descripcion) VALUES (%s, %s, %s, %s)',
                    (nombre, precio, url_foto, descripcion))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin'))
    
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background-color: #004d40; margin: 0; font-family: sans-serif; color: white; padding-bottom: 90px; }
            .header { padding: 20px; display: flex; align-items: center; border-bottom: 1px solid #00695c; background: #004d40; position: sticky; top: 0; z-index: 10; }
            .header h2 { margin: 0 0 0 15px; font-size: 18px; }
            form { padding: 20px; display: flex; flex-direction: column; gap: 15px; }
            .upload-box { border: 2px dashed #00796b; background: #003d33; height: 120px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
            .upload-box input { opacity: 0; position: absolute; width: 100%; height: 100%; }
            .field { border-bottom: 1px solid #00796b; padding: 5px 0; }
            label { font-size: 11px; color: #80cbc4; text-transform: uppercase; }
            input, textarea { background: transparent; border: none; color: white; width: 100%; font-size: 16px; outline: none; padding: 5px 0; font-family: sans-serif; }
            textarea { height: 60px; resize: none; }
            .btn-guardar { position: fixed; bottom: 0; left: 0; width: 100%; background: #2ecc71; color: #004d40; border: none; padding: 20px; font-size: 18px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="header"><span>←</span><h2>PRODUCTO</h2></div>
        <form action="/admin_hector" method="POST" enctype="multipart/form-data">
            <div class="upload-box">
                <span style="font-size: 30px;">📷</span>
                <p style="margin:5px 0; font-size: 12px;">* Galería (JPG o PNG)</p>
                <input type="file" name="foto" accept="image/*" required>
            </div>
            <div class="field"><label>* Nombre</label><input type="text" name="nombre" required></div>
            <div class="field"><label>* Descripción</label><textarea name="descripcion" placeholder="Detalles del producto..."></textarea></div>
            <div class="field"><label>Categoría</label><input type="text" name="categoria" placeholder="Cuidado del cabello, etc."></div>
            <div class="field"><label>* Precio Unitario</label><input type="number" name="precio" step="0.01" required></div>
            <button type="submit" class="btn-guardar">GUARDAR</button>
        </form>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
