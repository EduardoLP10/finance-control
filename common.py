# -*- coding: utf-8 -*-
"""Elementos de UI compartilhados entre as páginas do app (barra lateral, período)."""
from datetime import date

import streamlit as st

import db

MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
          "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def render_sidebar(caption: str = "Use o menu acima para navegar entre as páginas."):
    """Desenha o cabeçalho + seletor de mês/ano na barra lateral.

    Retorna (ano, mes) escolhidos, compartilhados via st.session_state
    para que todas as páginas usem o mesmo período de referência.
    """
    db.init_db()

    st.sidebar.title("💰 Minhas Finanças")
    st.sidebar.caption(caption)

    hoje = date.today()
    st.session_state.setdefault("ano_ref", hoje.year)
    st.session_state.setdefault("mes_ref", hoje.month)

    st.sidebar.subheader("Período de referência")
    mes_nome = st.sidebar.selectbox(
        "Mês", MESES, index=st.session_state["mes_ref"] - 1, key="sel_mes"
    )
    ano = st.sidebar.number_input(
        "Ano", min_value=2000, max_value=2100,
        value=st.session_state["ano_ref"], step=1, key="sel_ano"
    )
    mes = MESES.index(mes_nome) + 1
    st.session_state["mes_ref"] = mes
    st.session_state["ano_ref"] = ano

    st.sidebar.divider()
    st.sidebar.caption("💾 Faça backup regularmente pela página **Exportar**.")

    return ano, mes
