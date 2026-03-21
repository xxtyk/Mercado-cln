from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = "hector_cln_2026"

# TU BASE DE DATOS Y TU WHATSAPP DE CULIACÁN
DATABASE_URL = "postgresql://mercado_db_dcie_user:5MXf0RlYpfLs9Cjokjmttgop44auKfuV@dpg-d6v3vkk50q8c739drkd0-a/mercado_db_dcie"
MI_WHATSAPP = "526679771409"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# --- INICIO DE LA PÁGINA (LO QUE VE EL CLIENTE) ---
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

# --- PANEL DE CONTROL (TU HOJA BLANCA DE ADMIN) ---
@app.route('/admin_hector', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = float(request.form['precio'])
        imagen = request.form['imagen']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO productos (nombre, precio, imagen) VALUES (%s, %s, %s)',
                    (nombre, precio, imagen))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin'))
    
    # Este diseño hará que se vea como una hoja profesional en tu cel
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background-color: #f0f2f5; margin: 0; padding: 15px; font-family: sans-serif; }
            .hoja { background: white; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 100%; max-width: 400px; margin: auto; overflow: hidden; }
            .encabezado { background: #0d1b2a; color: white; padding: 20px; text-align: center; }
            form { padding: 20px; display: flex; flex-direction: column; gap: 15px; }
            label { font-weight: bold; color: #333; }
            input { padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 16px; }
            button { background: #0d1b2a; color: white; border: none; padding: 15px; border-radius: 6px; font-size: 18px; font-weight: bold; }
            .atras { text-align: center; padding: 15px; }
            a { color: #0d1b2a; text-decoration: none; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="hoja">
            <div class="encabezado">
                <h2>Panel Mercado CLN</h2>
                <p>Agrega tus productos</p>
            </div>
            <form action="/admin_hector" method="POST">
                <label>Nombre del Producto:</label>
                <input type="text" name="nombre" placeholder="Ej. Shampoo Negro" required>
                
                <label>Precio (MXN):</label>
                <input type="number" name="precio" placeholder="160" required>
                
                <label>Link de la Imagen:</label>
                <input type="text" name="imagen" placeholder="Pega el link de ImgBB aquí" required>
                
                <button type="submit">Guardar Producto</button>
            </form>
            <div class="atras"><a href="/">← Ver mi Tienda</a></div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
