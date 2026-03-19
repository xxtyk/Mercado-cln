from flask import Flask, render_template_string

app = Flask(__name__)

# --- DATOS DE LA TIENDA ---
LOGO_URL = "https://i.ibb.co/LzkpS9XF/logo-cln.png"

productos = [
    {"n": "Mascarilla Botox", "p": 150, "i": "https://i.ibb.co/7XgW9mYk/botox-capilar.jpg"},
    {"n": "Set de Shampoo", "p": 180, "i": "https://i.ibb.co/60pL5S8V/set-shampoo.jpg"},
    {"n": "Minisplit Mirage", "p": 8500, "i": "https://i.ibb.co/wZw9R0W2/minisplit-mirage.jpg"},
    {"n": "Boiler de Paso", "p": 3200, "i": "https://i.ibb.co/C5f7Tz4Y/boiler-paso.jpg"}
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; margin: 0; padding-bottom: 80px; }
        .bar { background: #000; border-bottom: 2px solid #00E5FF; padding: 15px; text-align: center; font-weight: bold; }
        .btn-ins { background: #00E5FF; border: none; padding: 5px 10px; border-radius: 5px; margin-left: 10px; }
        header { text-align: center; padding: 20px; border-bottom: 1px solid #333; }
        header img { height: 70px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: #111; border: 1px solid #333; border-radius: 10px; overflow: hidden; text-align: center; }
        .card img { width: 100%; height: 120px; object-fit: cover; }
        .precio { color: #00E5FF; font-weight: bold; font-size: 1.1em; }
        .btn-add { background: #00E5FF; border: none; width: 90%; padding: 10px; margin: 10px 0; border-radius: 5px; font-weight: bold; }
        #wa { position: fixed; bottom: 20px; left: 5%; width: 90%; background: #25d366; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; display: none; }
    </style>
</head>
<body>
    <div class="bar" onclick="alert('Pica en los 3 puntos de tu navegador y dale a Instalar')">
        Instala la App <button class="btn-ins">INSTALAR</button>
    </div>
    <header>
        <img src="''' + LOGO_URL + '''">
        <h2 style="margin:5px 0;">Mercado en Línea</h2>
        <small style="color: #607D8B;">Culiacán • Pago Contra Entrega</small>
    </header>
    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.i }}">
            <div style="padding: 5px; font-size: 0.8em;">{{ p.n }}</div>
            <div class="precio">${{ p.p }}</div>
            <button class="btn-add" onclick="document.getElementById('wa').style.display='block'">AGREGAR</button>
        </div>
        {% endfor %}
    </div>
    <div id="wa" onclick="location.href='https://wa.me/526671377298?text=Hola Hector, quiero un pedido'">
        ENVIAR PEDIDO POR WHATSAPP
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML, lista=productos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
