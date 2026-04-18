import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime, date
import re

st.set_page_config(page_title="💰 Financial OS Pro", layout="wide", page_icon="💰")

# =============================================================================
# 🔐 PASSWORD PROTECTION
# =============================================================================
def check_password():
    """Returns True if user enters correct password"""
    PASSWORD = st.secrets.get("APP_PASSWORD", "Prihaan1208")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        # Show logout button in sidebar
        if st.sidebar.button("🔓 Logout"):
            st.session_state.authenticated = False
            st.rerun()
        return True
    
    # Password form
    st.markdown("<div style='text-align: center; padding: 50px;'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Financial OS Pro")
    st.markdown("Enter password to access your dashboard")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Password", type="password", key="pwd_input", label_visibility="collapsed")
        if st.button("🔓 Unlock Dashboard", type="primary", use_container_width=True):
            if password == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Incorrect password")
    return False

if not check_password():
    st.stop()

# =============================================================================
# 🗄️ SUPABASE CONNECTION
# =============================================================================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("⚠️ Configure SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets")
        return None

supabase = init_supabase()

# =============================================================================
# 🛡️ SAFE DATABASE HELPER
# =============================================================================
def safe_db_call(func, fallback=None, error_prefix="Database Error"):
    try:
        if not supabase:
            return fallback
        result = func()
        return result
    except Exception as e:
        st.warning(f"🔌 {error_prefix}: {type(e).__name__}")
        return fallback

# =============================================================================
# 📦 CRUD FUNCTIONS
# =============================================================================
def add_transaction(data: dict):
    return safe_db_call(
        lambda: supabase.table("transactions").insert(data).execute(),
        fallback=None, error_prefix="Failed to add transaction"
    )

def get_transactions(start_date=None, end_date=None, category=None):
    def _fetch():
        query = supabase.table("transactions").select("*").order("transaction_date", desc=True)
        if start_date: query = query.gte("transaction_date", start_date.isoformat())
        if end_date: query = query.lte("transaction_date", end_date.isoformat())
        if category and category != "All": query = query.eq("category", category)
        response = query.execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    return safe_db_call(_fetch, fallback=pd.DataFrame(), error_prefix="Could not load transactions")

def update_transaction(transaction_id: str, updates: dict):
    def _update():
        updates["updated_at"] = datetime.now().isoformat()
        return supabase.table("transactions").update(updates).eq("id", transaction_id).execute()
    return safe_db_call(_update, fallback=None, error_prefix="Failed to update")

def delete_transaction(transaction_id: str):
    return safe_db_call(
        lambda: supabase.table("transactions").delete().eq("id", transaction_id).execute(),
        fallback=None, error_prefix="Failed to delete"
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

def get_all_assets():
    def _fetch():
        res = supabase.table("assets").select("*").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    return safe_db_call(_fetch, fallback=pd.DataFrame(), error_prefix="Could not load assets")

# =============================================================================
# 🤖 AUTO-CATEGORIZE (Based on YOUR Excel data patterns)
# =============================================================================
def auto_categorize(description: str) -> tuple[str, str]:
    desc_lower = description.lower()
    
    # Your actual patterns from Monthly_Expense.xlsx
    patterns = [
        (["home loan", "loan installment", "emi"], "Loan EMI", "Home Loan"),
        (["amaze", "honda", "car emi"], "Loan EMI", "Car Loan - Amaze"),
        (["petrol", "diesel", "fuel", "cbi"], "Fuel", "Petrol/Diesel"),
        (["hdfc credit", "credit card", "axis bank"], "Credit Card", "HDFC/Axis"),
        (["home", "rent", "maintenance", "netra", "marble", "pvc"], "Home", "Rent/Maintenance"),
        (["dips", "to dips", "transfer to dips"], "Family Transfer", "Dips"),
        (["mom", "mother", "pension", "shilpa"], "Family", "Mom Expenses"),
        (["prihaan", "baby", "school", "toy", "edu"], "Child", "Prihaan"),
        (["zomato", "swiggy", "dosa", "nasto", "pizza", "khiru"], "Food", "Dining Out"),
        (["amazon", "flipkart", "meesho", "reliance", "dmart", "zepto"], "Shopping", "Online/Retail"),
        (["torrent", "adani", "power", "light bill", "electricity"], "Utilities", "Electricity"),
        (["jio", "airtel", "vodafone", "recharge", "broadband"], "Utilities", "Mobile/Internet"),
        (["medicine", "hospital", "clinic", "pranami", "ketorol"], "Healthcare", "Medical"),
        (["ratnavatika", "rajumama", "mandal"], "Contributions", "Mandal/Fund"),
        (["lic", "tata aia", "insurance"], "Insurance", "LIC/Premium"),
        (["netflix", "hotstar", "prime"], "Entertainment", "Subscriptions"),
        (["uber", "ola", "gsrtc", "train", "ticket"], "Transport", "Travel"),
        (["gold", "jewellery", "chain", "necklace"], "Investment", "Gold"),
        (["fd", "ppf", "mutual fund", "elss", "upstox"], "Investment", "FD/MF"),
    ]
    
    for keywords, cat, sub in patterns:
        if any(k in desc_lower for k in keywords):
            return cat, sub
    return "Other", "Uncategorized"

# =============================================================================
# 📤 EXCEL MIGRATION (Tailored to YOUR file structure)
# =============================================================================
def migrate_excel_to_db(file, table_name: str):
    if not supabase: 
        return "❌ Supabase not connected"
    
    try:
        if table_name == "transactions":
            excel_file = pd.ExcelFile(file)
            total_records = 0
            all_records = []
            
            for sheet_name in excel_file.sheet_names:
                # Skip non-month sheets
                if not re.match(r'^[A-Z][a-z]{2}-\d{2}$', sheet_name):
                    continue
                
                try:
                    # Read with header at row 3 (0-indexed) based on your Excel structure
                    df = pd.read_excel(file, sheet_name=sheet_name, header=3)
                    df = df.dropna(how='all').dropna(axis=1, how='all')
                    
                    if df.shape[1] < 3:
                        continue
                    
                    # Your columns: Date (0), Rs (1), Discription (2)
                    for _, row in df.iterrows():
                        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):
                            continue
                        
                        try:
                            date_val = row.iloc[0]
                            amount = float(str(row.iloc[1]).replace(',', ''))
                            desc = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
                            
                            # Skip summary/header rows
                            if any(k in desc.lower() for k in ["total", "income", "expense", "bank", "details", "salary", "---"]):
                                continue
                            
                            cat, sub = auto_categorize(desc)
                            
                            # Parse date
                            if isinstance(date_val, pd.Timestamp):
                                date_iso = date_val.date().isoformat()
                                month_year = date_val.strftime("%b-%y")
                            else:
                                date_iso = str(date_val)
                                month_year = sheet_name
                            
                            all_records.append({
                                "transaction_date": date_iso,
                                "amount": -abs(amount),  # All expenses negative
                                "description": desc,
                                "category": cat,
                                "subcategory": sub,
                                "payment_method": "Unknown",
                                "month_year": month_year,
                                "is_recurring": any(k in desc.lower() for k in ["emi", "installment", "rd", "lic"]),
                                "notes": ""
                            })
                            total_records += 1
                        except:
                            continue
                except:
                    continue
            
            if all_records:
                # Batch insert in chunks
                for i in range(0, len(all_records), 100):
                    chunk = all_records[i:i+100]
                    safe_db_call(
                        lambda c=chunk: supabase.table("transactions").insert(c).execute(),
                        fallback=None
                    )
                return f"✅ Migrated {total_records} transactions from {len(excel_file.sheet_names)} months"
            return "⚠️ No valid transactions found"
            
        elif table_name == "assets":
            df = pd.read_excel(file, sheet_name=0, header=2)
            records = []
            for _, row in df.iterrows():
                if pd.notna(row.iloc[0]) and pd.notna(row.iloc[1]):
                    try:
                        value = float(str(row.iloc[0]).replace(',', ''))
                        name = str(row.iloc[1]).strip()
                        if "home" in name.lower() or "netra" in name.lower():
                            asset_type = "Property"
                        elif "gold" in name.lower() or "jewel" in name.lower():
                            asset_type = "Gold"
                        elif "fan" in name.lower() or "light" in name.lower() or "tv" in name.lower():
                            asset_type = "Electronics"
                        else:
                            asset_type = "Other"
                        records.append({
                            "asset_name": name,
                            "asset_type": asset_type,
                            "purchase_value": value,
                            "current_value": value,
                            "purchase_date": date.today().isoformat(),
                            "location": "Netra Heights" if "home" in name.lower() else "",
                            "notes": ""
                        })
                    except:
                        continue
            if records:
                safe_db_call(lambda: supabase.table("assets").insert(records).execute())
                return f"✅ Migrated {len(records)} assets"
            return "⚠️ No assets found"
            
        elif table_name == "loans":
            # Add your Axis Home Loan from home.xlsx
            record = {
                "loan_name": "Axis Home Loan",
                "lender": "Axis Bank",
                "principal_amount": 2381324.00,
                "current_balance": 2381324.00,
                "interest_rate": 7.15,
                "emi_amount": 56100.00,
                "start_date": "2023-05-01",
                "tenure_months": 240,
                "remaining_emis": 160,
                "status": "active",
                "notes": "Netra Heights home loan"
            }
            safe_db_call(lambda: supabase.table("loans").insert([record]).execute())
            return "✅ Added Axis Home Loan"
            
        return f"⚠️ Migration for '{table_name}' not configured"
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# =============================================================================
# 🧮 NET WORTH CALCULATOR
# =============================================================================
def calculate_net_worth():
    """Calculate total net worth from all tables"""
    assets_val = 0
    investments_val = 0
    debt = 0
    
    # Assets
    df_assets = get_all_assets()
    if not df_assets.empty and "current_value" in df_assets.columns:
        assets_val = pd.to_numeric(df_assets["current_value"], errors="coerce").fillna(0).sum()
    
    # Investments
    df_inv = get_all_investments()
    if not df_inv.empty and "current_value" in df_inv.columns:
        investments_val = pd.to_numeric(df_inv["current_value"], errors="coerce").fillna(0).sum()
    
    # Debt (Loans)
    df_loans = get_all_loans()
    if not df_loans.empty and "current_balance" in df_loans.columns:
        debt = pd.to_numeric(df_loans["current_balance"], errors="coerce").fillna(0).sum()
    
    # Cash from recent transactions (last 30 days)
    df_trans = get_transactions()
    cash = 0
    if not df_trans.empty and "amount" in df_trans.columns:
        df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors="coerce").fillna(0)
        cash = df_trans[df_trans["amount"] > 0]["amount"].sum() + df_trans[df_trans["amount"] < 0]["amount"].sum()
    
    return assets_val + investments_val + cash - debt, assets_val, investments_val, debt, cash

# =============================================================================
# 🧭 SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.title("💰 Financial OS Pro")
st.sidebar.markdown("---")

page = st.sidebar.radio("📊 Navigate", [
    "🏠 Dashboard", "📝 Transactions", "💳 Loans", "📈 Investments", "🏠 Assets", "⚙️ Settings"
])

st.sidebar.markdown("---")
st.sidebar.subheader("📁 Import Data")
uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx", "csv"])
target_table = st.sidebar.selectbox("Import to:", ["transactions", "assets", "loans"])

if uploaded_file and st.sidebar.button("🔄 Migrate"):
    with st.spinner("Processing..."):
        result = migrate_excel_to_db(uploaded_file, target_table)
        st.sidebar.success(result) if "✅" in result else st.sidebar.error(result)

# Connection status
if supabase:
    try:
        supabase.table("transactions").select("id").limit(1).execute()
        st.sidebar.success("🟢 Connected")
    except:
        st.sidebar.warning("🔴 Check RLS/Tables")
else:
    st.sidebar.error("🔴 Supabase not configured")

# =============================================================================
# 🏠 DASHBOARD PAGE
# =============================================================================
if page == "🏠 Dashboard":
    st.title("🏠 Financial Dashboard")
    
    # Net Worth Calculation
    net_worth, assets, investments, debt, cash = calculate_net_worth()
    
    # KPI Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("💎 Net Worth", f"₹ {net_worth:,.0f}")
    c2.metric("🏠 Assets", f"₹ {assets:,.0f}")
    c3.metric("📈 Investments", f"₹ {investments:,.0f}")
    c4.metric("💳 Debt", f"₹ {debt:,.0f}", delta=f"{-debt:,.0f}", delta_color="inverse")
    c5.metric("💵 Cash Flow", f"₹ {cash:,.0f}")
    
    # Transactions Chart
    df_trans = get_transactions()
    if not df_trans.empty:
        df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors="coerce").fillna(0)
        df_trans["transaction_date"] = pd.to_datetime(df_trans["transaction_date"], errors="coerce")
        
        # Monthly trend
        monthly = df_trans.groupby(df_trans["transaction_date"].dt.to_period("M"))["amount"].sum().reset_index()
        monthly["period"] = monthly["transaction_date"].astype(str)
        
        fig = px.bar(
            monthly, x="period", y="amount",
            title="📊 Monthly Cashflow",
            color="amount", color_continuous_scale=["#ef4444", "#22c55e"],
            labels={"period": "Month", "amount": "Amount (₹)"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Category breakdown
        expenses = df_trans[df_trans["amount"] < 0].copy()
        expenses["abs_amt"] = expenses["amount"].abs()
        if "category" in expenses.columns:
            cat_summary = expenses.groupby("category")["abs_amt"].sum().nlargest(8).reset_index()
            fig2 = px.pie(cat_summary, values="abs_amt", names="category", title="🎯 Expense Categories", hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("📭 Import your Excel file to see data")

# =============================================================================
# 📝 TRANSACTIONS PAGE (Full CRUD)
# =============================================================================
elif page == "📝 Transactions":
    st.title("📝 Manage Transactions")
    tab1, tab2, tab3 = st.tabs(["📋 View/Edit", "➕ Add New", "🗑️ Delete"])
    
    with tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            start_dt = st.date_input("From", value=date(2023, 1, 1))
        with col2:
            end_dt = st.date_input("To", value=date.today())
        with col3:
            cat_filter = st.selectbox("Category", ["All", "Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Family Transfer", "Child", "Other"])
        
        df = get_transactions(start_dt, end_dt, cat_filter)
        
        if not df.empty:
            # Editable table
            edited = st.data_editor(
                df,
                column_config={
                    "id": None, "created_at": None, "updated_at": None,
                    "transaction_date": st.column_config.DateColumn("Date"),
                    "amount": st.column_config.NumberColumn("Amount (₹)", format="₹ %.2f"),
                    "description": st.column_config.TextColumn("Description", width="large"),
                    "category": st.column_config.SelectboxColumn("Category", options=["Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Family Transfer", "Child", "Contributions", "Credit Card", "Other"]),
                    "subcategory": st.column_config.TextColumn("Subcategory"),
                    "payment_method": st.column_config.SelectboxColumn("Method", options=["CBI", "HDFC", "Axis", "UPI", "Cash", "Credit Card"]),
                    "is_recurring": st.column_config.CheckboxColumn("Recurring"),
                },
                hide_index=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 Save Changes", type="primary"):
                saved = 0
                for idx, row in edited.iterrows():
                    if idx < len(df):
                        orig_id = df.iloc[idx]["id"]
                        updates = {
                            "transaction_date": row["transaction_date"].isoformat() if isinstance(row["transaction_date"], date) else row["transaction_date"],
                            "amount": float(row["amount"]),
                            "description": row["description"],
                            "category": row["category"],
                            "subcategory": row["subcategory"],
                            "payment_method": row["payment_method"],
                            "is_recurring": bool(row["is_recurring"])
                        }
                        if update_transaction(orig_id, updates):
                            saved += 1
                st.success(f"✅ Saved {saved} changes!")
                st.rerun()
        else:
            st.warning("No transactions. Import Excel or add manually.")
    
    with tab2:
        with st.form("add_txn_form"):
            col1, col2 = st.columns(2)
            with col1:
                txn_date = st.date_input("Date", value=date.today())
                amount = st.number_input("Amount (₹)", step=0.01, format="%.2f")
                is_income = st.checkbox("✅ This is Income")
                method = st.selectbox("Payment Method", ["CBI", "HDFC", "Axis", "UPI", "Cash", "Credit Card"])
            with col2:
                desc = st.text_input("Description", placeholder="e.g., Honda Amaze EMI, Petrol at Viramgam")
                if desc:
                    auto_cat, auto_sub = auto_categorize(desc)
                    st.caption(f"🤖 Suggested: {auto_cat} → {auto_sub}")
                category = st.selectbox("Category", ["Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Family Transfer", "Child", "Contributions", "Credit Card", "Other"])
                subcategory = st.text_input("Subcategory")
            
            is_recurring = st.checkbox("🔄 Recurring (EMI/Subscription)")
            notes = st.text_area("Notes (optional)")
            
            if st.form_submit_button("✨ Add Transaction", type="primary"):
                final_amt = abs(amount) if is_income else -abs(amount)
                result = add_transaction({
                    "transaction_date": txn_date.isoformat(),
                    "amount": final_amt,
                    "description": desc,
                    "category": category,
                    "subcategory": subcategory,
                    "payment_method": method,
                    "month_year": txn_date.strftime("%b-%y"),
                    "is_recurring": is_recurring,
                    "notes": notes
                })
                if result:
                    st.success("✅ Added!")
                    st.rerun()
    
    with tab3:
        search = st.text_input("🔍 Search description to delete")
        if search:
            df_s = get_transactions()
            df_s = df_s[df_s["description"].str.contains(search, case=False, na=False)]
            for _, r in df_s.iterrows():
                if st.button(f"🗑️ Delete: ₹{r['amount']:,.2f} | {r['description'][:50]}", key=f"del_{r['id']}"):
                    delete_transaction(r["id"])
                    st.success("Deleted!")
                    st.rerun()

# =============================================================================
# 💳 LOANS PAGE
# =============================================================================
elif page == "💳 Loans":
    st.title("💳 Loan Tracker")
    
    df_loans = get_all_loans()
    if not df_loans.empty:
        # Summary
        total_debt = pd.to_numeric(df_loans["current_balance"], errors="coerce").fillna(0).sum()
        total_emi = pd.to_numeric(df_loans["emi_amount"], errors="coerce").fillna(0).sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🏦 Total Debt", f"₹ {total_debt:,.0f}")
        c2.metric("📅 Monthly EMI", f"₹ {total_emi:,.0f}")
        c3.metric("📊 Active Loans", f"{len(df_loans[df_loans['status']=='active'])}")
        
        # Table
        st.dataframe(
            df_loans[["loan_name", "lender", "current_balance", "emi_amount", "interest_rate", "remaining_emis", "status"]],
            column_config={
                "current_balance": st.column_config.NumberColumn("Balance (₹)", format="₹ %.0f"),
                "emi_amount": st.column_config.NumberColumn("EMI (₹)", format="₹ %.0f"),
                "interest_rate": st.column_config.NumberColumn("Rate (%)", format="%.2f%%"),
            },
            hide_index=True
        )
        
        # Prepayment Calculator
        st.subheader("🎯 Prepayment Simulator")
        loan = st.selectbox("Select Loan", df_loans["loan_name"])
        selected = df_loans[df_loans["loan_name"] == loan].iloc[0]
        
        extra = st.number_input("Extra Payment/Month (₹)", min_value=0, step=1000)
        if extra > 0:
            new_emi = selected["emi_amount"] + extra
            months_saved = int((selected["current_balance"] / selected["emi_amount"]) - (selected["current_balance"] / new_emi))
            interest_saved = months_saved * selected["emi_amount"] * (selected["interest_rate"]/1200)
            st.success(f"✨ Paying ₹{extra:,.0f} extra could save ~{months_saved} EMIs and ₹{interest_saved:,.0f} interest!")
    else:
        st.info("Add loans via Settings → Add Loan")

# =============================================================================
# 📈 INVESTMENTS PAGE
# =============================================================================
elif page == "📈 Investments":
    st.title("📈 Portfolio")
    
    df_inv = get_all_investments()
    if not df_inv.empty:
        total_inv = pd.to_numeric(df_inv["invested_amount"], errors="coerce").fillna(0).sum()
        current_val = pd.to_numeric(df_inv["current_value"], errors="coerce").fillna(0).sum()
        gain = current_val - total_inv
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Invested", f"₹ {total_inv:,.0f}")
        c2.metric("📊 Current", f"₹ {current_val:,.0f}")
        c3.metric("📈 Gain/Loss", f"₹ {gain:,.0f}", delta=f"{(gain/total_inv)*100:.1f}%" if total_inv else None)
        
        # Pie chart
        if "investment_type" in df_inv.columns:
            fig = px.pie(df_inv, values="current_value", names="investment_type", title="🥧 Allocation", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(
            df_inv[["investment_name", "investment_type", "institution", "invested_amount", "current_value", "interest_rate", "maturity_date"]],
            column_config={
                "invested_amount": st.column_config.NumberColumn("Invested (₹)", format="₹ %.0f"),
                "current_value": st.column_config.NumberColumn("Current (₹)", format="₹ %.0f"),
                "interest_rate": st.column_config.NumberColumn("Rate (%)", format="%.2f%%"),
                "maturity_date": st.column_config.DateColumn("Maturity"),
            },
            hide_index=True
        )
    else:
        st.info("Add investments via Settings")

# =============================================================================
# 🏠 ASSETS PAGE
# =============================================================================
elif page == "🏠 Assets":
    st.title("🏠 Assets Tracker")
    
    df_assets = get_all_assets()
    if not df_assets.empty:
        total_assets = pd.to_numeric(df_assets["current_value"], errors="coerce").fillna(0).sum()
        st.metric("🏠 Total Asset Value", f"₹ {total_assets:,.0f}")
        
        # By type
        if "asset_type" in df_assets.columns:
            type_summary = df_assets.groupby("asset_type")["current_value"].sum().reset_index()
            fig = px.bar(type_summary, x="asset_type", y="current_value", title="📊 Assets by Type", labels={"current_value": "Value (₹)"})
            st.plotly_chart(fig, use_container_width=True)
        
        # Table
        st.dataframe(
            df_assets[["asset_name", "asset_type", "purchase_value", "current_value", "location", "purchase_date"]],
            column_config={
                "purchase_value": st.column_config.NumberColumn("Purchase (₹)", format="₹ %.0f"),
                "current_value": st.column_config.NumberColumn("Current (₹)", format="₹ %.0f"),
                "purchase_date": st.column_config.DateColumn("Purchased"),
            },
            hide_index=True
        )
    else:
        st.info("Add assets via Settings or import home.xlsx")

# =============================================================================
# ⚙️ SETTINGS PAGE
# =============================================================================
elif page == "⚙️ Settings":
    st.title("⚙️ Add Data Manually")
    t1, t2, t3 = st.tabs(["💳 Add Loan", "📈 Add Investment", "🏠 Add Asset"])
    
    with t1:
        with st.form("add_loan"):
            n = st.text_input("Loan Name", placeholder="Axis Home Loan")
            l = st.text_input("Lender", placeholder="Axis Bank")
            b = st.number_input("Current Balance (₹)", step=1000.0)
            e = st.number_input("EMI Amount (₹)", step=100.0)
            r = st.number_input("Interest Rate (%)", step=0.05)
            rem = st.number_input("Remaining EMIs", step=1)
            if st.form_submit_button("💾 Save Loan"):
                safe_db_call(lambda: supabase.table("loans").insert({
                    "loan_name": n, "lender": l, "current_balance": b,
                    "emi_amount": e, "interest_rate": r, "remaining_emis": rem, "status": "active"
                }).execute())
                st.success("✅ Loan added!")
    
    with t2:
        with st.form("add_inv"):
            n = st.text_input("Investment Name")
            t = st.selectbox("Type", ["FD", "LIC", "MutualFund", "Gold", "PPF", "Stocks", "Other"])
            inst = st.text_input("Institution")
            inv = st.number_input("Invested (₹)", step=1000.0)
            cur = st.number_input("Current Value (₹)", step=1000.0)
            rate = st.number_input("Rate (%)", step=0.1)
            mat = st.date_input("Maturity Date", value=None)
            if st.form_submit_button("💾 Save Investment"):
                safe_db_call(lambda: supabase.table("investments").insert({
                    "investment_name": n, "investment_type": t, "institution": inst,
                    "invested_amount": inv, "current_value": cur, "interest_rate": rate,
                    "maturity_date": mat.isoformat() if mat else None, "status": "active"
                }).execute())
                st.success("✅ Investment added!")
    
    with t3:
        with st.form("add_asset"):
            n = st.text_input("Asset Name", placeholder="Netra Heights Flat")
            t = st.selectbox("Type", ["Property", "Gold", "Vehicle", "Electronics", "Furniture", "Other"])
            pv = st.number_input("Purchase Value (₹)", step=1000.0)
            cv = st.number_input("Current Value (₹)", step=1000.0)
            loc = st.text_input("Location", placeholder="Netra Heights, Viramgam")
            pd = st.date_input("Purchase Date", value=date.today())
            if st.form_submit_button("💾 Save Asset"):
                safe_db_call(lambda: supabase.table("assets").insert({
                    "asset_name": n, "asset_type": t, "purchase_value": pv,
                    "current_value": cv, "location": loc, "purchase_date": pd.isoformat()
                }).execute())
                st.success("✅ Asset added!")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("💰 Financial OS Pro | Built for Tejas | Data secured in Supabase Cloud 🔐")
