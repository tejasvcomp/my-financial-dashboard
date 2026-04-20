import streamlit as st
from supabase import create_client
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
import time

st.set_page_config(page_title="Tejas | Finance Dashboard",page_icon="💰",layout="wide",initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.stApp{background:#060d1a}
.main .block-container{padding:1.5rem 2rem 3rem;max-width:1400px}
[data-testid="stSidebar"]{background:linear-gradient(175deg,#0a0f1e 0%,#0d1527 100%);border-right:1px solid #1a2540}
[data-testid="stSidebar"] *{color:#8b9dc3!important}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{color:#e8f0ff!important}
[data-testid="stSidebarNav"]{display:none}
h1{font-size:1.75rem!important;font-weight:800!important;background:linear-gradient(135deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
h2{font-size:1.15rem!important;font-weight:600!important;color:#e2e8f0!important}
[data-testid="metric-container"]{background:linear-gradient(135deg,#111827 0%,#1a2540 100%);border:1px solid #1e3a5f;border-radius:14px;padding:1rem 1.3rem}
[data-testid="stMetricLabel"]{color:#64748b!important;font-size:.72rem!important;text-transform:uppercase;letter-spacing:.06em;font-weight:600!important}
[data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:1.5rem!important;font-weight:800!important}
[data-testid="stMetricDelta"] svg{display:none}
.stButton>button{border-radius:9px!important;font-size:.8rem!important;font-weight:500!important;padding:.45rem 1.1rem!important;border:1px solid #1e3a5f!important;background:#0f1f3d!important;color:#60a5fa!important;transition:all .15s!important}
.stButton>button:hover{border-color:#3b82f6!important;background:#1e3a5f!important;color:#93c5fd!important}
.primary-btn>button{background:linear-gradient(135deg,#1d4ed8,#4f46e5)!important;border-color:#3b82f6!important;color:#fff!important}
.primary-btn>button:hover{background:linear-gradient(135deg,#2563eb,#6366f1)!important;color:#fff!important}
.danger-btn>button{background:#2d0a0a!important;border-color:#ef4444!important;color:#fca5a5!important}
.danger-btn>button:hover{background:#7f1d1d!important;color:#fff!important}
.success-btn>button{background:linear-gradient(135deg,#14532d,#166534)!important;border-color:#22c55e!important;color:#86efac!important}
.stTextInput>div>div>input,.stNumberInput>div>div>input,.stSelectbox>div>div,.stDateInput>div>div>input,.stTextArea>div>div>textarea{background:#0d1830!important;border:1px solid #1e3a5f!important;color:#e2e8f0!important;border-radius:9px!important}
.stTextInput>label,.stNumberInput>label,.stSelectbox>label,.stDateInput>label,.stTextArea>label{color:#64748b!important;font-size:.75rem!important;font-weight:500!important}
.stTabs [data-baseweb="tab-list"]{background:#080e1c;border-bottom:1px solid #1a2540;gap:2px}
.stTabs [data-baseweb="tab"]{color:#64748b;border-radius:8px 8px 0 0;padding:.5rem 1.3rem;font-size:.82rem;font-weight:500}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#1d4ed8,#4f46e5)!important;color:#fff!important}
.streamlit-expanderHeader{background:#0d1830!important;border:1px solid #1e3a5f!important;border-radius:10px!important;color:#94a3b8!important}
.streamlit-expanderContent{background:#060d1a!important;border:1px solid #1a2540!important;border-radius:0 0 10px 10px!important}
hr{border-color:#1a2540!important}
.stSuccess{background:#0a1f0a!important;border:1px solid #166534!important;color:#86efac!important;border-radius:10px}
.stError{background:#1f0a0a!important;border:1px solid #991b1b!important;color:#fca5a5!important;border-radius:10px}
.stWarning{background:#1f1400!important;border:1px solid #92400e!important;color:#fbbf24!important;border-radius:10px}
.stInfo{background:#0a1629!important;border:1px solid #1e3a5f!important;color:#93c5fd!important;border-radius:10px}
.stat-row{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-radius:10px;background:#0d1830;border:1px solid #1a2540;margin-bottom:6px;font-size:13px}
.stat-lbl{color:#64748b}.stat-val{color:#f1f5f9;font-weight:600}
.sec-hd{font-size:.68rem;font-weight:700;color:#3b82f6;text-transform:uppercase;letter-spacing:.08em;padding-bottom:7px;border-bottom:1px solid #1a2540;margin-bottom:12px}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.68rem;font-weight:700;letter-spacing:.04em}
.bg{background:#0a2e18;color:#4ade80;border:1px solid #166534}
.br{background:#2d0a0a;color:#f87171;border:1px solid #991b1b}
.ba{background:#2d1800;color:#fb923c;border:1px solid #92400e}
.bb{background:#050f29;color:#60a5fa;border:1px solid #1e3a5f}
.bp{background:#150929;color:#c084fc;border:1px solid #6d28d9}
.bt{background:#00201a;color:#34d399;border:1px solid #065f46}
.prg-track{height:10px;background:#1a2540;border-radius:5px;overflow:hidden;margin:6px 0}
.prg-fill{height:100%;border-radius:5px;transition:width .6s ease}
.glow-card{background:linear-gradient(135deg,#0d1830,#111827);border:1px solid #1e3a5f;border-radius:16px;padding:1.3rem 1.5rem;margin-bottom:1rem}
.glow-card:hover{border-color:#3b82f6}
.mbar-wrap{height:6px;background:#1a2540;border-radius:3px;overflow:hidden;margin-top:4px}
.mbar-fill{height:100%;border-radius:3px}
.alert-banner{background:linear-gradient(135deg,#1f0a0a,#2d1010);border:1px solid #7f1d1d;border-radius:12px;padding:.75rem 1rem;margin-bottom:.5rem;display:flex;align-items:flex-start;gap:10px;font-size:.82rem;color:#fca5a5}
.alert-banner.warn{background:linear-gradient(135deg,#1a1000,#2d1f00);border-color:#92400e;color:#fbbf24}
.alert-banner.good{background:linear-gradient(135deg,#051f0a,#0a2e18);border-color:#166534;color:#86efac}
.pulse{display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-right:6px;animation:pulse-anim 2s infinite}
@keyframes pulse-anim{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.2)}}
.login-card{background:linear-gradient(135deg,#0d1830 0%,#111827 100%);border:1px solid #1e3a5f;border-radius:20px;padding:2.5rem 2rem;max-width:420px;margin:2rem auto;box-shadow:0 20px 60px rgba(0,0,0,.5)}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_sb():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
sb = get_sb()

# ── AUTH FIXED ──────────────────────────────────────────────────────────────
def do_login(email, password):
    try:
        res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if res and res.user:
            st.session_state["user"]    = res.user
            st.session_state["session"] = res.session
            st.session_state["email"]   = res.user.email
            return True, "OK"
        return False, "Invalid credentials."
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_grant" in msg.lower():
            return False, "Invalid credentials — check email and password."
        if "Email not confirmed" in msg:
            return False, "Please confirm your email first (check inbox)."
        return False, f"Auth error: {msg}"

def do_signup(email, password):
    try:
        res = sb.auth.sign_up({"email": email, "password": password})
        if res and res.user:
            return True, "Account created! Check your email to confirm, then log in."
        return False, "Signup failed."
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower():
            return False, "Email already registered — just log in."
        return False, f"Error: {msg}"

def check_session():
    if "user" in st.session_state:
        return True
    try:
        sess = sb.auth.get_session()
        if sess and sess.user:
            st.session_state["user"]    = sess.user
            st.session_state["session"] = sess
            st.session_state["email"]   = sess.user.email
            return True
    except:
        pass
    return False

if not check_session():
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Finance Dashboard")
        st.markdown("<p style='color:#64748b;font-size:.85rem'>Tejas Patel · Personal Finance Manager</p>", unsafe_allow_html=True)
        mode     = st.radio("", ["Login","Sign Up"], horizontal=True, label_visibility="collapsed")
        email    = st.text_input("Email",    placeholder="you@email.com")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if mode == "Login":
            st.markdown('<div class="primary-btn">', unsafe_allow_html=True)
            if st.button("🔐 Login", use_container_width=True):
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    with st.spinner("Logging in..."):
                        ok, msg = do_login(email, password)
                    if ok:
                        st.success("Welcome back!")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(msg)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-btn">', unsafe_allow_html=True)
            if st.button("✨ Create Account", use_container_width=True):
                if not email or not password:
                    st.error("Fill both fields.")
                elif len(password) < 6:
                    st.error("Password needs 6+ characters.")
                else:
                    ok, msg = do_signup(email, password)
                    (st.success if ok else st.error)(msg)
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#334155;font-size:.72rem;margin-top:1rem'>Secured by Supabase Auth</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── DB HELPERS ───────────────────────────────────────────────────────────────
def q(table, order="created_at", desc=True):
    try:
        r = sb.table(table).select("*").order(order, desc=desc).execute()
        return r.data or []
    except Exception as e:
        st.error(f"DB error ({table}): {e}"); return []

def ins(table, data):
    try:
        sb.table(table).insert(data).execute()
        st.cache_data.clear(); return True
    except Exception as e:
        st.error(f"Insert error: {e}"); return False

def upd(table, rid, data):
    try:
        sb.table(table).update(data).eq("id", rid).execute()
        st.cache_data.clear(); return True
    except Exception as e:
        st.error(f"Update error: {e}"); return False

def dlt(table, rid):
    try:
        sb.table(table).delete().eq("id", rid).execute()
        st.cache_data.clear(); return True
    except Exception as e:
        st.error(f"Delete error: {e}"); return False

def inr(v, lakh=True):
    v = float(v or 0)
    if lakh and abs(v) >= 100000: return f"₹{v/100000:.2f}L"
    return f"₹{int(round(v)):,}"

def pb(pct, color="#3b82f6"):
    p = min(max(float(pct),0),100)
    return f'<div class="prg-track"><div class="prg-fill" style="width:{p}%;background:{color}"></div></div>'

def mbar(v, mx, color="#3b82f6"):
    p = min(int(v/mx*100),100) if mx else 0
    return f'<div class="mbar-wrap"><div class="mbar-fill" style="width:{p}%;background:{color}"></div></div>'

PLOTBG="#060d1a"; GRIDC="#1a2540"; TEXTC="#64748b"
PAL=["#3b82f6","#22c55e","#f59e0b","#8b5cf6","#ec4899","#14b8a6","#f97316","#06b6d4"]
EXP_CATS=["Loan","Home","Bills","Transport","Savings","Shopping","Education","Entertainment","Medical","Food","Family","Other"]
INC_CATS=["Salary","Dividend","Bonus","Freelance","Interest","Rental","Other"]
INV_TYPES=["FD","PPF","Stocks","MF","Lock-in","Gratuity","Mandal","Other"]
CAT_CLR={"Loan":"br","Bills":"ba","Savings":"bg","Transport":"bb","Shopping":"bp","Education":"bt","Home":"bb","Entertainment":"bp","Medical":"br","Food":"bg","Family":"bt","Other":"ba"}

def dfig(fig, h=300):
    fig.update_layout(height=h,plot_bgcolor=PLOTBG,paper_bgcolor=PLOTBG,
        font=dict(color=TEXTC,family="Inter",size=11),margin=dict(l=6,r=6,t=30,b=6),
        xaxis=dict(gridcolor=GRIDC,linecolor=GRIDC),yaxis=dict(gridcolor=GRIDC,linecolor=GRIDC),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="#0d1830",bordercolor="#1e3a5f",font=dict(color="#e2e8f0",family="Inter")))
    return fig

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div style="padding:4px 0 12px"><div style="font-size:1.1rem;font-weight:800;color:#e8f0ff">💰 Finance Hub</div><div style="font-size:.75rem;color:#334155;margin-top:2px"><span class="pulse"></span>Live · {st.session_state.get("email","").split("@")[0]}</div></div>', unsafe_allow_html=True)
    page = st.radio("", ["📊  Overview","💸  Expenses","📈  Income","🏦  Banks & MFs","🏛️  Investments","🏠  Home Loan","👥  Dues","📅  Budget","🔔  Alerts"], label_visibility="collapsed")
    st.divider()

    # Sidebar totals — FIX: ALL banks included
    banks_all = q("bank_accounts","id",False)
    inv_all   = q("investments","id",False)
    dues_all  = q("dues","created_at")
    loan_all  = q("home_loan","id",False)
    bank_total = sum(float(b["balance"]) for b in banks_all)   # ALL accounts
    inv_total  = sum(float(i["amount"])  for i in inv_all)
    due_pend   = sum(float(d["amount"])  for d in dues_all if d["status"]!="Settled")
    loan_out   = float(loan_all[0]["pending_emi"])*float(loan_all[0]["monthly_emi"]) if loan_all else 0
    net_worth  = bank_total + inv_total - loan_out

    for lbl,val,col in [("All Banks+MFs",inr(bank_total),"#60a5fa"),("Investments",inr(inv_total),"#4ade80"),("Loan left",inr(loan_out),"#fb923c"),("Dues out",inr(due_pend),"#f87171"),("Net worth",inr(net_worth),"#c084fc")]:
        st.markdown(f'<div class="stat-row"><span class="stat-lbl">{lbl}</span><span style="color:{col};font-weight:700;font-size:.82rem">{val}</span></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        try: sb.auth.sign_out()
        except: pass
        for k in ["user","session","email"]: st.session_state.pop(k,None)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("cozpsoousfuhhydetflp.supabase.co")

p = page.strip().split("  ")[1]

# ═══════════════════════════════════════════════════
if p == "Overview":
    st.title("📊 Financial Command Center")
    exp_data=q("expenses","date"); inc_data=q("income","date")
    exp_total=sum(float(e["amount"]) for e in exp_data)
    inc_total=sum(float(i["amount"]) for i in inc_data)
    net_cf=inc_total-exp_total
    k1,k2,k3,k4,k5=st.columns(5)
    k1.metric("💳 All Banks+MFs",inr(bank_total),f"{len(banks_all)} accounts")
    k2.metric("📈 Investments",inr(inv_total),f"{len(inv_all)} entries")
    k3.metric("🏠 Loan Outstanding",inr(loan_out),f"{loan_all[0]['pending_emi']} EMIs" if loan_all else "")
    k4.metric("💰 Net Worth",inr(net_worth),"Assets − Loan")
    k5.metric("🔄 Month Net",inr(net_cf),"↑ Surplus" if net_cf>=0 else "↓ Deficit")
    st.divider()
    c1,c2=st.columns([3,2])
    with c1:
        st.markdown('<div class="sec-hd">Expense by category</div>', unsafe_allow_html=True)
        if exp_data:
            df=pd.DataFrame(exp_data); df["amount"]=df["amount"].astype(float)
            cat=df.groupby("category")["amount"].sum().sort_values().reset_index()
            fig=go.Figure(go.Bar(y=cat["category"],x=cat["amount"],orientation="h",
                marker=dict(color=cat["amount"],colorscale=[[0,"#1e3a5f"],[0.5,"#3b82f6"],[1,"#818cf8"]],showscale=False,line=dict(width=0)),
                text=[inr(v) for v in cat["amount"]],textposition="outside",textfont=dict(color="#94a3b8",size=11),
                hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"))
            fig.update_layout(xaxis=dict(showticklabels=False,showgrid=False),yaxis=dict(tickfont=dict(size=11,color="#94a3b8")))
            dfig(fig,max(260,len(cat)*38)); st.plotly_chart(fig,use_container_width=True)
        else: st.info("No expenses yet.")
    with c2:
        st.markdown('<div class="sec-hd">Net worth composition</div>', unsafe_allow_html=True)
        bk=sum(float(b["balance"]) for b in banks_all if b["type"]!="Mutual Fund")
        mf=sum(float(b["balance"]) for b in banks_all if b["type"]=="Mutual Fund")
        fd=sum(float(i["amount"]) for i in inv_all if i["type"]=="FD")
        li=sum(float(i["amount"]) for i in inv_all if i["type"]!="FD")
        fig2=go.Figure(go.Pie(labels=["Bank Cash","MF Portfolios","Fixed Deposits","Lock-in/PPF"],values=[bk,mf,fd,li],hole=0.65,
            marker=dict(colors=["#3b82f6","#8b5cf6","#22c55e","#f59e0b"],line=dict(color=PLOTBG,width=2)),
            textinfo="label+percent",textfont=dict(size=10.5,color="#94a3b8"),
            hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"))
        dfig(fig2,260); st.plotly_chart(fig2,use_container_width=True)
        nc_col="#4ade80" if net_cf>=0 else "#f87171"
        st.markdown(f'<div class="glow-card" style="padding:1rem"><div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1a2540;font-size:13px"><span style="color:#64748b">Income</span><span style="color:#4ade80;font-weight:600">{inr(inc_total)}</span></div><div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1a2540;font-size:13px"><span style="color:#64748b">Expenses</span><span style="color:#f87171;font-weight:600">{inr(exp_total)}</span></div><div style="display:flex;justify-content:space-between;padding:5px 0;font-size:13px"><span style="color:#64748b">Net</span><span style="color:{nc_col};font-weight:700">{inr(net_cf)}</span></div></div>', unsafe_allow_html=True)
    st.divider()
    rc1,rc2=st.columns(2)
    with rc1:
        st.markdown('<div class="sec-hd">Recent expenses</div>', unsafe_allow_html=True)
        for e in sorted(exp_data,key=lambda x:x["date"],reverse=True)[:6]:
            bc=CAT_CLR.get(e["category"],"bb")
            st.markdown(f'<div class="stat-row"><div><span style="color:#e2e8f0;font-size:.82rem">{e["description"][:30]}</span><br><span class="badge {bc}" style="margin-top:3px">{e["category"]}</span></div><span style="color:#f87171;font-weight:700">{inr(float(e["amount"]))}</span></div>', unsafe_allow_html=True)
    with rc2:
        st.markdown('<div class="sec-hd">Investment by type</div>', unsafe_allow_html=True)
        tt={}
        for i in inv_all: tt[i["type"]]=tt.get(i["type"],0)+float(i["amount"])
        mx=max(tt.values()) if tt else 1
        clr={"FD":"#22c55e","PPF":"#3b82f6","Stocks":"#8b5cf6","MF":"#a78bfa","Mandal":"#f59e0b","Gratuity":"#f59e0b"}
        for t,v in sorted(tt.items(),key=lambda x:-x[1]):
            c=clr.get(t,"#64748b")
            st.markdown(f'<div class="stat-row"><div style="flex:1"><span style="color:#e2e8f0;font-size:.82rem">{t}</span>{mbar(v,mx,c)}</div><span style="color:{c};font-weight:700;margin-left:12px">{inr(v)}</span></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
elif p == "Expenses":
    st.title("💸 Expenses")
    tab1,tab2,tab3=st.tabs(["📋  All Expenses","➕  Add Expense","📊  Analytics"])
    with tab1:
        data=q("expenses","date")
        if data:
            df=pd.DataFrame(data); df["amount"]=df["amount"].astype(float)
            total=df["amount"].sum()
            k1,k2,k3=st.columns(3)
            k1.metric("Total",inr(total),f"{len(df)} transactions")
            k2.metric("Highest",inr(df["amount"].max()),df.loc[df["amount"].idxmax(),"description"][:28])
            k3.metric("Categories",str(df["category"].nunique()),"unique")
            st.divider()
            fc1,fc2,fc3=st.columns([2,1.5,1.5])
            f_cat=fc1.selectbox("Category",["All"]+sorted(df["category"].unique().tolist()),key="ef_cat")
            f_sort=fc2.selectbox("Sort",["Date ↓","Date ↑","Amount ↓","Amount ↑"])
            f_srch=fc3.text_input("Search",placeholder="search...")
            dv=df.copy()
            if f_cat!="All": dv=dv[dv["category"]==f_cat]
            if f_srch: dv=dv[dv["description"].str.contains(f_srch,case=False,na=False)]
            sm={"Date ↓":("date",False),"Date ↑":("date",True),"Amount ↓":("amount",False),"Amount ↑":("amount",True)}
            sc,sa=sm[f_sort]; dv=dv.sort_values(sc,ascending=sa)
            st.markdown(f"**{len(dv)} records** · Total: **{inr(dv['amount'].sum())}**")
            for _,row in dv.iterrows():
                with st.expander(f"**{row['description'][:45]}** — ₹{float(row['amount']):,.0f}  |  {row['date']}"):
                    c1,c2,c3=st.columns([2,2,1])
                    nd=c1.text_input("Description",row["description"],key=f"ed_{row['id']}")
                    na=c2.number_input("Amount",value=float(row["amount"]),key=f"ea_{row['id']}")
                    nc=c1.selectbox("Category",EXP_CATS,index=EXP_CATS.index(row["category"]) if row["category"] in EXP_CATS else 0,key=f"ec_{row['id']}")
                    ndt=c2.date_input("Date",value=datetime.strptime(row["date"],"%Y-%m-%d").date(),key=f"edt_{row['id']}")
                    nn=c1.text_input("Notes",row.get("notes","") or "",key=f"en_{row['id']}")
                    b1,b2=c3.columns(2)
                    with b1:
                        st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
                        if st.button("💾",key=f"es_{row['id']}"):
                            if upd("expenses",row["id"],{"description":nd,"amount":na,"category":nc,"date":str(ndt),"notes":nn}): st.success("Saved!"); st.rerun()
                        st.markdown('</div>',unsafe_allow_html=True)
                    with b2:
                        st.markdown('<div class="danger-btn">',unsafe_allow_html=True)
                        if st.button("🗑️",key=f"edel_{row['id']}"):
                            if dlt("expenses",row["id"]): st.success("Deleted!"); st.rerun()
                        st.markdown('</div>',unsafe_allow_html=True)
        else: st.info("No expenses yet.")
    with tab2:
        st.subheader("Add expense")
        with st.form("add_exp_f",clear_on_submit=True):
            f1,f2=st.columns(2)
            desc=f1.text_input("Description *",placeholder="e.g. Grocery at DMart")
            amt=f2.number_input("Amount (₹) *",min_value=0.01,step=100.0)
            cat=f1.selectbox("Category *",EXP_CATS)
            dt=f2.date_input("Date *",value=date.today())
            note=st.text_input("Notes",placeholder="optional")
            st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
            ok=st.form_submit_button("➕ Add Expense",use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        if ok:
            if not desc or amt<=0: st.error("Fill description and amount.")
            elif ins("expenses",{"description":desc,"amount":float(amt),"category":cat,"date":str(dt),"notes":note}): st.success(f"✅ Added — {desc} — {inr(amt)}")
    with tab3:
        data=q("expenses","date")
        if data:
            df=pd.DataFrame(data); df["amount"]=df["amount"].astype(float); df["date"]=pd.to_datetime(df["date"])
            st.markdown('<div class="sec-hd">Spending over time</div>',unsafe_allow_html=True)
            daily=df.groupby("date")["amount"].sum().reset_index()
            fig=go.Figure(); fig.add_trace(go.Scatter(x=daily["date"],y=daily["amount"],mode="lines+markers",line=dict(color="#3b82f6",width=2.5),marker=dict(size=5,color="#60a5fa"),fill="tozeroy",fillcolor="rgba(59,130,246,.08)",hovertemplate="%{x|%d %b}<br>₹%{y:,.0f}<extra></extra>"))
            dfig(fig,220); st.plotly_chart(fig,use_container_width=True)
            st.markdown('<div class="sec-hd">By category</div>',unsafe_allow_html=True)
            cat_df=df.groupby("category")["amount"].sum().reset_index()
            fig2=go.Figure(go.Pie(labels=cat_df["category"],values=cat_df["amount"],hole=0.55,marker=dict(colors=PAL,line=dict(color=PLOTBG,width=2)),textinfo="label+percent",hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"))
            dfig(fig2,270); st.plotly_chart(fig2,use_container_width=True)
        else: st.info("Add expenses to see analytics.")

# ═══════════════════════════════════════════════════
elif p == "Income":
    st.title("📈 Income")
    tab1,tab2=st.tabs(["📋  All Income","➕  Add Income"])
    with tab1:
        data=q("income","date")
        if data:
            df=pd.DataFrame(data); df["amount"]=df["amount"].astype(float); total=df["amount"].sum()
            exp_t=sum(float(e["amount"]) for e in q("expenses","date"))
            k1,k2,k3=st.columns(3)
            k1.metric("Total income",inr(total),f"{len(df)} entries")
            k2.metric("Net cashflow",inr(total-exp_t),"income − expenses")
            k3.metric("Salary %",f"{df[df['category']=='Salary']['amount'].sum()/total*100:.0f}%","of income")
            st.divider()
            for _,row in df.sort_values("date",ascending=False).iterrows():
                with st.expander(f"**{row['description']}** — ₹{float(row['amount']):,.0f}  |  {row['date']}"):
                    c1,c2,c3=st.columns([2,2,1])
                    nd=c1.text_input("Desc",row["description"],key=f"id_{row['id']}")
                    na=c2.number_input("Amount",value=float(row["amount"]),key=f"ia_{row['id']}")
                    nc=c1.selectbox("Category",INC_CATS,index=INC_CATS.index(row["category"]) if row["category"] in INC_CATS else 0,key=f"ic_{row['id']}")
                    ndt=c2.date_input("Date",value=datetime.strptime(row["date"],"%Y-%m-%d").date(),key=f"idt_{row['id']}")
                    b1,b2=c3.columns(2)
                    with b1:
                        st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
                        if st.button("💾",key=f"is_{row['id']}"):
                            if upd("income",row["id"],{"description":nd,"amount":na,"category":nc,"date":str(ndt)}): st.success("Saved!"); st.rerun()
                        st.markdown('</div>',unsafe_allow_html=True)
                    with b2:
                        st.markdown('<div class="danger-btn">',unsafe_allow_html=True)
                        if st.button("🗑️",key=f"idel_{row['id']}"):
                            if dlt("income",row["id"]): st.success("Deleted!"); st.rerun()
                        st.markdown('</div>',unsafe_allow_html=True)
        else: st.info("No income records yet.")
    with tab2:
        st.subheader("Add income")
        with st.form("add_inc_f",clear_on_submit=True):
            f1,f2=st.columns(2)
            desc=f1.text_input("Description *",placeholder="e.g. GLS Salary April")
            amt=f2.number_input("Amount (₹) *",min_value=0.01,step=100.0)
            cat=f1.selectbox("Category *",INC_CATS)
            dt=f2.date_input("Date *",value=date.today())
            note=st.text_input("Notes",placeholder="optional")
            st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
            ok=st.form_submit_button("➕ Add Income",use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        if ok:
            if not desc or amt<=0: st.error("Fill description and amount.")
            elif ins("income",{"description":desc,"amount":float(amt),"category":cat,"date":str(dt),"notes":note}): st.success(f"✅ Added — {desc} — {inr(amt)}")

# ═══════════════════════════════════════════════════
# BANKS — FIX: Total Cash = ALL accounts including Axis
elif p == "Banks & MFs":
    st.title("🏦 Banks & MF Portfolios")
    data=q("bank_accounts","id",False)
    banks=[b for b in data if b["type"]!="Mutual Fund"]
    mfs=[b for b in data if b["type"]=="Mutual Fund"]
    bk_tot=sum(float(b["balance"]) for b in banks)   # HDFC+Axis+Mehsana+CBI
    mf_tot=sum(float(b["balance"]) for b in mfs)
    all_tot=bk_tot+mf_tot
    k1,k2,k3,k4=st.columns(4)
    k1.metric("Total Bank Cash",inr(bk_tot),f"{len(banks)} accounts (all banks)")
    k2.metric("MF Portfolios",inr(mf_tot),f"{len(mfs)} portfolios")
    k3.metric("Grand Total",inr(all_tot),"banks + MFs")
    k4.metric("Largest",max(data,key=lambda x:float(x["balance"]))["name"] if data else "—",inr(max(float(b["balance"]) for b in data)) if data else "₹0")
    st.divider()
    tab1,tab2=st.tabs(["📋  Accounts","➕  Add Account"])
    with tab1:
        for grp_title,grp in [("Bank Accounts",banks),("Mutual Fund Portfolios",mfs)]:
            st.markdown(f'<div class="sec-hd">{grp_title}</div>',unsafe_allow_html=True)
            for b in grp:
                bal=float(b["balance"]); pct=int(bal/all_tot*100) if all_tot else 0
                with st.expander(f"**{b['name']}** — {inr(bal)}  ({pct}% of total)"):
                    c1,c2,c3=st.columns([2,2,1])
                    nn=c1.text_input("Name",b["name"],key=f"bn_{b['id']}")
                    nb=c2.number_input("Balance (₹)",value=bal,key=f"bb_{b['id']}")
                    types=["Savings","Current","RD","FD","Mutual Fund"]
                    nt=c1.selectbox("Type",types,index=types.index(b["type"]) if b["type"] in types else 0,key=f"bt_{b['id']}")
                    no=c2.text_input("Note",b.get("note","") or "",key=f"bno_{b['id']}")
                    b1,b2=c3.columns(2)
                    with b1:
                        st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
                        if st.button("💾",key=f"bs_{b['id']}"):
                            if upd("bank_accounts",b["id"],{"name":nn,"balance":nb,"type":nt,"note":no}): st.success("Saved!"); st.rerun()
                        st.markdown('</div>',unsafe_allow_html=True)
                    with b2:
                        st.markdown('<div class="danger-btn">',unsafe_allow_html=True)
                        if st.button("🗑️",key=f"bdel_{b['id']}"):
                            if dlt("bank_accounts",b["id"]): st.success("Deleted!"); st.rerun()
                        st.markdown('</div>',unsafe_allow_html=True)
        st.divider()
        if data:
            fig=go.Figure(go.Pie(labels=[b["name"] for b in data],values=[float(b["balance"]) for b in data],hole=0.58,marker=dict(colors=PAL,line=dict(color=PLOTBG,width=2)),textinfo="label+percent",textfont=dict(size=10.5),hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>"))
            dfig(fig,300); st.plotly_chart(fig,use_container_width=True)
    with tab2:
        st.subheader("Add account")
        with st.form("add_bank_f",clear_on_submit=True):
            f1,f2=st.columns(2)
            name=f1.text_input("Name *",placeholder="e.g. SBI Savings")
            bal=f2.number_input("Balance (₹) *",min_value=0.0,step=1000.0)
            typ=f1.selectbox("Type *",["Savings","Current","RD","FD","Mutual Fund"])
            note=f2.text_input("Note",placeholder="optional")
            st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
            ok=st.form_submit_button("➕ Add Account",use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        if ok:
            if not name: st.error("Name required.")
            elif ins("bank_accounts",{"name":name,"balance":float(bal),"type":typ,"note":note}): st.success(f"✅ Added: {name}")

# ═══════════════════════════════════════════════════
# INVESTMENTS — FIX: form submission outside form block; unique widget keys
elif p == "Investments":
    st.title("🏛️ Investment Portfolio")
    data=q("investments","id",False)
    total=sum(float(i["amount"]) for i in data)
    fd_total=sum(float(i["amount"]) for i in data if i["type"]=="FD")
    fd_gain=sum(float(i["amount"])*float(i.get("rate") or 0)/100 for i in data if i["type"]=="FD" and float(i.get("rate") or 0)>0)
    k1,k2,k3,k4=st.columns(4)
    k1.metric("Total portfolio",inr(total),f"{len(data)} entries")
    k2.metric("FDs principal",inr(fd_total),f"{sum(1 for i in data if i['type']=='FD')} FDs")
    k3.metric("FD annual gain",inr(fd_gain),"expected interest")
    k4.metric("Non-FD assets",inr(total-fd_total),"PPF + others")
    st.divider()
    tab1,tab2=st.tabs(["📋  All Investments","➕  Add Investment"])
    with tab1:
        ORD=["FD","PPF","Gratuity","Stocks","MF","Mandal","Lock-in","Other"]
        TBDG={"FD":"bg","PPF":"bb","Stocks":"bp","MF":"bp","Mandal":"ba","Gratuity":"ba","Lock-in":"ba","Other":"bb"}
        for inv in sorted(data,key=lambda x:(ORD.index(x["type"]) if x["type"] in ORD else 99)):
            amt=float(inv["amount"]); rate=float(inv.get("rate") or 0)
            mat_v=amt*(1+rate/100) if rate>0 else None
            lbl=f"**{inv['description']}** — {inr(amt)}"
            if rate>0 and mat_v: lbl+=f"  |  {rate}%  →  {inr(mat_v)}"
            lbl+=f"  |  {inv.get('maturity') or '—'}"
            with st.expander(lbl):
                c1,c2,c3=st.columns([2,2,1])
                # FIX: all keys use inv_X_id pattern — no conflicts
                nd=c1.text_input("Description",inv["description"],key=f"inv_d_{inv['id']}")
                na=c2.number_input("Amount (₹)",value=amt,min_value=0.0,key=f"inv_a_{inv['id']}")
                nt=c1.selectbox("Type",INV_TYPES,index=INV_TYPES.index(inv["type"]) if inv["type"] in INV_TYPES else 0,key=f"inv_t_{inv['id']}")
                nr=c2.number_input("Rate % (FDs)",value=rate,step=0.01,min_value=0.0,key=f"inv_r_{inv['id']}")
                nm=c1.text_input("Maturity",inv.get("maturity","") or "",key=f"inv_m_{inv['id']}")
                nn=c2.text_input("Notes",inv.get("notes","") or "",key=f"inv_n_{inv['id']}")
                if rate>0 and na>0:
                    mc=na*(1+nr/100)
                    st.markdown(f'<div style="font-size:.78rem;color:#4ade80;margin-top:2px">→ Maturity value: <strong>{inr(mc)}</strong> (gain: {inr(mc-na)})</div>',unsafe_allow_html=True)
                b1,b2=c3.columns(2)
                with b1:
                    st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
                    if st.button("💾",key=f"inv_sv_{inv['id']}"):
                        if upd("investments",inv["id"],{"description":nd,"amount":float(na),"type":nt,"rate":float(nr),"maturity":nm,"notes":nn}): st.success("Saved!"); st.rerun()
                    st.markdown('</div>',unsafe_allow_html=True)
                with b2:
                    st.markdown('<div class="danger-btn">',unsafe_allow_html=True)
                    if st.button("🗑️",key=f"inv_dl_{inv['id']}"):
                        if dlt("investments",inv["id"]): st.success("Deleted!"); st.rerun()
                    st.markdown('</div>',unsafe_allow_html=True)
        if data:
            st.divider()
            df2=pd.DataFrame(data); df2["amount"]=df2["amount"].astype(float)
            tdf=df2.groupby("type")["amount"].sum().sort_values().reset_index()
            fig=go.Figure(go.Bar(y=tdf["type"],x=tdf["amount"],orientation="h",
                marker=dict(color=list(range(len(tdf))),colorscale=[[0,"#1e3a5f"],[0.4,"#3b82f6"],[1,"#8b5cf6"]],showscale=False,line=dict(width=0)),
                text=[inr(v) for v in tdf["amount"]],textposition="outside",textfont=dict(color="#94a3b8",size=11),
                hovertemplate="<b>%{y}</b><br>%{text}<extra></extra>"))
            fig.update_layout(xaxis=dict(showticklabels=False,showgrid=False),yaxis=dict(tickfont=dict(size=11,color="#94a3b8")))
            dfig(fig,max(220,len(tdf)*42)); st.plotly_chart(fig,use_container_width=True)
    with tab2:
        # FIX: form submission result checked OUTSIDE the form
        st.subheader("Add investment")
        with st.form("add_inv_form",clear_on_submit=True):
            f1,f2=st.columns(2)
            new_desc=f1.text_input("Description *",placeholder="e.g. SBI FD 2027")
            new_amt=f2.number_input("Amount (₹) *",min_value=0.01,step=1000.0)
            new_type=f1.selectbox("Type *",INV_TYPES)
            new_rate=f2.number_input("Rate % (FDs only)",min_value=0.0,step=0.01,value=0.0)
            new_mat=f1.text_input("Maturity date/label",placeholder="e.g. 01-01-2028 or Liquid")
            new_note=f2.text_input("Notes (optional)")
            st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
            add_ok=st.form_submit_button("➕ Add Investment",use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        if add_ok:  # FIX: outside form block — no StreamlitAPIException
            if not new_desc or new_amt<=0: st.error("Description and amount are required.")
            elif ins("investments",{"description":new_desc,"amount":float(new_amt),"type":new_type,"rate":float(new_rate),"maturity":new_mat,"notes":new_note}):
                st.success(f"✅ Added: {new_desc} — {inr(new_amt)}")

# ═══════════════════════════════════════════════════
elif p == "Home Loan":
    st.title("🏠 Home Loan — Axis Bank")
    loan=q("home_loan","id",False); rates=q("loan_rate_history","id",False)
    if not loan: st.warning("Run schema.sql in Supabase to seed loan data."); st.stop()
    L=loan[0]; paid=int(L["total_emi"])-int(L["pending_emi"]); pct=round(paid/int(L["total_emi"])*100,1); out=float(L["pending_emi"])*float(L["monthly_emi"])
    k1,k2,k3,k4=st.columns(4)
    k1.metric("Original loan",inr(float(L["principal"])),L["disbursed"])
    k2.metric("EMIs paid",f"{paid}/{L['total_emi']}",f"{pct}% done ✓")
    k3.metric("Remaining",str(L["pending_emi"]),f"~{int(L['pending_emi'])//12} years")
    k4.metric("Rate",f"{L['rate']}%","⬇ from 8.75%")
    st.divider()
    st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:.8rem;color:#64748b;margin-bottom:4px"><span>Paid — {paid} EMIs ({pct}%)</span><span>Remaining — {L["pending_emi"]}</span></div>{pb(pct,"#3b82f6")}',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    c1.markdown(f'<div class="glow-card"><div class="sec-hd">Outstanding</div><div style="font-size:1.4rem;font-weight:700;color:#fb923c">{inr(out)}</div></div>',unsafe_allow_html=True)
    c2.markdown(f'<div class="glow-card"><div class="sec-hd">Monthly EMI</div><div style="font-size:1.4rem;font-weight:700;color:#f1f5f9">{inr(float(L["monthly_emi"]))}</div></div>',unsafe_allow_html=True)
    c3.markdown(f'<div class="glow-card"><div class="sec-hd">Advance paid</div><div style="font-size:1.4rem;font-weight:700;color:#4ade80">{inr(float(L["advance_paid"]))}</div></div>',unsafe_allow_html=True)
    st.divider()
    col1,col2=st.columns(2)
    with col1:
        st.markdown('<div class="sec-hd">Edit loan details</div>',unsafe_allow_html=True)
        with st.form("loan_edit_f"):
            lc1,lc2=st.columns(2)
            np_=lc1.number_input("Pending EMIs",value=int(L["pending_emi"]))
            nr_=lc2.number_input("Rate (%)",value=float(L["rate"]),step=0.01)
            ne_=lc1.number_input("Monthly EMI (₹)",value=float(L["monthly_emi"]))
            npr_=lc2.number_input("Principal (₹)",value=float(L["principal"]))
            st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
            if st.form_submit_button("💾 Update",use_container_width=True):
                if upd("home_loan",L["id"],{"pending_emi":np_,"rate":nr_,"monthly_emi":ne_,"principal":npr_}): st.success("Updated!"); st.rerun()
            st.markdown('</div>',unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="sec-hd">Rate history</div>',unsafe_allow_html=True)
        for i,r in enumerate(rates):
            is_cur=i==len(rates)-1; clr="#4ade80" if is_cur else "#475569"; mk="◉" if is_cur else "○"
            st.markdown(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1a2540;font-size:.82rem"><span style="color:{clr}">{mk} {r["date"]}</span><span style="font-weight:700;color:{clr}">{r["rate"]}%</span><span style="color:#475569">{r["remaining"]} EMIs</span></div>',unsafe_allow_html=True)
        with st.expander("➕ Log rate change"):
            with st.form("rate_hist_f"):
                rc1,rc2=st.columns(2)
                rd=rc1.text_input("Date (e.g. Apr 2026)"); rr=rc2.number_input("New rate (%)",min_value=0.0,step=0.01); rem=rc1.number_input("Remaining EMIs",min_value=0)
                if st.form_submit_button("Add"):
                    if ins("loan_rate_history",{"date":rd,"rate":rr,"remaining":rem}): st.success("Added!"); st.rerun()

# ═══════════════════════════════════════════════════
elif p == "Dues":
    st.title("👥 Dues & Receivables")
    data=q("dues","created_at")
    pend=sum(float(d["amount"]) for d in data if d["status"]=="Pending")
    part=sum(float(d["amount"]) for d in data if d["status"]=="Partial")
    sett=sum(float(d["amount"]) for d in data if d["status"]=="Settled")
    k1,k2,k3,k4=st.columns(4)
    k1.metric("🔴 Pending",inr(pend),f"{sum(1 for d in data if d['status']=='Pending')} items")
    k2.metric("🟡 Partial",inr(part),f"{sum(1 for d in data if d['status']=='Partial')} items")
    k3.metric("🟢 Settled",inr(sett),"recovered ✓")
    k4.metric("Total given",inr(pend+part+sett),"all time")
    st.divider()
    tab1,tab2=st.tabs(["📋  All Dues","➕  Add Due"])
    with tab1:
        SORD={"Pending":0,"Partial":1,"Settled":2}; SICON={"Pending":"🔴","Partial":"🟡","Settled":"🟢"}
        for d in sorted(data,key=lambda x:SORD.get(x["status"],9)):
            icon=SICON.get(d["status"],"⚪")
            with st.expander(f"{icon} **{d['person']}** — {d['purpose']} — ₹{float(d['amount']):,.0f}  |  {d['status']}"):
                dc1,dc2,dc3=st.columns([2,2,1])
                np_=dc1.text_input("Person",d["person"],key=f"dp_{d['id']}")
                na_=dc2.number_input("Amount",value=float(d["amount"]),key=f"da_{d['id']}")
                npr_=dc1.text_input("Purpose",d["purpose"],key=f"dpr_{d['id']}")
                ns_=dc2.selectbox("Status",["Pending","Partial","Settled"],index=["Pending","Partial","Settled"].index(d["status"]) if d["status"] in ["Pending","Partial","Settled"] else 0,key=f"ds_{d['id']}")
                nn_=dc1.text_input("Notes",d.get("notes","") or "",key=f"dn_{d['id']}")
                b1,b2=dc3.columns(2)
                with b1:
                    st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
                    if st.button("💾",key=f"dsv_{d['id']}"):
                        if upd("dues",d["id"],{"person":np_,"amount":float(na_),"purpose":npr_,"status":ns_,"notes":nn_}): st.success("Saved!"); st.rerun()
                    st.markdown('</div>',unsafe_allow_html=True)
                with b2:
                    st.markdown('<div class="danger-btn">',unsafe_allow_html=True)
                    if st.button("🗑️",key=f"ddel_{d['id']}"):
                        if dlt("dues",d["id"]): st.success("Deleted!"); st.rerun()
                    st.markdown('</div>',unsafe_allow_html=True)
    with tab2:
        st.subheader("Add due / receivable")
        with st.form("add_due_f",clear_on_submit=True):
            f1,f2=st.columns(2)
            person=f1.text_input("Person *",placeholder="e.g. Bhargav")
            amt=f2.number_input("Amount (₹) *",min_value=0.01,step=100.0)
            purpose=f1.text_input("Purpose *",placeholder="e.g. TV EMI 5")
            status=f2.selectbox("Status *",["Pending","Partial","Settled"])
            ddate=f1.date_input("Due date",value=date.today())
            note=f2.text_input("Notes (optional)")
            st.markdown('<div class="primary-btn">',unsafe_allow_html=True)
            ok=st.form_submit_button("➕ Add Due",use_container_width=True)
            st.markdown('</div>',unsafe_allow_html=True)
        if ok:
            if not person or not purpose or amt<=0: st.error("Fill person, purpose and amount.")
            elif ins("dues",{"person":person,"amount":float(amt),"purpose":purpose,"status":status,"due_date":str(ddate),"notes":note}): st.success(f"✅ Added: {person} — {purpose}")

# ═══════════════════════════════════════════════════
elif p == "Budget":
    st.title("📅 Monthly Budget Planner")
    exp_data=q("expenses","date")
    cat_actual={} 
    if exp_data:
        df=pd.DataFrame(exp_data); df["amount"]=df["amount"].astype(float)
        cat_actual=df.groupby("category")["amount"].sum().to_dict()
    defaults={"Loan":65000,"Home":8000,"Bills":5000,"Transport":6000,"Savings":7000,"Shopping":5000,"Education":12000,"Entertainment":2000,"Medical":3000,"Food":3000,"Family":5000,"Other":3000}
    st.markdown('<div class="sec-hd">Set monthly budget limits</div>',unsafe_allow_html=True)
    cols=st.columns(3); budgets={}
    for i,cat in enumerate(EXP_CATS):
        with cols[i%3]:
            actual=cat_actual.get(cat,0); default=defaults.get(cat,3000)
            budget=st.number_input(cat,value=default,step=500,key=f"bgt_{cat}",min_value=0)
            budgets[cat]=budget
            if actual>0:
                over=actual>budget; pct2=min(int(actual/budget*100),100) if budget else 100
                color="#ef4444" if over else "#22c55e"
                st.markdown(f'<div style="font-size:.72rem;color:{"#fca5a5" if over else "#86efac"};margin-top:-8px;margin-bottom:4px">Spent: ₹{actual:,.0f} / ₹{budget:,} ({pct2}%)</div><div class="mbar-wrap" style="height:5px"><div class="mbar-fill" style="width:{pct2}%;background:{color}"></div></div>',unsafe_allow_html=True)
    st.divider()
    tb=sum(budgets.values()); ta=sum(cat_actual.values()) if cat_actual else 0
    k1,k2,k3=st.columns(3)
    k1.metric("Budget set",inr(tb),"total"); k2.metric("Total spent",inr(ta),"this month")
    k3.metric("Remaining",inr(tb-ta),"↑ under" if tb>=ta else "↓ over")
    if exp_data:
        st.divider(); st.markdown('<div class="sec-hd">Budget vs actual</div>',unsafe_allow_html=True)
        cats=[c for c in EXP_CATS if c in cat_actual or budgets.get(c,0)>0]
        fig=go.Figure()
        fig.add_trace(go.Bar(name="Budget",x=cats,y=[budgets.get(c,0) for c in cats],marker_color="#1e3a5f",marker_line_width=0))
        fig.add_trace(go.Bar(name="Actual",x=cats,y=[cat_actual.get(c,0) for c in cats],marker_color=[("#ef4444" if cat_actual.get(c,0)>budgets.get(c,0) else "#22c55e") for c in cats],marker_line_width=0))
        fig.update_layout(barmode="group",yaxis_tickformat="₹,.0f",xaxis_tickangle=-30)
        dfig(fig,300); st.plotly_chart(fig,use_container_width=True)

# ═══════════════════════════════════════════════════
elif p == "Alerts":
    st.title("🔔 Smart Alerts & Insights")
    exp_data=q("expenses","date"); inc_data=q("income","date")
    dues_d=q("dues","created_at"); loan_d=q("home_loan","id",False); inv_d=q("investments","id",False)
    exp_total=sum(float(e["amount"]) for e in exp_data); inc_total=sum(float(i["amount"]) for i in inc_data)
    net_cf=inc_total-exp_total; pend_dues=[d for d in dues_d if d["status"]=="Pending"]
    alerts=[]
    if net_cf<0: alerts.append(("br","🔴 Deficit",f"Expenses ({inr(exp_total)}) exceed income ({inr(inc_total)}) by {inr(abs(net_cf))}."))
    else: alerts.append(("good","🟢 Surplus",f"You have a surplus of {inr(net_cf)} this month!"))
    for inv in inv_d:
        m=inv.get("maturity","") or ""
        if "2026" in m and inv["type"]=="FD": alerts.append(("warn","🟡 FD Maturing Soon",f'{inv["description"]} ({inr(float(inv["amount"]))}) matures {m} — plan reinvestment.'))
    if pend_dues:
        tot=sum(float(d["amount"]) for d in pend_dues)
        alerts.append(("warn","🟡 Pending Dues",f'{len(pend_dues)} dues totalling {inr(tot)} from {", ".join(set(d["person"] for d in pend_dues))}.'))
    if loan_d:
        L=loan_d[0]; pend_emi=int(L["pending_emi"])
        if pend_emi<=24: alerts.append(("good","🟢 Loan Almost Done",f"Only {pend_emi} EMIs left! Finish line is near."))
        elif pend_emi>120: alerts.append(("warn","🟡 Long Loan Horizon",f"{pend_emi} EMIs (~{pend_emi//12} yrs). Consider prepayment."))
    if exp_data:
        df=pd.DataFrame(exp_data); df["amount"]=df["amount"].astype(float)
        for _,row in df[df["amount"]>20000].iterrows():
            alerts.append(("br","🔴 Large Expense",f'{row["description"]} — {inr(row["amount"])} on {row["date"]}.'))
    st.markdown('<div class="sec-hd">Active alerts</div>',unsafe_allow_html=True)
    for cls,title,msg in alerts:
        st.markdown(f'<div class="alert-banner {cls}"><div><strong>{title}</strong><br><span style="font-size:.8rem;opacity:.85">{msg}</span></div></div>',unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="sec-hd">Financial health score</div>',unsafe_allow_html=True)
    score=70
    if net_cf>=0: score+=15
    if net_cf<0: score-=20
    if len(pend_dues)>3: score-=10
    if loan_d and int(loan_d[0]["pending_emi"])<=24: score+=10
    if inv_total>500000: score+=10
    if bank_total>100000: score+=5
    score=max(0,min(100,score))
    color="#22c55e" if score>=75 else "#f59e0b" if score>=50 else "#ef4444"
    label="Excellent 🎉" if score>=75 else "Good 👍" if score>=60 else "Needs attention ⚠️"
    st.markdown(f'<div class="glow-card" style="text-align:center;padding:2rem"><div style="font-size:4rem;font-weight:800;color:{color};line-height:1">{score}</div><div style="font-size:1rem;color:{color};margin-top:.3rem;font-weight:600">{label}</div><div style="font-size:.78rem;color:#475569;margin-top:.5rem">/100 Financial Health Score</div>{pb(score,color)}</div>',unsafe_allow_html=True)
