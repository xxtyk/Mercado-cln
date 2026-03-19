from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# --- TU LOGOTIPO Y COLORES ---
# Reemplaza esta URL con el enlace directo de tu logo (el que termina en .jpg)
LOGO_URL = "https://tu-link-de-postimages.jpg" 

productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "imagen": "", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "imagen": "", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "imagen": "", "cat": "Electro"},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200, "imagen": "", "cat": "Hogar"}
]

# --- VISTA DE LA APLICACIÓN (TIENDA) ---
HTML_APP = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#000000">
    <title>Mercado CLN</title>
    <style>
        /* Pantalla de Carga (Splash) */
        #splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; color: white; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 5000;
        }
        #splash img { max-width: 200px; margin-bottom: 20px; }
        
        /* Banner de Descarga */
        #install-banner {
            background: #000; color: #fff; padding: 15px; text-align: center;
            font-size: 0.9em; border-bottom: 2px solid #0056b3; display: none;
        }
        #install-btn {
            background: #0056b3; color: white; border: none; padding: 8px 15px;
            border-radius: 5px; font-weight: bold; margin-top: 10px; cursor: pointer;
        }

        body { font-family: sans-serif; margin: 0; background: #f4f4f4; padding-bottom: 80px; }
        header { background: #fff; padding: 15px; text-align: center; border-bottom: 1px solid #ddd; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .card img { width: 100%; height: 160px; object-fit: cover; }
        .info { padding: 10px; }
        .precio { font-weight: bold; font-size: 1.2em; color: #000; }
        .btn-add { background: #000; color: #fff; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; margin-top: 10px; }
        
        #cart-bar { position: fixed; bottom: 20px; left: 5%; width: 90%; background: #25d366; color: white; padding: 18px; border-radius: 35px; text-align: center; font-weight: bold; display: none; box-shadow: 0 5px 15px rgba(0,0,0,0.3); z-index: 1000; }
    </style>
</head>
<body onload="initApp()">

    <div id="splash">
        <img src="''' + LOGO_URL + '''" alt="Logo">
        <p>Cargando Mercado CLN...</p>
    </div>

    <div id="install-banner">
        <div>Descarga la aplicación para que los pedidos sean más fácil</div>
        <button id="install-btn">DESCARGAR APLICACIÓN</button>
    </div>

    <header>
        <img src="''' + LOGO_URL + '''" style="height: 40px; margin-bottom: 5px;">
        <h2 style="margin:0; font-size: 1.2em;">Mercado en Línea</h2>
        <small style="color: #666;">Culiacán • Pago Contra Entrega</small>
    </header>

    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}" onerror="this.src='https://via.placeholder.com/150?text=Sin+Foto'">
            <div class="info">
                <div style="font-size: 0.9em; height: 35px; color: #444;">{{ p.nombre }}</div>
                <div class="precio">${{ p.precio }}</div>
                <button class="btn-add" onclick="addToCart()">AGREGAR</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="cart-bar" onclick="sendWhatsApp()">ENVIAR PEDIDO POR WHATSAPP</div>

    <script>
        function initApp() {
            setTimeout(() => { document.getElementById('splash').style.display = 'none'; }, 2000);
        }

        function addToCart() {
            document.getElementById('cart-bar').style.display = 'block';
        }

        function sendWhatsApp() {
            window.location.href = "https://wa.me/526671377298?text=Hola Hector, quiero hacer un pedido.";
        }

        // Lógica de Instalación
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            document.getElementById('install-banner').style.display = 'block';
        });

        document.getElementById('install-btn').addEventListener('click', () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        document.getElementById('install-banner').style.display = 'none';
                    }
                });
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_APP, lista=productos)

# --- ARCHIVOS NECESARIOS PARA LA INSTALACIÓN ---
@app.route('/manifest.json')
def manifest():
    return {
        "name": "Mercado CLN",
        "short_name": "Mercado",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",
        "icons": [{"src": LOGO_URL, "sizes": "512x512", "type": "image/png"}]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
