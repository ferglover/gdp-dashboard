from pathlib import Path
from datetime import datetime, timedelta
import calendar

import streamlit as st
import pandas as pd

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="KPI Calculator",
    layout="wide"
)

# =====================================
# SIMPLE LOGIN
# =====================================

USERNAME = "admin"
PASSWORD = "uvc2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")

    user = st.text_input("User")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# =====================================
# STYLES
# =====================================

st.markdown("""
<style>
/* INPUT EDITABLE */
div[data-baseweb="input"] input {
    font-size: 36px !important;
    font-weight: 400 !important;
}

/* BOTONES + / - */
button[data-testid="stNumberInputStepUp"],
button[data-testid="stNumberInputStepDown"] {
    height: 38px !important;
    width: 38px !important;
}

/* LABEL DEL INPUT */
label[data-testid="stWidgetLabel"] p {
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* MATRIZ */
.matrix-header {
    font-size: 16px;
    font-weight: 800;
    padding: 8px 0 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 8px;
}

.matrix-kpi {
    font-size: 16px;
    font-weight: 700;
    padding-top: 14px;
}

.matrix-value {
    font-size: 28px;
    font-weight: 700;
    line-height: 1.15;
    padding-top: 10px;
}

.matrix-card {
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 12px;
    padding: 14px 14px 12px 14px;
    min-height: 110px;
    background: rgba(255,255,255,0.02);
}
</style>
""", unsafe_allow_html=True)

# =====================================
# PATH
# =====================================

BASE_DIR = Path(__file__).resolve().parent

# =====================================
# LOAD ACTUAL DATA
# =====================================

@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / "data" / "kpi_table.csv")

    df.columns = (
        df.columns
        .str.replace("[", "", regex=False)
        .str.replace("]", "", regex=False)
        .str.strip()
    )

    return df

# =====================================
# LOAD FORECAST DATA
# =====================================

@st.cache_data
def load_forecast():
    df = pd.read_csv(
        BASE_DIR / "data" / "FORECAST MAY.csv",
        header=None,
        names=["SalesRoom", "Metric", "Value"],
        encoding="latin1"
    )

    df["SalesRoom"] = df["SalesRoom"].astype(str).str.strip()
    df["Metric"] = df["Metric"].astype(str).str.strip()
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    def clean_metric(x):
        x = str(x).strip()

        if "Penetr" in x:
            return "Penetration"

        x = x.replace("Q’s", "Qs").replace("Q´s", "Qs").replace("Q's", "Qs")
        x = x.replace("Contracts ", "Contracts").replace("Average Price ", "Average Price")
        x = x.replace("Closing Rate ", "Closing Rate").replace("VPG ", "VPG")
        x = x.replace("Volume ", "Volume").replace("Arrivals ", "Arrivals")

        return x

    df["Metric"] = df["Metric"].apply(clean_metric)

    df = df.pivot_table(
        index="SalesRoom",
        columns="Metric",
        values="Value",
        aggfunc="first"
    ).reset_index()

    df.columns.name = None
    return df

df = load_data()
forecast_df = load_forecast()

# =====================================
# TITLE
# =====================================

st.title("Calculadora BI")

yesterday = datetime.now() - timedelta(days=1)
st.caption(f"Data until {yesterday.strftime('%B %d, %Y')}")

# =====================================
# SALESROOM FILTER
# =====================================

salesroom = st.selectbox(
    "Select SalesRoom",
    sorted(df["SalesRoom"].dropna().unique().tolist())
)

filtered = df[df["SalesRoom"] == salesroom]
forecast_filtered = forecast_df[forecast_df["SalesRoom"] == salesroom]

if filtered.empty:
    st.warning("No actual data found")
    st.stop()

if forecast_filtered.empty:
    st.warning("No forecast data found")
    st.stop()

row = filtered.iloc[0]
forecast_row = forecast_filtered.iloc[0]

# =====================================
# HELPERS
# =====================================

def input_cell(title, value, step, fmt="%d"):
    return st.number_input(
        title,
        value=value,
        step=step,
        format=fmt,
        label_visibility="collapsed"
    )

def value_cell(value):
    st.markdown(
        f"""
        <div class="matrix-card">
            <div class="matrix-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def kpi_label(text):
    st.markdown(f"<div class='matrix-kpi'>{text}</div>", unsafe_allow_html=True)

def fmt_int(v):
    return f"{v:,.0f}"

def fmt_money(v):
    return f"${v:,.0f}"

def fmt_pct(v):
    return f"{v:.2f}%"

def fmt_pp(v):
    return f"{v:+.2f} pp"

# =====================================
# ACTUAL INPUTS
# =====================================

arrivals = int(round(float(row["Arrivals"])))
contracts = int(round(float(row["Contracts Processable"])))
closing_rate = float(row["Closing Rate"]) * 100 if float(row["Closing Rate"]) <= 1 else float(row["Closing Rate"])
avg_price = int(round(float(row["Average Price"])))

cols = st.columns([1.6, 1, 1, 1, 1], gap="small")

with cols[0]:
    ...
with cols[1]:
    ...
with cols[2]:
    ...
with cols[3]:
    ...
with cols[4]:
    ...

# =====================================
# CALCULATIONS - ACTUALS
# =====================================

qs = contracts / (closing_rate / 100) if closing_rate else 0
penetration = (qs / arrivals * 100) if arrivals else 0
volume = contracts * avg_price
vpg = volume / qs if qs else 0

# =====================================
# FORECAST TARGETS
# =====================================

forecast_arrivals = float(forecast_row.get("Arrivals", 0))

forecast_penetration = float(forecast_row.get("Penetration", 0))
if forecast_penetration <= 1:
    forecast_penetration *= 100

forecast_qs = float(forecast_row.get("Qs", 0))
forecast_contracts = float(forecast_row.get("Contracts", 0))
forecast_avg_price = float(forecast_row.get("Average Price", 0))

forecast_closing_rate = float(forecast_row.get("Closing Rate", 0))
if forecast_closing_rate <= 1:
    forecast_closing_rate *= 100

forecast_vpg = float(forecast_row.get("VPG", 0))
forecast_volume = float(forecast_row.get("Volume", 0))

# =====================================
# FORECAST EOM
# =====================================

today = pd.Timestamp.today().normalize()
legend_date = today - pd.Timedelta(days=1)

days_elapsed = legend_date.day
days_in_month = calendar.monthrange(legend_date.year, legend_date.month)[1]
days_remaining = days_in_month - days_elapsed

def project_mtd(value):
    return (value / days_elapsed) * days_in_month if days_elapsed else 0

proj_arrivals = project_mtd(arrivals)
proj_contracts = project_mtd(contracts)
proj_qs = project_mtd(qs)
proj_volume = project_mtd(volume)

proj_penetration = (proj_qs / proj_arrivals * 100) if proj_arrivals else 0
proj_closing_rate = (proj_contracts / proj_qs * 100) if proj_qs else 0
proj_vpg = (proj_volume / proj_qs) if proj_qs else 0
proj_avg_price = (proj_volume / proj_contracts) if proj_contracts else 0

# =====================================
# VARIANCES
# =====================================

var_arrivals = proj_arrivals - forecast_arrivals
var_contracts = proj_contracts - forecast_contracts
var_qs = proj_qs - forecast_qs
var_volume = proj_volume - forecast_volume
var_penetration_pp = proj_penetration - forecast_penetration
var_closing_pp = proj_closing_rate - forecast_closing_rate
var_vpg = proj_vpg - forecast_vpg
var_avg_price = proj_avg_price - forecast_avg_price

# =====================================
# MATRIX
# =====================================

rows = [
    ("Arrivals", arrivals, proj_arrivals, forecast_arrivals, var_arrivals, "int"),
    ("Contracts Processable", contracts, proj_contracts, forecast_contracts, var_contracts, "int"),
    ("Closing Rate", closing_rate, proj_closing_rate, forecast_closing_rate, var_closing_pp, "pct"),
    ("Average Price", avg_price, proj_avg_price, forecast_avg_price, var_avg_price, "money"),
    ("Qs", qs, proj_qs, forecast_qs, var_qs, "int"),
    ("Penetration", penetration, proj_penetration, forecast_penetration, var_penetration_pp, "pct"),
    ("VPG", vpg, proj_vpg, forecast_vpg, var_vpg, "money"),
    ("Volume", volume, proj_volume, forecast_volume, var_volume, "money"),
]

st.markdown("### KPI Matrix")
st.caption(
    f"Projection based on {legend_date.strftime('%B %d, %Y')} | "
    f"{days_elapsed} days elapsed | {days_remaining} days remaining"
)

for i, (label, actual_val, proj_val, fcst_val, var_val, kind) in enumerate(rows):
    cols = st.columns([1.6, 1, 1, 1, 1], gap="small")

    with cols[0]:
        kpi_label(label)

    with cols[1]:
        if label in ["Arrivals", "Contracts Processable", "Closing Rate", "Average Price"]:
            if label == "Arrivals":
                arrivals = input_cell("Arrivals", arrivals, step=1, fmt="%d")
                actual_val = arrivals
            elif label == "Contracts Processable":
                contracts = input_cell("Contracts Processable", contracts, step=1, fmt="%d")
                actual_val = contracts
            elif label == "Closing Rate":
                closing_rate = input_cell("Closing Rate", closing_rate, step=0.1, fmt="%.1f")
                actual_val = closing_rate
            elif label == "Average Price":
                avg_price = input_cell("Average Price", avg_price, step=100, fmt="%d")
                actual_val = avg_price

            # Recalculate actuals/projections if inputs changed
            qs = contracts / (closing_rate / 100) if closing_rate else 0
            penetration = (qs / arrivals * 100) if arrivals else 0
            volume = contracts * avg_price
            vpg = volume / qs if qs else 0

            proj_arrivals = project_mtd(arrivals)
            proj_contracts = project_mtd(contracts)
            proj_qs = project_mtd(qs)
            proj_volume = project_mtd(volume)

            proj_penetration = (proj_qs / proj_arrivals * 100) if proj_arrivals else 0
            proj_closing_rate = (proj_contracts / proj_qs * 100) if proj_qs else 0
            proj_vpg = (proj_volume / proj_qs) if proj_qs else 0
            proj_avg_price = (proj_volume / proj_contracts) if proj_contracts else 0

            var_arrivals = proj_arrivals - forecast_arrivals
            var_contracts = proj_contracts - forecast_contracts
            var_qs = proj_qs - forecast_qs
            var_volume = proj_volume - forecast_volume
            var_penetration_pp = proj_penetration - forecast_penetration
            var_closing_pp = proj_closing_rate - forecast_closing_rate
            var_vpg = proj_vpg - forecast_vpg
            var_avg_price = proj_avg_price - forecast_avg_price

        else:
            value_cell(fmt_int(actual_val) if kind == "int" else fmt_money(actual_val) if kind == "money" else fmt_pct(actual_val))

    with cols[2]:
        if kind == "int":
            value_cell(fmt_int(proj_val))
        elif kind == "money":
            value_cell(fmt_money(proj_val))
        else:
            value_cell(fmt_pct(proj_val))

    with cols[3]:
        if kind == "int":
            value_cell(fmt_int(fcst_val))
        elif kind == "money":
            value_cell(fmt_money(fcst_val))
        else:
            value_cell(fmt_pct(fcst_val))

    with cols[4]:
        if kind == "pct":
            value_cell(fmt_pp(var_val))
        elif kind == "money":
            value_cell(fmt_money(var_val))
        else:
            value_cell(fmt_int(var_val))
