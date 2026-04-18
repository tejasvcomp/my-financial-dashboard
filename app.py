import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date
import traceback

st.set_page_config(page_title="Financial OS Pro", layout="wide", page_icon="💰")
# -----------------------------
# 🔐 SIMPLE PASSWORD PROTECTION
# -----------------------------
def check_password():
    """Returns True if user enters correct password"""
    # Set your password here (or use st.secrets for production)
    PASSWORD = st.secrets.get("APP_PASSWORD", "Prihaan1208")  # Default fallback
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    # Password form
    st.markdown("### 🔐 Enter Password to Access Financial Dashboard")
    password = st.text_input("Password", type="password", key="pwd_input")
    
    if st.button("Unlock"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Incorrect password")
            return False
    
    return False

# Block access if not authenticated
if not check_password():
    st.stop()  # Stop app execution here if not logged in
    
# -----------------------------
# SUPABASE CONNECTION & ENV
# -----------------------------

@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("⚠️ Please configure Supabase secrets in Streamlit Cloud Settings")
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
    """Migrate Excel data to Supabase database"""
    if not supabase: 
        return "❌ Supabase not connected"
    
    try:
        # Read Excel file - handle multiple sheets/months
        excel_file = pd.ExcelFile(file)
        total_records = 0
        
        if table_name == "transactions":
            all_records = []
            
            # Process each sheet (month) in the Excel file
            for sheet_name in excel_file.sheet_names:
                try:
                    # Read the sheet, skip header rows
                    df = pd.read_excel(file, sheet_name=sheet_name, header=3)
                    
                    # Clean and process the dataframe
                    # Your Excel has: Date, Rs, Discription columns
                    df = df.dropna(how='all')  # Remove empty rows
                    
                    # Filter to only rows with actual transaction data
                    for _, row in df.iterrows():
                        # Check if we have valid date and amount
                        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):
                            continue
                            
                        try:
                            date_val = row.iloc[0]
                            amount = float(row.iloc[1])
                            desc = str(row.iloc[2]) if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                            
                            # Skip summary rows
                            if "total" in desc.lower() or "income" in desc.lower() or "expense" in desc.lower():
                                continue
                            
                            # Auto-categorize
                            cat, sub = auto_categorize(desc)
                            
                            # Determine month_year from sheet name or date
                            if isinstance(date_val, pd.Timestamp):
                                month_year = date_val.strftime("%b-%y")
                                date_iso = date_val.date().isoformat()
                            else:
                                month_year = sheet_name[:7] if len(sheet_name) >= 7 else "Unknown"
                                date_iso = str(date_val)
                            
                            all_records.append({
                                "transaction_date": date_iso,
                                "amount": -abs(amount) if amount > 0 else amount,  # Expenses are negative
                                "description": desc.strip(),
                                "category": cat,
                                "subcategory": sub,
                                "payment_method": "Unknown",
                                "month_year": month_year,
                                "is_recurring": "emi" in desc.lower() or "installment" in desc.lower() or "loan" in desc.lower(),
                                "notes": ""
                            })
                            total_records += 1
                            
                        except Exception as row_error:
                            # Skip problematic rows
                            continue
                            
                except Exception as sheet_error:
                    # Skip problematic sheets
                    continue
            
            # Insert all records in batch
            if all_records:
                # Insert in chunks of 100 to avoid timeout
                chunk_size = 100
                for i in range(0, len(all_records), chunk_size):
                    chunk = all_records[i:i+chunk_size]
                    result = safe_db_call(
                        lambda: supabase.table("transactions").insert(chunk).execute(),
                        fallback=None,
                        error_prefix="Batch insert failed"
                    )
                
                return f"✅ Successfully migrated {total_records} transactions from {len(excel_file.sheet_names)} months"
            else:
                return "⚠️ No valid transactions found. Check Excel format."
                
        elif table_name == "assets":
            # Handle home.xlsx assets migration
            df = pd.read_excel(file, sheet_name=0, header=2)
            records = []
            
            for _, row in df.iterrows():
                if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                    try:
                        records.append({
                            "asset_name": str(row.iloc[1]),
                            "asset_type": "Property" if "Home" in str(row.iloc[1]) else "Other",
                            "purchase_value": float(str(row.iloc[0]).replace(',', '')),
                            "current_value": float(str(row.iloc[0]).replace(',', '')),
                            "purchase_date": date.today().isoformat(),
                            "location": "Netra Heights" if "Home" in str(row.iloc[1]) else "",
                            "notes": ""
                        })
                    except:
                        continue
            
            if records:
                safe_db_call(lambda: supabase.table("assets").insert(records).execute())
                return f"✅ Migrated {len(records)} assets"
            
        elif table_name == "loans":
            # Handle home.xlsx loan migration
            df = pd.read_excel(file, sheet_name="Home Loan", header=2)
            records = []
            
            for _, row in df.iterrows():
                if "LOAN DISBURSED" in str(row.iloc[2]):
                    try:
                        records.append({
                            "loan_name": "Axis Home Loan",
                            "lender": "Axis Bank",
                            "principal_amount": float(str(row.iloc[1]).replace(',', '')),
                            "current_balance": float(str(row.iloc[1]).replace(',', '')),
                            "interest_rate": 7.15,
                            "emi_amount": 56100.00,  # From your data
                            "start_date": "2023-05-01",
                            "tenure_months": 240,
                            "remaining_emis": 160,
                            "status": "active",
                            "notes": "Home loan for Netra Heights"
                        })
                        break
                    except:
                        continue
            
            if records:
                safe_db_call(lambda: supabase.table("loans").insert(records).execute())
                return f"✅ Migrated {len(records)} loan(s)"
                
        else:
            return f"⚠️ Migration for '{table_name}' not yet configured"
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return f"❌ Migration Error: {str(e)}\n\nDetails: {error_detail}"

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
