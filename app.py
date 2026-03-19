from flask import Flask, render_template_string, request, redirect
import os

app = Flask(__name__)

# --- TU LISTA DE PRODUCTOS ---
productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "desc": "Reparación total 1L", "imagen": "https://m.media-amazon.com/images/I/71XGZ-U5f-L._SL1500_.jpg", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "desc": "2 piezas jengibre", "imagen": "https://m.media-amazon.com/images/I/61S7I6-fU6L._SL1000_.jpg", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "desc": "1.5 Toneladas", "imagen": "https://m.media-amazon.com/images/I/41uS859S3bL._AC_SL1000_.jpg", "cat": "Electro"},
]

HTML_TIENDA = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mercado en Línea Culiacán</title>
    <style>
        body { font-family: sans-serif; margin: 0; background: #f4f4f4; padding-bottom: 80px; }
        header { background: #000; color: white; padding: 15px; text-align: center; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: white; border-radius: 8px; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); position: relative; }
        .card img { width: 100%; height: 150px; object-fit: cover; border-radius: 5px; }
        .precio { font-weight: bold; color: #d93025; font-size: 1.2em; margin: 5px 0; }
        .btn-add { background: #333; color: white; border: none; padding: 8px; width: 100%; border-radius: 5px; cursor: pointer; }
        
        /* Carrito flotante */
        #carrito-barra { position: fixed; bottom: 0; width: 100%; background: #25d366; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 1.1em; cursor: pointer; display: none; }
        
        /* Formulario final */
        #seccion-pago { display: none; padding: 20px; background: white; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
    </style>
</head>
<body>

<header>
    <h1>🛒 Mercado CLN</h1>
    <small>Culiacán, Sinaloa</small>
</header>

<div id="tienda">
    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}">
            <h4 style="margin: 5px 0;">{{ p.nombre }}</h4>
            <p class="precio">${{ p.precio }}</p>
            <button class="btn-add" onclick="agregar('{{ p.nombre }}', {{ p.precio }})">Añadir +</button>
        </div>
        {% endfor %}
    </div>
</div>

<div id="seccion-pago">
    <button onclick="cerrarPago()" style="background:none; border:none; color:blue;">⬅️ Volver</button>
    <h3>Finalizar Pedido</h3>
    <div id="lista-carrito"></div>
    <hr>
    <label>Nombre y Apellidos:</label>
    <input type="text" id="nombre" placeholder="Tu nombre...">
    <label>Dirección y Colonia:</label>
    <input type="text" id="dir" placeholder="Calle, número y colonia...">
    <label>WhatsApp:</label>
    <input type="tel" id="tel" placeholder="667...">
    <label>Tipo de Entrega:</label>
    <select id="envio" onchange="calcularTotal()">
        <option value="0">Pasar a recoger ($0)</option>
        <option value="40">Envío a domicilio (+$40)</option>
    </select>
    <h2 id="total-txt">Total: $0</h2>
    <button onclick="mandarWhatsApp()" style="width:100%; padding:15px; background:#25d366; color:white; border:none; border-radius:10px; font-weight:bold; font-size:1.1em;">ENVIAR FICHA AL GRUPO</button>
</div>

<div id="carrito-barra" onclick="verPago()">
    Ver Carrito: <span id="cant-items">0</span> | <span id="total-barra">$0</span>
</div>

<script>
let carrito = [];
let totalBase = 0;

function agregar(nombre, precio) {
    carrito.push({nombre, precio});
    totalBase += precio;
    document.getElementById('carrito-barra').style.display = 'block';
    document.getElementById('cant-items').innerText = carrito.length;
    document.getElementById('total-barra').innerText = '$' + totalBase;
}

function verPago() {
    document.getElementById('tienda').style.display = 'none';
    document.getElementById('seccion-pago').style.display = 'block';
    document.getElementById('carrito-barra').style.display = 'none';
    
    // Autorelleno
    if(localStorage.getItem('h_nombre')) {
        document.getElementById('nombre').value = localStorage.getItem('h_nombre');
        document.getElementById('dir').value = localStorage.getItem('h_dir');
        document.getElementById('tel').value = localStorage.getItem('h_tel');
    }
    calcularTotal();
}

function cerrarPago() {
    document.getElementById('tienda').style.display = 'block';
    document.getElementById('seccion-pago').style.display = 'none';
    document.getElementById('carrito-barra').style.display = 'block';
}

function calcularTotal() {
    let envio = parseInt(document.getElementById('envio').value);
    document.getElementById('total-txt').innerText = 'Total: $' + (totalBase + envio);
}

function mandarWhatsApp() {
    let n = document.getElementById('nombre').value;
    let d = document.getElementById('dir').value;
    let t = document.getElementById('tel').value;
    let e = document.getElementById('envio').value == "40" ? "Envío a domicilio" : "Pasa a recoger";
    let tot = document.getElementById('total-txt').innerText;

    // Guardar para la próxima vez
    localStorage.setItem('h_nombre', n);
    localStorage.setItem('h_dir', d);
    localStorage.setItem('h_tel', t);

    let items = carrito.map(i => "- " + i.nombre).join("%0A");
    let mensaje = `*NUEVO PEDIDO*%0A*Cliente:* ${n}%0A*Dir:* ${d}%0A*Tel:* ${t}%0A*Entrega:* ${e}%0A%0A*PRODUCTOS:*%0A${items}%0A%0A*${tot}*%0A(Pago contra entrega)`;
    
    // Aquí pon TU número de WhatsApp
    window.open("https://wa.me/526671234567?text=" + mensaje);
}
</script>
</body>
</html>
'''

@app.route('/')
def tienda():
    return render_template_string(HTML_TIENDA, lista=productos)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
