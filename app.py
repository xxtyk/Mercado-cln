from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE TU MARCA ---
# Usamos url_for para que Flask busque 'logo.png' dentro de la carpeta 'static'
# Si tu archivo se llama diferente (ej: logo.jpg), cámbialo aquí abajo.
NOMBRE_LOGO = "logo.png" 

# --- PALETA DE COLORES ---
COLOR_FONDO = "#000000"       # Fondo Negro
COLOR_ACENTO = "#00E5FF"      # Azul Cyan
COLOR_TEXTO = "#FFFFFF"       # Blanco
COLOR_SECUNDARIO = "#607D8B"  # Gris

productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150, "imagen": "", "cat": "Cabello"},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180, "imagen": "", "cat": "Cabello"},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500, "imagen": "", "cat": "Electro"},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200, "imagen": "", "cat": "Hogar"}
]

HTML_APP = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="{{ color_fondo }}">
    <title>Mercado CLN</title>
    <style>
        #splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: {{ color_fondo }}; color: {{ color_texto }}; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 5000;
        }
        #splash img { max-width: 220px; height: auto; margin-bottom: 20px; }
        
        body { font-family: sans-serif; margin: 0; background: {{ color_fondo }}; color: {{ color_texto }}; padding-top: 60px; padding-bottom: 80px; }
        
        #top-install-bar {
            position: fixed; top: 0; left: 0; width: 100%; height: 60px;
            background: {{ color_fondo }}; color: {{ color_texto }}; display: flex; 
            justify-content: center; align-items: center; z-index: 1000;
            border-bottom: 2px solid {{ color_acento }}; font-weight: bold; font-size: 0.85em;
        }
        .btn-install { background: {{ color_acento }}; color: {{ color_fondo }}; border: none; padding: 8px 12px; border-radius: 5px; font-weight: bold; margin-left: 10px;}

        header { background: {{ color_fondo }}; padding: 15px; text-align: center; border-bottom: 1px solid {{ color_secundario }}; }
        header img { height: 60px; margin-bottom: 5px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: {{ color_fondo }}; border-radius: 12px; overflow: hidden; border: 1px solid {{ color_secundario }}; }
        .card img { width: 100%; height: 160px; object-fit: cover; }
        .info { padding: 10px; }
        .precio { font-weight: bold; font-size: 1.2em; color: {{ color_acento }}; }
        .btn-add { background: {{ color_acento }}; color: {{ color_fondo }}; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; margin-top: 10px; }
        
        #cart-bar { position: fixed; bottom: 20px; left: 5%; width: 90%; background: #25d366; color: white; padding: 18px; border-radius: 35px; text-align: center; font-weight: bold; display: none; z-index: 1000; }
    </style>
</head>
<body onload="initApp()">

    <div id="splash">
        <img src="{{ url_for('static', filename=logo_name) }}" alt="Logo Mercado CLN">
        <p>Cargando Mercado CLN...</p>
    </div>

    <div id="top-install-bar" onclick="installApp()">
        <span>¿Quieres la App?</span>
        <button class="btn-install">INSTALAR</button>
    </div>

    <header>
        <img src="{{ url_for('static', filename=logo_name) }}" alt="Logo">
        <h2 style="margin:0;">Mercado en Línea</h2>
        <small style="color: {{ color_secundario }};">Culiacán • Entrega a Domicilio</small>
    </header>

    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.imagen }}" onerror="this.src='https://via.placeholder.com/150?text=Producto'">
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
            setTimeout(() => { document.getElementById('splash').style.display = 'none'; }, 2500);
        }
        function addToCart() { document.getElementById('cart-bar').style.display = 'block'; }
        function sendWhatsApp() { window.location.href = "https://wa.me/526671377298?text=Hola Hector, me interesa un producto."; }
    </script>
</body>
</html>
'''

@app.route('/')
def home(): 
    return render_template_string(HTML_APP, 
                                 lista=productos, 
                                 logo_name=NOMBRE_LOGO,
                                 color_fondo=COLOR_FONDO,
                                 color_acento=COLOR_ACENTO,
                                 color_texto=COLOR_TEXTO,
                                 color_secundario=COLOR_SECUNDARIO)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
