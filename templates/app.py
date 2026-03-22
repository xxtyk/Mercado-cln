from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

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
    if request.method
