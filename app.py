from flask import Flask, render_template

app = Flask(__name__)

productos = [
    {"nombre": "Mascarilla para cabello", "precio": 160},
    {"nombre": "Rasuradora", "precio": 250},
    {"nombre": "Pechuga de pollo", "precio": 120}
]

@app.route('/')
def index():
    return render_template('index.html', productos=productos)

if __name__ == '__main__':
    app.run(debug=True)
