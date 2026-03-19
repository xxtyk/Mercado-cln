from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# --- TU LISTA DE PRODUCTOS (Cámbialos cuando quieras) ---
productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "desc": "Reparación 1L", "imagen": "https://m.media-amazon.com/images/I/71XGZ-U5f-L._SL1500_.jpg", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "desc": "Jengibre 2 pzas", "imagen": "https://m.media-amazon.com/images/I/61S7I6-fU6L._SL1000_.jpg", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "desc": "1.5 Toneladas", "imagen": "https://m.media-amazon.com/images/I/41uS859S3bL._AC_SL1000_.jpg", "cat": "Electro"},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200, "desc": "Automático", "imagen": "https://m.media-amazon.com/images/I/51p0vX1v1SL._AC_SL1000_.jpg", "cat": "Hogar"}
]

HTML_TIENDA = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mercado en Línea Culiacán</title>
    <style>
        body { font-family: sans-serif; margin: 0; background: #f8f9fa; color: #333; }
        header { background: #fff; padding: 15px; text-align: center; border-bottom: 1px solid #ddd; position: sticky; top: 0; z-index: 100; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; }
        .card img { width: 100%; height: 160px; object-fit: cover; }
        .info { padding: 10px; }
        .precio { font-size: 1.1em; font-weight: bold; color: #222; margin: 5px 0; }
        .btn-add { background: #000; color: #fff; border: none; padding: 10px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
        
        #carrito-flotante { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; background: #000; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; display: none; z-index: 1000; }
        
        #pantalla-pago { display: none; background: #fff; min-height: 100vh; padding: 20px; box-sizing: border-box; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; font-size: 16px; box-sizing: border-box; }
        .resumen { background: #f1f1f1; padding: 15px; border-radius: 10px; margin: 20px 0; }
    </style>
</head>
<body>

<div id="pantalla-tienda">
    <header>
        <h2 style="margin:0;">Mercado CLN</h2>
        <p style="margin:0; font-size:0.8em; color:gray;">Culiacán • Pago Contra Entrega</p>
    </header>
    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}">
            <div class="info">
                <div style="font-size:0.8em; color:#666;">{{ p.cat }}</div>
                <div style="font-weight:bold; height: 35px; overflow: hidden; font-size:0.9em;">{{ p.nombre }}</div>
                <div class="precio">${{ p.precio }}</div>
                <button class="btn-add" onclick="agregarAlCarrito('{{ p.nombre }}', {{ p.precio }})">+</button>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<div id="pantalla-pago">
    <button onclick="irATienda()" style="background:none; border:none; color:#007bff; font-size:16px; margin-bottom:20px;">← Volver</button>
    <h3>Finalizar Pedido</h3>
    <div id="items-pedido"></div>
    
    <div class="resumen">
        <p id="txt-subtotal">Subtotal: $0</p>
        <p id="txt-envio">Envío: $0</p>
        <h2 id="txt-total">Total: $0</h2>
    </div>

    <label><b>Nombre y Apellidos:</b></label>
    <input type="text" id="form-nombre" placeholder="Tu nombre...">
    <label><b>Dirección (Calle, No, Colonia):</b></label>
    <input type="text" id="form-dir" placeholder="Nevado de Colima 186, Villa Bonita...">
    <label><b>WhatsApp:</b></label>
    <input type="tel" id="form-tel" placeholder="667...">
    <label><b>Tipo de Entrega:</b></label>
    <select id="form-envio" onchange="dibujarCarrito()">
        <option value="0">Pasar a recoger ($0)</option>
        <option value="40">Envío a domicilio (+$40)</option>
    </select>

    <button onclick="enviarWhatsApp()" style="width:100%; padding:18px; background:#25d366; color:white; border:none; border-radius:12px; font-size:18px; font-weight:bold; margin-top:10px;">
        FINALIZAR Y ENVIAR AL GRUPO
    </button>
</div>

<div id="carrito-flotante" onclick="irAPago()">
    VER CARRITO • <span id="cart-count">0</span> PRODUCTOS
</div>

<script>
let carrito = [];

function agregarAlCarrito(nombre, precio) {
    carrito.push({nombre, precio});
    document.getElementById('carrito-flotante').style.display = 'block';
    document.getElementById('cart-count').innerText = carrito.length;
}

function irAPago() {
    document.getElementById('pantalla-tienda').style.display = 'none';
    document.getElementById('pantalla-pago').style.display = 'block';
    
    // Autorelleno desde la memoria del celular
    document.getElementById('form-nombre').value = localStorage.getItem('h_nombre') || '';
    document.getElementById('form-dir').value = localStorage.getItem('h_dir') || '';
    document.getElementById('form-tel').value = localStorage.getItem('h_tel') || '';
    
    dibujarCarrito();
}

function irATienda() {
    document.getElementById('pantalla-tienda').style.display = 'block';
    document.getElementById('pantalla-pago').style.display = 'none';
}

function dibujarCarrito() {
    let sub = 0;
    let html = "";
    carrito.forEach(i => {
        html += `<div style="display:flex; justify-content:space-between; margin:5px 0;"><span>${i.nombre}</span> <span>$${i.precio}</span></div>`;
        sub += i.precio;
    });
    let costoEnvio = parseInt(document.getElementById('form-envio').value);
    
    document.getElementById('items-pedido').innerHTML = html;
    document.getElementById('txt-subtotal').innerText = "Subtotal: $" + sub;
    document.getElementById('txt-envio').innerText = "Envío: $" + costoEnvio;
    document.getElementById('txt-total').innerText = "Total: $" + (sub + costoEnvio);
}

function enviarWhatsApp() {
    let nom = document.getElementById('form-nombre').value;
    let dir = document.getElementById('form-dir').value;
    let tel = document.getElementById('form-tel').value;
    let env = document.getElementById('form-envio').value == "40" ? "ENVÍO A DOMICILIO" : "PASA A RECOGER";
    let tot = document.getElementById('txt-total').innerText;

    if(!nom || !dir || !tel) {
        alert("Por favor rellena todos los datos");
        return;
    }

    // Guardar para la siguiente vez
    localStorage.setItem('h_nombre', nom);
    localStorage.setItem('h_dir', dir);
    localStorage.setItem('h_tel', tel);

    let productosTexto = carrito.map(i => "- " + i.nombre).join("%0A");
    let mensaje = `*NUEVO PEDIDO - MERCADO CLN*%0A%0A*Cliente:* ${nom}%0A*Dirección:* ${dir}%0A*Tel:* ${tel}%0A*Entrega:* ${env}%0A%0A*PRODUCTOS:*%0A${productosTexto}%0A%0A*${tot}*%0A_Pago contra entrega_`;
    
    // Enlace al grupo de WhatsApp
    window.open("https://chat.whatsapp.com/HtBWXyZmMAxJImgPY5SRXU?text=" + mensaje);
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
