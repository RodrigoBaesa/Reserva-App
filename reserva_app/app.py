from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/cadastro")
def cadastrar():
    return render_template("cadastro.html")

@app.route("/gerenciar/lista-salas")
def lista():
    return render_template("listar-salas.html")

@app.route("/gerenciar/cadastrar-salas")
def cadastrar_salas():
    return render_template("cadastrar-sala.html")

@app.route("/reservas")
def reservas():
    return render_template("reservas.html")

@app.route("/reserva/<id>")
def detalhe_reserva():
    return render_template("detalhe_reserva.html")