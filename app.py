import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Personal Financial OS", page_icon="🧭", layout="wide")

# --- SIDEBAR & FILE UPLOADS ---
st.sidebar.title("🧭 Financial OS")
st.sidebar.write("Upload your data sheets below. Your data remains private in your browser session.")

# File Uploaders
wealth_file = st.sidebar.file_uploader("Upload Wealth/Home Sheet (Excel/CSV)", type=["csv", "xlsx"])
cashflow_file = st.sidebar.file_uploader("Upload Cashflow/BAAL Sheet (Excel/CSV)", type=["csv", "xlsx"])
loan_file = st.sidebar.file_uploader("Upload Loan/Property Sheet (Excel/CSV)", type=["csv", "xlsx"])

# Navigation
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["🌟 Master Dashboard", "🏠 Wealth & Assets", "🏦 Cashflow & Bank", "📉 Loan Tracker"])

# --- HELPER FUNCTIONS ---
@st.cache_data
def load_data(file):
    if file is not None:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    return None

# Load the data dynamically
df_wealth = load_data(wealth_file)
df_cashflow = load_data(cashflow_file)
df_loan = load_data(loan_file)

# --- PAGE 1: MASTER DASHBOARD ---
if page == "🌟 Master Dashboard":
    st.title("🌟 Executive Summary")
    st.markdown("A high-level view combining Wealth, Cashflow, and Liabilities.")
    
    # Placeholder Metrics (These will update when files are uploaded)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Estimated Net Worth", value="₹ --")
    with col2:
        st.metric(label="Total Liquid Cash", value="₹ --")
    with col3:
        st.metric(label="Outstanding Debt", value="₹ --")
    with col4:
        st.metric(label="Avg Monthly Burn", value="₹ --")

    st.info("👆 Upload your files in the sidebar to populate the metrics and charts.")

    # Sample layout for Master Charts
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Assets vs Liabilities")
        st.caption("Visual breakdown will appear here once Wealth & Loan sheets are uploaded.")
    with colB:
        st.subheader("Cashflow Trend (Last 6 Months)")
        st.caption("Bar chart will appear here once Cashflow sheets are uploaded.")

# --- PAGE 2: WEALTH & ASSETS ---
elif page == "🏠 Wealth & Assets":
    st.title("🏠 Wealth & Assets")
    if df_wealth is not None:
        st.success("Wealth Data Loaded!")
        st.dataframe(df_wealth.head()) # Shows a preview of your data
        # Add your specific wealth chart logic here based on your columns
    else:
        st.warning("Please upload your Wealth/Home sheet in the sidebar.")

# --- PAGE 3: CASHFLOW & BANK ---
elif page == "🏦 Cashflow & Bank":
    st.title("🏦 Cashflow & Bank Balances")
    if df_cashflow is not None:
        st.success("Cashflow Data Loaded!")
        st.dataframe(df_cashflow.head())
        # Example: if you have a 'Bank' and 'Balance' column, you can uncomment below:
        # fig = px.pie(df_cashflow, values='Balance', names='Bank', title='Liquidity Breakdown')
        # st.plotly_chart(fig)
    else:
        st.warning("Please upload your Cashflow/BAAL sheet in the sidebar.")

# --- PAGE 4: LOAN TRACKER ---
elif page == "📉 Loan Tracker":
    st.title("📉 Loan & Property Tracker")
    if df_loan is not None:
        st.success("Loan Data Loaded!")
        st.dataframe(df_loan.head())
        # Example progress bar for EMIs
        st.progress(0.45, text="EMI Completion Progress (Example)")
    else:
        st.warning("Please upload your Loan sheet in the sidebar.")

st.sidebar.markdown("---")
st.sidebar.caption("Secure & Private • V1.0")