from flask import Flask, redirect, render_template, request, url_for
import uuid

app = Flask(__name__)

# Cadastrar e validar usuario
def cadastrar_usuario(u):
    linha = f"\n{u['nome']},{u['email']},{u['password']}"
    with open("usuarios.csv", "a") as file:
        file.write(linha)

def validar_usuario(email, password):
    with open("usuarios.csv", "r") as file:
        linhas = file.readlines()
        for linha in linhas:
            nome, user_email, user_password = linha.strip().split(",")
            if email == user_email and password == user_password:
                return True
    return False

# Cadastrar e carregar salas
def cadastrar_sala(s):
    sala_id = str(uuid.uuid4())
    linha = f"\n{sala_id},{s['tipo']},{s['capacidade']},{s['descricao']},Sim"
    with open("salas.csv", "a") as file:
        file.write(linha)

def carregar_salas():
    salas = []
    with open("salas.csv", "r") as file:
        for linha in file:
            sala_id, tipo, capacidade, descricao, ativa = linha.strip().split(",")
            sala = {
                "id": sala_id,
                "tipo": tipo,
                "capacidade": capacidade,
                "descricao": descricao,
                "ativa": ativa
            }
            salas.append(sala)
    return salas

# Rotas
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/cadastro", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        password = request.form.get("password")
        cadastrar_usuario({"nome": nome, "email": email, "password": password})
        return redirect(url_for("index"))
    return render_template("cadastro.html")

@app.route("/gerenciar/lista-salas")
def lista_salas():
    salas = carregar_salas()
    return render_template("listar-salas.html", salas=salas)

# Cadastrar salas
@app.route("/gerenciar/cadastrar-salas", methods=["GET", "POST"])
def cadastrar_salas():
    if request.method == "POST":
        tipo = request.form.get("tipo")
        capacidade = request.form.get("capacidade")
        descricao = request.form.get("descricao")
        cadastrar_sala({"tipo": tipo, "capacidade": capacidade, "descricao": descricao})
        return redirect(url_for("lista_salas"))
    return render_template("cadastrar-sala.html")

# Excluir salas
@app.route("/gerenciar/excluir-sala/<sala_id>", methods=["POST"])
def excluir_sala(sala_id):
    salas = carregar_salas()
    salas = [sala for sala in salas if sala["id"] != sala_id]
    
    with open("salas.csv", "w") as file:
        for sala in salas:
            linha = f"{sala['id']},{sala['tipo']},{sala['capacidade']},{sala['descricao']}\n"
            file.write(linha)
    
    return redirect(url_for("lista_salas"))

# Desativar salas
@app.route("/gerenciar/desativar-sala/<sala_id>", methods=["POST"])
def desativar_sala(sala_id):
    salas = carregar_salas()
    for sala in salas:
        if sala["id"] == sala_id:
            sala["ativa"] = "Não" if sala["ativa"] == "Sim" else "Sim"
    
    with open("salas.csv", "w") as file:
        for sala in salas:
            linha = f"{sala['id']},{sala['tipo']},{sala['capacidade']},{sala['descricao']},{sala['ativa']}\n"
            file.write(linha)
    
    return redirect(url_for("lista_salas"))

@app.route("/reservas")
def reservas():
    return render_template("reservas.html")

@app.route("/reservaa")
def detalhe_reserva():
    return render_template("detalhe_reserva.html")

@app.route("/reservar")
def reservar_sala():
    return render_template("reservar-sala.html")

# TODO: Editar salas
#       Login e cadastro de usuários
#       detalhe-reserva