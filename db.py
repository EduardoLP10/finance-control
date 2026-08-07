# -*- coding: utf-8 -*-
"""
db.py — Camada de acesso a dados do app de Controle de Finanças.

Usa SQLite (arquivo local "financas.db"). Todas as páginas do app
importam este módulo para ler/gravar dados, então a lógica de banco
fica centralizada em um único lugar.
"""
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).parent / "financas.db"

CATEGORIAS_PADRAO = [
    ("Moradia", "Despesa"),
    ("Alimentação", "Despesa"),
    ("Transporte", "Despesa"),
    ("Saúde", "Despesa"),
    ("Educação", "Despesa"),
    ("Lazer", "Despesa"),
    ("Vestuário", "Despesa"),
    ("Contas e Assinaturas", "Despesa"),
    ("Cuidados Pessoais", "Despesa"),
    ("Outras Despesas", "Despesa"),
    ("Salário", "Receita"),
    ("Freelance/Renda Extra", "Receita"),
    ("Investimentos", "Receita"),
    ("Outras Receitas", "Receita"),
]

FORMAS_PAGAMENTO = [
    "Dinheiro", "Cartão de Débito", "Cartão de Crédito", "Pix",
    "Transferência", "Boleto",
]


@st.cache_resource(show_spinner=False)
def get_connection():
    """Retorna uma conexão SQLite reaproveitável entre reruns do Streamlit."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Cria as tabelas (se não existirem) e semeia categorias padrão."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            tipo TEXT NOT NULL CHECK (tipo IN ('Receita','Despesa'))
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('Receita','Despesa')),
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL CHECK (valor >= 0),
            forma_pagamento TEXT,
            status TEXT DEFAULT 'Pago'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ano INTEGER NOT NULL,
            mes INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            valor_orcado REAL NOT NULL DEFAULT 0,
            UNIQUE(ano, mes, categoria)
        )
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM categorias")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO categorias (nome, tipo) VALUES (?,?)", CATEGORIAS_PADRAO)
        conn.commit()


# ---------------------------------------------------------------- Categorias
def get_categorias(tipo: str | None = None) -> list[str]:
    conn = get_connection()
    if tipo:
        rows = conn.execute(
            "SELECT nome FROM categorias WHERE tipo=? ORDER BY nome", (tipo,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT nome FROM categorias ORDER BY tipo, nome").fetchall()
    return [r[0] for r in rows]


def get_categorias_df() -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query("SELECT nome AS Categoria, tipo AS Tipo FROM categorias ORDER BY tipo, nome", conn)


def add_categoria(nome: str, tipo: str) -> tuple[bool, str]:
    nome = nome.strip()
    if not nome:
        return False, "Informe um nome de categoria."
    conn = get_connection()
    try:
        conn.execute("INSERT INTO categorias (nome, tipo) VALUES (?,?)", (nome, tipo))
        conn.commit()
        return True, f"Categoria '{nome}' adicionada."
    except sqlite3.IntegrityError:
        return False, f"A categoria '{nome}' já existe."


def delete_categoria(nome: str):
    conn = get_connection()
    conn.execute("DELETE FROM categorias WHERE nome=?", (nome,))
    conn.commit()


# --------------------------------------------------------------- Transações
def add_transacao(data_lanc: date, tipo: str, categoria: str, descricao: str,
                   valor: float, forma_pagamento: str, status: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO transacoes (data, tipo, categoria, descricao, valor, forma_pagamento, status) "
        "VALUES (?,?,?,?,?,?,?)",
        (data_lanc.isoformat(), tipo, categoria, descricao, valor, forma_pagamento, status),
    )
    conn.commit()


def update_transacao(id_: int, data_lanc: date, tipo: str, categoria: str, descricao: str,
                      valor: float, forma_pagamento: str, status: str):
    conn = get_connection()
    conn.execute(
        "UPDATE transacoes SET data=?, tipo=?, categoria=?, descricao=?, valor=?, "
        "forma_pagamento=?, status=? WHERE id=?",
        (data_lanc.isoformat(), tipo, categoria, descricao, valor, forma_pagamento, status, id_),
    )
    conn.commit()


def delete_transacao(id_: int):
    conn = get_connection()
    conn.execute("DELETE FROM transacoes WHERE id=?", (id_,))
    conn.commit()


def get_transacoes_df(ano: int | None = None, mes: int | None = None) -> pd.DataFrame:
    conn = get_connection()
    query = "SELECT id, data, tipo, categoria, descricao, valor, forma_pagamento, status FROM transacoes"
    params = []
    conds = []
    if ano is not None:
        conds.append("strftime('%Y', data) = ?")
        params.append(f"{ano:04d}")
    if mes is not None:
        conds.append("strftime('%m', data) = ?")
        params.append(f"{mes:02d}")
    if conds:
        query += " WHERE " + " AND ".join(conds)
    query += " ORDER BY data DESC, id DESC"
    df = pd.read_sql_query(query, conn, params=params)
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"]).dt.date
    return df


# ------------------------------------------------------------------ Resumos
def total_por_tipo(ano: int, mes: int, tipo: str) -> float:
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM transacoes "
        "WHERE tipo=? AND strftime('%Y',data)=? AND strftime('%m',data)=?",
        (tipo, f"{ano:04d}", f"{mes:02d}"),
    ).fetchone()
    return row[0] or 0.0


def total_geral_por_tipo(tipo: str) -> float:
    conn = get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(valor),0) FROM transacoes WHERE tipo=?", (tipo,)
    ).fetchone()
    return row[0] or 0.0


def despesas_por_categoria(ano: int, mes: int) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT categoria AS Categoria, COALESCE(SUM(valor),0) AS Valor FROM transacoes "
        "WHERE tipo='Despesa' AND strftime('%Y',data)=? AND strftime('%m',data)=? "
        "GROUP BY categoria HAVING Valor > 0 ORDER BY Valor DESC",
        conn, params=(f"{ano:04d}", f"{mes:02d}"),
    )
    return df


def evolucao_mensal(n_meses: int = 6) -> pd.DataFrame:
    """Receitas e despesas por mês (YYYY-MM), últimos n_meses com lançamentos."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT strftime('%Y-%m', data) AS Mes, tipo AS Tipo, SUM(valor) AS Valor "
        "FROM transacoes GROUP BY Mes, Tipo ORDER BY Mes",
        conn,
    )
    if df.empty:
        return df
    pivot = df.pivot_table(index="Mes", columns="Tipo", values="Valor", fill_value=0).reset_index()
    for col in ("Receita", "Despesa"):
        if col not in pivot.columns:
            pivot[col] = 0.0
    return pivot.tail(n_meses)


# -------------------------------------------------------------- Orçamentos
def set_orcamento(ano: int, mes: int, categoria: str, valor: float):
    conn = get_connection()
    conn.execute(
        "INSERT INTO orcamentos (ano, mes, categoria, valor_orcado) VALUES (?,?,?,?) "
        "ON CONFLICT(ano, mes, categoria) DO UPDATE SET valor_orcado=excluded.valor_orcado",
        (ano, mes, categoria, valor),
    )
    conn.commit()


def get_orcamento_df(ano: int, mes: int) -> pd.DataFrame:
    """Uma linha por categoria de despesa, com orçado e realizado."""
    conn = get_connection()
    orcado = pd.read_sql_query(
        "SELECT categoria, valor_orcado FROM orcamentos WHERE ano=? AND mes=?",
        conn, params=(ano, mes),
    )
    categorias_despesa = get_categorias("Despesa")
    base = pd.DataFrame({"Categoria": categorias_despesa})
    base = base.merge(orcado.rename(columns={"categoria": "Categoria", "valor_orcado": "Orçado"}),
                       on="Categoria", how="left")
    base["Orçado"] = base["Orçado"].fillna(0.0)

    realizado = despesas_por_categoria(ano, mes).rename(columns={"Valor": "Realizado"})
    base = base.merge(realizado, on="Categoria", how="left")
    base["Realizado"] = base["Realizado"].fillna(0.0)
    base["Diferença"] = base["Orçado"] - base["Realizado"]
    base["% Utilizado"] = base.apply(
        lambda r: (r["Realizado"] / r["Orçado"] * 100) if r["Orçado"] > 0 else 0.0, axis=1
    )
    return base
