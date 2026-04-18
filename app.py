import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Financial OS Pro", layout="wide")

# -----------------------------
# SMART LOADER
# -----------------------------
def smart_read_excel(file):
    for i in range(5):
        try:
            df = pd.read_excel(file, header=i)
            if df.shape[1] > 2:
                return df
        except:
            continue
    return pd.read_excel(file)

def normalize_cols(df):
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    return df

def clean_df(df):
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.str.contains("^unnamed")]
    return df

def detect_columns(df):
    mapping = {"date": None, "amount": None, "desc": None, "category": None}
    for c in df.columns:
        if "date" in c:
            mapping["date"] = c
        elif any(k in c for k in ["amount", "amt", "value"]):
            mapping["amount"] = c
        elif any(k in c for k in ["desc", "remark", "narration"]):
            mapping["desc"] = c
        elif any(k in c for k in ["category", "type"]):
            mapping["category"] = c
    return mapping

@st.cache_data(show_spinner=False)
def load_file(file):
    try:
        if file is None:
            return None, None

        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = smart_read_excel(file)

        df = normalize_cols(df)
        df = clean_df(df)
        mapping = detect_columns(df)

        return df, mapping
    except Exception as e:
        st.error(f"Error loading {file.name}")
        st.exception(e)
        return None, None

# -----------------------------
# AUTO CATEGORY
# -----------------------------
def auto_classify(df, desc_col):
    keywords = {
        "food": ["zomato", "swiggy"],
        "emi": ["emi", "loan"],
        "fuel": ["petrol", "diesel"],
        "shopping": ["amazon", "flipkart"]
    }

    df["auto_category"] = "other"

    if desc_col:
        for cat, words in keywords.items():
            df.loc[
                df[desc_col].astype(str).str.lower().str.contains("|".join(words)),
                "auto_category"
            ] = cat
    return df

# -----------------------------
# AI INSIGHTS
# -----------------------------
def generate_insights(df_c, map_c, df_l, df_p):
    insights = []

    if df_c is not None:
        amt = map_c.get("amount")
        desc = map_c.get("desc")
        date = map_c.get("date")

        if amt:
            df = df_c.copy()
            df[amt] = pd.to_numeric(df[amt], errors="coerce").fillna(0)

            exp = df[df[amt] < 0].copy()
            exp["abs_amt"] = exp[amt].abs()

            total_exp = exp["abs_amt"].sum()

            if "auto_category" in df.columns:
                cat = exp.groupby("auto_category")["abs_amt"].sum().sort_values(ascending=False)
                if not cat.empty:
                    top = cat.index[0]
                    pct = (cat.iloc[0] / total_exp) * 100 if total_exp else 0
                    insights.append(f"Top expense: {top} ({pct:.1f}%)")

                    if pct > 40:
                        insights.append("High concentration risk in spending")

            if date:
                df[date] = pd.to_datetime(df[date], errors="coerce")
                m = df.groupby(df[date].dt.to_period("M"))[amt].sum()
                if len(m) >= 2 and m.iloc[-1] < m.iloc[-2]:
                    insights.append("Cashflow declining last month")

    if df_l is not None:
        insights.append("Active loans detected – consider prepayment if surplus exists")

    if df_p is not None and "pnl" in df_p.columns:
        if df_p["pnl"].sum() < 0:
            insights.append("Portfolio is in loss – review allocations")

    return insights

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Financial OS Pro")

wealth_file = st.sidebar.file_uploader("Wealth", ["csv", "xlsx"])
cash_file = st.sidebar.file_uploader("Cashflow", ["csv", "xlsx"])
loan_file = st.sidebar.file_uploader("Loans", ["csv", "xlsx"])
portfolio_file = st.sidebar.file_uploader("Portfolio", ["csv", "xlsx"])

page = st.sidebar.radio("Navigate", [
    "Dashboard", "Wealth", "Cashflow", "Loans", "Portfolio", "AI Insights"
])

df_w, map_w = load_file(wealth_file)
df_c, map_c = load_file(cash_file)
df_l, map_l = load_file(loan_file)
df_p, map_p = load_file(portfolio_file)

# -----------------------------
# ENGINE
# -----------------------------
net_worth = 0
cash = 0
debt = 0
burn = 0

# Wealth
if df_w is not None:
    col = map_w.get("amount")
    if col:
        net_worth += df_w[col].sum()

# Cashflow
if df_c is not None:
    amt = map_c.get("amount")
    desc = map_c.get("desc")

    if amt:
        df_c[amt] = pd.to_numeric(df_c[amt], errors="coerce").fillna(0)
        cash = df_c[amt].sum()

        df_c = auto_classify(df_c, desc)
        burn = abs(df_c[df_c[amt] < 0][amt].sum())

# Loans
if df_l is not None:
    col = map_l.get("amount")
    if col:
        debt = df_l[col].sum()

# Portfolio
portfolio_val = 0
invested = 0
pnl = 0

if df_p is not None:
    qty = next((c for c in df_p.columns if "qty" in c), None)
    buy = next((c for c in df_p.columns if "buy" in c or "avg" in c), None)
    ltp = next((c for c in df_p.columns if "ltp" in c or "price" in c), None)

    if qty and buy and ltp:
        df_p[qty] = pd.to_numeric(df_p[qty], errors="coerce").fillna(0)
        df_p[buy] = pd.to_numeric(df_p[buy], errors="coerce").fillna(0)
        df_p[ltp] = pd.to_numeric(df_p[ltp], errors="coerce").fillna(0)

        df_p["invested"] = df_p[qty] * df_p[buy]
        df_p["current"] = df_p[qty] * df_p[ltp]
        df_p["pnl"] = df_p["current"] - df_p["invested"]

        invested = df_p["invested"].sum()
        portfolio_val = df_p["current"].sum()
        pnl = df_p["pnl"].sum()

net_worth = net_worth + cash + portfolio_val - debt

# -----------------------------
# DASHBOARD
# -----------------------------
if page == "Dashboard":
    st.title("Dashboard")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Net Worth", f"₹ {net_worth:,.0f}")
    c2.metric("Cash", f"₹ {cash:,.0f}")
    c3.metric("Debt", f"₹ {debt:,.0f}")
    c4.metric("Burn", f"₹ {burn:,.0f}")
    c5.metric("Portfolio", f"₹ {portfolio_val:,.0f}")

# -----------------------------
# PORTFOLIO
# -----------------------------
elif page == "Portfolio":
    st.title("Portfolio")

    if df_p is not None:
        st.dataframe(df_p)

        if "current" in df_p.columns:
            fig = px.pie(df_p, values="current", names=df_p.columns[0])
            st.plotly_chart(fig)

# -----------------------------
# AI INSIGHTS
# -----------------------------
elif page == "AI Insights":
    st.title("AI Financial Insights")

    insights = generate_insights(df_c, map_c, df_l, df_p)

    if insights:
        for i in insights:
            st.info(i)
    else:
        st.success("No major risks detected")
