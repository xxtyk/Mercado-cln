import os
import json
from flask import Flask, request

app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE CARPETAS ---
UPLOAD_FOLDER = 'static/img'
DATA_FILE = 'productos.json' 
if not os.path.exists(UPLOAD_FOLDER): 
    os.makedirs(UPLOAD_FOLDER)

# Función segura para cargar productos
def cargar_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except:
            return []
    return []

# --- VISTA DEL CLIENTE ---
@app.route('/')
def home():
    productos = cargar_db()
    html_prods = ""
    for p in productos:
        html_prods += f'''
            <div class="card">
                <img src="/static/img/{p['img']}" onerror="this.src='https://via.placeholder.com/150'">
                <h4>{p['nombre']}</h4>
                <p class="precio">${p['precio']}</p>
                <button class="btn-accion" onclick="abrirFicha('{p['nombre']}', '{p['precio']}')">AGREGAR</button>
            </div>
        '''

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mercado en Línea Culiacán</title>
        <style>
            body {{ font-family: sans-serif; margin: 0; background: #000; color: #fff; text-align: center; }}
            .logo-inicio {{ width: 250px; height: auto; margin-top: 40px; border: none; }}
            .info-sub {{ font-size: 14px; color: #888; margin-top: 10px; margin-bottom: 30px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 15px; }}
            .card {{ background: #111; border: 1px solid #333; border-radius: 12px; padding: 10px; }}
            .card img {{ width: 100%; height: 120px; object-fit: cover; border-radius: 8px; }}
            .precio {{ color: #00f2ff; font-weight: bold; font-size: 19px; }}
            .btn-accion {{ background: #00f2ff; color: #000; border: none; padding: 10px; width: 100%; border-radius: 6px; font-weight: bold; cursor: pointer; }}
            .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 100; }}
            .modal-content {{ background: #111; margin: 15% auto; padding: 20px; width: 85%; border-radius: 15px; border: 1px solid #00f2ff; }}
            input {{ width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #333; background: #000; color:#fff; box-sizing: border-box; }}
        </style>
    </head>
    <body>
        <img src="/static/img/logo.jpg" class="logo-inicio" onerror="this.src='https://via.placeholder.com/200?text=SUBIR+LOGO'">
        <p class="info-sub">Culiacán • Pago Contra Entrega</p>
        <div class="grid">{html_prods}</div>
        <div id="modalFicha" class="modal">
            <div class="modal-content">
                <h3 id="pNom" style="color:#00f2ff;"></h3>
                <input type="text" id="c" placeholder="Tu Nombre">
                <input type="text" id="d" placeholder="Dirección">
                <input type="text" id="r" placeholder="Referencia">
                <button class="btn-accion" onclick="enviar()">ENVIAR AL GRUPO</button>
                <button onclick="document.getElementById('modalFicha').style.display='none'" style="background:none; color:red; border:none; margin-top:15px; cursor:pointer;">Cancelar</button>
            </div>
        </div>
        <script>
            let sel = {{}};
            function abrirFicha(n, p) {{
                sel = {{n, p}};
                document.getElementById('pNom').innerText = "Pedido: " + n;
                document.getElementById('modalFicha').style.display = 'block';
            }}
            function enviar() {{
                const c = document.getElementById('c').value;
                const d = document.getElementById('d').value;
                if(!c || !d) return alert("Llena los datos");
                const m = `*PEDIDO MERCADO CLN*%0A*Producto:* ${{sel.n}}%0A*Precio:* $${{sel.p}}%0A*Cliente:* ${{c}}%0A*Dirección:* ${{d}}`;
                window.open(`https://wa.me/?text=${{m}}`, '_blank');
            }}
        </script>
        <a href="/config" style="display:block; color:#222; margin-top:50px; text-decoration:none; font-size:10px;">Panel</a>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL ---
@app.route('/config', methods=['GET', 'POST'])
def config():
    msg = ""
    if request.method == 'POST':
        file = request.files.get('foto')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        
        if file and not nombre:
            file.save(os.path.join(UPLOAD_FOLDER, 'logo.jpg'))
            msg = "<p style='color:green;'>¡Logo actualizado!</p>"
            
        elif file and nombre and precio:
            img_name = nombre.replace(" ", "_").lower() + ".jpg"
            file.save(os.path.join(UPLOAD_FOLDER, img_name))
            db = cargar_db()
            db.append({"nombre": nombre, "precio": precio, "img": img_name})
            with open(DATA_FILE, 'w', encoding='utf-8') as f: 
                json.dump(db, f, indent=4)
            msg = f"<p style='color:green;'>Producto {nombre} guardado.</p>"

    return f'''
    <body style="font-family:sans-serif; padding:20px; max-width:500px; margin:auto; background:#eee;">
        <h2>CONTROL DE MERCADO CLN</h2>
        {msg}
        <a href="/" style="display:block; margin-bottom:20px;">👁️ Ver Catálogo</a>
        <div style="background:#fff; padding:20px; border-radius:15px; margin-bottom:20px; border:1px solid #ccc;">
            <h3>Cambiar Logo</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:black; color:white; border:none; border-radius:5px;">ACTUALIZAR LOGO</button>
            </form>
        </div>
        <div style="background:#fff; padding:20px; border-radius:15px; border:1px solid #ccc;">
            <h3>Nuevo Producto</h3>
            <form method="post" enctype="multipart/form-data">
                <input type="text" name="nombre" placeholder="Nombre" style="width:100%; padding:10px; margin-bottom:10px;" required>
                <input type="number" name="precio" placeholder="Precio" style="width:100%; padding:10px; margin-bottom:10px;" required>
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:15px; background:#000; color:white; border:none; border-radius:10px;">GUARDAR</button>
            </form>
        </div>
    </body>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
