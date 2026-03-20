import os
import sqlite3
import cloudinary
import cloudinary.uploader
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDINARY ---
# Render leerá automáticamente la variable CLOUDINARY_URL que configuraste en su panel
cloudinary.config(secure=True)

# --- BASE DE DATOS (PARA QUE NO SE BORREN LOS PRODUCTOS) ---
def init_db():
    conn = sqlite3.connect('datos.db')
    cursor = conn.cursor()
    # Tabla de productos
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, precio TEXT, categoria TEXT, foto TEXT)''')
    # Tabla de categorías
    cursor.execute('''CREATE TABLE IF NOT EXISTS categorias 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, foto TEXT)''')
    # Tabla de configuración (Logo y Nombre)
    cursor.execute('''CREATE TABLE IF NOT EXISTS config 
                      (id INTEGER PRIMARY KEY, logo TEXT, nombre_tienda TEXT)''')
    
    # Valores iniciales si la tabla está vacía
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

# --- RUTAS DE LA TIENDA ---

@app.route('/')
def tienda():
    conn = sqlite3.connect('datos.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    categorias = cursor.execute("SELECT * FROM categorias").fetchall()
    productos = cursor.execute("SELECT * FROM productos").fetchall()
    config = cursor.execute("SELECT * FROM config WHERE id=1").fetchone()
    conn.close()

    contenido_catalogo = ""
    for cat in categorias:
        prods_cat = [p for p in productos if p['categoria'] == cat['nombre']]
        if prods_cat:
            contenido_catalogo += f'''
            <div style="margin-top:40px; text-align:left; padding: 0 10px;">
                <div style="display:flex; align-items:center; border-bottom:2px solid #00f2ff; padding-bottom:10px; margin-bottom:20px;">
                    <img src="{cat['foto']}" style="width:50px; height:50px; border-radius:50%; object-fit:cover; margin-right:15px; border:2px solid #00f2ff;">
                    <h2 style="color:#00f2ff; margin:0; text-transform:uppercase; font-size:1.2rem;">{cat['nombre']}</h2>
                </div>'''
            for p in prods_cat:
                contenido_catalogo += f'''
                <div style="background:#1a1a1a; padding:15px; border-radius:15px; border:1px solid #333; margin-bottom:20px;">
                    <img src="{p['foto']}" style="width:100%; border-radius:10px; margin-bottom:10px; max-height:300px; object-fit:cover;">
                    <h3 style="color:#fff; margin:0;">{p['nombre']}</h3>
                    <p style="color:#00f2ff; font-weight:bold; font-size:2
