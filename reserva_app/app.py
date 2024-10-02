from flask import Flask, redirect, render_template, request, url_for, session
import random
import uuid, base64, hashlib, datetime
from bisect import bisect_left, bisect_right


app = Flask(__name__)

app.secret_key = 'testingsecretkey'

# Cadastrar e validar usuario
def cadastrar_usuario(u):
    password = u['password'].encode('utf-8')
    salt = uuid.uuid4().hex.encode('utf-8')
    hashed_password = hashlib.sha512(password + salt).hexdigest()

    linha = f"\n{u['nome']},{u['email']},{hashed_password},{salt.decode('utf-8')}"
    with open("usuarios.csv", "a") as file:
        file.write(linha)

def validar_usuario(email, password):
    password = password.encode('utf-8')
    with open("usuarios.csv", "r") as file:
        linhas = file.readlines()
        for linha in linhas:
            nome, user_email, user_password, salt = linha.strip().split(",")
            salt = salt.encode('utf-8')
            hashed_password = hashlib.sha512(password + salt).hexdigest()
            if email == user_email and hashed_password == user_password:
                session['user'] = nome
                return True
    return False

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

def carregar_usuarios():
    usuarios = []
    with open("usuarios.csv", "r") as file:
        for linha in file:
            nome, email, password, salt = linha.strip().split(",")
            usuario = {
                "nome": nome,
                "email": email,
            }
            usuarios.append(usuario)
    return usuarios

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

@app.route("/gerenciar/lista-usuarios", methods=["GET", "POST"])
def lista_usuarios():
    usuarios = carregar_usuarios()

    # Ordenar os usuários por nome para a busca binária
    usuarios_ordenados_por_nome = sorted(usuarios, key=lambda u: u['nome'].lower())

    usuario_encontrado = None

    if request.method == "POST":
        nome_usuario = request.form.get("nome_usuario")
        
        if nome_usuario:
            usuario_encontrado = busca_binaria_usuario(usuarios_ordenados_por_nome, nome_usuario)
        
        # Se o usuário for encontrado, mostrar somente o resultado filtrado
        if usuario_encontrado:
            return render_template("listar-usuarios.html", usuarios=[usuario_encontrado])

    # Retornar todos os usuários se não houver busca
    return render_template("listar-usuarios.html", usuarios=usuarios)

# Cadastrar, carregar e buscar salas
def cadastrar_sala(s):
    sala_id = str(random.randint(10000000, 99999999))
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
    salas.sort(key=lambda sala: sala['id'])
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
        sala_id = request.form.get("sala_id")
        
        if sala_id:
            salas = carregar_salas()
            for sala in salas:
                if sala["id"] == sala_id:
                    sala["tipo"] = tipo
                    sala["capacidade"] = capacidade
                    sala["descricao"] = descricao
            
            with open("salas.csv", "w") as file:
                for sala in salas:
                    linha = f"{sala['id']},{sala['tipo']},{sala['capacidade']},{sala['descricao']},{sala['ativa']}\n"
                    file.write(linha)
        else:
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

# Editar Sala
@app.route("/gerencia/editar-sala/<sala_id>", methods=["GET", "POST"])
def editar_sala(sala_id):
    if request.method == "POST":
        tipo = request.form.get("tipo")
        capacidade = request.form.get("capacidade")
        descricao = request.form.get("descricao")
        
        salas = carregar_salas()
        for sala in salas:
            if sala["id"] == sala_id:
                sala["tipo"] = tipo
                sala["capacidade"] = capacidade
                sala["descricao"] = descricao
        
        with open("salas.csv", "w") as file:
            for sala in salas:
                linha = f"{sala['id']},{sala['tipo']},{sala['capacidade']},{sala['descricao']},{sala['ativa']}\n"
                file.write(linha)
        
        return redirect(url_for("lista_salas"))

    salas = carregar_salas()
    sala = busca_binaria_salas(salas, sala_id)
    
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
    reservas = []
    with open("reservas.csv", "r") as file:
        for linha in file:
            id_reserva, sala_id, inicio, fim, usuario = linha.strip().split(",")
            reservas.append({
                "id_reserva": id_reserva,
                "sala_id": sala_id,
                "inicio": datetime.datetime.fromisoformat(inicio),
                "fim": datetime.datetime.fromisoformat(fim),
                "usuario": usuario
            })
    reservas.sort(key=lambda r: r["usuario"].lower())
    return reservas



def gerar_id_reserva():
    reservas = carregar_reservas()
    if reservas:
        ultimo_id = int(reservas[-1]["id_reserva"][2:])  
        return "RE" + str(ultimo_id + 1)  
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
    linha = f"{id_reserva},{sala_id},{inicio},{fim},{usuario}\n"
    with open("reservas.csv", "a") as file:
        file.write(linha)
