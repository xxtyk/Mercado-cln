from flask import Flask, request

app = Flask(__name__)

# 1. LA TIENDA (Lo que ve el cliente)
@app.route('/')
def inicio():
    return '''
    <body style="margin:0; background:#f4f4f4; font-family:Arial; text-align:center;">
        
        <div style="padding:50px;">
            <h1>Mercado en Línea Culiacán</h1>
            
            <a href="/admin" style="display:block; margin:20px auto; width:220px; height:70px; background:red; color:white; text-align:center; line-height:70px; font-weight:bold; text-decoration:none; border-radius:15px; font-size:18px; box-shadow: 0 4px 8px rgba(0,0,0,0.3); z-index:99999;">ENTRAR AL PANEL</a>
            
            <div style="border:1px solid #ccc; padding:20px; background:white; display:inline-block; border-radius:10px; margin-top:20px;">
                <p>Catálogo de Productos activo</p>
                <button style="background:#007bff; color:white; border:none; padding:10px 20px; border-radius:5px;">Ver Productos</button>
            </div>
        </div>
    </body>
    '''

# 2. PANEL DE CONTROL (Para subir productos)
@app.route('/admin')
def admin():
    return '''
    <body style="font-family: Arial; text-align: center; background: #eef2f3; padding: 30px;">
        <h1 style="color: #2c3e50;">Panel de Victoria</h1>
        
        <div style="background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 400px; margin: 0 auto;">
            <h3 style="color: #27ae60;">Agregar Nuevo Producto</h3>
            <hr>
            <p>Nombre del Producto:</p>
            <input type="text" style="width:90%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ddd;">
            
            <p>Precio:</p>
            <input type="number" style="width:90%; padding:10px; margin-bottom:15px; border-radius:5px; border:1px solid #ddd;">
            
            <p>Foto del Producto:</p>
            <input type="file" style="width:90%; padding:10px; margin-bottom:20px;">
            
            <button style="background:#27ae60; color:white; border:none; padding:15px; border-radius:5px; width:100%; font-weight:bold;">SUBIR PRODUCTO</button>
        </div>
        
        <br>
        <a href="/" style="text-decoration:none; color:#2980b9;">← Volver a la Tienda</a>
    </body>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
