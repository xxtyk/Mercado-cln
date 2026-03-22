from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

# archivo donde se guardan productos
DB = "productos.json"

# crear archivo si no existe
if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump([], f)

# funciones
def cargar_productos():
    with open(DB, "r") as f:
        return json.load(f)

def guardar_productos(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)

# INICIO (TIENDA)
@app.route('/')
def inicio():
    productos = cargar_productos()
    return render_template('index.html', productos=productos)

# AGREGAR PRODUCTO
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        descripcion = request.form.get('descripcion', '')
        categoria = request.form.get('categoria', '')

        imagen = request.files['imagen']
        url_imagen = ""

        if imagen:
            ruta = "static/" + imagen.filename
            imagen.save(ruta)
            url_imagen = ruta

        producto = {
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "categoria": categoria,
            "imagen": url_imagen
        }

        datos = cargar_productos()
        datos.append(producto)
        guardar_productos(datos)

        return redirect('/')

    return render_template('agregar.html')


if __name__ == '__main__':
    app.run(debug=True)
