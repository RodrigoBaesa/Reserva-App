from flask import Flask, redirect, render_template, request, url_for, session
import mysql.connector
import random
import uuid, base64, hashlib, datetime
from bisect import bisect_left, bisect_right


app = Flask(__name__)

app.secret_key = 'testingsecretkey'

def conexao_abrir():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin",
        database="reservas"
    )

# Cadastrar e validar usuario
def cadastrar_usuario(u):
    con = conexao_abrir()
    cursor = con.cursor()

    senha_hash = hashlib.sha512(u['password'].encode('utf-8')).hexdigest()

    query = "INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)"
    cursor.execute(query, (u['nome'], u['email'], senha_hash))

    con.commit()
    cursor.close()
    con.close()

def validar_usuario(email, password):
    con = conexao_abrir()
    cursor = con.cursor(dictionary=True)

    query = "SELECT * FROM usuario WHERE email = %s"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    cursor.close()
    con.close()

    if usuario and usuario['senha'] == hashlib.sha512(password.encode('utf-8')).hexdigest():
        session['user'] = usuario['nome']
        return True
    return False

def carregar_usuarios():
    conn = conexao_abrir()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT nome, email FROM usuario")
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()
    return usuarios

@app.route("/", methods=["GET", "POST"])
def mensagem_erro():
    error_message = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if validar_usuario(email, password):
            return redirect(url_for("reservas"))
        else:
            error_message = "E-mail ou senha incorretos. Tente novamente."
    return render_template("login.html", error_message=error_message)

def busca_binaria_usuario(usuarios, chave):
    inicio = 0
    fim = len(usuarios) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        if usuarios[meio]['nome'].lower() == chave.lower():
            return usuarios[meio]
        elif usuarios[meio]['nome'].lower() < chave.lower():
            inicio = meio + 1
        else:
            fim = meio - 1
    return None

def busca_binaria_email(usuarios, email):
    inicio = 0
    fim = len(usuarios) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        if usuarios[meio]['email'].lower() == email.lower():
            return usuarios[meio]
        elif usuarios[meio]['email'].lower() < email.lower():
            inicio = meio + 1
        else:
            fim = meio - 1
    return None


@app.route("/gerenciar/lista-usuarios", methods=["GET", "POST"])
def lista_usuarios():
    usuarios = carregar_usuarios()

    usuarios_sortedname = sorted(usuarios, key=lambda u: u['nome'].lower())
    usuarios_sortedemail = sorted(usuarios, key=lambda u: u['email'].lower())

    usuario_encontrado = None

    if request.method == "POST":
        nome_usuario = request.form.get("nome_usuario")
        email_usuario = request.form.get("email_usuario")
        
        if nome_usuario:
            usuario_encontrado = busca_binaria_usuario(usuarios_sortedname, nome_usuario)
        
        elif email_usuario:
            usuario_encontrado = busca_binaria_email(usuarios_sortedemail, email_usuario)
        
        if usuario_encontrado:
            return render_template("listar-usuarios.html", usuarios=[usuario_encontrado])

    return render_template("listar-usuarios.html", usuarios=usuarios)

# Cadastrar, carregar e buscar salas
def cadastrar_sala(s):
    con = conexao_abrir()
    cursor = con.cursor()

    query = "INSERT INTO salas (numero, tipo, capacidade, descricao) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (random.randint(1, 10000000), s['tipo'], s['capacidade'], s['descricao']))

    con.commit()
    cursor.close()
    con.close()

def carregar_salas():
    con = conexao_abrir()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM salas")
    salas = cursor.fetchall()

    cursor.close()
    con.close()
    return salas

def busca_binaria_salas(salas, sala_id):
    inicio = 0
    fim = len(salas) - 1

    while inicio <= fim:
        meio = (inicio + fim) // 2
        sala_atual = salas[meio]

        if sala_atual["id"] == sala_id:
            return sala_atual
        elif sala_atual["id"] < sala_id:
            inicio = meio + 1
        else:
            fim = meio - 1

    return None

# Rotas
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if validar_usuario(email, password):
            return redirect(url_for("reservas"))
        else:
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user', None) 
    return redirect(url_for("login.html"))

@app.route("/cadastro", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        password = request.form.get("password")
        cadastrar_usuario({"nome": nome, "email": email, "password": password})
        return redirect(url_for("index"))
    return render_template("cadastro.html")

@app.route("/gerenciar/lista-salas", methods=["GET", "POST"])
def lista_salas():
    salas = carregar_salas()
    sala_encontrada = None

    if request.method == "POST":
        sala_id = request.form.get("sala_id")
        sala_encontrada = busca_binaria_salas(salas, sala_id)

    return render_template("listar-salas.html", salas=salas, sala_encontrada=sala_encontrada)


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
@app.route("/gerenciar/excluir-sala/<int:sala_id>", methods=["POST"])
def excluir_sala(sala_id):
    con = conexao_abrir()
    cursor = con.cursor()

    query = "DELETE FROM salas WHERE id = %s"
    cursor.execute(query, (sala_id,))

    con.commit()
    cursor.close()
    con.close()

    return redirect(url_for("lista_salas"))

# Desativar salas
@app.route("/gerenciar/desativar-sala/<int:sala_id>", methods=["POST"])
def desativar_sala(sala_id):
    con = conexao_abrir()
    cursor = con.cursor(dictionary=True)

    query_select = "SELECT ativa FROM salas WHERE id = %s"
    cursor.execute(query_select, (sala_id,))
    sala = cursor.fetchone()

    nova_ativa = "Não" if sala["ativa"] == "Sim" else "Sim"

    query_update = "UPDATE salas SET ativa = %s WHERE id = %s"
    cursor.execute(query_update, (nova_ativa, sala_id))

    con.commit()
    cursor.close()
    con.close()

    return redirect(url_for("lista_salas"))


# Editar Sala
@app.route("/gerenciar/editar-sala/<int:sala_id>", methods=["GET", "POST"])
def editar_sala(sala_id):
    con = conexao_abrir()
    cursor = con.cursor(dictionary=True)

    if request.method == "POST":
        tipo = request.form.get("tipo")
        capacidade = request.form.get("capacidade")
        descricao = request.form.get("descricao")

        query_update = "UPDATE salas SET tipo = %s, capacidade = %s, descricao = %s WHERE id = %s"
        cursor.execute(query_update, (tipo, capacidade, descricao, sala_id))

        con.commit()
        cursor.close()
        con.close()

        return redirect(url_for("lista_salas"))
    
    query_select = "SELECT * FROM salas WHERE id = %s"
    cursor.execute(query_select, (sala_id,))
    sala = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template("cadastrar-sala.html", sala=sala, editar=True)

# Reservas
"""@app.route("/reservas")
def reservas():
    return render_template("reservas.html")
"""

@app.route("/reservas", methods=["GET", "POST"])
def reservas():
    reservas = carregar_reservas()
    reservas_filtradas = reservas  
    reserva_encontrada = None  

    if request.method == "POST":
        id_reserva = request.form.get("id_reserva")
        inicio = request.form.get("inicio")
        fim = request.form.get("fim")
        usuario = request.form.get("usuario")  

        if id_reserva:
            reserva_encontrada = busca_binaria_reserva(reservas, id_reserva)
            if reserva_encontrada:
                return render_template("reservas.html", reservas=[reserva_encontrada], reserva_encontrada=reserva_encontrada)

        if usuario:
            reservas_filtradas = buscar_reservas_por_usuario(reservas, usuario)
            return render_template("reservas.html", reservas=reservas_filtradas)

        if inicio and fim:
            inicio_dt = datetime.datetime.fromisoformat(inicio)
            fim_dt = datetime.datetime.fromisoformat(fim)
            reservas_filtradas = [reserva for reserva in reservas if reserva["inicio"] >= inicio_dt and reserva["fim"] <= fim_dt]

            if usuario:
                reservas_filtradas = [reserva for reserva in reservas_filtradas if reserva["usuario"].lower() == usuario.lower()]

            return render_template("reservas.html", reservas=reservas_filtradas)

    return render_template("reservas.html", reservas=reservas, reserva_encontrada=reserva_encontrada)

def carregar_reservas():
    con = conexao_abrir()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reservas")
    reservas = cursor.fetchall()

    for reserva in reservas:
        reserva["inicio"] = datetime.datetime.fromisoformat(reserva["inicio"].isoformat())
        reserva["fim"] = datetime.datetime.fromisoformat(reserva["fim"].isoformat())

    cursor.close()
    con.close()
    return reservas

def gerar_id_reserva():
    con = conexao_abrir()
    cursor = con.cursor()

    cursor.execute("SELECT MAX(id_reserva) FROM reservas")
    ultimo_id = cursor.fetchone()[0]

    cursor.close()
    con.close()

    if ultimo_id:
        novo_id = int(ultimo_id[2:]) + 1
        return "RE" + str(novo_id)
    return "RE1"

def verificar_conflito(sala_id, inicio, fim):
    reservas = carregar_reservas()
    for reserva in reservas:
        if reserva["sala_id"] == sala_id:
            if not (fim <= reserva["inicio"] or inicio >= reserva["fim"]):
                return True
    return False

def busca_binaria_reserva(reservas, id_reserva):
    inicio = 0
    fim = len(reservas) - 1

    while inicio <= fim:
        meio = (inicio + fim) // 2
        reserva_atual = reservas[meio]

        if reserva_atual["id_reserva"] == id_reserva:
            return reserva_atual
        elif reserva_atual["id_reserva"] < id_reserva:
            inicio = meio + 1
        else:
            fim = meio - 1

    return None

def busca_binaria_intervalo(reservas, inicio_periodo, fim_periodo):

    reservas_ordenadas = sorted(reservas, key=lambda x: x["inicio"])

    indices_inicio = bisect_left([reserva["inicio"] for reserva in reservas_ordenadas], inicio_periodo)
    indices_fim = bisect_right([reserva["fim"] for reserva in reservas_ordenadas], fim_periodo)

    return reservas_ordenadas[indices_inicio:indices_fim]


def buscar_reservas_por_usuario(reservas, usuario):
    return [reserva for reserva in reservas if reserva["usuario"].lower() == usuario.lower()]


@app.route("/detalhe-reserva")
def detalhe_reserva():
    id_reserva = request.args.get("id_reserva")
    sala_id = request.args.get("sala_id")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")
    inicio_dt = datetime.datetime.fromisoformat(inicio)
    fim_dt = datetime.datetime.fromisoformat(fim)

    salas = carregar_salas()
    sala = next((s for s in salas if s["id"] == sala_id), None)

    usuario = session['user']

    return render_template("reserva/detalhe-reserva.html", id_reserva=id_reserva, sala=sala, inicio=inicio_dt, fim=fim_dt, usuario=usuario)


@app.route("/reservar", methods=["GET", "POST"])
def reservar_sala():
    salas = carregar_salas()
    if request.method == "POST":
        sala_id = request.form.get("sala")
        inicio = request.form.get("inicio")
        fim = request.form.get("fim")

        inicio_dt = datetime.datetime.fromisoformat(inicio)
        fim_dt = datetime.datetime.fromisoformat(fim)

        if verificar_conflito(sala_id, inicio_dt, fim_dt):
            return render_template("reservar-sala.html", salas=salas, error="Conflito de horário! Escolha outro horário.")
        
        usuario = session['user']  
        id_reserva = gerar_id_reserva()  
        salvar_reserva(id_reserva, sala_id, inicio, fim, usuario)
        
        return redirect(url_for("detalhe_reserva", id_reserva=id_reserva, sala_id=sala_id, inicio=inicio, fim=fim))

    return render_template("reservar-sala.html", salas=salas)

def salvar_reserva(id_reserva, sala_id, inicio, fim, usuario):
    con = conexao_abrir()
    cursor = con.cursor()

    query = "INSERT INTO reservas (id_reserva, sala_id, inicio, fim, usuario) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (id_reserva, sala_id, inicio, fim, usuario))

    con.commit()
    cursor.close()
    con.close()