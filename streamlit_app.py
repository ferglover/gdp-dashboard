import streamlit as st
import pandas as pd

st.set_page_config(page_title="KPI Calculator", layout="wide")

@st.cache_data
def load_data():
    # Si el archivo está en tu repo
    return pd.read_csv("data/kpi_table.csv")

df = load_data()

st.title("Calculadora BI")

salesroom = st.selectbox(
    "Select SalesRoom",
    sorted(df["SalesRoom"].dropna().unique().tolist())
)

row = df[df["SalesRoom"] == salesroom].iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    arrivals = st.number_input(
        "Arrivals",
        value=float(row["Arrivals"]),
        step=1.0
    )
    qs = st.number_input(
        "Qs",
        value=float(row["Qs"]),
        step=1.0
    )

with col2:
    contracts = st.number_input(
        "Contracts Processable",
        value=float(row["Contracts Processable"]),
        step=1.0
    )
    closing_rate = st.number_input(
        "Closing Rate",
        value=float(row["Closing Rate"]),
        step=0.1
    )

with col3:
    avg_price = st.number_input(
        "Average Price",
        value=float(row["Average Price"]),
        step=1.0
    )

# Cálculo ejemplo
vpg = (contracts * avg_price / qs) if qs else 0
volume = contracts * avg_price
penetration = (qs / arrivals * 100) if arrivals else 0

st.subheader("Calculated KPIs")
st.write(f"Penetration: {penetration:.2f}%")
st.write(f"VPG: {vpg:,.2f}")
st.write(f"Volume: {volume:,.2f}")

st.subheader("Source row")
st.dataframe(row.to_frame().T, use_container_width=True)
