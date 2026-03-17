from flask import Flask, request, redirect, url_for

app = Flask(__name__)
productos = []

# Aquí están las categorías que "recuperaste" del agente
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
    # Diseño de la tienda con los colores robados
    cats_html = ""
    for c in CATEGORIAS:
        cats_html += f'''
        <div style="background:{c["color"]}; color:white; padding:15px; border-radius:15px; text-align:center; font-weight:bold; box-shadow:0 4px 8px rgba(0,0,0,0.2);">
            <span style="font-size:24px;">{c["emoji"]}</span><br>
            <span style="font-size:12px;">{c["nombre"]}</span>
        </div>'''

    return f'''
    <body style="margin:0; font-family:Arial; background:#f4f7f6;">
        <div style="background:#000; padding:20px; text-align:center; color:white;">
            <h1 style="margin:0; font-size:22px;">🛒 Mercado CLN</h1>
        </div>
        <div style="padding:15px;">
            <a href="/admin" style="display:block; background:#ff4757; color:white; text-align:center; padding:18px; border-radius:12px; font-weight:bold; text-decoration:none; margin-bottom:20px; font-size:18px;">+ AGREGAR PRODUCTO</a>

            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px; margin-bottom:25px;">
                {cats_html}
            </div>

            <div style="text-align:center; color:#999; padding:40px;">
                <p>Tu inventario aparecerá aquí abajo...</p>
            </div>
        </div>
    </body>
    '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    opciones = "".join([f'<option value="{c["id"]}">{c["emoji"]} {c["nombre"]}</option>' for c in CATEGORIAS])

    return f'''
    <body style="font-family:Arial; background:#f4f7f6; padding:15px;">
        <div style="background:white; padding:25px; border-radius:20px; box-shadow:0 10px 25px rgba(0,0,0,0.1); max-width:500px; margin:0 auto;">
            <h2 style="text-align:center;">Panel de Control</h2>
            <form>
                <label style="font-weight:bold;">Nombre:</label>
                <input type="text" style="width:100%; padding:15px; margin:10px 0 20px 0; border-radius:10px; border:1px solid #ddd;">

                <label style="font-weight:bold;">Categoría:</label>
                <select style="width:100%; padding:15px; margin:10px 0 20px 0; border-radius:10px; border:1px solid #ddd;">
                    {opciones}
                </select>

                <div style="border:2px dashed #ccc; padding:30px; text-align:center; border-radius:15px; background:#fafafa; margin-bottom:20px;">
                    <span style="font-size:30px;">📸</span><br>
                    <input type="file" style="margin-top:10px;">
                </div>

                <button type="button" style="background:#2ed573; color:white; border:none; padding:20px; border-radius:12px; width:100%; font-size:20px; font-weight:bold;">PUBLICAR PRODUCTO</button>
            </form>
            <a href="/" style="display:block; text-align:center; margin-top:20px; color:#ff4757; text-decoration:none;">← Volver</a>
        </div>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
