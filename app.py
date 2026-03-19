from flask import Flask, render_template, request

app = Flask(__name__)

# --- VENTANA 1: VISTA PARA CLIENTES ---
@app.route('/')
def index():
    # Aquí jalaremos los productos de la base de datos después
    return render_template('cliente.html')

# --- VENTANA 2: CONFIGURACIÓN (ADMIN) ---
@app.route('/admin')
def admin():
    # Aquí es donde tú gestionas todo
    return render_template('admin.html')

if __name__ == "__main__":
    app.run(debug=True)
