from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "12345"

USUARIO = "admin"
PASSWORD = "1234"

DB = "productos.json"
PEDIDOS = "pedidos.json"

# crear archivos si no existen
for archivo in [DB, PEDIDOS]:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)

def cargar():
    with open(DB, "r") as f:
        return json.load(f)

def guardar(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)

# TIENDA
@app.route('/')
def index():
    productos = cargar()
    categoria = request.args.get('categoria')

    if categoria:
        productos = [p for p in productos if p['categoria'] == categoria]

    categorias = list(set([p['categoria'] for p in cargar()]))

    return render_template('index.html', productos=productos, categorias=categorias)

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['usuario'] == USUARIO and request.form['password'] == PASSWORD:
            session['admin'] = True
            return redirect('/admin')

    return render_template('login.html')

# ADMIN
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

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

# GUARDAR PEDIDO
@app.route('/guardar_pedido', methods=['POST'])
def guardar_pedido():
    data = request.json

    with open(PEDIDOS, "r") as f:
        pedidos = json.load(f)

    pedidos.append(data)

    with open(PEDIDOS, "w") as f:
        json.dump(pedidos, f, indent=4)

    return {"status": "ok"}

if __name__ == '__main__':
    app.run(debug=True)
