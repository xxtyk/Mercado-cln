from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

DB = "productos.json"

# Crear archivo si no existe
if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump([], f)

def cargar():
    with open(DB, "r") as f:
        return json.load(f)

def guardar(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)

# TIENDA (clientes)
@app.route('/')
def index():
    productos = cargar()
    return render_template('index.html', productos=productos)

# PANEL ADMIN
@app.route('/admin')
def admin():
    productos = cargar()
    return render_template('admin.html', productos=productos)

# AGREGAR PRODUCTO
@app.route('/agregar', methods=['POST'])
def agregar():
    productos = cargar()

    nuevo = {
        "nombre": request.form['nombre'],
        "precio": request.form['precio'],
        "imagen": request.form['imagen'],
        "categoria": request.form['categoria']
    }

    productos.append(nuevo)
    guardar(productos)

    return redirect('/admin')

# ELIMINAR PRODUCTO
@app.route('/eliminar/<int:index>')
def eliminar(index):
    productos = cargar()
    productos.pop(index)
    guardar(productos)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
