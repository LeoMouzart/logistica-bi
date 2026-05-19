# ------------------------ Importando as bibliotecas ---------------------

import streamlit as st
import pandas as pd
import plotly.express as px 



st.set_page_config(
    page_title="BI Logístico",
    page_icon="🚚",
    layout="wide"
)


st.title("🚚 BI Logístico — Painel Executivo")
st.markdown("Análise de Operação Logística")


# -------------- Carregando os dados - --------------

@st.cache_data
def importacao_dados():
    df = pd.read_parquet("base_limpa.parquet")
    return df

df = importacao_dados()

st.success(f"Base carregada com sucesso! {len(df)} pedidos encontrados")



with st.sidebar:
    st.markdown("### 🚚 Filtros")

    transportadoras = sorted(df["Transportadoras"].unique())
    sel_transp = st.multiselect(
        "Transportadora",
        transportadoras, 
        default=transportadoras

    )

    opcoes_status = sorted(df["Status_Entrega"].unique())
    sel_status = st.multiselect(
        "Status_Entrega",
        opcoes_status,
        default=opcoes_status
    )


    datas = df["Data_Pedido"].sort_values()
    data_inicio, data_fim = st.date_input(
        "Periodo",
        [datas.min().date(),datas.max().date()]
    )


    df_filtrado = df[
    df["Transportadora"].isin(sel_transp) &
    df["Status_Entrega"].isin(sel_status) &
    (df["Data_Pedido"].dt.date >= data_ini) &
    (df["Data_Pedido"].dt.date <= data_fim)
]

st.info(f"Exibindo {len(df_filtrado)} pedidos filtrados")