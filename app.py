import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Financial OS Pro", layout="wide", page_icon="💰")

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key) if url and key else None

supabase = init_supabase()

# -----------------------------
# CRUD FUNCTIONS
# -----------------------------
def add_transaction(data: dict):
    """Insert new transaction"""
    if supabase:
        return supabase.table("transactions").insert(data).execute()
    return None

def get_transactions(start_date=None, end_date=None, category=None):
    """Fetch transactions with optional filters"""
    if not supabase:
        return pd.DataFrame()
    
    query = supabase.table("transactions").select("*").order("transaction_date", desc=True)
    
    if start_date:
        query = query.gte("transaction_date", start_date.isoformat())
    if end_date:
        query = query.lte("transaction_date", end_date.isoformat())
    if category:
        query = query.eq("category", category)
    
    response = query.execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

def update_transaction(transaction_id: str, updates: dict):
    """Update existing transaction"""
    if supabase:
        updates["updated_at"] = datetime.now().isoformat()
        return supabase.table("transactions").update(updates).eq("id", transaction_id).execute()
    return None

def delete_transaction(transaction_id: str):
    """Soft delete or hard delete transaction"""
    if supabase:
        return supabase.table("transactions").delete().eq("id", transaction_id).execute()
    return None

# -----------------------------
# AUTO-CATEGORY (Based on Your Data Patterns)
# -----------------------------
def auto_categorize(description: str) -> tuple[str, str]:
    """Return (category, subcategory) based on keywords from your Excel"""
    desc_lower = description.lower()
    
    # Your actual patterns from Monthly_Expense.xlsx
    if any(k in desc_lower for k in ["emi", "installment", "loan"]):
        if "home loan" in desc_lower:
            return "Loan EMI", "Home Loan"
        elif "amaze" in desc_lower or "honda" in desc_lower:
            return "Loan EMI", "Car Loan - Amaze"
        return "Loan EMI", "Other Loan"
    
    if any(k in desc_lower for k in ["petrol", "diesel", "fuel", "cbi"]):
        return "Fuel", "Petrol/Diesel"
    
    if any(k in desc_lower for k in ["hdfc credit", "credit card", "axis bank"]):
        return "Credit Card", "HDFC/Axis"
    
    if any(k in desc_lower for k in ["home", "rent", "maintenance", "netra"]):
        return "Home", "Rent/Maintenance"
    
    if any(k in desc_lower for k in ["mandal", "ratnavatika", "rajumama"]):
        return "Contributions", "Mandal/Fund"
    
    if any(k in desc_lower for k in ["dips", "transfer to dips", "to dips"]):
        return "Family Transfer", "Dips"
    
    if any(k in desc_lower for k in ["mom", "mother", "pension"]):
        return "Family", "Mom Expenses"
    
    if any(k in desc_lower for k in ["prihaan", "baby", "toy", "school"]):
        return "Child", "Prihaan"
    
    if any(k in desc_lower for k in ["zomato", "swiggy", "dosa", "pizza", "nasto"]):
        return "Food", "Dining Out"
    
    if any(k in desc_lower for k in ["amazon", "flipkart", "meesho", "reliance"]):
        return "Shopping", "Online"
    
    if any(k in desc_lower for k in ["torrent", "adani", "power", "light bill"]):
        return "Utilities", "Electricity"
    
    if any(k in desc_lower for k in ["recharge", "jio", "airtel", "vodafone"]):
        return "Utilities", "Mobile/Internet"
    
    if any(k in desc_lower for k in ["medicine", "hospital", "clinic", "pranami"]):
        return "Healthcare", "Medicine/Doctor"
    
    return "Other", "Uncategorized"

# -----------------------------
# EXCEL MIGRATION TOOL
# -----------------------------
def migrate_excel_to_db(file, table_name: str):
    """One-time migration from Excel to Supabase"""
    try:
        df = pd.read_excel(file)
        df = df.dropna(how="all")
        
        if table_name == "transactions":
            # Map your Monthly_Expense.xlsx columns
            records = []
            for _, row in df.iterrows():
                if pd.isna(row.get("Date")) or pd.isna(row.get("Rs")):
                    continue
                desc = str(row.get("Discription", ""))
                cat, subcat = auto_categorize(desc)
                records.append({
                    "transaction_date": pd.to_datetime(row["Date"]).date(),
                    "amount": float(row["Rs"]),
                    "description": desc,
                    "category": cat,
                    "subcategory": subcat,
                    "payment_method": "Unknown",  # Can be enhanced
                    "month_year": pd.to_datetime(row["Date"]).strftime("%b-%y"),
                    "is_recurring": "emi" in desc.lower() or "installment" in desc.lower()
                })
            
            if records and supabase:
                result = supabase.table("transactions").insert(records).execute()
                return f"✅ Migrated {len(records)} transactions"
        
        return "⚠️ Migration not configured for this table"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.title("💰 Financial OS Pro")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📊 Navigate",
    ["🏠 Dashboard", "📝 Transactions", "💳 Loans", "📈 Investments", "🏠 Assets", "⚙️ Settings"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("📁 Data Management")
uploaded_file = st.sidebar.file_uploader("Import Excel (One-time)", type=["xlsx", "csv"])
target_table = st.sidebar.selectbox("Import to:", ["transactions", "assets", "loans", "investments"])

if uploaded_file and st.sidebar.button("🔄 Migrate to Database"):
    with st.spinner("Migrating..."):
        result = migrate_excel_to_db(uploaded_file, target_table)
        st.sidebar.success(result) if "✅" in result else st.sidebar.error(result)

# -----------------------------
# PAGE: DASHBOARD
# -----------------------------
if page == "🏠 Dashboard":
    st.title("🏠 Financial Dashboard")
    
    # Fetch summary data
    df_trans = get_transactions()
    
    if not df_trans.empty:
        # Convert amount to numeric
        df_trans["amount"] = pd.to_numeric(df_trans["amount"], errors="coerce").fillna(0)
        
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        total_income = df_trans[df_trans["amount"] > 0]["amount"].sum()
        total_expense = abs(df_trans[df_trans["amount"] < 0]["amount"].sum())
        net_cashflow = total_income + total_expense  # expense is negative
        
        col1.metric("💵 Total Income", f"₹ {total_income:,.0f}")
        col2.metric("💸 Total Expenses", f"₹ {abs(total_expense):,.0f}")
        col3.metric("📊 Net Cashflow", f"₹ {net_cashflow:,.0f}", 
                   delta=f"{net_cashflow/total_income*100:.1f}%" if total_income else None)
        col4.metric("🔄 Transactions", f"{len(df_trans)}")
        
        # Monthly Trend
        df_trans["transaction_date"] = pd.to_datetime(df_trans["transaction_date"])
        monthly = df_trans.groupby(df_trans["transaction_date"].dt.to_period("M"))["amount"].sum().reset_index()
        monthly["period"] = monthly["transaction_date"].astype(str)
        
        fig = px.bar(monthly, x="period", y="amount", 
                    title="📈 Monthly Cashflow Trend",
                    color="amount", color_continuous_scale=["red", "green"])
        st.plotly_chart(fig, use_container_width=True)
        
        # Category Breakdown
        if "category" in df_trans.columns:
            expenses = df_trans[df_trans["amount"] < 0].copy()
            expenses["abs_amt"] = expenses["amount"].abs()
            cat_summary = expenses.groupby("category")["abs_amt"].sum().nlargest(10).reset_index()
            
            fig2 = px.pie(cat_summary, values="abs_amt", names="category", 
                         title="🎯 Top Expense Categories")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("📭 No transactions found. Import your Excel file or add manually below.")

# -----------------------------
# PAGE: TRANSACTIONS (CRUD)
# -----------------------------
elif page == "📝 Transactions":
    st.title("📝 Manage Transactions")
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📋 View", "➕ Add New", "✏️ Edit/Delete"])
    
    with tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            start_dt = st.date_input("From", value=date(2023, 1, 1))
        with col2:
            end_dt = st.date_input("To", value=date.today())
        with col3:
            cat_filter = st.selectbox("Category", ["All"] + ["Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Other"])
        
        # Fetch and display
        df = get_transactions(start_dt, end_dt, cat_filter if cat_filter != "All" else None)
        
        if not df.empty:
            # Editable dataframe (Streamlit's built-in editor)
            edited_df = st.data_editor(
                df,
                column_config={
                    "id": None,  # Hide ID
                    "transaction_date": st.column_config.DateColumn("Date"),
                    "amount": st.column_config.NumberColumn("Amount (₹)", format="₹ %.2f"),
                    "description": st.column_config.TextColumn("Description", width="large"),
                    "category": st.column_config.SelectboxColumn("Category", options=["Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Family Transfer", "Child", "Contributions", "Credit Card", "Other"]),
                    "subcategory": st.column_config.TextColumn("Subcategory"),
                    "payment_method": st.column_config.SelectboxColumn("Method", options=["CBI", "HDFC", "Axis", "UPI", "Cash", "Credit Card"]),
                    "month_year": None,  # Auto-calculated
                    "is_recurring": st.column_config.CheckboxColumn("Recurring"),
                    "notes": st.column_config.TextColumn("Notes"),
                    "created_at": None,
                    "updated_at": None,
                },
                hide_index=True,
                num_rows="dynamic"
            )
            
            # Save changes button
            if st.button("💾 Save Changes"):
                for index, row in edited_df.iterrows():
                    if index < len(df):  # Existing row
                        orig_id = df.iloc[index]["id"]
                        updates = {
                            "transaction_date": row["transaction_date"].isoformat() if isinstance(row["transaction_date"], date) else row["transaction_date"],
                            "amount": float(row["amount"]),
                            "description": row["description"],
                            "category": row["category"],
                            "subcategory": row["subcategory"],
                            "payment_method": row["payment_method"],
                            "is_recurring": bool(row["is_recurring"]),
                            "notes": row["notes"]
                        }
                        update_transaction(orig_id, updates)
                st.success("✅ Changes saved!")
                st.rerun()
        else:
            st.warning("No transactions match your filters.")
    
    with tab2:
        st.subheader("➕ Add New Transaction")
        with st.form("add_txn_form"):
            col1, col2 = st.columns(2)
            with col1:
                txn_date = st.date_input("Date", value=date.today())
                amount = st.number_input("Amount (₹)", step=0.01, format="%.2f")
                is_income = st.checkbox("This is Income (positive)")
                payment_method = st.selectbox("Payment Method", ["CBI", "HDFC", "Axis", "UPI", "Cash", "Credit Card"])
            with col2:
                description = st.text_input("Description", placeholder="e.g., Honda Amaze EMI, Petrol at Viramgam")
                # Auto-suggest category
                if description:
                    auto_cat, auto_sub = auto_categorize(description)
                    st.caption(f"🤖 Auto-suggested: {auto_cat} → {auto_sub}")
                category = st.selectbox("Category", ["Loan EMI", "Fuel", "Home", "Food", "Shopping", "Healthcare", "Utilities", "Family Transfer", "Child", "Contributions", "Credit Card", "Other"])
                subcategory = st.text_input("Subcategory", placeholder="e.g., Home Loan, HDFC Card")
            
            is_recurring = st.checkbox("Recurring Expense (e.g., EMI, Subscription)")
            notes = st.text_area("Notes (optional)")
            
            submitted = st.form_submit_button("✨ Add Transaction")
            
            if submitted:
                final_amount = abs(amount) if is_income else -abs(amount)
                data = {
                    "transaction_date": txn_date.isoformat(),
                    "amount": final_amount,
                    "description": description,
                    "category": category,
                    "subcategory": subcategory,
                    "payment_method": payment_method,
                    "month_year": txn_date.strftime("%b-%y"),
                    "is_recurring": is_recurring,
                    "notes": notes
                }
                result = add_transaction(data)
                if result:
                    st.success("✅ Transaction added!")
                    st.rerun()
                else:
                    st.error("❌ Failed to add. Check Supabase connection.")
    
    with tab3:
        st.subheader("✏️ Edit or Delete Existing")
        search_term = st.text_input("🔍 Search by description...")
        if search_term:
            df_search = get_transactions()
            df_search = df_search[df_search["description"].str.contains(search_term, case=False, na=False)]
            
            if not df_search.empty:
                for _, row in df_search.iterrows():
                    with st.expander(f"{row['transaction_date']} | ₹{row['amount']:,.2f} | {row['description'][:50]}..."):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Category:** {row['category']} | **Method:** {row['payment_method']}")
                            if row['notes']:
                                st.write(f"📝 {row['notes']}")
                        with col2:
                            if st.button("🗑️ Delete", key=f"del_{row['id']}"):
                                delete_transaction(row['id'])
                                st.success("Deleted!")
                                st.rerun()
            else:
                st.info("No matches found.")

# -----------------------------
# PAGE: LOANS
# -----------------------------
elif page == "💳 Loans":
    st.title("💳 Loan Tracker")
    
    # Fetch loans
    if supabase:
        loans_resp = supabase.table("loans").select("*").execute()
        df_loans = pd.DataFrame(loans_resp.data) if loans_resp.data else pd.DataFrame()
    else:
        df_loans = pd.DataFrame()
    
    if not df_loans.empty:
        # Summary cards
        total_debt = df_loans["current_balance"].sum()
        total_emi = df_loans["emi_amount"].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("🏦 Total Debt", f"₹ {total_debt:,.0f}")
        c2.metric("📅 Monthly EMI", f"₹ {total_emi:,.0f}")
        c3.metric("📊 Active Loans", f"{len(df_loans[df_loans['status']=='active'])}")
        
        # Loan details table
        st.dataframe(
            df_loans[["loan_name", "lender", "current_balance", "emi_amount", "interest_rate", "remaining_emis", "status"]],
            column_config={
                "current_balance": st.column_config.NumberColumn("Balance (₹)", format="₹ %.0f"),
                "emi_amount": st.column_config.NumberColumn("EMI (₹)", format="₹ %.0f"),
                "interest_rate": st.column_config.NumberColumn("Rate (%)", format="%.2f%%"),
            },
            hide_index=True
        )
        
        # Prepayment calculator (simple)
        st.subheader("🎯 Prepayment Simulator")
        selected_loan = st.selectbox("Select Loan", df_loans["loan_name"])
        loan = df_loans[df_loans["loan_name"] == selected_loan].iloc[0]
        
        extra_payment = st.number_input("Extra Payment per Month (₹)", min_value=0, step=1000)
        if extra_payment > 0:
            # Simplified calculation
            new_emi = loan["emi_amount"] + extra_payment
            # Approximate months saved (not exact amortization)
            months_saved = int((loan["current_balance"] / loan["emi_amount"]) - (loan["current_balance"] / new_emi))
            interest_saved = months_saved * loan["emi_amount"] * (loan["interest_rate"]/1200)
            
            st.success(f"✨ Paying ₹{extra_payment:,.0f} extra/month could save ~{months_saved} EMIs and ₹{interest_saved:,.0f} in interest!")
    else:
        st.info("No loans recorded. Add your Home Loan, Car Loan details in Settings → Add Loan")

# -----------------------------
# PAGE: INVESTMENTS
# -----------------------------
elif page == "📈 Investments":
    st.title("📈 Investment Portfolio")
    
    if supabase:
        inv_resp = supabase.table("investments").select("*").execute()
        df_inv = pd.DataFrame(inv_resp.data) if inv_resp.data else pd.DataFrame()
    else:
        df_inv = pd.DataFrame()
    
    if not df_inv.empty:
        # Portfolio summary
        total_invested = df_inv["invested_amount"].sum()
        current_value = df_inv["current_value"].sum()
        total_gain = current_value - total_invested
        
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Invested", f"₹ {total_invested:,.0f}")
        c2.metric("📊 Current Value", f"₹ {current_value:,.0f}")
        c3.metric("📈 Total Gain/Loss", f"₹ {total_gain:,.0f}", 
                 delta=f"{(total_gain/total_invested)*100:.2f}%" if total_invested else None)
        
        # Pie chart by type
        fig = px.pie(df_inv, values="current_value", names="investment_type", 
                    title="🥧 Allocation by Type", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.dataframe(
            df_inv[["investment_name", "investment_type", "institution", "invested_amount", "current_value", "interest_rate", "maturity_date", "status"]],
            column_config={
                "invested_amount": st.column_config.NumberColumn("Invested (₹)", format="₹ %.0f"),
                "current_value": st.column_config.NumberColumn("Current (₹)", format="₹ %.0f"),
                "interest_rate": st.column_config.NumberColumn("Rate (%)", format="%.2f%%"),
                "maturity_date": st.column_config.DateColumn("Maturity"),
            },
            hide_index=True
        )
    else:
        st.info("No investments tracked yet. Add FDs, LIC, Mutual Funds in Settings.")

# -----------------------------
# PAGE: SETTINGS (Add Assets, Manage Data)
# -----------------------------
elif page == "⚙️ Settings":
    st.title("⚙️ Settings & Data Management")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Asset", "➕ Add Loan", "➕ Add Investment"])
    
    with tab1:
        st.subheader("🏠 Add New Asset")
        with st.form("add_asset"):
            asset_name = st.text_input("Asset Name", placeholder="e.g., Netra Heights Flat, Gold Necklace")
            asset_type = st.selectbox("Type", ["Property", "Gold", "Vehicle", "Electronics", "Furniture", "Other"])
            purchase_value = st.number_input("Purchase Value (₹)", min_value=0.0, step=1000.0)
            current_value = st.number_input("Current Estimated Value (₹)", min_value=0.0, step=1000.0)
            purchase_date = st.date_input("Purchase Date")
            location = st.text_input("Location", placeholder="e.g., Netra Heights, Viramgam Home")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("💾 Save Asset"):
                if supabase:
                    supabase.table("assets").insert({
                        "asset_name": asset_name,
                        "asset_type": asset_type,
                        "purchase_value": purchase_value,
                        "current_value": current_value,
                        "purchase_date": purchase_date.isoformat(),
                        "location": location,
                        "notes": notes
                    }).execute()
                    st.success("✅ Asset added!")
                else:
                    st.error("❌ Supabase not connected")
    
    with tab2:
        st.subheader("💳 Add New Loan")
        with st.form("add_loan"):
            loan_name = st.text_input("Loan Name", placeholder="e.g., Home Loan - Axis Bank")
            lender = st.text_input("Lender", placeholder="Axis Bank, Bank of Baroda")
            principal = st.number_input("Principal Amount (₹)", min_value=0.0, step=10000.0)
            current_balance = st.number_input("Current Balance (₹)", min_value=0.0, step=10000.0)
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0, step=0.05)
            emi_amount = st.number_input("EMI Amount (₹)", min_value=0.0, step=100.0)
            start_date = st.date_input("Start Date")
            tenure = st.number_input("Tenure (months)", min_value=1, step=12)
            remaining = st.number_input("Remaining EMIs", min_value=0)
            
            if st.form_submit_button("💾 Save Loan"):
                if supabase:
                    supabase.table("loans").insert({
                        "loan_name": loan_name,
                        "lender": lender,
                        "principal_amount": principal,
                        "current_balance": current_balance,
                        "interest_rate": interest_rate,
                        "emi_amount": emi_amount,
                        "start_date": start_date.isoformat(),
                        "tenure_months": tenure,
                        "remaining_emis": remaining,
                        "status": "active"
                    }).execute()
                    st.success("✅ Loan added!")
    
    with tab3:
        st.subheader("📈 Add New Investment")
        with st.form("add_investment"):
            inv_name = st.text_input("Investment Name", placeholder="e.g., Saurashtra FD, LIC Policy")
            inv_type = st.selectbox("Type", ["FD", "LIC", "MutualFund", "Gold", "PPF", "Stocks", "Other"])
            institution = st.text_input("Institution", placeholder="Saurashtra Bank, HDFC, Upstox")
            invested = st.number_input("Invested Amount (₹)", min_value=0.0, step=1000.0)
            current_val = st.number_input("Current Value (₹)", min_value=0.0, step=1000.0)
            rate = st.number_input("Interest Rate / Expected Return (%)", min_value=0.0, step=0.1)
            maturity = st.date_input("Maturity Date (if applicable)")
            holder = st.selectbox("Account Holder", ["Tejas", "Mom", "Dips", "Prihaan", "Joint"])
            
            if st.form_submit_button("💾 Save Investment"):
                if supabase:
                    supabase.table("investments").insert({
                        "investment_name": inv_name,
                        "investment_type": inv_type,
                        "institution": institution,
                        "invested_amount": invested,
                        "current_value": current_val,
                        "interest_rate": rate,
                        "maturity_date": maturity.isoformat() if maturity else None,
                        "account_holder": holder,
                        "status": "active"
                    }).execute()
                    st.success("✅ Investment added!")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("💰 Financial OS Pro | Built for Tejas | Data secured in Supabase Cloud")
