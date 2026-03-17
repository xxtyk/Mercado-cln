from flask import Flask, request, redirect, url_for
import os

app = Flask(__name__)

productos = []

@app.route('/')
def inicio():
    tarjetas_html = ""
    for p in productos:
        tarjetas_html += f"""
        <div style="background:white; border-radius:20px; overflow:hidden; box-shadow:0 10px 20px rgba(0,0,0,0.08); border:1px solid #eee;">
            <div style="background:#f8f9fa; height:180px; display:flex; align-items:center; justify-content:center; font-size:50px;">
                📦
            </div>
            <div style="padding:20px; text-align:left;">
                <b style="font-size:20px; color:#333; display:block; margin-bottom:10px;">{p['nombre']}</b>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#27ae60; font-size:24px; font-weight:bold;">${p['precio']}</span>
                    <button style="background:#000; color:white; border:none; padding:10px 15px; border-radius:10px; font-weight:bold;">Ver</button>
                </div>
            </div>
        </div>"""

    return f'''
    <body style="margin:0; background:#f4f7f6; font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
        <div style="background:#1a1a1a; padding:25px; text-align:center; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
            <div style="color:#aaa; font-size:12px; letter-spacing:3px; margin-bottom:8px; font-weight:bold;">MARKETPLACE CULIACÁN</div>
            <h1 style="color:white; margin:0; font-size:28px;">🛒 Mercado CLN</h1>
        </div>

        <div style="padding:25px;">
            <a href="/admin" style="display:block; background:#ff4757; color:white; text-align:center; padding:20px; border-radius:15px; font-weight:bold; text-decoration:none; margin-bottom:30px; font-size:20px; box-shadow:0 4px 15px rgba(255,71,87,0.3);">
                + AGREGAR NUEVO PRODUCTO
            </a>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
                {tarjetas_html if tarjetas_html else "<p style='grid-column:1/3; text-align:center; color:#999; font-size:20px; margin-top:50px;'>No hay productos todavía...</p>"}
            </div>
        </div>
    </body>
    '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        if nombre and precio:
            productos.append({'nombre': nombre, 'precio': precio})
            return redirect(url_for('inicio'))

    return '''
    <body style="font-family:Sans-Serif; background:#f4f7f6; padding:20px;">
        <div style="background:white; padding:40px; border-radius:30px; max-width:500px; margin:20px auto; box-shadow:0 15px 35px rgba(0,0,0,0.1);">
            <h2 style="text-align:center; font-size:32px; margin-bottom:30px; color:#1a1a1a;">Panel Administrativo</h2>
            <form method="POST">
                <label style="font-size:22px; font-weight:bold; color:#555;">Nombre del Producto</label>
                <input type="text" name="nombre" placeholder="Ej. Minisplit 1 Ton" required style="width:100%; padding:20px; font-size:22px; margin:15px 0 30px 0; border:2px solid #eee; border-radius:15px; background:#fafafa;">

                <label style="font-size:22px; font-weight:bold; color:#555;">Precio de Venta</label>
                <input type="number" name="precio" placeholder="0.00" required style="width:100%; padding:20px; font-size:22px; margin:15px 0 30px 0; border:2px solid #eee; border-radius:15px; background:#fafafa;">

                <button type="submit" style="background:#2ed573; color:white; border:none; padding:25px; border-radius:15px; width:100%; font-size:24px; font-weight:bold; cursor:pointer; box-shadow:0 6px 20px rgba(46,213,115,0.3);">
                    PUBLICAR AHORA
                </button>
            </form>
            <a href="/" style="display:block; text-align:center; margin-top:35px; color:#ff4757; font-weight:bold; text-decoration:none; font-size:20px;">← Salir sin guardar</a>
        </div>
    </body>
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
