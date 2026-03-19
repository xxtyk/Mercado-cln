from flask import Flask, render_template_string

app = Flask(__name__)

# --- DATOS CORREGIDOS ---
LOGO = "https://images2.imgbox.com/39/17/Pq7vPzZJ_o.png"

productos = [
    {"n": "Mascarilla Botox", "p": 150, "i": "https://images2.imgbox.com/f0/67/VpXh1uF6_o.jpg"},
    {"n": "Set de Shampoo", "p": 180, "i": "https://images2.imgbox.com/13/2e/qMskbMvU_o.jpg"},
    {"n": "Minisplit Mirage", "p": 8500, "i": "https://images2.imgbox.com/8f/94/aXy063R8_o.jpg"},
    {"n": "Boiler de Paso", "p": 3200, "i": "https://images2.imgbox.com/d9/0f/p8mYtFOf_o.jpg"}
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; margin: 0; padding-top: 60px; padding-bottom: 90px; }
        
        /* ESTE ES EL PANEL QUE NO ENCONTRABAS */
        .panel-instalacion { 
            position: fixed; top: 0; width: 100%; background: #111; 
            border-bottom: 2px solid #00E5FF; padding: 12px; 
            text-align: center; z-index: 999; font-weight: bold; 
        }
        .btn-instalar { background: #00E5FF; color: #000; border: none; padding: 6px 15px; border-radius: 5px; margin-left: 10px; font-weight: bold; }

        header { text-align: center; padding: 20px; }
        header img { height: 80px; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: #111; border: 1px solid #333; border-radius: 10px; overflow: hidden; }
        .card img { width: 100%; height: 130px; object-fit: cover; }
        
        .precio { color: #00E5FF; font-weight: bold; font-size: 1.2em; margin: 5px 0; }
        .btn-add { background: #00E5FF; color: #000; border: none; width: 90%; padding: 10px; margin: 10px; border-radius: 8px; font-weight: bold; }

        #btn-whatsapp { 
            position: fixed; bottom: 20px; left: 5%; width: 90%; 
            background: #25d366; color: #fff; padding: 18px; 
            border-radius: 40px; text-align: center; font-weight: bold; 
            display: none; z-index: 999; 
        }
    </style>
</head>
<body>
    <div class="panel-instalacion" onclick="alert('Dale a los 3 puntos de tu navegador y selecciona -Instalar-')">
        ¿Quieres la App en tu inicio? <button class="btn-instalar">SÍ, INSTALAR</button>
    </div>

    <header>
        <img src="''' + LOGO + '''">
        <h2 style="margin:0;">Mercado en Línea</h2>
        <p style="color: #888; font-size: 14px;">Culiacán • Pago Contra Entrega</p>
    </header>

    <div class="grid">
        {% for p in lista %}
        <div class="card">
            <img src="{{ p.i }}">
            <div style="padding:10px; text-align:center;">
                <div style="font-size: 13px; height: 32px;">{{ p.n }}</div>
                <div class="precio">${{ p.p }}</div>
                <button class="btn-add" onclick="document.getElementById('btn-whatsapp').style.display='block'">AGREGAR</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <div id="btn-whatsapp" onclick="location.href='https://wa.me/526671377298?text=Hola Hector, quiero un pedido'">
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
