# Locadora de Filmes

Trabalho de Programação Orientada a Objetos II (UFPI - CSHNB).

Sistema de locadora feito com PySide6. Os dados ficam em um banco PostgreSQL e a
interface conversa com ele por meio de uma API Flask. O banco e a API rodam em
contêineres Docker.

## Como rodar

```bash
docker compose up -d --build
pip install -r requirements.txt
python locadora.py
```

Login do administrador: `admin` / `admin123`.

As mudanças de cada entrega estão no `changelog.txt`.
