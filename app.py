from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# --- BASE DE DATOS INICIAL (Se edita desde el panel) ---
productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "imagen": "", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "imagen": "", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "imagen": "", "cat": "Electro"},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200, "imagen": "", "cat": "Hogar"}
]

# --- VISTA: MENÚ DEL DUEÑO (Héctor) ---
HTML_MENU_DUENO = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; background: #f0f2f5; padding: 20px; text-align: center; }
        .opcion { background: white; padding: 20px; margin-bottom: 15px; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: block; text-decoration: none; color: black; font-weight: bold; border: 1px solid #ddd; }
        .icon { font-size: 2em; display: block; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h2>Gestión Mercado CLN</h2>
    <p>Panel de Control - Héctor</p>
    <hr>
    <a href="/tienda" class="opcion"><span class="icon">👁️</span> Ver catálogo (Cliente)</a>
    <a href="/admin_productos" class="opcion"><span class="icon">📦</span> Gestionar productos y fotos</a>
    <a href="/admin_categorias" class="opcion"><span class="icon">📂</span> Gestionar categorías</a>
</body>
</html>
'''

# --- VISTA: GESTIÓN DE PRODUCTOS ---
HTML_GESTION = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; padding: 15px; background: #eee; }
        .card { background: white; padding: 15px; margin-bottom: 10px; border-radius: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 10px; margin: 5px 0 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #000; color: white; border: none; border-radius: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <h3>📦 Editar Productos</h3>
    <a href="/">← Volver al Menú</a>
    <hr>
    {% for p in lista %}
    <div class="card">
        <form action="/update/{{ p.id }}" method="POST">
            <label><small>Nombre:</small></label>
            <input type="text" name="n" value="{{ p.nombre }}">
            <label><small>Precio ($):</small></label>
            <input type="number" name="p" value="{{ p.precio }}">
            <label><small>Link de la Imagen (URL):</small></label>
            <input type="text" name="img" value="{{ p.imagen }}" placeholder="https://link-de-la-foto.jpg">
            <button type="submit">Guardar Cambios</button>
        </form>
    </div>
    {% endfor %}
</body>
</html>
'''

# --- VISTA: TIENDA DEL CLIENTE (2 COLUMNAS) ---
HTML_TIENDA = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Mercado CLN</title>
    <style>
        body { font-family: sans-serif; margin: 0; background: #f4f4f4; padding-bottom: 80px; }
        header { background: #fff; padding: 10px; text-align: center; border-bottom: 1px solid #ddd; position: sticky; top: 0; z-index: 100; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 8px; }
        .card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .card img { width: 100%; height: 140px; object-fit: cover; background: #eee; }
        .info { padding: 8px; }
        .nombre { font-size: 0.85em; font-weight: bold; height: 32px; overflow: hidden; }
        .precio { font-size: 1.1em; font-weight: 900; }
        .btn-add { background: #000; color: #fff; border: none; padding: 8px; width: 100%; border-radius: 6px; margin-top: 5px; }
        #cart-bar { position: fixed; bottom: 15px; left: 5%; width: 90%; background: #25d366; color: white; padding: 15px; border-radius: 30px; text-align: center; display: none; z-index: 1000; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <h2 style="margin:0; font-size: 1.1em;">Mercado CLN</h2>
        <p style="margin:0; font-size: 0.7em; color: gray;">Culiacán • Pago Contra Entrega</p>
    </header>
    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}" onerror="this.src='https://via.placeholder.com/150?text=Sin+Foto'">
            <div class="info">
                <div class="nombre">{{ p.nombre }}</div>
                <div class="precio">${{ p.precio }}</div>
                <button class="btn-add" onclick="add()">+</button>
            </div>
        </div>
        {% endfor %}
    </div>
    <div id="cart-bar">VER PEDIDO</div>
    <script>
        function add() { document.getElementById('cart-bar').style.display = 'block'; }
    </script>
</body>
</html>
'''

@app.route('/')
def menu(): return render_template_string(HTML_MENU_DUENO)

@app.route('/admin_productos')
def admin_p(): return render_template_string(HTML_GESTION, lista=productos)

@app.route('/tienda')
def tienda(): return render_template_string(HTML_TIENDA, lista=productos)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    productos[id]['nombre'] = request.form['n']
    productos[id]['precio'] = int(request.form['p'])
    productos[id]['imagen'] = request.form['img']
    return redirect(url_for('admin_p'))

@app.route('/admin_categorias')
def admin_c(): return "Sección de categorías (Próximamente)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
