from flask import Flask, render_template_string

app = Flask(__name__)

# --- LINK CORREGIDO DE TU LOGO REAL ---
LOGO_URL = "https://i.ibb.co/LzkpS9XF/logo-cln.png"

# --- CONFIGURACIÓN DE COLORES ---
COLOR_FONDO = "#000000"
COLOR_ACENTO = "#00E5FF"
COLOR_TEXTO = "#FFFFFF"

productos = [
    {"id": 0, "nombre": "Mascarilla Botox", "precio": 150},
    {"id": 1, "nombre": "Set de Shampoo", "precio": 180},
    {"id": 2, "nombre": "Minisplit Mirage", "precio": 8500},
    {"id": 3, "nombre": "Boiler de Paso", "precio": 3200}
]

HTML_APP = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mercado CLN</title>
    <style>
        body { font-family: sans-serif; margin: 0; background: {{ fondo }}; color: {{ texto }}; }
        #splash {
            position: fixed; top:0; left:0; width:100%; height:100%;
            background: {{ fondo }}; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 99;
        }
        #splash img { max-width: 220px; height: auto; margin-bottom: 20px; }
        header { padding: 20px; text-align: center; border-bottom: 1px solid #333; }
        header img { height: 80px; width: auto; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: #111; border: 1px solid #333; border-radius: 12px; padding: 15px; text-align: center; }
        .precio { color: {{ acento }}; font-weight: bold; font-size: 1.2em; }
        .btn { background: {{ acento }}; color: #000; border: none; padding: 10px; width: 100%; border-radius: 5px; font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body onload="cerrarSplash()">
    <div id="splash">
        <img src="{{ logo }}" alt="Cargando...">
        <p>Cargando Mercado CLN...</p>
    </div>
    <header>
        <img src="{{ logo }}" alt="Mercado CLN">
        <h2 style="margin:5px 0 0 0;">Mercado en Línea</h2>
        <small style="color: #888;">Culiacán • Pago Contra Entrega</small>
    </header>
    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <div style="font-size: 0.9em;">{{ p.nombre }}</div>
            <div class="precio">${{ p.precio }}</div>
            <button class="btn">AGREGAR</button>
        </div>
        {% endfor %}
    </div>
    <script>
        function cerrarSplash() {
            setTimeout(() => { document.getElementById('splash').style.display = 'none'; }, 2500);
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_APP, 
                                 lista=productos, 
                                 logo=LOGO_URL, 
                                 fondo=COLOR_FONDO, 
                                 texto=COLOR_TEXTO, 
                                 acento=COLOR_ACENTO)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
