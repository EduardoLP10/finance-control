# -*- coding: utf-8 -*-
"""Página de Exportar — baixar backup dos lançamentos em CSV ou Excel."""
from io import BytesIO

import pandas as pd
import streamlit as st

import common
import db

st.set_page_config(page_title="Exportar", page_icon="📤", layout="wide")
common.render_sidebar()

st.title("📤 Exportar / Backup")
st.caption(
    "Baixe seus dados regularmente. Isso é importante porque, em hospedagens "
    "gratuitas, o arquivo de banco de dados pode ser reiniciado quando o app "
    "é atualizado ou reimplantado."
)

df = db.get_transacoes_df()

if df.empty:
    st.info("Nenhum lançamento para exportar ainda.")
else:
    df_export = df.drop(columns=["id"]).rename(columns={
        "data": "Data", "tipo": "Tipo", "categoria": "Categoria",
        "descricao": "Descrição", "valor": "Valor", "forma_pagamento": "Forma de Pagamento",
        "status": "Status",
    })

    st.subheader("Prévia dos dados")
    st.dataframe(df_export, width='stretch', hide_index=True)

    csv_bytes = df_export.to_csv(index=False).encode("utf-8-sig")

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Transações")
    excel_bytes = buffer.getvalue()

    c1, c2 = st.columns(2)
    c1.download_button(
        "⬇️ Baixar CSV", data=csv_bytes, file_name="financas_backup.csv",
        mime="text/csv", width='stretch',
    )
    c2.download_button(
        "⬇️ Baixar Excel", data=excel_bytes, file_name="financas_backup.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch',
    )

st.divider()
st.subheader("Importar lançamentos de um CSV")
st.caption(
    "O arquivo precisa ter as colunas: Data, Tipo, Categoria, Descrição, Valor, "
    "Forma de Pagamento, Status. Use o CSV exportado daqui como modelo."
)
arquivo = st.file_uploader("Escolha um arquivo CSV", type=["csv"])
if arquivo is not None:
    try:
        df_import = pd.read_csv(arquivo)
        st.dataframe(df_import.head(10), width='stretch', hide_index=True)
        if st.button("✅ Confirmar importação"):
            colunas_esperadas = {"Data", "Tipo", "Categoria", "Descrição", "Valor",
                                  "Forma de Pagamento", "Status"}
            if not colunas_esperadas.issubset(df_import.columns):
                st.error(f"O CSV precisa conter as colunas: {', '.join(sorted(colunas_esperadas))}")
            else:
                importados = 0
                for _, row in df_import.iterrows():
                    data_val = pd.to_datetime(row["Data"]).date()
                    db.add_transacao(
                        data_val, row["Tipo"], row["Categoria"],
                        str(row.get("Descrição", "") or ""), float(row["Valor"]),
                        row.get("Forma de Pagamento", "") or "", row.get("Status", "Pago") or "Pago",
                    )
                    importados += 1
                st.success(f"{importados} lançamento(s) importado(s) com sucesso.")
                st.rerun()
    except Exception as e:
        st.error(f"Não foi possível ler o arquivo: {e}")
