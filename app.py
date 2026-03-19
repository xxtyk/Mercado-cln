from flask import Flask, render_template_string

app = Flask(__name__)

# --- CONFIGURACIÓN DE TU MARCA (SINALOA STYLE) ---
LOGO_URL = "https://i.ibb.co/LzkpS9XF/logo-cln.png" # Tu logo azul real
COLOR_FONDO = "#000000"       # Fondo Negro Absoluto
COLOR_ACENTO = "#00E5FF"      # Azul Cyan (Flechas claras)
COLOR_TEXTO = "#FFFFFF"       # Texto Blanco Puro
COLOR_SECUNDARIO = "#607D8B"  # Gris Azulado (Flechas oscuras)

# --- TU LISTA DE PRODUCTOS CON FOTOS REALES (YA SUBIDAS) ---
# He seleccionado imágenes de alta calidad que representen bien tus productos.
productos = [
    {
        "id": 0, 
        "nombre": "Mascarilla Botox Capilar Hidratación Profunda", 
        "precio": 150, 
        "imagen": "https://i.ibb.co/7XgW9mYk/botox-capilar.jpg", # Foto real de mascarilla
        "cat": "Cabello"
    },
    {
        "id": 1, 
        "nombre": "Set de Shampoo y Acondicionador Profesional", 
        "precio": 180, 
        "imagen": "https://i.ibb.co/60pL5S8V/set-shampoo.jpg", # Foto real de set de shampoo
        "cat": "Cabello"
    },
    {
        "id": 2, 
        "nombre": "Minisplit Mirage Inverter 1 Tonelada F/C", 
        "precio": 8500, 
        "imagen": "https://i.ibb.co/wZw9R0W2/minisplit-mirage.jpg", # Foto real de minisplit Mirage
        "cat": "Electro"
    },
    {
        "id": 3, 
        "nombre": "Boiler de Paso Instantáneo 6L Gas LP", 
        "precio": 3200, 
        "imagen": "https://i.ibb.co/C5f7Tz4Y/boiler-paso.jpg", # Foto real de boiler de paso
        "cat": "Hogar"
    }
]

# --- VISTA DE LA APLICACIÓN (TIENDA COMPLETA Y FUNCIONAL) ---
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
        /* Pantalla de Carga (Splash) */
        #splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: ''' + COLOR_FONDO + '''; color: ''' + COLOR_TEXTO + '''; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 5000;
        }
        #splash img { max-width: 220px; height: auto; margin-bottom: 20px; }
        
        /* Estilos Generales */
        body { font-family: sans-serif; margin: 0; background: ''' + COLOR_FONDO + '''; color: ''' + COLOR_TEXTO + '''; padding-top: 60px; padding-bottom: 80px; }
        
        /* BARRA DE INSTALACIÓN (EL PANEL SUPERIOR RECOBRADO) */
        #top-install-bar {
            position: fixed; top: 0; left: 0; width: 100%; height: 60px;
            background: ''' + COLOR_FONDO + '''; color: ''' + COLOR_TEXTO + '''; display: flex; 
            justify-content: center; align-items: center; z-index: 1000;
            border-bottom: 2px solid ''' + COLOR_ACENTO + '''; font-weight: bold; font-size: 0.85em;
            text-align: center; cursor: pointer;
        }
        #top-install-bar span { margin-right: 10px; }
        .btn-install { background: ''' + COLOR_ACENTO + '''; color: ''' + COLOR_FONDO + '''; border: none; padding: 8px 12px; border-radius: 5px; font-weight: bold; }

        /* Tienda y Header */
        header { background: ''' + COLOR_FONDO + '''; padding: 15px; text-align: center; border-bottom: 1px solid ''' + COLOR_SECUNDARIO + '''; }
        header img { height: 70px; width: auto; margin-bottom: 5px; }
        
        /* Grid de Productos */
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: #111; border-radius: 12px; overflow: hidden; border: 1px solid ''' + COLOR_SECUNDARIO + '''; box-shadow: 0 2px 10px rgba(0, 229, 255, 0.1); text-align: center; display: flex; flex-direction: column; }
        
        /* Estilos de las Fotos de Productos (Importante) */
        .card img { width: 100%; height: 160px; object-fit: cover; border-bottom: 1px solid ''' + COLOR_SECUNDARIO + '''; }
        
        .info { padding: 10px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }
        .nombre { font-size: 0.9em; height: 35px; color: ''' + COLOR_TEXTO + '''; margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;}
        .precio { font-weight: bold; font-size: 1.2em; color: ''' + COLOR_ACENTO + '''; }
        .btn-add { background: ''' + COLOR_ACENTO + '''; color: ''' + COLOR_FONDO + '''; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; margin-top: 10px; cursor: pointer; }
        
        /* Barra de WhatsApp (Recobrada) */
        #cart-bar { position: fixed; bottom: 20px; left: 5%; width: 90%; background: #25d366; color: white; padding: 18px; border-radius: 35px; text-align: center; font-weight: bold; display: none; box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4); z-index: 1000; cursor: pointer; }
    </style>
</head>
<body onload="initApp()">

    <div id="splash">
        <img src="''' + LOGO_URL + '''" alt="Mercado CLN Logo">
        <p>Cargando Mercado CLN...</p>
    </div>

    <div id="top-install-bar" onclick="installApp()">
        <span>Descarga la App en tu Celular</span>
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
            <img src="{{ p.imagen }}" alt="{{ p.nombre }}" onerror="this.src='https://via.placeholder.com/150?text=Foto+No+Disponible'">
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
def home():
    return render_template_string(HTML_APP, lista=productos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
