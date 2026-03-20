import os
import json
from flask import Flask, request

app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE CARPETAS ---
UPLOAD_FOLDER = 'static/img'
DATA_FILE = 'productos.json'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def cargar_db():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return []
    return []

# --- VISTA PRINCIPAL (PORTADA Y TIENDA) ---
@app.route('/')
def home():
    productos = cargar_db()
    html_prods = ""
    for p in productos:
        html_prods += f'''
            <div class="card">
                <img src="/static/img/{p['img']}" onerror="this.src='https://via.placeholder.com/150?text=Producto'">
                <div class="card-info">
                    <h4>{p['nombre']}</h4>
                    <p class="precio">${p['precio']}</p>
                    <button class="btn-accion" onclick="abrirFicha('{p['nombre']}', '{p['precio']}')">PEDIR</button>
                </div>
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
            
            /* PORTADA QUE OCUPA TODO AL ABRIR */
            #portada {{ 
                width: 100%; height: 100vh; display: flex; flex-direction: column; 
                align-items: center; justify-content: center; background: #000;
            }}
            .logo-grande {{ width: 85%; max-width: 450px; height: auto; border: none; }}
            
            /* BOTÓN PARA BAJAR AL CATÁLOGO */
            .btn-entrar {{ 
                margin-top: 20px; background: #00f2ff; color: #000; border: none; 
                padding: 15px 40px; border-radius: 30px; font-weight: bold; font-size: 18px; cursor: pointer;
            }}

            /* CATÁLOGO */
            #tienda {{ padding: 15px; display: none; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .card {{ background: #111; border: 1px solid #333; border-radius: 12px; overflow: hidden; }}
            .card img {{ width: 100%; height: 130px; object-fit: cover; }}
            .card-info {{ padding: 10px; }}
            .precio {{ color: #00f2ff; font-weight: bold; font-size: 20px; }}
            .btn-accion {{ background: #00f2ff; color: #000; border: none; padding: 10px; width: 100%; border-radius: 6px; font-weight: bold; }}
            
            /* PANEL LINK */
            .panel-link {{ display: block; color: #222; margin-top: 50px; text-decoration: none; font-size: 10px; }}
        </style>
    </head>
    <body>
        
        <div id="portada">
            <img src="/static/img/logo.jpg" class="logo-grande" onerror="this.src='https://via.placeholder.com/400?text=MERCADO+CULIACÁN'">
            <button class="btn-entrar" onclick="verTienda()">VER PRODUCTOS</button>
            <p style="color: #666; margin-top: 20px;">Culiacán, Sinaloa</p>
        </div>

        <div id="tienda">
            <h2 style="color:#00f2ff;">Nuestro Catálogo</h2>
            <div class="grid">{html_prods}</div>
            <a href="/config" class="panel-link">Acceso Panel</a>
        </div>

        <script>
            function verTienda() {{
                document.getElementById('portada').style.display = 'none';
                document.getElementById('tienda').style.display = 'block';
                window.scrollTo(0,0);
            }}
            function abrirFicha(n, p) {{
                alert("Pedido para: " + n + "\\nPrecio: $" + p);
            }}
        </script>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL ---
@app.route('/config', methods=['GET', 'POST'])
def config():
    msg = ""
    if request.method == 'POST':
        f = request.files.get('foto')
        n = request.form.get('nombre')
        p = request.form.get('precio')
        if f and not n:
            f.save(os.path.join(UPLOAD_FOLDER, 'logo.jpg'))
            msg = "✅ Logo actualizado"
        elif f and n and p:
            img_name = n.replace(" ", "_").lower() + ".jpg"
            f.save(os.path.join(UPLOAD_FOLDER, img_name))
            db = cargar_db()
            db.append({"nombre": n, "precio": p, "img": img_name})
            with open(DATA_FILE, 'w', encoding='utf-8') as file: json.dump(db, file, indent=4)
            msg = f"✅ Guardado: {n}"

    return f'''
    <body style="font-family:sans-serif; padding:20px; background:#f0f0f0; text-align:center;">
        <div style="max-width:400px; margin:auto; background:#fff; padding:20px; border-radius:15px; border:1px solid #ccc;">
            <h2>PANEL HÉCTOR</h2>
            <p style="color:blue;">{msg}</p>
            <a href="/">👁️ Ver Portada</a>
            <hr>
            <form method="post" enctype="multipart/form-data">
                <p><b>Cambiar Logo de Portada:</b></p>
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:#00f2ff; border:none; border-radius:5px;">SUBIR LOGO</button>
            </form>
            <hr>
            <form method="post" enctype="multipart/form-data">
                <p><b>Nuevo Producto:</b></p>
                <input type="text" name="nombre" placeholder="Nombre" required style="width:90%; padding:10px; margin-bottom:10px;"><br>
                <input type="number" name="precio" placeholder="Precio" required style="width:90%; padding:10px; margin-bottom:10px;"><br>
                <input type="file" name="foto" required><br><br>
                <button type="submit" style="width:100%; padding:10px; background:#000; color:#fff; border:none; border-radius:5px;">GUARDAR PRODUCTO</button>
            </form>
        </div>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
