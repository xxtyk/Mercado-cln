import os
from flask import Flask, render_template, render_template_string, request, redirect


app = Flask(__name__)

# ESTA ES TU LISTA DE PRODUCTOS
productos = [
    {"nombre": "Champú de Jengibre", "precio": 150, "desc": "Cuidado natural para tu cabello."},
    {"nombre": "Minisplit Mirage 1.5T", "precio": 8500, "desc": "Aire acondicionado 220V."},
    {"nombre": "Boiler de Paso", "precio": 3200, "desc": "Agua caliente al instante."},
    {"nombre": "Cable Uso Rudo 2x14", "precio": 25, "desc": "Precio por metro."}
]

@app.route('/')
def tienda():
    html = '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mercado en Línea Culiacán</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; }
            header { background: #1a73e8; color: white; padding: 20px; text-align: center; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; padding: 20px; }
            .card { background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; }
            .precio { color: #d93025; font-size: 1.5rem; font-weight: bold; margin: 15px 0; }
            .btn-comprar { background: #25d366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 30px; font-weight: bold; display: inline-block; }
        </style>
    </head>
    <body>
        <header>
            <h1>🛒 Mercado en Línea Culiacán</h1>
            <p>Calidad y confianza en cada entrega</p>
        </header>
        <div class="grid">
            {% for p in lista %}
            <div class="card">
               <div class="card">
    <img src="{{ p.imagen }}" style="width:100%; height:200px; object-fit:cover; border-radius:10px; margin-bottom:10px;">
    
    <h3>{{ p.nombre }}</h3>
    <p>{{ p.desc }}</p>
    ...

                <h3>{{ p.nombre }}</h3>
                <p>{{ p.desc }}</p>
                <div class="precio">${{ p.precio }}</div>
                <a href="https://wa.me/526671234567?text=Hola,%20me%20interesa%20el%20{{ p.nombre }}" class="btn-comprar">Pedir por WhatsApp</a>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    '''
    return render_template_string(html, lista=productos)

@app.route('/admin')
def admin():
    # Este es tu Modo Configuración
    html_admin = '''
    <html>
    <head><title>Configuración Mercado CLN</title></head>
    <body style="font-family:sans-serif; padding:20px;">
        <h2>⚙️ Modo Configuración - Héctor</h2>
        <a href="/">Ir a ver la tienda</a>
        <hr>
        {% for p in lista %}
        <div style="border:1px solid #ccc; padding:10px; margin-bottom:10px;">
            <p><strong>Producto:</strong> {{ p.nombre }}</p>
            <form action="/update" method="POST">
                <input type="hidden" name="id" value="{{ loop.index0 }}">
                Nombre: <input type="text" name="nombre" value="{{ p.nombre }}"><br><br>
                Precio: <input type="text" name="precio" value="{{ p.precio }}"><br><br>
                Foto (Link): <input type="text" name="imagen" value="{{ p.imagen }}"><br><br>
                <button type="submit" style="background:green; color:white;">Guardar Cambios</button>
            </form>
        </div>
        {% endfor %}
    </body>
    </html>
    '''
    return render_template_string(html_admin, lista=productos)

@app.route('/update', methods=['POST'])
def update():
    idx = int(request.form.get('id'))
    productos[idx]['nombre'] = request.form.get('nombre')
    productos[idx]['precio'] = request.form.get('precio')
    productos[idx]['imagen'] = request.form.get('imagen')
    return redirect('/admin')
