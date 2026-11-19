# API da locadora feita com Flask.
# A interface (locadora.py) nao acessa o banco direto: ela faz requisicoes HTTP
# para esta API, e e a API que conversa com o PostgreSQL.

import hashlib
import os

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

# Dentro do Docker o banco e acessado pelo nome do servico ("db")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORTA = 5432
DB_NOME = "locadora"
DB_USUARIO = "locadora"
DB_SENHA = "locadora123"


def conectar():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORTA, dbname=DB_NOME,
        user=DB_USUARIO, password=DB_SENHA,
    )


@app.route("/status", methods=["GET"])
def status():
    # Usado pela interface para saber se a API e o banco estao no ar
    conexao = conectar()
    conexao.close()
    return jsonify({"status": "ok"})


@app.route("/filmes", methods=["GET"])
def listar_filmes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT titulo, diretor, ano, genero, duracao_min, estoque FROM filmes ORDER BY titulo")
    filmes = []
    for linha in cursor.fetchall():
        filmes.append({
            "titulo": linha[0],
            "diretor": linha[1],
            "ano": linha[2],
            "genero": linha[3],
            "duracao_min": linha[4],
            "estoque": linha[5],
        })
    conexao.close()
    return jsonify(filmes)


@app.route("/clientes", methods=["GET"])
def listar_clientes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, cpf, telefone, email FROM clientes ORDER BY nome")
    clientes = []
    for linha in cursor.fetchall():
        clientes.append({
            "nome": linha[0],
            "cpf": linha[1],
            "telefone": linha[2],
            "email": linha[3] or "",
        })
    conexao.close()
    return jsonify(clientes)


@app.route("/locacoes", methods=["GET"])
def listar_locacoes():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT filme_titulo, cliente_cpf, retirada, prevista, devolucao FROM locacoes ORDER BY id")
    locacoes = []
    for linha in cursor.fetchall():
        # Datas viram texto no formato AAAA-MM-DD para ir no JSON
        locacoes.append({
            "filme": linha[0],
            "cliente_cpf": linha[1],
            "retirada": linha[2].isoformat(),
            "prevista": linha[3].isoformat(),
            "devolucao": linha[4].isoformat() if linha[4] else None,
        })
    conexao.close()
    return jsonify(locacoes)


@app.route("/login", methods=["POST"])
def login():
    # Recebe usuario e senha, compara o hash com o que esta no banco
    dados = request.get_json()
    senha_hash = hashlib.sha256(dados["senha"].encode("utf-8")).hexdigest()

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT senha_hash FROM usuarios WHERE usuario = %s", (dados["usuario"],))
    linha = cursor.fetchone()
    conexao.close()

    if linha and linha[0] == senha_hash:
        return jsonify({"ok": True})
    return jsonify({"ok": False}), 401


@app.route("/dados", methods=["PUT"])
def salvar_dados():
    # Recebe filmes, clientes e locacoes e regrava tudo em uma transacao.
    # Se der erro no meio, o rollback desfaz e nada se perde.
    dados = request.get_json()
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM locacoes")
        cursor.execute("DELETE FROM clientes")
        cursor.execute("DELETE FROM filmes")

        for f in dados["filmes"]:
            cursor.execute(
                "INSERT INTO filmes (titulo, diretor, ano, genero, duracao_min, estoque) VALUES (%s, %s, %s, %s, %s, %s)",
                (f["titulo"], f["diretor"], f["ano"], f["genero"], f["duracao_min"], f["estoque"]),
            )
        for c in dados["clientes"]:
            cursor.execute(
                "INSERT INTO clientes (nome, cpf, telefone, email) VALUES (%s, %s, %s, %s)",
                (c["nome"], c["cpf"], c["telefone"], c["email"]),
            )
        for l in dados["locacoes"]:
            cursor.execute(
                "INSERT INTO locacoes (filme_titulo, cliente_cpf, retirada, prevista, devolucao) VALUES (%s, %s, %s, %s, %s)",
                (l["filme"], l["cliente_cpf"], l["retirada"], l["prevista"], l["devolucao"]),
            )
        conexao.commit()
    except psycopg2.Error as e:
        conexao.rollback()
        return jsonify({"erro": str(e)}), 400
    finally:
        conexao.close()

    return jsonify({"ok": True})


if __name__ == "__main__":
    # host 0.0.0.0 para aceitar conexoes de fora do conteiner
    app.run(host="0.0.0.0", port=5000)
