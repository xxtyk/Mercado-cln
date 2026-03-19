from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# --- BASE DE DATOS DE PRODUCTOS ---
productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "imagen": "https://m.media-amazon.com/images/I/71XGZ-U5f-L._SL1500_.jpg", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "imagen": "https://m.media-amazon.com/images/I/61S7I6-fU6L._SL1000_.jpg", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "imagen": "https://m.media-amazon.com/images/I/41uS859S3bL._AC_SL1000_.jpg", "cat": "Electro"},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200, "imagen": "https://m.media-amazon.com/images/I/51p0vX1v1SL._AC_SL1000_.jpg", "cat": "Hogar"}
]

HTML_TIENDA = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Mercado CLN</title>
    <style>
        body { font-family: -apple-system, sans-serif; margin: 0; background: #f4f4f4; color: #333; overflow-x: hidden; }
        header { background: #fff; padding: 10px; text-align: center; border-bottom: 1px solid #ddd; position: sticky; top: 0; z-index: 100; }
        
        /* DISEÑO DE 2 COLUMNAS PARA CELULAR */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 8px; }
        .card { background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; }
        .card img { width: 100%; height: 140px; object-fit: cover; background: #eee; }
        .info { padding: 8px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .nombre { font-size: 0.85em; font-weight: bold; margin-bottom: 4px; height: 32px; overflow: hidden; }
        .precio { font-size: 1.1em; font-weight: 900; color: #000; }
        .btn-add { background: #000; color: #fff; border: none; padding: 8px; width: 100%; border-radius: 6px; font-weight: bold; margin-top: 5px; }

        /* BOTÓN DE CONFIGURACIÓN FLOTANTE (PARA QUE NO SE PIERDA) */
        .admin-fab { position: fixed; top: 10px; right: 10px; background: #fff; border: 1px solid #ddd; border-radius: 50%; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; text-decoration: none; z-index: 200; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }

        #carrito-barra { position: fixed; bottom: 15px; left: 5%; width: 90%; background: #25d366; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; display: none; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        
        #pantalla-pago { display: none; background: #fff; min-height: 100vh; padding: 15px; }
        input, select { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .resumen { background: #f9f9f9; padding: 12px; border-radius: 8px; margin: 15px 0; border: 1px solid #eee; }
    </style>
</head>
<body>

<div id="tienda">
    <header>
        <a href="/admin" class="admin-fab">⚙️</a>
        <h2 style="margin:0; font-size: 1.2em;">Mercado CLN</h2>
        <p style="margin:0; font-size: 0.75em; color: #777;">Culiacán • Pago Contra Entrega</p>
    </header>

    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}" onerror="this.src='https://via.placeholder.com/150?text=Cargando...'">
            <div class="info">
                <div class="nombre">{{ p.nombre }}</div>
                <div class="precio">${{ p.precio }}</div>
                <button class="btn-add" onclick="agregar('{{ p.nombre }}', {{ p.precio }})">+</button>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<div id="pantalla-pago">
    <button onclick="cerrar()" style="background:none; border:none; color:#007bff; font-size:16px; padding:0;">← Atrás</button>
    <h3>Finalizar Pedido</h3>
    <div id="lista-items" style="font-size: 0.9em;"></div>
    <div class="resumen">
        <div style="display:flex; justify-content:space-between;"><span>Subtotal:</span><span id="sub-val">$0</span></div>
        <div style="display:flex; justify-content:space-between;"><span>Envío:</span><span id="env-val">$0</span></div>
        <hr>
        <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.2em;"><span>Total:</span><span id="tot-val">$0</span></div>
    </div>
    <input type="text" id="nom" placeholder="Tu nombre completo">
    <input type="text" id="ubi" placeholder="Calle, número y colonia">
    <input type="tel" id="whatsapp" placeholder="Tu WhatsApp">
    <select id="metodo" onchange="renderizar()">
        <option value="0">Pasar por él ($0)</option>
        <option value="40">Envío a domicilio (+$40)</option>
    </select>
    <button onclick="enviar()" style="width:100%; padding:16px; background:#25d366; color:white; border:none; border-radius:12px; font-weight:bold; font-size:1.1em; margin-top:10px;">ENVIAR AL GRUPO</button>
</div>

<div id="carrito-barra" onclick="abrirPago()">
    CARRITO (<span id="count">0</span>) • <span id="total-b">$0</span>
</div>

<script>
let cart = [];
function agregar(n, p) {
    cart.push({n, p});
    document.getElementById('carrito-barra').style.display = 'block';
    document.getElementById('count').innerText = cart.length;
    let total = cart.reduce((s, i) => s + i.p, 0);
    document.getElementById('total-b').innerText = '$' + total;
}
function abrirPago() {
    document.getElementById('tienda').style.display='none';
    document.getElementById('pantalla-pago').style.display='block';
    document.getElementById('nom').value = localStorage.getItem('h_n') || '';
    document.getElementById('ubi').value = localStorage.getItem('h_u') || '';
    document.getElementById('whatsapp').value = localStorage.getItem('h_w') || '';
    renderizar();
}
function cerrar() {
    document.getElementById('tienda').style.display='block';
    document.getElementById('pantalla-pago').style.display='none';
}
function renderizar() {
    let sub = cart.reduce((s, i) => s + i.p, 0);
    let env = parseInt(document.getElementById('metodo').value);
    document.getElementById('sub-val').innerText = '$' + sub;
    document.getElementById('env-val').innerText = '$' + env;
    document.getElementById('tot-val').innerText = '$' + (sub + env);
    let itemsHtml = cart.map(i => `<div style="display:flex; justify-content:space-between; margin-bottom:4px;"><span>${i.n}</span><span>$${i.p}</span></div>`).join('');
    document.getElementById('lista-items').innerHTML = itemsHtml;
}
function enviar() {
    let n = document.getElementById('nom').value;
    let u = document.getElementById('ubi').value;
    let w = document.getElementById('whatsapp').value;
    let e = document.getElementById('metodo').value == "40" ? "DOMICILIO" : "RECOGER";
    if(!n || !u || !w) return alert("Rellena tus datos");
    localStorage.setItem('h_n', n); localStorage.setItem('h_u', u); localStorage.setItem('h_w', w);
    let prod = cart.map(i => "- " + i.n).join("%0A");
    let msg = `*NUEVO PEDIDO*%0A*Cliente:* ${n}%0A*Dirección:* ${u}%0A*Entrega:* ${e}%0A%0A*PRODUCTOS:*%0A${prod}%0A%0A*TOTAL: ${document.getElementById('tot-val').innerText}*`;
    window.open("https://chat.whatsapp.com/HtBWXyZmMAxJImgPY5SRXU?text=" + msg);
}
</script>
</body>
</html>
'''

# --- PANEL ADMIN ---
HTML_ADMIN = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; padding: 15px; background: #eee; }
        .item { background: white; padding: 10px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        input { width: 100%; padding: 8px; margin: 4px 0; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background: #000; color: white; border: none; border-radius: 5px; margin-top: 5px; }
    </style>
</head>
<body>
    <h3>⚙️ Configuración</h3>
    <a href="/">← Volver a la tienda</a>
    <hr>
    {% for p in lista %}
    <div class="item">
        <form action="/edit/{{ p.id }}" method="POST">
            <input type="text" name="n" value="{{ p.nombre }}">
            <input type="number" name="p" value="{{ p.precio }}">
            <button type="submit">Guardar Cambios</button>
        </form>
    </div>
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def index(): return render_template_string(HTML_TIENDA, lista=productos)

@app.route('/admin')
def admin(): return render_template_string(HTML_ADMIN, lista=productos)

@app.route('/edit/<int:id>', methods=['POST'])
def edit(id):
    productos[id]['nombre'] = request.form['n']
    productos[id]['precio'] = int(request.form['p'])
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
