from flask import Flask, request, redirect, url_for

app = Flask(__name__)
productos = []

# Aquí están las categorías que recuperamos del agente profesional
CATEGORIAS = [
    {"id":"cabello","nombre":"Cuidado del cabello","emoji":"💆","color":"#7b1fa2"},
    {"id":"cocina","nombre":"Cocina","emoji":"🍳","color":"#e65100"},
    {"id":"mascotas","nombre":"Mascotas","emoji":"🐾","color":"#2e7d32"},
    {"id":"musica","nombre":"Música y sonido","emoji":"🎵","color":"#1565c0"},
    {"id":"personal","nombre":"Cuidado personal","emoji":"💄","color":"#c62828"},
    {"id":"electrodomesticos","nombre":"Electrodomésticos","emoji":"⚡","color":"#37474f"}
]

@app.route('/')
def inicio():
    cats_html = ""
    for c in CATEGORIAS:
        cats_html += f'''
        <div style="background:{c["color"]}; color:white; padding:15px; border-radius:15px; text-align:center; font-weight:bold; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
            <span style="font-size:24px;">{c["emoji"]}</span><br>
            <span style="font-size:12px;">{c["nombre"]}</span>
        </div>'''

    return f'''
    <body style="margin:0; font-family:Arial; background:#f4f7f6;">
        <div style="background:#000; padding:25px; text-align:center; color:white; box-shadow:0 4px 12px rgba(0,0,0,0.3);">
            <h1 style="margin:0; font-size:24px;">🛒 MERCADO CLN</h1>
            <small style="color:#aaa; letter-spacing:2px;">CULIACÁN, SINALOA</small>
        </div>
        <div style="padding:15px;">
            <a href="/admin" style="display:block; background:#ff4757; color:white; text-align:center; padding:20px; border-radius:15px; font-weight:bold; text-decoration:none; margin-bottom:25px; font-size:20px; box-shadow:0 4px 15px rgba(255,71,87,0.4);">
                + AGREGAR PRODUCTO NUEVO
            </a>

            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-bottom:30px;">
                {cats_html}
            </div>

            <div style="text-align:center; color:#999; padding:50px; border:2px dashed #ccc; border-radius:20px;">
                <p style="font-size:18px;">Tu tienda está lista.<br>¡Empieza a subir mercancía!</p>
            </div>
        </div>
    </body>
    '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    opciones = "".join([f'<option value="{c["id"]}">{c["emoji"]} {c["nombre"]}</option>' for c in CATEGORIAS])

    return f'''
    <body style="font-family:Arial; background:#f4f7f6; padding:20px;">
        <div style="background:white; padding:35px; border-radius:30px; box-shadow:0 15px 35px rgba(0,0,0,0.1); max-width:500px; margin:0 auto;">
            <h2 style="text-align:center; color:#1a1a1a; font-size:28px; margin-bottom:30px;">Panel de Control</h2>
            <form>
                <label style="font-weight:bold; font-size:18px; color:#555;">Nombre del Artículo:</label>
                <input type="text" placeholder="Ej. Minisplit 1 Ton" style="width:100%; padding:18px; margin:10px 0 25px 0; border-radius:12px; border:2px solid #eee; font-size:18px; background:#fafafa;">

                <label style="font-weight:bold; font-size:18px; color:#555;">Categoría:</label>
                <select style="width:100%; padding:18px; margin:10px 0 25px 0; border-radius:12px; border:2px solid #eee; font-size:18px; background:#fafafa;">
                    {opciones}
                </select>

                <div style="border:3px dashed #2ed573; padding:40px; text-align:center; border-radius:20px; background:#fafffa; margin-bottom:30px;">
                    <span style="font-size:40px;">📸</span><br>
                    <input type="file" style="margin-top:15px; font-size:16px;">
                    <p style="color:#27ae60; font-weight:bold; margin-top:10px;">Toca para subir la foto</p>
                </div>

                <button type="button" style="background:#2ed573; color:white; border:none; padding:25px; border-radius:20px; width:100%; font-size:22px; font-weight:bold; box-shadow:0 6px 20px rgba(46,213,115,0.3);">
                    PUBLICAR EN LA TIENDA
                </button>
            </form>
            <a href="/" style="display:block; text-align:center; margin-top:30px; color:#ff4757; text-decoration:none; font-weight:bold; font-size:18px;">← Cancelar y salir</a>
        </div>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
