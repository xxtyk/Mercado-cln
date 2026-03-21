from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "mi_clave_super_secreta"

# Usuario de prueba
USUARIO = "admin"
PASSWORD = "1234"

# --- Rutas ---

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

# --- Ejecutar ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
