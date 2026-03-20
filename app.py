import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Mercado en Línea Culiacán</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: sans-serif; text-align: center; background: #f4f4f4; }
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 10px; }
                .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                .header { background: black; color: white; padding: 20px; }
            </style>
        </head>
        <body>
            <div class="header"><h1>MERCADO EN LÍNEA</h1></div>
            <h3>CATEGORÍAS</h3>
            <div class="grid">
                <div class="card" style="border-bottom: 5px solid red;">Cuidado del cabello</div>
                <div class="card" style="border-bottom: 5px solid orange;">Cocina</div>
                <div class="card" style="border-bottom: 5px solid green;">Mascotas</div>
                <div class="card" style="border-bottom: 5px solid blue;">Música y sonido</div>
            </div>
        </body>
    </html>
    '''

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
