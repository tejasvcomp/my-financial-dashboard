import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Financial OS Pro", layout="wide")

# -----------------------------
# Helpers
# -----------------------------
def normalize_cols(df):
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def find_col(df, keys):
    for c in df.columns:
        for k in keys:
            if k in c:
                return c
    return None

def classify_cashflow(df, desc_col, amt_col):
    df["type"] = "other"
    df.loc[df[amt_col] > 0, "type"] = "income"
    df.loc[df[amt_col] < 0, "type"] = "expense"
    return df

@st.cache_data(show_spinner=False)
def load_file(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return normalize_cols(df)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Financial OS Pro")

wealth_file = st.sidebar.file_uploader("Wealth / Assets", type=["csv", "xlsx"])
cash_file   = st.sidebar.file_uploader("Cashflow / Bank", type=["csv", "xlsx"])
loan_file   = st.sidebar.file_uploader("Loans", type=["csv", "xlsx"])

page = st.sidebar.radio("Navigate", [
    "Dashboard", "Wealth", "Cashflow", "Loans"
])

df_w = load_file(wealth_file)
df_c = load_file(cash_file)
df_l = load_file(loan_file)

# -----------------------------
# ENGINE
# -----------------------------
net_worth = 0
liquid_cash = 0
debt = 0
burn = 0
runway = 0

# ---- Wealth ----
if df_w is not None:
    val_col = find_col(df_w, ["value", "amount", "worth"])
    if val_col:
        net_worth += df_w[val_col].fillna(0).sum()

# ---- Cashflow ----
if df_c is not None:
    amt_col = find_col(df_c, ["amount", "balance", "amt"])
    date_col = find_col(df_c, ["date"])
    desc_col = find_col(df_c, ["desc", "remark", "note"])

    if amt_col:
        df_c[amt_col] = pd.to_numeric(df_c[amt_col], errors="coerce").fillna(0)
        liquid_cash = df_c[amt_col].sum()

        df_c = classify_cashflow(df_c, desc_col, amt_col)
        burn = abs(df_c[df_c["type"] == "expense"][amt_col].sum())

    if date_col:
        df_c[date_col] = pd.to_datetime(df_c[date_col], errors="coerce")

# ---- Loans ----
if df_l is not None:
    loan_col = find_col(df_l, ["outstanding", "loan", "balance"])
    paid_col = find_col(df_l, ["paid"])
    total_col = find_col(df_l, ["total", "sanction"])

    if loan_col:
        debt = df_l[loan_col].fillna(0).sum()

# ---- Final Net Worth ----
net_worth = net_worth + liquid_cash - debt

if burn > 0:
    runway = liquid_cash / burn

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":
    st.title("Executive Dashboard")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Net Worth", f"₹ {net_worth:,.0f}")
    c2.metric("Cash", f"₹ {liquid_cash:,.0f}")
    c3.metric("Debt", f"₹ {debt:,.0f}")
    c4.metric("Burn", f"₹ {burn:,.0f}")
    c5.metric("Runway (months)", f"{runway:.1f}" if runway else "-")

    st.divider()

    # --- Cashflow Trend ---
    if df_c is not None and date_col and amt_col:
        trend = df_c.groupby(df_c[date_col].dt.to_period("M"))[amt_col].sum().reset_index()
        trend[date_col] = trend[date_col].astype(str)

        fig = px.bar(trend, x=date_col, y=amt_col, title="Monthly Cashflow")
        st.plotly_chart(fig, use_container_width=True)

    # --- Asset vs Debt ---
    data = pd.DataFrame({
        "Type": ["Assets", "Debt"],
        "Value": [net_worth + debt, debt]
    })
    fig2 = px.pie(data, names="Type", values="Value", title="Assets vs Debt")
    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# WEALTH
# -----------------------------
elif page == "Wealth":
    st.title("Wealth Analysis")
    if df_w is not None:
        st.dataframe(df_w)

        val_col = find_col(df_w, ["value", "amount"])
        cat_col = find_col(df_w, ["type", "category"])

        if val_col and cat_col:
            fig = px.pie(df_w, names=cat_col, values=val_col, title="Asset Allocation")
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# CASHFLOW
# -----------------------------
elif page == "Cashflow":
    st.title("Cashflow Intelligence")

    if df_c is not None:
        st.dataframe(df_c)

        if "type" in df_c.columns:
            fig = px.pie(df_c, names="type", values=amt_col, title="Income vs Expense")
            st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# LOANS
# -----------------------------
elif page == "Loans":
    st.title("Loan Intelligence")

    if df_l is not None:
        st.dataframe(df_l)

        if paid_col and total_col:
            progress = df_l[paid_col].sum() / df_l[total_col].sum()
            st.progress(progress, text=f"Repayment {progress*100:.1f}%")
