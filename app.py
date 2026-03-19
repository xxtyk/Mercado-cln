from flask import Flask, render_template_string, url_for

app = Flask(__name__)

# --- AQUÍ AGREGA LOS PRODUCTOS QUE QUIERAS ---
# Solo copia una línea de estas, cámbiale el nombre y la foto
productos = [
    {"n": "Mascarilla Botox", "p": 150, "i": "botox.jpg", "c": "Cuidado del Cabello"},
    {"n": "Set de Shampoo", "p": 180, "i": "shampoo.jpg", "c": "Cuidado del Cabello"},
    {"n": "Minisplit Mirage", "p": 8500, "i": "mirage.jpg", "c": "Hogar"},
    {"n": "Boiler de Paso", "p": 3200, "i": "boiler.jpg", "c": "Hogar"}
]

CATEGORIAS = ["Cuidado del Cabello", "Hogar", "Cocina", "Mascotas"]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; margin: 0; }
        header { background: #111; padding: 15px; text-align: center; border-bottom: 2px solid #00E5FF; }
        header img { height: 60px; }
        .cat-titulo { background: #222; padding: 10px; font-size: 18px; font-weight: bold; color: #00E5FF; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
        .card { background: #111; border: 1px solid #333; border-radius: 12px; overflow: hidden; text-align: center; }
        .card img { width: 100%; height: 140px; object-fit: cover; }
        .precio { color: #00E5FF; font-weight: bold; font-size: 1.2em; margin: 5px 0; }
        .btn-add { background: #00E5FF; color: #000; border: none; width: 90%; padding: 12px; margin-bottom: 10px; border-radius: 8px; font-weight: bold; }
    </style>
</head>
<body>
    <header>
        <img src="/logo.png" onerror="this.src='/static/logo.png'">
        <h2 style="margin:5px 0 0 0;">Mercado en Línea</h2>
    </header>

    {% for cat in cats %}
        {% set items = lista | selectattr('c', 'equalto', cat) | list %}
        {% if items %}
            <div class="cat-titulo">{{ cat }}</div>
            <div class="grid">
                {% for p in items %}
                <div class="card">
                    <img src="/{{ p.i }}" onerror="this.src='/static/{{ p.i }}'">
                    <div style="padding:8px;">
                        <div style="font-size:13px; height: 32px; overflow: hidden;">{{ p.n }}</div>
                        <div class="precio">${{ p.p }}</div>
                        <button class="btn-add" onclick="location.href='https://wa.me/526671377298?text=Hola, quiero el producto: {{ p.n }}'">AGREGAR</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endfor %}
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML, lista=productos, cats=CATEGORIAS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
