import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mercado en Línea Culiacán</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; background-color: #f0f0f0; }
            .header { background: #000; color: white; padding: 15px; text-align: center; }
            .container { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
            .card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
            .card img { width: 100%; height: 150px; object-fit: cover; }
            .card h4 { margin: 10px 0; font-size: 14px; }
            .whatsapp-btn { position: fixed; bottom: 20px; right: 20px; background: #25d366; width: 60px; height: 60px; border-radius: 50%; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        </style>
    </head>
    <body>
        <div class="header"><h2>MERCADO EN LÍNEA</h2></div>
        <div class="container">
            <div class="card">
                <img src="https://via.placeholder.com/150" alt="Cabello">
                <h4>Cuidado del cabello</h4>
            </div>
            <div class="card">
                <img src="https://via.placeholder.com/150" alt="Cocina">
                <h4>Cocina</h4>
            </div>
            <div class="card">
                <img src="https://via.placeholder.com/150" alt="Mascotas">
                <h4>Mascotas</h4>
            </div>
            <div class="card">
                <img src="https://via.placeholder.com/150" alt="Electro">
                <h4>Electrodomésticos</h4>
            </div>
        </div>
        <div class="whatsapp-btn">
            <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" width="35">
        </div>
    </body>
    </html>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
