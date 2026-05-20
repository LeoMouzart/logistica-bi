# ------------------------ IMPORTANDO BIBLIOTECAS ------------------------

import streamlit as st
import pandas as pd
import plotly.express as px



# CONFIGURAÇÃO DA PÁGINA


st.set_page_config(
    page_title="BI Logístico",
    page_icon="🚚",
    layout="wide"
)



# TÍTULO


st.title("🚚 BI Logístico — Painel Executivo")
st.markdown("Análise de Operação Logística")



# IMPORTAÇÃO DOS DADOS


@st.cache_data
def importacao_dados():
    df = pd.read_parquet("base_limpa.parquet")
    return df


df = importacao_dados()

st.success(
    f"Base carregada com sucesso! {len(df)} pedidos encontrados"
)



# SIDEBAR / FILTROS


with st.sidebar:

    st.markdown("## 🚚 Filtros")

    # ---------------- TRANSPORTADORAS ----------------

    transportadoras = sorted(df["Transportadora"].unique())

    sel_transp = st.multiselect(
        "Transportadora",
        transportadoras,
        default=transportadoras
    )

    # ---------------- STATUS ----------------

    opcoes_status = sorted(df["Status_Entrega"].unique())

    sel_status = st.multiselect(
        "Status Entrega",
        opcoes_status,
        default=opcoes_status
    )

    # ---------------- PERÍODO ----------------

    datas = df["Data_Pedido"].sort_values()

    data_inicio, data_fim = st.date_input(
        "Período",
        [datas.min().date(), datas.max().date()]
    )



# FILTRO PRINCIPAL


df_filtrado = df[
    df["Transportadora"].isin(sel_transp)
    &
    df["Status_Entrega"].isin(sel_status)
    &
    (df["Data_Pedido"].dt.date >= data_inicio)
    &
    (df["Data_Pedido"].dt.date <= data_fim)
]

st.info(f"Exibindo {len(df_filtrado)} pedidos filtrados")



# KPIs


st.markdown("---")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:

    st.metric(
        "Total Pedidos",
        len(df_filtrado)
    )

with k2:

    taxa = df_filtrado["Pedido_Atrasado"].mean() * 100

    st.metric(
        "Taxa Atraso",
        f"{taxa:.1f}%"
    )

with k3:

    extraviado = df_filtrado[
        df_filtrado["Status_Entrega"] == "Extraviado"
    ]["Valor_NF_BRL"].sum()

    st.metric(
        "Valor Extraviado",
        f"R$ {extraviado:,.0f}"
    )

with k4:

    satisfacao = df_filtrado[
        "Satisfacao_Cliente"
    ].mean()

    st.metric(
        "Satisfação Média",
        f"{satisfacao:.2f} ⭐"
    )

with k5:

    desvio = df_filtrado[
        "Desvio_Dias"
    ].mean()

    st.metric(
        "Desvio Médio",
        f"{desvio:+.1f} dias"
    )



# TRATAMENTO DOS DADOS


# ---------------- MENSAL ----------------

mensal = df_filtrado.groupby(
    "Mês_Ano"
).agg(
    Pedidos=("ID_Pedido", "count"),
    Atrasos=("Pedido_Atrasado", "sum")
).reset_index()

mensal["Taxa_Atraso_%"] = (
    mensal["Atrasos"] / mensal["Pedidos"] * 100
).round(1)

mensal = mensal.sort_values("Mês_Ano")


# ---------------- TRANSPORTADORAS ----------------

transp = df_filtrado.groupby(
    "Transportadora"
).agg(
    Pedidos=("ID_Pedido", "count"),
    Taxa_Atraso=("Pedido_Atrasado", "mean"),
    Satisfacao=("Satisfacao_Cliente", "mean")
).reset_index()

transp["Taxa_Atraso"] = (
    transp["Taxa_Atraso"] * 100
).round(1)


# ---------------- STATUS ----------------

status = df_filtrado[
    "Status_Entrega"
].value_counts().reset_index()

status.columns = [
    "Status",
    "Quantidade"
]


# ---------------- FINANCEIRO ----------------

financeiro = df_filtrado.groupby(
    "Mês_Ano"
).agg(
    Valor_Total=("Valor_NF_BRL", "sum")
).reset_index()


# ---------------- CORRELAÇÃO ----------------

correlacao = df_filtrado.groupby(
    "Transportadora"
).agg(
    Taxa_Atraso=("Pedido_Atrasado", "mean"),
    Satisfacao=("Satisfacao_Cliente", "mean"),
    Pedidos=("ID_Pedido", "count")
).reset_index()

correlacao["Taxa_Atraso"] = (
    correlacao["Taxa_Atraso"] * 100
).round(1)



# INSIGHTS


melhor = correlacao.sort_values(
    ["Taxa_Atraso", "Satisfacao"],
    ascending=[True, False]
).iloc[0]

pior = correlacao.sort_values(
    ["Taxa_Atraso", "Satisfacao"],
    ascending=[False, True]
).iloc[0]



# TEMA ESCURO PADRONIZADO


COR_FUNDO = "#0E1117"
COR_CARD = "#161B22"
COR_TEXTO = "#FAFAFA"
COR_GRID = "rgba(255,255,255,0.08)"
COR_PRIMARIA = "#4F8BF9"



# CRIAÇÃO DOS GRÁFICOS



# GRÁFICO MENSAL


fig_mensal = px.bar(
    mensal,
    x="Mês_Ano",
    y="Pedidos",
    text="Pedidos",
    title="Volume de Pedidos por Mês",
    color_discrete_sequence=[COR_PRIMARIA]
)

fig_mensal.update_layout(
    plot_bgcolor=COR_CARD,
    paper_bgcolor=COR_CARD,
    font=dict(
        size=14,
        color=COR_TEXTO
    ),
    title_font=dict(size=20),
    xaxis_title="",
    yaxis_title=""
)

fig_mensal.update_traces(
    textfont_color=COR_TEXTO
)

fig_mensal.update_yaxes(
    showgrid=True,
    gridcolor=COR_GRID
)

fig_mensal.update_xaxes(
    showgrid=False
)



# GRÁFICO TRANSPORTADORAS


fig_transp = px.bar(
    transp.sort_values("Pedidos", ascending=False),
    x="Transportadora",
    y="Pedidos",
    text="Pedidos",
    title="Performance das Transportadoras",
    color_discrete_sequence=["#5B8FB9"]
)

fig_transp.update_layout(
    plot_bgcolor=COR_CARD,
    paper_bgcolor=COR_CARD,
    font=dict(
        size=14,
        color=COR_TEXTO
    ),
    title_font=dict(size=20),
    xaxis_title="",
    yaxis_title=""
)

fig_transp.update_traces(
    textfont_color=COR_TEXTO
)

fig_transp.update_yaxes(
    showgrid=True,
    gridcolor=COR_GRID
)

fig_transp.update_xaxes(
    showgrid=False
)



# GRÁFICO STATUS


fig_status = px.pie(
    status,
    names="Status",
    values="Quantidade",
    hole=0.55,
    color_discrete_sequence=[
        "#4F8BF9",
        "#6EA8FE",
        "#8EC5FF",
        "#B6DAFF"
    ]
)

fig_status.update_layout(
    paper_bgcolor=COR_CARD,
    font=dict(
        size=14,
        color=COR_TEXTO
    )
)

fig_status.update_traces(
    textfont_size=14,
    textfont_color=COR_TEXTO
)



# GRÁFICO FINANCEIRO


fig_financeiro = px.line(
    financeiro,
    x="Mês_Ano",
    y="Valor_Total",
    markers=True,
    title="Evolução Financeira"
)

fig_financeiro.update_traces(
    line=dict(
        width=4,
        color="#52D273"
    )
)

fig_financeiro.update_layout(
    plot_bgcolor=COR_CARD,
    paper_bgcolor=COR_CARD,
    font=dict(
        size=14,
        color=COR_TEXTO
    ),
    title_font=dict(size=20),
    xaxis_title="",
    yaxis_title=""
)

fig_financeiro.update_yaxes(
    showgrid=True,
    gridcolor=COR_GRID
)

fig_financeiro.update_xaxes(
    showgrid=False
)



# GRÁFICO CORRELAÇÃO


fig_correlacao = px.scatter(
    correlacao,
    x="Taxa_Atraso",
    y="Satisfacao",
    size="Pedidos",
    hover_name="Transportadora",
    title="Relação entre Atraso e Satisfação",
    color_discrete_sequence=[COR_PRIMARIA]
)

fig_correlacao.update_traces(
    marker=dict(
        opacity=0.85,
        line=dict(
            width=1,
            color="#FFFFFF"
        )
    )
)

fig_correlacao.update_layout(
    plot_bgcolor=COR_CARD,
    paper_bgcolor=COR_CARD,
    font=dict(
        size=14,
        color=COR_TEXTO
    ),
    title_font=dict(size=20),
    xaxis_title="Taxa de Atraso (%)",
    yaxis_title="Satisfação Média"
)

fig_correlacao.update_yaxes(
    showgrid=True,
    gridcolor=COR_GRID
)

fig_correlacao.update_xaxes(
    showgrid=True,
    gridcolor=COR_GRID
)



# GRID / LAYOUT


# ---------------- LINHA 1 ----------------

st.markdown("---")

st.subheader("📅 Evolução Mensal de Pedidos")

aba1, aba2, aba3 = st.tabs([
    "📊 Visão Geral",
    "🚚 Transportadoras",
    "📋 Dados"
])



# ABA 1 — VISÃO GERAL


with aba1:

    st.subheader("📅 Evolução Mensal de Pedidos")
    st.plotly_chart(
        fig_mensal,
        use_container_width=True,
        key="grafico_mensal"
    )

    st.subheader("💰 Evolução Financeira")
    st.plotly_chart(
        fig_financeiro,
        use_container_width=True,
        key="grafico_financeiro"
    )



# ABA 2 — TRANSPORTADORAS


with aba2:

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🚚 Performance Transportadoras")
        st.plotly_chart(
            fig_transp,
            use_container_width=True,
            key="grafico_transportadora"
        )

    with col2:
        st.subheader("📦 Status das Entregas")
        st.plotly_chart(
            fig_status,
            use_container_width=True,
            key="grafico_status"
        )

    st.subheader("📈 Satisfação x Atraso")
    st.plotly_chart(
        fig_correlacao,
        use_container_width=True,
        key="grafico_correlacao"
    )



# ABA 3 — DADOS


with aba3:

    st.subheader("🧠 Insights Operacionais")

    c1, c2 = st.columns(2)

    with c1:
        st.success(
            f"""
            Melhor performance operacional

            🚚 {melhor['Transportadora']}

            • Taxa de atraso: {melhor['Taxa_Atraso']}%
            • Satisfação: {melhor['Satisfacao']:.2f} ⭐
            """
        )

    with c2:
        st.error(
            f"""
            Pior performance operacional

            🚚 {pior['Transportadora']}

            • Taxa de atraso: {pior['Taxa_Atraso']}%
            • Satisfação: {pior['Satisfacao']:.2f} ⭐
            """
        )

    st.markdown("---")
    st.subheader("📋 Dados Detalhados")
    st.dataframe(
        df_filtrado,
        use_container_width=True,
        height=400
    )

    st.markdown("---")
    st.subheader("📤 Exportação")

    csv = df_filtrado.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Exportar Dados CSV",
        data=csv,
        file_name="dados_filtrados.csv",
        mime="text/csv",
        use_container_width=True
    )