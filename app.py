import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tejas | Finance Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── THEME ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark app background */
.stApp { background: #0a0f1e; }
.main .block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b27 100%);
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f0f6fc !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #8b949e !important; }
[data-testid="stSidebarNav"] { display: none; }

/* Headings */
h1 { font-size: 1.8rem !important; font-weight: 700 !important; color: #f0f6fc !important; }
h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: #e6edf3 !important; }
h3 { font-size: 1rem !important; font-weight: 500 !important; color: #c9d1d9 !important; }

/* KPI metric cards */
[data-testid="metric-container"] {
    background: #161b27;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { color: #f0f6fc !important; font-size: 1.6rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"] svg { display: none; }

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    border: 1px solid #30363d !important;
    background: #21262d !important;
    color: #c9d1d9 !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    border-color: #58a6ff !important;
    color: #58a6ff !important;
    background: #1c2128 !important;
}

/* Primary button override via class trick */
.primary-btn > button {
    background: #1f6feb !important;
    border-color: #1f6feb !important;
    color: white !important;
}
.primary-btn > button:hover {
    background: #388bfd !important;
    border-color: #388bfd !important;
    color: white !important;
}

/* Danger button */
.danger-btn > button {
    background: #3d1a1a !important;
    border-color: #da3633 !important;
    color: #ff7b72 !important;
}
.danger-btn > button:hover {
    background: #da3633 !important;
    color: white !important;
}

/* Forms */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #161b27 !important;
    border: 1px solid #30363d !important;
    color: #f0f6fc !important;
    border-radius: 8px !important;
}
.stTextInput > label, .stNumberInput > label,
.stSelectbox > label, .stDateInput > label,
.stTextArea > label { color: #8b949e !important; font-size: 0.78rem !important; }

/* Dataframe / table */
.stDataFrame { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrame"] { background: #161b27; }

/* Expander */
.streamlit-expanderHeader {
    background: #161b27 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
    color: #c9d1d9 !important;
}
.streamlit-expanderContent {
    background: #0d1117 !important;
    border: 1px solid #21262d !important;
    border-radius: 0 0 8px 8px !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #0d1117; border-bottom: 1px solid #21262d; gap: 4px; }
.stTabs [data-baseweb="tab"] { color: #8b949e; border-radius: 6px 6px 0 0; padding: 0.5rem 1.2rem; font-size: 0.85rem; }
.stTabs [aria-selected="true"] { background: #1f6feb !important; color: white !important; }

/* Divider */
hr { border-color: #21262d !important; }

/* Success/error messages */
.stSuccess { background: #0d1f0d !important; border: 1px solid #2ea043 !important; color: #56d364 !important; border-radius: 8px; }
.stError { background: #1f0d0d !important; border: 1px solid #da3633 !important; color: #ff7b72 !important; border-radius: 8px; }
.stWarning { background: #1f1a0d !important; border: 1px solid #9e6a03 !important; color: #f0883e !important; border-radius: 8px; }

/* Custom card style via markdown */
.fin-card {
    background: #161b27;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.75rem;
}
.fin-card-title {
    font-size: 0.7rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.4rem;
}
.fin-card-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #f0f6fc;
    line-height: 1.1;
}
.fin-card-sub { font-size: 0.75rem; margin-top: 0.3rem; }
.green { color: #56d364; }
.red { color: #ff7b72; }
.amber { color: #f0883e; }
.blue { color: #58a6ff; }
.purple { color: #bc8cff; }
.teal { color: #39d353; }
.muted { color: #8b949e; }

/* Badge */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.badge-green  { background: #0d2918; color: #56d364; border: 1px solid #2ea043; }
.badge-red    { background: #2d1114; color: #ff7b72; border: 1px solid #da3633; }
.badge-amber  { background: #2d1f05; color: #f0883e; border: 1px solid #9e6a03; }
.badge-blue   { background: #051229; color: #58a6ff; border: 1px solid #1f6feb; }
.badge-purple { background: #1a0d29; color: #bc8cff; border: 1px solid #8957e5; }
.badge-teal   { background: #0a1f1f; color: #3fb950; border: 1px solid #1a7f37; }

.progress-track {
    height: 10px;
    background: #21262d;
    border-radius: 5px;
    overflow: hidden;
    margin: 8px 0;
}
.progress-fill {
    height: 100%;
    border-radius: 5px;
    transition: width 0.5s ease;
}

.section-header {
    font-size: 0.7rem;
    font-weight: 600;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding-bottom: 8px;
    border-bottom: 1px solid #21262d;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─── SUPABASE CONNECTION ───────────────────────────────────────────────────────
@st.cache_resource
def get_supabase():
    url  = st.secrets["SUPABASE_URL"]
    key  = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

sb = get_supabase()

# ─── DB HELPERS ───────────────────────────────────────────────────────────────
def q(table, order="created_at", desc=True):
    try:
        r = sb.table(table).select("*").order(order, desc=desc).execute()
        return r.data or []
    except:
        return []

def insert(table, data):
    try:
        sb.table(table).insert(data).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Insert failed: {e}")
        return False

def update(table, id, data):
    try:
        sb.table(table).update(data).eq("id", id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Update failed: {e}")
        return False

def delete(table, id):
    try:
        sb.table(table).delete().eq("id", id).execute()
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Delete failed: {e}")
        return False

# ─── FORMATTING ───────────────────────────────────────────────────────────────
def inr(v, lakh=True):
    v = float(v or 0)
    if lakh and abs(v) >= 100000:
        return f"₹{v/100000:.1f}L"
    return f"₹{int(round(v)):,}"

def badge(text, color="blue"):
    return f'<span class="badge badge-{color}">{text}</span>'

def progress_bar(pct, color="#1f6feb"):
    return f'''<div class="progress-track">
        <div class="progress-fill" style="width:{pct}%;background:{color}"></div>
    </div>'''

PLOT_BG   = "#0d1117"
GRID_CLR  = "#21262d"
TEXT_CLR  = "#8b949e"
COLORS    = ["#1f6feb","#2ea043","#da3633","#9e6a03","#8957e5","#1a7f37","#0969da"]

def plotly_dark(fig, height=320):
    fig.update_layout(
        height=height, plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=TEXT_CLR, family="Inter"),
        margin=dict(l=8,r=8,t=32,b=8),
        xaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR),
        yaxis=dict(gridcolor=GRID_CLR, linecolor=GRID_CLR),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_CLR)),
    )
    return fig

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💰 Finance Hub")
    st.markdown("**Tejas Patel** · Personal Finance")
    st.divider()

    page = st.radio("", [
        "📊  Overview",
        "💸  Expenses",
        "📈  Income",
        "🏦  Banks & MFs",
        "🏛️  Investments",
        "🏠  Home Loan",
        "👥  Dues",
    ], label_visibility="collapsed")

    st.divider()

    # Live snapshot in sidebar
    banks_data = q("bank_accounts", order="id", desc=False)
    inv_data   = q("investments", order="id", desc=False)
    dues_data  = q("dues", order="created_at")
    loan_data  = q("home_loan", order="id", desc=False)

    bank_total = sum(float(b["balance"]) for b in banks_data)
    inv_total  = sum(float(i["amount"])  for i in inv_data)
    due_total  = sum(float(d["amount"])  for d in dues_data if d["status"] != "Settled")
    loan_pend  = (float(loan_data[0]["pending_emi"]) * float(loan_data[0]["monthly_emi"])) if loan_data else 0

    st.markdown(f"**Banks + MFs** &nbsp; `{inr(bank_total)}`")
    st.markdown(f"**Investments** &nbsp; `{inr(inv_total)}`")
    st.markdown(f"**Loan left** &nbsp; `{inr(loan_pend)}`")
    st.markdown(f"**Dues out** &nbsp; `{inr(due_total)}`")
    st.divider()
    st.caption(f"Connected · cozpsoousfuhhydetflp")

# ─── PAGE ROUTER ──────────────────────────────────────────────────────────────
p = page.strip().split("  ")[1]

# ══════════════════════════════════════════════════════════════════════════════
# 1. OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if p == "Overview":
    st.title("📊 Financial Overview")

    exp_data = q("expenses", order="date")
    inc_data = q("income", order="date")

    exp_total = sum(float(e["amount"]) for e in exp_data)
    inc_total = sum(float(i["amount"]) for i in inc_data)
    net       = inc_total - exp_total

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Cash + MFs",   inr(bank_total),  f"{len(banks_data)} accounts")
    c2.metric("Investments",         inr(inv_total),   "FDs + PPF + Lock-in")
    c3.metric("Loan Outstanding",    inr(loan_pend),   f"{loan_data[0]['pending_emi']} EMIs left" if loan_data else "")
    c4.metric("This Month Expenses", inr(exp_total),   f"Income: {inr(inc_total)}")

    st.divider()
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-header">Expense breakdown by category</div>', unsafe_allow_html=True)
        if exp_data:
            df = pd.DataFrame(exp_data)
            df["amount"] = df["amount"].astype(float)
            cat_df = df.groupby("category")["amount"].sum().sort_values(ascending=True).reset_index()
            fig = go.Figure(go.Bar(
                y=cat_df["category"], x=cat_df["amount"], orientation="h",
                marker=dict(color=COLORS[0], opacity=0.85),
                text=[inr(v) for v in cat_df["amount"]], textposition="outside",
                textfont=dict(color=TEXT_CLR, size=11),
                hovertemplate="%{y}<br>%{text}<extra></extra>"
            ))
            fig.update_layout(xaxis=dict(showticklabels=False, showgrid=False),
                              yaxis=dict(tickfont=dict(size=11)))
            plotly_dark(fig, height=max(250, len(cat_df)*38))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded yet.")

    with col2:
        st.markdown('<div class="section-header">Net worth composition</div>', unsafe_allow_html=True)
        fd_amt  = sum(float(i["amount"]) for i in inv_data if i["type"]=="FD")
        li_amt  = sum(float(i["amount"]) for i in inv_data if i["type"]!="FD")
        bk_amt  = sum(float(b["balance"]) for b in banks_data if b["type"]!="Mutual Fund")
        mf_amt  = sum(float(b["balance"]) for b in banks_data if b["type"]=="Mutual Fund")

        fig2 = go.Figure(go.Pie(
            labels=["Bank Cash", "MF Portfolios", "Fixed Deposits", "Lock-in / PPF"],
            values=[bk_amt, mf_amt, fd_amt, li_amt],
            hole=0.62,
            marker=dict(colors=["#1f6feb","#8957e5","#2ea043","#f0883e"]),
            textinfo="label+percent", textfont=dict(size=11),
            hovertemplate="%{label}<br>%{text}<extra></extra>",
            customdata=[inr(v) for v in [bk_amt, mf_amt, fd_amt, li_amt]]
        ))
        plotly_dark(fig2, height=280)
        st.plotly_chart(fig2, use_container_width=True)

        # quick cashflow summary
        net_color = "green" if net >= 0 else "red"
        st.markdown(f"""
        <div style="background:#161b27;border:1px solid #21262d;border-radius:10px;padding:14px;font-size:13px">
          <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #21262d">
            <span class="muted">Monthly income</span><span class="green">{inr(inc_total)}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid #21262d">
            <span class="muted">Monthly expenses</span><span class="red">{inr(exp_total)}</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:4px 0">
            <span class="muted">Net cashflow</span><span class="{net_color}" style="font-weight:600">{inr(net)}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    # Recent transactions
    st.divider()
    st.markdown('<div class="section-header">Recent expenses</div>', unsafe_allow_html=True)
    if exp_data:
        df_show = pd.DataFrame(exp_data[:10])[["date","description","category","amount"]]
        df_show["amount"] = df_show["amount"].apply(lambda x: f"₹{float(x):,.0f}")
        st.dataframe(df_show, use_container_width=True, hide_index=True,
                     column_config={"date":"Date","description":"Description",
                                    "category":"Category","amount":"Amount"})


# ══════════════════════════════════════════════════════════════════════════════
# 2. EXPENSES
# ══════════════════════════════════════════════════════════════════════════════
elif p == "Expenses":
    st.title("💸 Expenses")
    CATS = ["Loan","Home","Bills","Transport","Savings","Shopping","Education",
            "Entertainment","Medical","Food","Family","Other"]

    tab1, tab2 = st.tabs(["📋  All Expenses", "➕  Add Expense"])

    with tab1:
        data = q("expenses", order="date")
        if data:
            df = pd.DataFrame(data)
            df["amount"] = df["amount"].astype(float)
            total = df["amount"].sum()

            c1,c2,c3 = st.columns(3)
            c1.metric("Total",        inr(total),          f"{len(df)} transactions")
            c2.metric("Largest item", inr(df["amount"].max()), df.loc[df["amount"].idxmax(),"description"][:30])
            c3.metric("Categories",   df["category"].nunique(), "unique")

            st.divider()

            # Filter
            fcol1, fcol2 = st.columns([2,1])
            cats_avail = ["All"] + sorted(df["category"].unique().tolist())
            f_cat = fcol1.selectbox("Filter by category", cats_avail, key="exp_cat_f")
            f_sort = fcol2.selectbox("Sort by", ["Date (newest)", "Date (oldest)", "Amount (high)", "Amount (low)"])

            df_v = df if f_cat == "All" else df[df["category"]==f_cat]
            sort_map = {
                "Date (newest)": ("date", False), "Date (oldest)": ("date", True),
                "Amount (high)": ("amount", False), "Amount (low)": ("amount", True)
            }
            sc, sa = sort_map[f_sort]
            df_v = df_v.sort_values(sc, ascending=sa)

            st.markdown(f"**{len(df_v)} records** — Total: **{inr(df_v['amount'].sum())}**")

            for _, row in df_v.iterrows():
                cat_colors = {"Loan":"red","Bills":"amber","Savings":"green","Transport":"blue","Shopping":"purple","Education":"teal"}
                bc = cat_colors.get(row["category"], "blue")
                with st.expander(f"**{row['description']}** — ₹{float(row['amount']):,.0f}  |  {row['date']}"):
                    ec1, ec2, ec3 = st.columns([2,2,1])
                    new_desc = ec1.text_input("Description", row["description"], key=f"ed_{row['id']}")
                    new_amt  = ec2.number_input("Amount (₹)", value=float(row["amount"]), key=f"ea_{row['id']}")
                    new_cat  = ec1.selectbox("Category", CATS, index=CATS.index(row["category"]) if row["category"] in CATS else 0, key=f"ec_{row['id']}")
                    new_date = ec2.date_input("Date", value=datetime.strptime(row["date"], "%Y-%m-%d").date(), key=f"edt_{row['id']}")
                    new_note = ec1.text_input("Notes", row.get("notes","") or "", key=f"en_{row['id']}")

                    bc1, bc2 = ec3.columns(2)
                    with bc1:
                        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                        if st.button("Save", key=f"es_{row['id']}"):
                            if update("expenses", row["id"], {
                                "description": new_desc, "amount": new_amt,
                                "category": new_cat, "date": str(new_date), "notes": new_note
                            }):
                                st.success("Saved!"); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with bc2:
                        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                        if st.button("Del", key=f"edel_{row['id']}"):
                            if delete("expenses", row["id"]):
                                st.success("Deleted!"); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No expenses yet. Use the **Add Expense** tab.")

    with tab2:
        st.subheader("Add new expense")
        with st.form("add_expense", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            desc = fc1.text_input("Description *", placeholder="e.g. Grocery shopping")
            amt  = fc2.number_input("Amount (₹) *", min_value=0.0, step=100.0)
            cat  = fc1.selectbox("Category *", CATS)
            dt   = fc2.date_input("Date *", value=date.today())
            note = st.text_input("Notes (optional)", placeholder="Any extra details")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if not desc or amt <= 0:
                    st.error("Description and amount are required.")
                elif insert("expenses", {"description":desc,"amount":amt,"category":cat,"date":str(dt),"notes":note}):
                    st.success(f"✅ Added: {desc} — ₹{amt:,.0f}")


# ══════════════════════════════════════════════════════════════════════════════
# 3. INCOME
# ══════════════════════════════════════════════════════════════════════════════
elif p == "Income":
    st.title("📈 Income")
    INC_CATS = ["Salary","Dividend","Bonus","Freelance","Interest","Rental","Other"]

    tab1, tab2 = st.tabs(["📋  All Income", "➕  Add Income"])

    with tab1:
        data = q("income", order="date")
        if data:
            df = pd.DataFrame(data)
            df["amount"] = df["amount"].astype(float)
            total = df["amount"].sum()
            exp_total = sum(float(e["amount"]) for e in q("expenses", order="date"))

            c1,c2,c3 = st.columns(3)
            c1.metric("Total income",  inr(total), f"{len(df)} entries")
            c2.metric("Net cashflow",  inr(total - exp_total), "income − expenses")
            c3.metric("Salary share",  f"{df[df['category']=='Salary']['amount'].sum()/total*100:.0f}%", "of income")

            st.divider()
            for _, row in df.sort_values("date", ascending=False).iterrows():
                with st.expander(f"**{row['description']}** — ₹{float(row['amount']):,.0f}  |  {row['date']}"):
                    ec1, ec2, ec3 = st.columns([2,2,1])
                    nd = ec1.text_input("Description", row["description"], key=f"id_{row['id']}")
                    na = ec2.number_input("Amount (₹)", value=float(row["amount"]), key=f"ia_{row['id']}")
                    nc = ec1.selectbox("Category", INC_CATS, index=INC_CATS.index(row["category"]) if row["category"] in INC_CATS else 0, key=f"ic_{row['id']}")
                    ndt = ec2.date_input("Date", value=datetime.strptime(row["date"], "%Y-%m-%d").date(), key=f"idt_{row['id']}")
                    b1, b2 = ec3.columns(2)
                    with b1:
                        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                        if st.button("Save", key=f"is_{row['id']}"):
                            if update("income", row["id"], {"description":nd,"amount":na,"category":nc,"date":str(ndt)}):
                                st.success("Saved!"); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with b2:
                        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                        if st.button("Del", key=f"idel_{row['id']}"):
                            if delete("income", row["id"]):
                                st.success("Deleted!"); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No income records yet.")

    with tab2:
        st.subheader("Add new income")
        with st.form("add_income", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            desc = fc1.text_input("Description *", placeholder="e.g. GLS Salary")
            amt  = fc2.number_input("Amount (₹) *", min_value=0.0, step=100.0)
            cat  = fc1.selectbox("Category *", INC_CATS)
            dt   = fc2.date_input("Date *", value=date.today())
            note = st.text_input("Notes (optional)")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Add Income", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if not desc or amt <= 0:
                    st.error("Description and amount are required.")
                elif insert("income", {"description":desc,"amount":amt,"category":cat,"date":str(dt),"notes":note}):
                    st.success(f"✅ Added: {desc} — ₹{amt:,.0f}")


# ══════════════════════════════════════════════════════════════════════════════
# 4. BANKS & MFs
# ══════════════════════════════════════════════════════════════════════════════
elif p == "Banks & MFs":
    st.title("🏦 Banks & MF Portfolios")

    data = q("bank_accounts", order="id", desc=False)
    banks  = [b for b in data if b["type"] != "Mutual Fund"]
    mfs    = [b for b in data if b["type"] == "Mutual Fund"]
    bk_tot = sum(float(b["balance"]) for b in banks)
    mf_tot = sum(float(b["balance"]) for b in mfs)

    c1,c2,c3 = st.columns(3)
    c1.metric("Bank cash",    inr(bk_tot), f"{len(banks)} accounts")
    c2.metric("MF portfolios",inr(mf_tot), f"{len(mfs)} portfolios")
    c3.metric("Total liquid", inr(bk_tot+mf_tot), "combined")

    st.divider()
    tab1, tab2 = st.tabs(["📋  All Accounts", "➕  Add Account"])

    with tab1:
        for grp_name, grp in [("Bank Accounts", banks), ("Mutual Fund Portfolios", mfs)]:
            st.markdown(f'<div class="section-header">{grp_name}</div>', unsafe_allow_html=True)
            for b in grp:
                with st.expander(f"**{b['name']}** — {inr(float(b['balance']))}  |  {b['type']}"):
                    c1, c2, c3 = st.columns([2,2,1])
                    nn = c1.text_input("Name", b["name"], key=f"bn_{b['id']}")
                    nb = c2.number_input("Balance (₹)", value=float(b["balance"]), key=f"bb_{b['id']}")
                    nt = c1.selectbox("Type", ["Savings","Current","RD","FD","Mutual Fund"],
                                      index=["Savings","Current","RD","FD","Mutual Fund"].index(b["type"]) if b["type"] in ["Savings","Current","RD","FD","Mutual Fund"] else 0,
                                      key=f"bt_{b['id']}")
                    no = c2.text_input("Note", b.get("note","") or "", key=f"bno_{b['id']}")
                    b1, b2 = c3.columns(2)
                    with b1:
                        st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                        if st.button("Save", key=f"bs_{b['id']}"):
                            if update("bank_accounts", b["id"], {"name":nn,"balance":nb,"type":nt,"note":no,"updated_at":"now()"}):
                                st.success("Saved!"); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with b2:
                        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                        if st.button("Del", key=f"bdel_{b['id']}"):
                            if delete("bank_accounts", b["id"]):
                                st.success("Deleted!"); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

        # Chart
        st.divider()
        st.markdown('<div class="section-header">Balance distribution</div>', unsafe_allow_html=True)
        all_accs = [(b["name"], float(b["balance"])) for b in data]
        fig = go.Figure(go.Pie(
            labels=[a[0] for a in all_accs], values=[a[1] for a in all_accs],
            hole=0.55, marker=dict(colors=COLORS),
            textinfo="label+percent", textfont=dict(size=11),
            hovertemplate="%{label}<br>₹%{value:,.0f}<extra></extra>"
        ))
        plotly_dark(fig, 280)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Add bank account / MF")
        with st.form("add_bank", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            name = fc1.text_input("Account name *", placeholder="e.g. SBI Savings")
            bal  = fc2.number_input("Current balance (₹) *", min_value=0.0, step=1000.0)
            typ  = fc1.selectbox("Type *", ["Savings","Current","RD","FD","Mutual Fund"])
            note = fc2.text_input("Note", placeholder="optional")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Add Account", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if not name:
                    st.error("Name is required.")
                elif insert("bank_accounts", {"name":name,"balance":bal,"type":typ,"note":note}):
                    st.success(f"✅ Added: {name}")


# ══════════════════════════════════════════════════════════════════════════════
# 5. INVESTMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif p == "Investments":
    st.title("🏛️ Investment Portfolio")
    INV_TYPES = ["FD","PPF","Stocks","MF","Lock-in","Gratuity","Mandal","Other"]

    data = q("investments", order="id", desc=False)
    total = sum(float(i["amount"]) for i in data)
    fd_total = sum(float(i["amount"]) for i in data if i["type"] == "FD")
    fd_gain  = sum(float(i["amount"]) * float(i["rate"]) / 100 for i in data if i["type"] == "FD")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total portfolio",  inr(total),    f"{len(data)} entries")
    c2.metric("FDs principal",    inr(fd_total), f"{sum(1 for i in data if i['type']=='FD')} FDs")
    c3.metric("FD interest gain", inr(fd_gain),  "expected annual")
    c4.metric("Non-FD lock-in",   inr(total-fd_total), "PPF + Gratuity etc.")

    st.divider()
    tab1, tab2 = st.tabs(["📋  All Investments", "➕  Add Investment"])

    with tab1:
        type_order = ["FD","PPF","Gratuity","Stocks","MF","Mandal","Lock-in","Other"]
        sorted_data = sorted(data, key=lambda x: (type_order.index(x["type"]) if x["type"] in type_order else 99, x["id"]))

        for inv in sorted_data:
            amt  = float(inv["amount"])
            rate = float(inv["rate"] or 0)
            mat_val = amt * (1 + rate/100) if rate > 0 else None
            TYPE_COLORS = {"FD":"green","PPF":"blue","Stocks":"purple","MF":"purple","Mandal":"amber","Gratuity":"amber","Lock-in":"amber"}
            bc = TYPE_COLORS.get(inv["type"], "blue")

            label = f"**{inv['description']}** — {inr(amt)}"
            if rate > 0:
                label += f"  |  {rate}%  →  {inr(mat_val)}"
            label += f"  |  {inv['maturity'] or '—'}"

            with st.expander(label):
                c1, c2, c3 = st.columns([2,2,1])
                nd  = c1.text_input("Description", inv["description"], key=f"invd_{inv['id']}")
                na  = c2.number_input("Amount (₹)", value=amt, key=f"inva_{inv['id']}")
                nt  = c1.selectbox("Type", INV_TYPES, index=INV_TYPES.index(inv["type"]) if inv["type"] in INV_TYPES else 0, key=f"invt_{inv['id']}")
                nr  = c2.number_input("Rate % (FDs only)", value=rate, step=0.01, key=f"invr_{inv['id']}")
                nm  = c1.text_input("Maturity date/label", inv.get("maturity","") or "", key=f"invm_{inv['id']}")
                nn  = c2.text_input("Notes", inv.get("notes","") or "", key=f"invn_{inv['id']}")
                b1, b2 = c3.columns(2)
                with b1:
                    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                    if st.button("Save", key=f"invs_{inv['id']}"):
                        if update("investments", inv["id"], {"description":nd,"amount":na,"type":nt,"rate":nr,"maturity":nm,"notes":nn}):
                            st.success("Saved!"); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with b2:
                    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                    if st.button("Del", key=f"invdel_{inv['id']}"):
                        if delete("investments", inv["id"]):
                            st.success("Deleted!"); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # Allocation chart
        st.divider()
        st.markdown('<div class="section-header">Allocation by type</div>', unsafe_allow_html=True)
        df = pd.DataFrame(data)
        df["amount"] = df["amount"].astype(float)
        type_df = df.groupby("type")["amount"].sum().reset_index().sort_values("amount", ascending=True)
        fig = go.Figure(go.Bar(
            y=type_df["type"], x=type_df["amount"], orientation="h",
            marker_color=COLORS, text=[inr(v) for v in type_df["amount"]],
            textposition="outside", textfont=dict(color=TEXT_CLR, size=11),
            hovertemplate="%{y}<br>%{text}<extra></extra>"
        ))
        fig.update_layout(xaxis=dict(showticklabels=False, showgrid=False))
        plotly_dark(fig, height=max(220, len(type_df)*40))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Add new investment")
        with st.form("add_inv", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            desc = fc1.text_input("Description *", placeholder="e.g. SBI FD")
            amt  = fc2.number_input("Amount (₹) *", min_value=0.0, step=1000.0)
            typ  = fc1.selectbox("Type *", INV_TYPES)
            rate = fc2.number_input("Interest rate % (FDs only)", min_value=0.0, step=0.01)
            mat  = fc1.text_input("Maturity date / label", placeholder="e.g. 01-01-2027 or Liquid")
            note = fc2.text_input("Notes (optional)")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Add Investment", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if not desc or amt <= 0:
                    st.error("Description and amount are required.")
                elif insert("investments", {"description":desc,"amount":amt,"type":typ,"rate":rate,"maturity":mat,"notes":note}):
                    st.success(f"✅ Added: {desc} — {inr(amt)}")


# ══════════════════════════════════════════════════════════════════════════════
# 6. HOME LOAN
# ══════════════════════════════════════════════════════════════════════════════
elif p == "Home Loan":
    st.title("🏠 Home Loan — Axis Bank")

    loan = q("home_loan", order="id", desc=False)
    rates = q("loan_rate_history", order="id", desc=False)

    if not loan:
        st.warning("No loan data found. Please run the schema SQL to seed data.")
        st.stop()

    L = loan[0]
    paid  = int(L["total_emi"]) - int(L["pending_emi"])
    pct   = round(paid / int(L["total_emi"]) * 100, 1)
    out   = float(L["pending_emi"]) * float(L["monthly_emi"])

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Original loan",   inr(float(L["principal"])), L["disbursed"])
    c2.metric("EMIs paid",       f"{paid}/{L['total_emi']}", f"{pct}% complete")
    c3.metric("EMIs remaining",  str(L["pending_emi"]),      f"~{int(L['pending_emi'])//12} years")
    c4.metric("Current rate",    f"{L['rate']}%",            "Down from 8.75%")

    st.divider()

    # Progress bar
    st.markdown(f"""
    <div style="margin-bottom:6px;display:flex;justify-content:space-between;font-size:13px">
        <span class="muted">EMIs paid — {paid} ({pct}%)</span>
        <span class="muted">Remaining — {L['pending_emi']}</span>
    </div>
    {progress_bar(pct, "#1f6feb")}
    <div style="margin-top:4px;font-size:12px;color:#8b949e">
        Outstanding: <strong style="color:#f0883e">{inr(out)}</strong>
        &nbsp;·&nbsp; Monthly EMI: <strong style="color:#f0f6fc">{inr(float(L['monthly_emi']))}</strong>
        &nbsp;·&nbsp; Advance paid: <strong style="color:#56d364">{inr(float(L['advance_paid']))}</strong>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Edit loan details</div>', unsafe_allow_html=True)
        with st.form("edit_loan"):
            lc1, lc2 = st.columns(2)
            new_pend = lc1.number_input("Pending EMIs",   value=int(L["pending_emi"]))
            new_rate = lc2.number_input("Rate (%)",        value=float(L["rate"]),         step=0.01)
            new_emi  = lc1.number_input("Monthly EMI (₹)",value=float(L["monthly_emi"]))
            new_prin = lc2.number_input("Principal (₹)",  value=float(L["principal"]))
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.form_submit_button("💾 Update Loan", use_container_width=True):
                if update("home_loan", L["id"], {"pending_emi":new_pend,"rate":new_rate,"monthly_emi":new_emi,"principal":new_prin}):
                    st.success("Loan updated!"); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-header">Interest rate history</div>', unsafe_allow_html=True)
        for r in rates:
            is_current = r == rates[-1]
            color = "#56d364" if is_current else "#8b949e"
            marker = "◉" if is_current else "○"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #21262d;font-size:13px">
                <span style="color:{color}">{marker} {r['date']}</span>
                <span style="font-weight:600;color:{color}">{r['rate']}%</span>
                <span class="muted">{r['remaining']} EMIs</span>
            </div>""", unsafe_allow_html=True)

        # Add rate history entry
        st.markdown("")
        with st.expander("➕ Add rate change entry"):
            with st.form("add_rate"):
                rc1, rc2 = st.columns(2)
                rdate = rc1.text_input("Date (e.g. Apr 2026)")
                rrate = rc2.number_input("New rate (%)", min_value=0.0, step=0.01)
                rrem  = rc1.number_input("Remaining EMIs at that point", min_value=0)
                if st.form_submit_button("Add"):
                    if insert("loan_rate_history", {"date":rdate,"rate":rrate,"remaining":rrem}):
                        st.success("Added!"); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 7. DUES
# ══════════════════════════════════════════════════════════════════════════════
elif p == "Dues":
    st.title("👥 Dues & Receivables")

    data = q("dues", order="created_at")
    pend = sum(float(d["amount"]) for d in data if d["status"] == "Pending")
    part = sum(float(d["amount"]) for d in data if d["status"] == "Partial")
    sett = sum(float(d["amount"]) for d in data if d["status"] == "Settled")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Pending",     inr(pend), f"{sum(1 for d in data if d['status']=='Pending')} items")
    c2.metric("Partial",     inr(part), f"{sum(1 for d in data if d['status']=='Partial')} items")
    c3.metric("Settled",     inr(sett), "recovered ✓")
    c4.metric("Total given", inr(pend+part+sett), "all time")

    st.divider()
    tab1, tab2 = st.tabs(["📋  All Dues", "➕  Add Due"])

    with tab1:
        STATUS_ORDER = {"Pending": 0, "Partial": 1, "Settled": 2}
        STATUS_COLORS = {"Pending": "🔴", "Partial": "🟡", "Settled": "🟢"}

        for d in sorted(data, key=lambda x: STATUS_ORDER.get(x["status"], 9)):
            icon  = STATUS_COLORS.get(d["status"], "⚪")
            label = f"{icon} **{d['person']}** — {d['purpose']} — ₹{float(d['amount']):,.0f}  |  {d['status']}"

            with st.expander(label):
                dc1, dc2, dc3 = st.columns([2,2,1])
                np = dc1.text_input("Person",  d["person"],  key=f"dp_{d['id']}")
                na = dc2.number_input("Amount (₹)", value=float(d["amount"]), key=f"da_{d['id']}")
                npr = dc1.text_input("Purpose", d["purpose"], key=f"dpr_{d['id']}")
                ns  = dc2.selectbox("Status", ["Pending","Partial","Settled"],
                                    index=["Pending","Partial","Settled"].index(d["status"]) if d["status"] in ["Pending","Partial","Settled"] else 0,
                                    key=f"ds_{d['id']}")
                ndt = dc1.text_input("Date", str(d.get("due_date","") or ""), key=f"ddt_{d['id']}")
                nn  = dc2.text_input("Notes", d.get("notes","") or "", key=f"dn_{d['id']}")

                b1, b2 = dc3.columns(2)
                with b1:
                    st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
                    if st.button("Save", key=f"dsv_{d['id']}"):
                        if update("dues", d["id"], {"person":np,"amount":na,"purpose":npr,"status":ns,"due_date":ndt or None,"notes":nn}):
                            st.success("Saved!"); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                with b2:
                    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                    if st.button("Del", key=f"ddel_{d['id']}"):
                        if delete("dues", d["id"]):
                            st.success("Deleted!"); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Add new due / receivable")
        with st.form("add_due", clear_on_submit=True):
            fc1, fc2 = st.columns(2)
            person  = fc1.text_input("Person *", placeholder="e.g. Bhargav")
            amt     = fc2.number_input("Amount (₹) *", min_value=0.0, step=100.0)
            purpose = fc1.text_input("Purpose *", placeholder="e.g. TV EMI 3")
            status  = fc2.selectbox("Status *", ["Pending","Partial","Settled"])
            ddate   = fc1.date_input("Due date", value=date.today())
            note    = fc2.text_input("Notes (optional)")
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            submitted = st.form_submit_button("➕ Add Due", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if submitted:
                if not person or not purpose or amt <= 0:
                    st.error("Person, purpose and amount are required.")
                elif insert("dues", {"person":person,"amount":amt,"purpose":purpose,"status":status,"due_date":str(ddate),"notes":note}):
                    st.success(f"✅ Added: {person} — {purpose} — ₹{amt:,.0f}")
