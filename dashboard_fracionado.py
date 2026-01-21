import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Gerencial – Fracionado",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_excel(
        "FRACIONADO EXCELSIOR DEZEMBRO 2025.xlsx",
        header=7
    )

    df.columns = [
        "Ordem", "Filial", "Pedido", "CTE",
        "Local_Coleta", "Tipo_Veiculo",
        "Data_Coleta", "Data_Chegada",
        "Local_Entrega", "Atraso",
        "Justificativa"
    ]

    df = df.dropna(subset=["CTE"])
    # Limpeza da coluna Filial
df["Filial"] = df["Filial"].astype(str).str.strip()
df = df[df["Filial"].notna()]
df = df[df["Filial"] != ""]


    df["Data_Coleta"] = pd.to_datetime(df["Data_Coleta"], errors="coerce")
    df["Data_Chegada"] = pd.to_datetime(df["Data_Chegada"], errors="coerce")

    df["Atrasado"] = df["Atraso"].astype(str).str.upper().str.contains("SIM")

    return df

df = load_data()

st.title("📊 Dashboard Gerencial – Transporte Fracionado")

# ===== FILTRO =====
st.sidebar.header("Filtros")
lista_filiais = sorted(df["Filial"].dropna().unique().tolist())

filial = st.sidebar.multiselect(
    "Filial (Sigla CTE)",
    lista_filiais
)


if filial:
    df = df[df["Filial"].isin(filial)]

# ===== KPIs =====
col1, col2, col3, col4 = st.columns(4)

col1.metric("🚚 Cargas Carregadas", df["CTE"].nunique())
col2.metric("📦 Pedidos", df["Pedido"].nunique())
col3.metric("⏱️ % de Atraso", f"{df['Atrasado'].mean()*100:.1f}%")
col4.metric("🏢 Filiais", df["Filial"].nunique())

# ===== GRÁFICOS =====
st.subheader("Evolução de Cargas")

evolucao = (
    df.groupby(df["Data_Coleta"].dt.to_period("D"))
    .agg(Cargas=("CTE", "nunique"))
    .reset_index()
)
evolucao["Data_Coleta"] = evolucao["Data_Coleta"].astype(str)

fig1 = px.line(
    evolucao,
    x="Data_Coleta",
    y="Cargas",
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Ranking de Filiais")

ranking = (
    df.groupby("Filial")
    .agg(Cargas=("CTE", "nunique"))
    .sort_values("Cargas", ascending=False)
    .reset_index()
)

fig2 = px.bar(
    ranking,
    x="Cargas",
    y="Filial",
    orientation="h",
    template="plotly_dark"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Atrasos por Filial")

atrasos = (
    df.groupby("Filial")
    .agg(Atraso=("Atrasado", "mean"))
    .reset_index()
)

fig3 = px.bar(
    atrasos,
    x="Filial",
    y="Atraso",
    template="plotly_dark"
)
st.plotly_chart(fig3, use_container_width=True)
