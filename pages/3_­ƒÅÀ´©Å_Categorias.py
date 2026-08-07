# -*- coding: utf-8 -*-
"""Página de Categorias — adicionar ou remover categorias de receita/despesa."""
import streamlit as st

import common
import db

st.set_page_config(page_title="Categorias", page_icon="🏷️", layout="wide")
common.render_sidebar()

st.title("🏷️ Categorias")
st.caption("As categorias cadastradas aqui aparecem nos menus da página Lançamentos e Orçamento.")

st.subheader("Adicionar nova categoria")
with st.form("form_nova_categoria", clear_on_submit=True):
    c1, c2 = st.columns([2, 1])
    nome = c1.text_input("Nome da categoria")
    tipo = c2.selectbox("Tipo", ["Despesa", "Receita"])
    enviado = st.form_submit_button("➕ Adicionar")
    if enviado:
        ok, msg = db.add_categoria(nome, tipo)
        (st.success if ok else st.error)(msg)
        if ok:
            st.rerun()

st.divider()
st.subheader("Categorias cadastradas")

df = db.get_categorias_df()
if df.empty:
    st.info("Nenhuma categoria cadastrada ainda.")
else:
    col_desp, col_rec = st.columns(2)
    for coluna, tipo_filtro, titulo in (
        (col_desp, "Despesa", "Despesas"), (col_rec, "Receita", "Receitas")
    ):
        with coluna:
            st.markdown(f"**{titulo}**")
            subset = df[df["Tipo"] == tipo_filtro]["Categoria"].tolist()
            if not subset:
                st.caption("Nenhuma categoria.")
            for nome_cat in subset:
                cc1, cc2 = st.columns([4, 1])
                cc1.write(nome_cat)
                if cc2.button("🗑️", key=f"del_{tipo_filtro}_{nome_cat}", help=f"Excluir '{nome_cat}'"):
                    db.delete_categoria(nome_cat)
                    st.rerun()

st.caption(
    "⚠️ Excluir uma categoria não apaga lançamentos já feitos com ela, "
    "mas ela deixa de aparecer nos menus suspensos."
)
