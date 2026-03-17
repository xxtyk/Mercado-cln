from flask import Flask, request, redirect, url_for
import os

app = Flask(__name__)

# Creamos una lista para guardar los datos
productos = []

@app.route('/')
def inicio():
    lista_html = ""
    for p in productos:
        lista_html += f"<div style='border:1px solid #ddd; padding:15px; margin:10px; background:white; border-radius:10px;'><b>{p['nombre']}</b> - ${p['precio']}</div>"

    return f'''
    <body style="margin:0; background:#f4f4f4; font-family:Arial; text-align:center;">
        <div style="padding:50px;">
            <h1>Mercado en Línea Culiacán</h1>
            <a href="/admin" style="display:inline-block; margin:20px; padding:20px; background:red; color:white; font-weight:bold; text-decoration:none; border-radius:15px;">ENTRAR AL PANEL</a>
            <div style="margin-top:20px;">
                <h3>Catálogo de Productos</h3>
                {lista_html if lista_html else "<p>No hay productos aún</p>"}
            </div>
        </div>
    </body>
    '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        # Aquí es donde recibimos la foto
        foto = request.files.get('foto')

        if nombre and precio:
            # Por ahora lo guardamos sin la foto física para que no falle en Render
            # pero ya te deja seleccionarla
            productos.append({'nombre': nombre, 'precio': precio})
            return redirect(url_for('inicio'))

    return '''
    <body style="font-family: Arial; text-align: center; background: #eef2f3; padding: 30px;">
        <div style="background: white; padding: 25px; border-radius: 15px; max-width: 400px; margin: 0 auto;">
            <h3>Agregar Nuevo Producto</h3>
            <form method="POST" enctype="multipart/form-data">
                <p>Nombre del Producto:</p>
                <input type="text" name="nombre" required style="width:90%; padding:10px; margin-bottom:15px;">
                <p>Precio:</p>
                <input type="number" name="precio" required style="width:90%; padding:10px; margin-bottom:15px;">

                <p>Foto del Producto:</p>
                <input type="file" name="foto" style="width:90%; padding:10px; margin-bottom:20px;">

                <button type="submit" style="background:#27ae60; color:white; border:none; padding:15px; border-radius:5px; width:100%; font-weight:bold;">SUBIR PRODUCTO</button>
            </form>
        </div>
        <br><a href="/">← Volver a la Tienda</a>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
