from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# Aquí guardaremos los productos temporalmente para que los veas
productos = []

@app.route('/')
def inicio():
    lista_html = ""
    for p in productos:
        lista_html += f"<div style='border:1px solid #ddd; padding:10px; margin:10px; background:white; border-radius:10px;'><b>{p['nombre']}</b> - ${p['precio']}</div>"

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
        # ESTO ES LO QUE HACE QUE EL BOTÓN FUNCIONE
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        if nombre and precio:
            productos.append({'nombre': nombre, 'precio': precio})
            return redirect(url_for('inicio')) # Te manda a la tienda para que veas el producto

    return '''
    <body style="font-family: Arial; text-align: center; background: #eef2f3; padding: 30px;">
        <div style="background: white; padding: 25px; border-radius: 15px; max-width: 400px; margin: 0 auto;">
            <h3>Agregar Nuevo Producto</h3>
            <form method="POST">
                <p>Nombre del Producto:</p>
                <input type="text" name="nombre" required style="width:90%; padding:10px; margin-bottom:15px;">
                <p>Precio:</p>
                <input type="number" name="precio" required style="width:90%; padding:10px; margin-bottom:15px;">
                <button type="submit" style="background:#27ae60; color:white; border:none; padding:15px; border-radius:5px; width:100%; font-weight:bold; cursor:pointer;">SUBIR PRODUCTO</button>
            </form>
        </div>
        <br><a href="/">← Volver a la Tienda</a>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
