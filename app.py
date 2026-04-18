import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date
import os
from dotenv import load_dotenv
import traceback

st.set_page_config(page_title="Financial OS Pro", layout="wide", page_icon="💰")

# -----------------------------
# SUPABASE CONNECTION & ENV
# -----------------------------
load_dotenv()

@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        return create_client(url, key)
    return None

supabase = init_supabase()

# -----------------------------
# SAFE DB HELPER (Prevents Crashes)
# -----------------------------
def safe_db_call(func, fallback=None, error_prefix="DB Error"):
    """Wraps Supabase calls in try/except. Returns fallback on failure."""
    try:
        if not supabase:
            st.warning("⚠️ Supabase not connected. Check Secrets.")
            return fallback
        return func()
    except Exception as e:
        st.warning(f"🔌 {error_prefix}: {type(e).__name__}")
        st.caption("Tip: Disable Row Level Security (RLS) in Supabase for personal use.")
        return fallback

# -----------------------------
# CRUD FUNCTIONS
# -----------------------------
def add_transaction(data: dict):
    return safe_db_call(
        lambda: supabase.table("transactions").insert(data).execute(),
        fallback=None,
        error_prefix="Failed to add transaction"
    )

def get_transactions(start_date=None, end_date=None, category=None):
    def _fetch():
        query = supabase.table("transactions").select("*").order("transaction_date", desc=True)
        if start_date: query = query.gte("transaction_date", start_date.isoformat())
        if end_date: query = query.lte("transaction_date", end_date.isoformat())
        if category: query = query.eq("category", category)
        response = query.execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    
    return safe_db_call(_fetch, fallback=pd.DataFrame(), error_prefix="Could not load transactions")

def update_transaction(transaction_id: str, updates: dict):
    def _update():
        updates["updated_at"] = datetime.now().isoformat()
        return supabase.table("transactions").update(updates).eq("id", transaction_id).execute()
    return safe_db_call(_update, fallback=None, error_prefix="Failed to update transaction")

def delete_transaction(transaction_id: str):
    return safe_db_call(
        lambda: supabase.table("transactions").delete().eq("id", transaction_id).execute(),
        fallback=None, error_prefix="Failed to delete transaction"
    )

def get_all_loans():
    def _fetch():
        res = supabase.table("loans").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    return safe_db_call(_fetch, fallback=pd.DataFrame(), error_prefix="Could not load loans")

def get_all_investments():
    def _fetch():
        res = supabase.table("investments").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    return safe_db_call(_fetch, fallback=pd.DataFrame(), error_prefix="Could not load investments")

# -----------------------------
# AUTO-CATEGORY
# -----------------------------
def auto_categorize(description: str) -> tuple[str, str]:
    desc_lower = description.lower()
    rules = [
        (["emi", "installment", "loan"], "Loan EMI", "Other Loan"),
        (["petrol", "diesel", "fuel"], "Fuel", "Petrol/Diesel"),
        (["hdfc credit", "credit card"], "Credit Card", "HDFC/Axis"),
        (["home", "rent", "maintenance", "netra"], "Home", "Rent/Maintenance"),
        (["dips", "to dips"], "Family Transfer", "Dips"),
        (["mom", "mother"], "Family", "Mom Expenses"),
        (["prihaan", "baby", "school"], "Child", "Prihaan"),
        (["zomato", "swiggy", "dosa", "nasto"], "Food", "Dining Out"),
        (["amazon", "flipkart", "reliance", "dmart"], "Shopping", "Online/Retail"),
        (["torrent", "adani", "power", "light"], "Utilities", "Electricity"),
        (["jio", "airtel", "vodafone", "recharge"], "Utilities", "Mobile/Internet"),
        (["medicine", "hospital", "clinic"], "Healthcare", "Medical")
    ]
    for keywords, cat, sub in rules:
        if any(k in desc_lower for k in keywords): return cat, sub
    return "Other", "Uncategorized"

# -----------------------------
# EXCEL MIGRATION
# -----------------------------
def migrate_excel_to_db(file, table_name: str):
    if not supabase: return "❌ Supabase not connected"
    try:
        df = pd.read_excel(file).dropna(how="all")
        if table_name == "transactions":
            records = []
            for _, row in df.iterrows():
                if pd.isna(row.get("Date")) or pd.isna(row.get("Rs")): continue
                desc = str(row.get("Discription", ""))
                cat, sub = auto_categorize(desc)
                records.append({
                    "transaction_date": pd.to_datetime(row["Date"]).date().isoformat(),
                    "amount": float(row["Rs"]),
                    "description": desc,
                    "category": cat,
                    "subcategory": sub,
                    "month_year": pd.to_datetime(row["Date"]).strftime("%b-%y"),
                    "is_recurring": "emi" in desc.lower() or "installment" in desc.lower()
                })
            if records:
                safe_db_call(lambda: supabase.table("transactions").insert(records).execute())
                return f"✅ Migrated {len(records)} transactions"
        return f"⚠️ Migration for '{table_name}' not yet configured"
    except Exception as e:
        return f"❌ Migration Error: {str(e)}"

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("💰 Financial OS Pro")
st.sidebar.markdown("---")
page = st.sidebar.radio("📊 Navigate", ["🏠 Dashboard", "📝 Transactions", "💳 Loans", "📈 Investments", "⚙️ Settings"])

st.sidebar.markdown("---")
st.sidebar.subheader("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Import Excel (One-time)", type=["xlsx", "csv"])
target_table = st.sidebar.selectbox("Import to:", ["transactions"])
if uploaded_file and st.sidebar.button("🔄 Migrate to Database"):
    with st.spinner("Migrating..."):
        st.sidebar.success(migrate_excel_to_db(uploaded_file, target_table))

# DB Status Indicator
if supabase:
    try:
        supabase.table("transactions").select("id").limit(1).execute()
        st.sidebar.success("🟢 Supabase Connected")
    except Exception:
        st.sidebar.warning("🔴 Supabase Error (Check RLS)")
else:
    st.sidebar.warning("🔴 Supabase Not Configured")

# -----------------------------
# PAGE: DASHBOARD
# -----------------------------
if page == "🏠 Dashboard":
    st.title("🏠 Financial Dashboard")
    df_trans = get_transactions()
    
    if df_trans.empty:
        st.info("📭 No data yet. Import Excel or add transactions manually.")
    else:
        df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors="coerce").fillna(0)
        
        c1, c2, c3, c4 = st.columns(4)
        inc = df_trans[df_trans["amount"] > 0]["amount"].sum()
        exp = abs(df_trans[df_trans["amount"] < 0]["amount"].sum())
        net = inc - exp
        
        c1.metric("💵 Income", f"₹ {inc:,.0f}")
        c2.metric("💸 Expenses", f"₹ {exp:,.0f}")
        c3.metric("📊 Net", f"₹ {net:,.0f}", delta=f"{(net/inc)*100:.1f}%" if inc else None)
        c4.metric("🔄 Count", f"{len(df_trans)}")
        
        df_trans["transaction_date"] = pd.to_datetime(df_trans["transaction_date"])
        monthly = df_trans.groupby(df_trans["transaction_date"].dt.to_period("M"))["amount"].sum().reset_index()
        monthly["period"] = monthly["transaction_date"].astype(str)
        st.plotly_chart(px.bar(monthly, x="period", y="amount", color="amount", color_continuous_scale=["red", "green"]), use_container_width=True)

# -----------------------------
# PAGE: TRANSACTIONS (CRUD)
# -----------------------------
elif page == "📝 Transactions":
    st.title("📝 Manage Transactions")
    tab1, tab2, tab3 = st.tabs(["📋 View/Edit", "➕ Add New", "🗑️ Delete"])
    
    with tab1:
        df = get_transactions(date(2023, 1, 1), date.today())
        if not df.empty:
            edited = st.data_editor(df, column_config={"id": None, "created_at": None, "updated_at": None}, hide_index=True, num_rows="dynamic")
            if st.button("💾 Save All Changes"):
                for _, row in edited.iterrows():
                    orig_id = df.iloc[edited.index.get_loc(_)]["id"]
                    update_transaction(orig_id, {
                        "transaction_date": row["transaction_date"].isoformat() if isinstance(row["transaction_date"], date) else row["transaction_date"],
                        "amount": float(row["amount"]), "description": row["description"],
                        "category": row["category"], "subcategory": row["subcategory"]
                    })
                st.success("✅ Saved!")
                st.rerun()
        else: st.warning("No transactions.")

    with tab2:
        with st.form("add_txn"):
            col1, col2 = st.columns(2)
            with col1:
                d = st.date_input("Date", date.today())
                amt = st.number_input("Amount", step=0.01, format="%.2f")
                is_inc = st.checkbox("Income")
                method = st.selectbox("Method", ["CBI", "HDFC", "Axis", "UPI", "Cash"])
            with col2:
                desc = st.text_input("Description")
                cat, sub = auto_categorize(desc) if desc else ("Other", "")
                category = st.selectbox("Category", ["Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Other"], index=0)
                subcat = st.text_input("Subcategory", value=sub)
            
            if st.form_submit_button("✨ Add"):
                add_transaction({
                    "transaction_date": d.isoformat(), "amount": abs(amt) if is_inc else -abs(amt),
                    "description": desc, "category": category, "subcategory": subcat,
                    "payment_method": method, "month_year": d.strftime("%b-%y")
                })
                st.success("✅ Added!")
                st.rerun()

    with tab3:
        search = st.text_input("Search to delete")
        if search:
            df_s = df = get_transactions()
            df_s = df_s[df_s["description"].str.contains(search, case=False, na=False)]
            for _, r in df_s.iterrows():
                if st.button(f"🗑️ Delete: ₹{r['amount']} - {r['description'][:40]}", key=f"del_{r['id']}"):
                    delete_transaction(r["id"])
                    st.success("Deleted!")
                    st.rerun()

# -----------------------------
# PAGE: LOANS
# -----------------------------
elif page == "💳 Loans":
    st.title("💳 Loan Tracker")
    df_loans = get_all_loans()
    if not df_loans.empty:
        st.dataframe(df_loans[["loan_name", "lender", "current_balance", "emi_amount", "remaining_emis", "status"]])
    else: st.info("No loans recorded. Add via Settings.")

# -----------------------------
# PAGE: INVESTMENTS
# -----------------------------
elif page == "📈 Investments":
    st.title("📈 Portfolio")
    df_inv = get_all_investments()
    if not df_inv.empty:
        st.dataframe(df_inv[["investment_name", "investment_type", "invested_amount", "current_value", "institution"]])
    else: st.info("No investments tracked.")

# -----------------------------
# PAGE: SETTINGS
# -----------------------------
elif page == "⚙️ Settings":
    st.title("⚙️ Add Data Manually")
    t1, t2 = st.tabs(["💳 Add Loan", "📈 Add Investment"])
    
    with t1:
        with st.form("add_loan"):
            n = st.text_input("Loan Name")
            l = st.text_input("Lender")
            b = st.number_input("Balance", step=1000.0)
            e = st.number_input("EMI Amount", step=100.0)
            if st.form_submit_button("Save Loan"):
                safe_db_call(lambda: supabase.table("loans").insert({"loan_name": n, "lender": l, "current_balance": b, "emi_amount": e, "status": "active"}).execute())
                st.success("✅ Loan Added")
                
    with t2:
        with st.form("add_inv"):
            n = st.text_input("Investment Name")
            t = st.selectbox("Type", ["FD", "LIC", "MutualFund", "Gold", "Other"])
            i = st.number_input("Invested", step=1000.0)
            c = st.number_input("Current Value", step=1000.0)
            if st.form_submit_button("Save Investment"):
                safe_db_call(lambda: supabase.table("investments").insert({"investment_name": n, "investment_type": t, "invested_amount": i, "current_value": c, "status": "active"}).execute())
                st.success("✅ Investment Added")
