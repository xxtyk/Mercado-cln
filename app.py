import os

if __name__ == '__main__':
    # Render asigna el puerto automáticamente en la variable de entorno PORT
    # Si no la encuentra, usará el 10000 por defecto
    port = int(os.environ.get("PORT", 10000))
    
    # IMPORTANTE: host debe ser '0.0.0.0' para que Render pueda conectar
    app.run(host='0.0.0.0', port=port)
