# -*- coding: utf-8 -*-
"""
app.py — Dashboard principal do Controle de Finanças Pessoais.

Para rodar localmente:
    streamlit run app.py
"""
import plotly.express as px
import streamlit as st

import common
import db

st.set_page_config(
    page_title="Controle de Finanças",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

ano, mes = common.render_sidebar()
mes_nome = common.MESES[mes - 1]

# ----------------------------------------------------------------- Título --
st.title("Painel de Finanças")
st.caption(f"Resumo de **{mes_nome} de {ano}**")

# --------------------------------------------------------------- Métricas --
receitas_mes = db.total_por_tipo(ano, mes, "Receita")
despesas_mes = db.total_por_tipo(ano, mes, "Despesa")
saldo_mes = receitas_mes - despesas_mes

col1, col2, col3 = st.columns(3)
col1.metric("Receitas do mês", f"R$ {receitas_mes:,.2f}")
col2.metric("Despesas do mês", f"R$ {despesas_mes:,.2f}")
col3.metric("Saldo do mês", f"R$ {saldo_mes:,.2f}",
            delta=f"R$ {saldo_mes:,.2f}", delta_color="normal")

st.divider()

receitas_geral = db.total_geral_por_tipo("Receita")
despesas_geral = db.total_geral_por_tipo("Despesa")
saldo_geral = receitas_geral - despesas_geral

st.subheader("Totais gerais (todos os lançamentos)")
g1, g2, g3 = st.columns(3)
g1.metric("Total de receitas", f"R$ {receitas_geral:,.2f}")
g2.metric("Total de despesas", f"R$ {despesas_geral:,.2f}")
g3.metric("Saldo acumulado", f"R$ {saldo_geral:,.2f}")

st.divider()

# ------------------------------------------------------------------ Gráficos
col_pizza, col_evolucao = st.columns(2)

with col_pizza:
    st.subheader("Despesas por categoria (mês selecionado)")
    df_cat = db.despesas_por_categoria(ano, mes)
    if df_cat.empty:
        st.info("Nenhuma despesa lançada neste mês ainda.")
    else:
        fig = px.pie(df_cat, names="Categoria", values="Valor", hole=0.45)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=True, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, width='stretch')

with col_evolucao:
    st.subheader("Evolução mensal (últimos 6 meses)")
    df_evo = db.evolucao_mensal(6)
    if df_evo.empty:
        st.info("Ainda não há lançamentos suficientes para mostrar a evolução.")
    else:
        df_plot = df_evo.melt(id_vars="Mes", value_vars=["Receita", "Despesa"],
                               var_name="Tipo", value_name="Valor")
        fig2 = px.bar(df_plot, x="Mes", y="Valor", color="Tipo", barmode="group",
                       color_discrete_map={"Receita": "#1F7A1F", "Despesa": "#C00000"})
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title="")
        st.plotly_chart(fig2, width='stretch')

st.divider()

# ------------------------------------------------------------- Últimos itens
st.subheader("Últimos lançamentos")
df_recent = db.get_transacoes_df().head(8)
if df_recent.empty:
    st.info("Nenhum lançamento cadastrado. Vá até a página **Lançamentos** para começar.")
else:
    df_show = df_recent.rename(columns={
        "data": "Data", "tipo": "Tipo", "categoria": "Categoria",
        "descricao": "Descrição", "valor": "Valor (R$)",
        "forma_pagamento": "Forma de Pagamento", "status": "Status",
    }).drop(columns=["id"])
    st.dataframe(df_show, width='stretch', hide_index=True)
