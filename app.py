from flask import Flask, render_template, request, redirect, session, jsonify
import json
import os

app = Flask(__name__)
# Cambia esta clave por algo más largo después por seguridad
app.secret_key = "12345mercado_cln_secret"

USUARIO = "admin"
PASSWORD = "1234"

DB = "productos.json"
PEDIDOS = "pedidos.json"

# Crear archivos si no existen en el servidor
for archivo in [DB, PEDIDOS]:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)

def cargar():
    try:
        with open(DB, "r") as f:
            return json.load(f)
    except:
        return []

def guardar(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)

# --- RUTAS DE LA TIENDA ---

@app.route('/')
def index():
    productos = cargar()
    return render_template('index.html', productos=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Verificamos que los datos coincidan
        if request.form.get('usuario') == USUARIO and request.form.get('password') == PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Usuario o contraseña incorrectos"
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')
    productos = cargar()
    return render_template('admin.html', productos=productos)

@app.route('/agregar', methods=['POST'])
def agregar():
    if not session.get('admin'):
        return redirect('/login')
        
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

@app.route('/eliminar/<int:index>')
def eliminar(index):
    if not session.get('admin'):
        return redirect('/login')
    productos = cargar()
    if 0 <= index < len(productos):
        productos.pop(index)
        guardar(productos)
    return redirect('/admin')

@app.route('/guardar_pedido', methods=['POST'])
def guardar_pedido():
    data = request.json
    try:
        with open(PEDIDOS, "r") as f:
            pedidos = json.load(f)
    except:
        pedidos = []
        
    pedidos.append(data)
    with open(PEDIDOS, "w") as f:
        json.dump(pedidos, f, indent=4)
    return jsonify({"status": "ok"})

@app.route('/pedidos')
def pedidos():
    if not session.get('admin'):
        return redirect('/login')
    try:
        with open(PEDIDOS, "r") as f:
            lista_pedidos = json.load(f)
    except:
        lista_pedidos = []
    return render_template('pedidos.html', pedidos=lista_pedidos)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    # Ajuste para que Render asigne el puerto correctamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
