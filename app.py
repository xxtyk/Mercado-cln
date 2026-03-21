from flask import Flask, render_template, request, redirect, session, jsonify
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "hector_cln_2026"

# TU NUEVA LLAVE DE LA BASE DE DATOS
DATABASE_URL = "postgresql://mercado_db_dcie_user:5MXf0RlYpfLs9Cjokjmttgop44auKfuV@dpg-d6v3vkk50q8c739drkd0-a/mercado_db_dcie"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Crear la tabla de productos automáticamente si no existe
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            precio FLOAT NOT NULL,
            imagen TEXT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT nombre, precio, imagen FROM productos ORDER BY id DESC')
    rows = cur.fetchall()
    productos = [{"nombre": r[0], "precio": r[1], "imagen": r[2]} for r in rows]
    cur.close()
    conn.close()
    return render_template('index.html', productos=productos)

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
        return redirect('/admin_hector')
    return render_template('admin.html') # Asegúrate de tener este archivo en templates

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
