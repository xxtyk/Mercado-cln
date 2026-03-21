import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "mi_clave_super_secreta"  # Cambia esto si quieres más seguridad

# Usuario de prueba
USUARIO = "admin"
PASSWORD = "1234"

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == USUARIO and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("panel"))
        else:
            return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/panel")
def panel():
    if "user" in session:
        return render_template("panel.html", user=session["user"])
    else:
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/tienda")
def cliente():
    return "<h1>Tienda Mercado en Línea Culiacán</h1><p>Vista para clientes.</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
