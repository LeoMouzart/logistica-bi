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

    transportadoras = sorted(df["Transportadora"].unique())
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
    (df["Data_Pedido"].dt.date >= data_inicio) &
    (df["Data_Pedido"].dt.date <= data_fim)
]

st.info(f"Exibindo {len(df_filtrado)} pedidos filtrados")


# ----------------- Trabalhando os KPI's ---------------------------------

st.markdown("---")
k1,k2,k3,k4,k5 = st.columns(5)

with k1:
    st.metric("Total de pedidos", len(df_filtrado))

with k2:
    taxa = df_filtrado["Pedido_Atrasado"].mean()*100
    st.metric("Taxa de Atraso", f"{taxa:.2f}%")

with k3:
    extraviado = df_filtrado[df_filtrado["Status_Entrega"] =="Extraviado"]["Valor_NF_BRL"].sum()
    st.metric("Valor Extraviado", f"R$ {extraviado:,.0f}")

with k4:
    satisfacao = df_filtrado["Satisfacao_Cliente"].mean()
    st.metric("Satisfação Média", f"{satisfacao:.2f} ⭐")

with k5:
    desvio = df_filtrado["Desvio_Dias"].mean()
    st.metric("Desvio Médio", f"{desvio:+.1f} dias")