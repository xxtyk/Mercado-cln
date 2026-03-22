import os
from flask import Flask, render_template

app = Flask(__name__)

# ==============================
# RUTAS SIMPLES DE PRUEBA
# ==============================
@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

# ==============================
# SERVIDOR
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
