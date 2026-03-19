<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mercado Culichi</title>
    <style>
        body { font-family: Arial, sans-serif; background: #eee; margin: 0; padding: 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .boton { 
            padding: 25px 10px; border-radius: 15px; color: white; 
            text-decoration: none; text-align: center; font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .emoji { font-size: 30px; display: block; margin-bottom: 5px; }
    </style>
</head>
<body>
    <h2 style="text-align: center;">Mercado en Línea</h2>
    <div class="grid">
        {% for cat in categorias %}
        <a href="#" class="boton" style="background-color: {{ cat.color }};">
            <span class="emoji">{{ cat.emoji }}</span>
            {{ cat.nombre }}
        </a>
        {% endfor %}
    </div>
</body>
</html>
