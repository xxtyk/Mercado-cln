import os
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# --- CONFIGURACIÓN DE CLOUDINARY (Lectura desde Render) ---
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key = os.environ.get('CLOUDINARY_API_KEY'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET'),
    secure = True
)

# --- AQUÍ EMPIEZAN TUS RUTAS (Ejemplo de la ruta admin) ---
@app.route('/')
def index():
    return "Mercado en Línea Culiacán funcionando en Render"

# Tu lógica para guardar productos iría aquí abajo...
# Asegúrate de mantener tus funciones de @app.route anteriores

# --- BLOQUE FINAL PARA EL PUERTO DE RENDER ---
if __name__ == '__main__':
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 10000))
    # host '0.0.0.0' es obligatorio para que sea público
    app.run(host='0.0.0.0', port=port)
