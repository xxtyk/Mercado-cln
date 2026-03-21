from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
import cloudinary
import cloudinary.uploader
import urllib.parse

app = Flask(__name__)

# --- CONFIGURACIÓN PROFESIONAL DE CLOUDINARY (TUS DATOS) ---
cloudinary.config( 
  cloud_name = "dosyi726x", 
  api_key = "942229587198227", 
  api_secret = "JHn-OlPaUEdfqvCk1DvgTeSUhyQ" 
)

# --- CONEXIÓN A TU BASE DE DATOS Y WHATSAPP ---
DATABASE_URL = "postgresql://mercado_db_dcie_user:5MXf0RlYpfLs9Cjokjmttgop44auKfuV@dpg-d6v3vkk50q8c739drkd0-a/mercado_db_dcie"
MI_WHATSAPP = "526679771409"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT nombre, precio, imagen FROM productos ORDER BY id DESC')
    rows = cur.fetchall()
    productos = []
    for r in rows:
        mensaje = f"Hola Héctor, me interesa el producto: {r[0]} con precio de ${r[1]}"
        link_ws = f"https://wa.me/{MI_WHATSAPP}?text={urllib.parse.quote(mensaje)}"
        productos.append({"nombre": r[0], "precio": r[1], "imagen": r[2], "link_ws": link_ws})
    cur.close()
    conn.close()
    return render_template('index.html', productos=productos)

@app.route('/admin_hector', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        
        # SUBIR FOTO DIRECTO DESDE EL CELULAR
        archivo_foto = request.files['foto']
        resultado = cloudinary.uploader.upload(archivo_foto)
        url_foto = resultado['secure_url']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO productos (nombre, precio, imagen) VALUES (%s, %s, %s)',
                    (nombre, precio, url_foto))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin'))
    
    # DISEÑO "ESPEJO" DE TU FOTO (HOJA COMPLETA VERDE)
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background-color: #004d40; margin: 0; font-family: sans-serif; color: white; padding-bottom: 80px; }
            .header { padding: 20px; display: flex; align-items: center; border-bottom: 1px solid #00695c; }
            .header h2 { margin: 0 0 0 15px; font-size: 18px; text-transform: uppercase; }
            form { padding: 20px; display: flex; flex-direction: column; gap: 20px; }
            .upload-box { border: 2px dashed #00796b; background: #003d33; height: 150px; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
            .upload-box input { opacity: 0; position: absolute; width: 100%; height: 100%; cursor: pointer; }
            .field { border-bottom: 1px solid #00796b; padding: 10px 0; }
            label { font-size: 12px; color: #80cbc4; display: block; margin-bottom: 5px; }
            input[type="text"], input[type="number"] { background: transparent; border: none; color: white; width: 100%; font-size: 16px; outline: none; }
            .btn-guardar { position: fixed; bottom: 0; left: 0; width: 100%; background: #2ecc71; color: #003d33; border: none; padding: 20px; font-size: 18px; font-weight: bold; text-transform: uppercase; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="header">
            <span>←</span>
            <h2>PRODUCTO</h2>
        </div>
        <form action="/admin_hector" method="POST" enctype="multipart/form-data">
            <div class="upload-box">
                <span style="font-size: 40px;">📷</span>
                <p>* Galería (JPG o PNG)</p>
                <input type="file" name="foto" accept="image/*" required>
            </div>
            
            <div class="field">
                <label>* Nombre</label>
                <input type="text" name="nombre" placeholder="Nombre del producto" required>
            </div>
            
            <div class="field">
                <label>* Precio Unitario</label>
                <input type="number" name="precio" placeholder="0.00" step="0.01" required>
            </div>

            <button type="submit" class="btn-guardar">GUARDAR</button>
        </form>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
