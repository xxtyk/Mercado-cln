from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE TU MARCA (SINALOA STYLE) ---
# Cambia esta URL por la de tu logo real
LOGO_URL = "https://tu-link-de-postimages.jpg" 

# --- PALETA DE COLORES (EXTRAÍDA DE TU LOGO) ---
COLOR_FONDO = "#000000"       # Fondo Negro Absoluto
COLOR_ACENTO = "#00E5FF"      # Azul Cyan (Flechas claras)
COLOR_TEXTO = "#FFFFFF"       # Texto Blanco Puro
COLOR_SECUNDARIO = "#607D8B"  # Gris Azulado (Flechas oscuras)

productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "imagen": "", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "imagen": "", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "imagen": "", "cat": "Electro"},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200, "imagen": "", "cat": "Hogar"}
]

# --- VISTA DE LA APLICACIÓN (TIENDA CON TUS COLORES) ---
HTML_APP = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="''' + COLOR_FONDO + '''">
    <title>Mercado CLN</title>
    <style>
        /* Pantalla de Carga (Splash) con fondo negro y tu logo */
        #splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: ''' + COLOR_FONDO + '''; color: ''' + COLOR_TEXTO + '''; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 5000;
        }
        #splash img { max-width: 200px; margin-bottom: 20px; }
        
        /* Estilos Generales */
        body { font-family: sans-serif; margin: 0; background: ''' + COLOR_FONDO + '''; color: ''' + COLOR_TEXTO + '''; padding-top: 60px; padding-bottom: 80px; }
        
        /* BARRA DE DESCARGA PERMANENTE (Estilo Premium) */
        #top-install-bar {
            position: fixed; top: 0; left: 0; width: 100%; height: 60px;
            background: ''' + COLOR_FONDO + '''; color: ''' + COLOR_TEXTO + '''; display: flex; 
            justify-content: center; align-items: center; z-index: 1000;
            border-bottom: 2px solid ''' + COLOR_ACENTO + '''; font-weight: bold; font-size: 0.85em;
            text-align: center; cursor: pointer;
        }
        #top-install-bar span { margin-right: 10px; }
        .btn-install { background: ''' + COLOR_ACENTO + '''; color: ''' + COLOR_FONDO + '''; border: none; padding: 8px 12px; border-radius: 5px; font-weight: bold; }

        /* Tienda */
        header { background: ''' + COLOR_FONDO + '''; padding: 15px; text-align: center; border-bottom: 1px solid ''' + COLOR_SECUNDARIO + '''; }
        header img { height: 50px; margin-bottom: 5px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: ''' + COLOR_FONDO + '''; border-radius: 12px; overflow: hidden; border: 1px solid ''' + COLOR_SECUNDARIO + '''; box-shadow: 0 2px 10px rgba(0, 229, 255, 0.1); }
        .card img { width: 100%; height: 160px; object-fit: cover; border-bottom: 1px solid ''' + COLOR_SECUNDARIO + '''; }
        .info { padding: 10px; }
        .nombre { font-size: 0.9em; height: 35px; color: ''' + COLOR_TEXTO + '''; }
        .precio { font-weight: bold; font-size: 1.2em; color: ''' + COLOR_ACENTO + '''; }
        .btn-add { background: ''' + COLOR_ACENTO + '''; color: ''' + COLOR_FONDO + '''; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; margin-top: 10px; cursor: pointer; }
        
        /* Barra de WhatsApp (Estilo Premium) */
        #cart-bar { position: fixed; bottom: 20px; left: 5%; width: 90%; background: #25d366; color: white; padding: 18px; border-radius: 35px; text-align: center; font-weight: bold; display: none; box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4); z-index: 1000; cursor: pointer; }
    </style>
</head>
<body onload="initApp()">

    <div id="splash">
        <img src="''' + LOGO_URL + '''" alt="Mercado CLN Logo">
        <p>Cargando Mercado CLN...</p>
    </div>

    <div id="top-install-bar" onclick="installApp()">
        <span>Descarga la aplicación para pedidos más fáciles</span>
        <button class="btn-install">INSTALAR</button>
    </div>

    <header>
        <img src="''' + LOGO_URL + '''" alt="Mercado CLN">
        <h2 style="margin:0; font-size: 1.2em; color: ''' + COLOR_TEXTO + ''';">Mercado en Línea</h2>
        <small style="color: ''' + COLOR_SECUNDARIO + ''';">Culiacán • Pago Contra Entrega</small>
    </header>

    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}" onerror="this.src='https://via.placeholder.com/150?text=Cargando...'">
            <div class="info">
                <div class="nombre">{{ p.nombre }}</div>
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

        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
        });

        function installApp() {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then((choiceResult) => {
                    if (choiceResult.outcome === 'accepted') {
                        document.getElementById('top-install-bar').style.display = 'none';
                    }
                });
            } else {
                alert("Para instalar: Pica en los 3 puntos de tu navegador y selecciona 'Instalar aplicación' o 'Agregar a pantalla de inicio'.");
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home(): return render_template_string(HTML_APP, lista=productos)

@app.route('/manifest.json')
def manifest():
    return {
        "name": "Mercado CLN",
        "short_name": "Mercado",
        "start_url": "/",
        "display": "standalone",
        "background_color": COLOR_FONDO,
        "theme_color": COLOR_ACENTO,
        "icons": [{"src": LOGO_URL, "sizes": "512x512", "type": "image/png"}]
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
