import os
import json
from flask import Flask, request, redirect, url_for

# --- INICIO DE LA APLICACIÓN ---
app = Flask(__name__, static_folder='static')

# --- CONFIGURACIÓN DE CARPETAS Y PERMISOS ---
# Esto asegura que Render cree la carpeta de imágenes y el archivo de productos
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'img')
DATA_FILE = os.path.join(app.root_path, 'productos.json')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, mode=0o777, exist_ok=True)

# Función para cargar productos con manejo de errores
def cargar_db():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # Si hay error (archivo vacío o corrupto), empezamos de cero
        return []

# --- VISTA DEL CLIENTE (MERCADO EN LÍNEA CULIACÁN) ---
@app.route('/')
def home():
    productos = cargar_db()
    html_prods = ""
    for p in productos:
        # Mostramos los productos en la cuadrícula
        html_prods += f'''
            <div class="card">
                <img src="/static/img/{p['img']}" onerror="this.src='https://via.placeholder.com/150?text=Producto'">
                <div class="card-info">
                    <h4>{p['nombre']}</h4>
                    <p class="precio">${p['precio']}</p>
                    <button class="btn-accion" onclick="abrirFicha('{p['nombre']}', '{p['precio']}')">AGREGAR</button>
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
            /* FONDO NEGRO Y LETRAS BLANCAS */
            body {{ font-family: sans-serif; margin: 0; background: #000; color: #fff; text-align: center; padding-bottom: 50px; }}
            
            /* AJUSTE DEL LOGO: Más grande y centrado */
            .logo-inicio {{ width: 85%; max-width: 320px; height: auto; margin-top: 50px; border: none; display: block; margin-left: auto; margin-right: auto; }}
            
            /* Subtítulo minimalista */
            .info-sub {{ font-size: 15px; color: #aaa; margin-top: 15px; margin-bottom: 35px; }}

            /* GRID DE PRODUCTOS: Cuadrícula de 2 columnas */
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; padding: 15px; }}
            
            /* TARJETA DE PRODUCTO: Fondo gris muy oscuro y borde cyan suave */
            .card {{ background: #111; border: 1px solid #333; border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; }}
            .card img {{ width: 100%; height: 140px; object-fit: cover; border-bottom: 1px solid #333; }}
            .card-info {{ padding: 10px; flex-grow: 1; display: flex; flex-direction: column; justify-content: space-between; }}
            .card h4 {{ margin: 0; font-size: 16px; margin-bottom: 5px; }}
            
            /* Color Cyan para precios */
            .precio {{ color: #00f2ff; font-weight: bold; font-size: 20px; margin: 0 0 10px 0; }}
            
            /* Botón de Agregar: Cyan brillante */
            .btn-accion {{ background: #00f2ff; color: #000; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; }}
            
            /* ENLACE AL PANEL: Ahora es blanco, más grande y está abajo */
            .panel-link {{ display: block; color: #fff; margin-top: 80px; text-decoration: none; font-size: 16px; font-weight: bold; border: 1px solid #fff; padding: 10px 20px; border-radius: 20px; width: fit-content; margin-left: auto; margin-right: auto; }}
        </style>
    </head>
    <body>
        
        <img src="/static/img/logo.jpg" class="logo-inicio" onerror="this.src='https://via.placeholder.com/300x150?text=MERCADO+CULIACÁN'">
        
        <p class="info-sub">Culiacán • Pago Contra Entrega</p>
        
        <div class="grid">{html_prods}</div>
        
        <a href="/config" class="panel-link">⚙️ Acceder al Panel de Control</a>

        <script>
            // Función simple para la ficha (ya la integraremos con WhatsApp después)
            function abrirFicha(nombre, precio) {{
                alert("Producto: " + nombre + "\\nPrecio: $" + precio + "\\n\\n(Aquí abriremos la ficha de pedido en el siguiente paso)");
            }}
        </script>
    </body>
    </html>
    '''

# --- PANEL DE CONTROL (MEJORADO Y PROFESIONAL) ---
@app.route('/config', methods=['GET', 'POST'])
def config():
    msg = ""
    # Manejamos las subidas de archivos y datos
    if request.method == 'POST':
        file = request.files.get('foto')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        
        # CASO 1: Subir/Actualizar LOGO
        if file and not nombre and not precio:
            file.save(os.path.join(UPLOAD_FOLDER, 'logo.jpg'))
            msg = "<div class='alert success'>¡Logo actualizado con éxito! Ve a la tienda para verlo.</div>"
            
        # CASO 2: Subir NUEVO PRODUCTO (con precio)
        elif file and nombre and precio:
            # Limpiamos el nombre para el archivo de imagen
            img_name = nombre.replace(" ", "_").lower() + ".jpg"
            file.save(os.path.join(UPLOAD_FOLDER, img_name))
            
            # Guardamos los datos en productos.json
            db = cargar_db()
            db.append({"nombre": nombre, "precio": precio, "img": img_name})
            try:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=4)
                msg = f"<div class='alert success'>Producto '{nombre}' guardado con precio ${precio}.</div>"
            except Exception as e:
                msg = f"<div class='alert error'>Error al guardar datos: {str(e)}</div>"

    return f'''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel de Control - Mercado CLN</title>
        <style>
            /* DISEÑO PROFESIONAL DEL PANEL */
            body {{ font-family: sans-serif; padding: 20px; background: #f0f2f5; color: #333; margin: 0; }}
            .container {{ max-width: 500px; margin: auto; background: #fff; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            
            h2 {{ text-align: center; color: #000; margin-top: 0; margin-bottom: 10px; border-bottom: 2px solid #00f2ff; padding-bottom: 10px; }}
            h3 {{ color: #444; margin-top: 0; margin-bottom: 15px; }}
            
            /* Enlaces y alertas */
            .nav-link {{ display: block; text-align: center; color: #00f2ff; font-weight: bold; text-decoration: none; margin-bottom: 25px; }}
            .alert {{ padding: 15px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; text-align: center; }}
            .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
            .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}

            /* SECCIONES DEL FORMULARIO */
            .form-section {{ background: #f9f9f9; padding: 20px; border-radius: 15px; margin-bottom: 25px; border: 1px solid #eee; }}
            
            /* Inputs y Selectores Grandes */
            label {{ font-weight: bold; display: block; margin-bottom: 8px; color: #555; }}
            input[type="text"], input[type="number"], select {{ width: 100%; padding: 15px; margin-bottom: 18px; border: 1px solid #ddd; border-radius: 10px; box-sizing: border-box; font-size: 16px; background: #fff; }}
            input[type="file"] {{ margin-bottom: 20px; width: 100%; font-size: 15px; }}

            /* BOTONES: Negros con letras blancas, grandes y llamativos */
            .btn-submit {{ display: block; width: 100%; padding: 18px; background: #000; color: #fff; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 17px; transition: background 0.3s; }}
            .btn-submit:hover {{ background: #222; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>CONTROL DE MERCADO CLN</h2>
            <a href="/" class="nav-link">👁️ Volver a mi Tienda</a>
            
            {msg}

            <div class="form-section">
                <h3>1. Cambiar Logo Principal</h3>
                <form method="post" enctype="multipart/form-data">
                    <label>Selecciona la foto de tu logo (JPG):</label>
                    <input type="file" name="foto" required>
                    <button type="submit" class="btn-submit">ACTUALIZAR LOGO PRINCIPAL</button>
                </form>
            </div>

            <div class="form-section">
                <h3>2. Subir Nuevo Producto</h3>
                <form method="post" enctype="multipart/form-data">
                    <label>Nombre del Producto:</label>
                    <input type="text" name="nombre" placeholder="Ej: Jabón de Coche" required>
                    
                    <label>Precio ($):</label>
                    <input type="number" name="precio" placeholder="Ej: 150" required>
                    
                    <label>Foto del Producto (JPG):</label>
                    <input type="file" name="foto" required>
                    
                    <button type="submit" class="btn-submit">GUARDAR PRODUCTO CON PRECIO</button>
                </form>
            </div>
        </div>
        <p style="text-align:center; font-size:12px; color:#999; margin-top:20px;">Mercado CLN v3.3 - Héctor Edición</p>
    </body>
    </html>
    '''

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
