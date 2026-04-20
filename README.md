# 💰 Tejas Patel — Finance Dashboard
### Streamlit + Supabase · Full CRUD · Live Data

---

## 🚀 Setup in 4 steps

### Step 1 — Run the SQL schema in Supabase

1. Go to **https://cozpsoousfuhhydetflp.supabase.co**
2. Click **SQL Editor** in the left menu
3. Click **New query**
4. Copy the entire contents of `schema.sql` and paste it
5. Click **Run** — this creates all 7 tables and seeds your data

### Step 2 — Get your Supabase anon key

1. In Supabase → **Settings** → **API**
2. Copy the **anon / public** key (NOT the service_role key)

### Step 3 — Add secrets to Streamlit Cloud

1. Go to **https://share.streamlit.io**
2. Find your app: `my-financial-dashboard · main · app.py`
3. Click the **⋮ menu** → **Settings** → **Secrets**
4. Paste this (replace with your real key):

```toml
SUPABASE_URL = "https://cozpsoousfuhhydetflp.supabase.co"
SUPABASE_KEY = "your-anon-public-key-here"
```

5. Click **Save** — the app will restart automatically

### Step 4 — Push these files to GitHub

Push the following files to `tejasvcomp/my-financial-dashboard` (main branch):

```
app.py              ← main dashboard (replace existing)
requirements.txt    ← updated dependencies
schema.sql          ← run once in Supabase, then keep for reference
.gitignore          ← keeps secrets.toml out of Git
README.md           ← this file
```

**DO NOT push** `.streamlit/secrets.toml` — it's in .gitignore for security.

---

## 📊 Dashboard pages

| Page | Features |
|------|----------|
| **Overview** | KPI cards, expense breakdown chart, net worth donut, cashflow P&L |
| **Expenses** | Full CRUD — add, edit, delete, filter by category, sort |
| **Income** | Full CRUD — salary, dividends, bonuses tracked separately |
| **Banks & MFs** | Live balance editing for all 7 accounts + portfolios, distribution chart |
| **Investments** | 13 investments — FDs with maturity calc, PPF, Mandal, Stocks, MF |
| **Home Loan** | EMI progress bar, rate history, full loan detail editing |
| **Dues** | Receivables with Pending/Partial/Settled status, full CRUD |

---

## 🗄️ Database tables (Supabase / PostgreSQL)

| Table | Purpose |
|-------|---------|
| `expenses` | Every expense transaction |
| `income` | Salary, dividends, other income |
| `bank_accounts` | All bank accounts + MF portfolios |
| `investments` | FDs, PPF, Gratuity, Mandals, Stocks, MF |
| `home_loan` | Axis Bank home loan details |
| `loan_rate_history` | Rate change log |
| `dues` | Receivables / money given to others |

---

## 🔧 Local development

```bash
# Clone your repo
git clone https://github.com/tejasvcomp/my-financial-dashboard
cd my-financial-dashboard

# Install dependencies
pip install -r requirements.txt

# Create local secrets (DO NOT commit this file)
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
SUPABASE_URL = "https://cozpsoousfuhhydetflp.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
EOF

# Run locally
streamlit run app.py
```

---

## 🔐 Security notes

- The `.streamlit/secrets.toml` file is in `.gitignore` — it will never be pushed to GitHub
- Streamlit Cloud secrets are encrypted at rest
- Supabase anon key is safe for frontend use — it's designed to be public
- Row Level Security (RLS) is enabled on all tables with open policies (single-user app)
- For multi-user, add Supabase Auth and update RLS policies to `auth.uid()`
