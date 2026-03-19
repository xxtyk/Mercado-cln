import os
from flask import Flask, render_template_string

app = Flask(__name__)

# --- DISEÑO QUE LE COPIAMOS A REPLIT (HTML/CSS) ---
# Aquí es donde pondrás lo que el agente de Replit te diseñe
DISENO_MERCADO = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; margin: 0; text-align: center; }
        header { background: #111; padding: 20px; border-bottom: 2px solid #00E5FF; }
        .grid-categorias { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 15px; }
        .cat-card { background: #1a1a1a; border-radius: 15px; overflow: hidden; border: 1px solid #333; }
        .cat-card img { width: 100%; height: 120px; object-fit: cover; }
        .cat-name { padding: 10px; font-weight: bold; font-size: 14px; }
    </style>
</head>
<body>
    <header>
        <h2 style="color:#00E5FF; margin:0;">MERCADO EN LÍNEA</h2>
        <p style="font-size:12px; color:#888;">CULIACÁN</p>
    </header>

    <div style="padding:15px; background:#222; font-weight:bold;">CATEGORÍAS</div>

    <div class="grid-categorias">
        <div class="cat-card">
            <img src="https://via.placeholder.com/150/800000/FFFFFF?text=Cabello">
            <div class="cat-name">Cuidado del cabello</div>
        </div>
        <div class="cat-card">
            <img src="https://via.placeholder.com/150/FF4500/FFFFFF?text=Cocina">
            <div class="cat-name">Cocina</div>
        </div>
        <div class="cat-card">
            <img src="https://via.placeholder.com/150/008000/FFFFFF?text=Mascotas">
            <div class="cat-name">Mascotas</div>
        </div>
        <div class="cat-card">
            <img src="https://via.placeholder.com/150/0000FF/FFFFFF?text=Sonido">
            <div class="cat-name">Música y sonido</div>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def cliente():
    return render_template_string(DISENO_MERCADO)

@app.route('/config')
def admin():
    return "<h1>Panel de Configuración</h1><p>Aquí vas a gestionar tus mil productos, Hector.</p>"

if __name__ == "__main__":
    # Esto es lo que evita que Render te de error de puerto
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
