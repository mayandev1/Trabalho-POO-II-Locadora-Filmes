-- Tabelas do banco da locadora
-- Esse script roda sozinho na primeira vez que o conteiner sobe

CREATE TABLE usuarios (
    usuario     VARCHAR(50) PRIMARY KEY,
    senha_hash  VARCHAR(64) NOT NULL
);

CREATE TABLE filmes (
    titulo       VARCHAR(200) PRIMARY KEY,
    diretor      VARCHAR(200) NOT NULL,
    ano          INTEGER NOT NULL,
    genero       VARCHAR(50) NOT NULL,
    duracao_min  INTEGER NOT NULL,
    estoque      INTEGER NOT NULL CHECK (estoque >= 0)
);

CREATE TABLE clientes (
    cpf       VARCHAR(20) PRIMARY KEY,
    nome      VARCHAR(200) NOT NULL,
    telefone  VARCHAR(30) NOT NULL,
    email     VARCHAR(200)
);

CREATE TABLE locacoes (
    id            SERIAL PRIMARY KEY,
    filme_titulo  VARCHAR(200) NOT NULL REFERENCES filmes(titulo),
    cliente_cpf   VARCHAR(20) NOT NULL REFERENCES clientes(cpf),
    retirada      DATE NOT NULL,
    prevista      DATE NOT NULL,
    devolucao     DATE
);

-- Admin padrao: usuario admin, senha admin123 (guardada como hash SHA-256)
INSERT INTO usuarios VALUES ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9');
