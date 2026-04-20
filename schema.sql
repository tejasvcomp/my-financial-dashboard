-- ============================================================
-- TEJAS PATEL — FINANCE DASHBOARD — SUPABASE SCHEMA
-- Run this entire file in your Supabase SQL Editor
-- Project: cozpsoousfuhhydetflp.supabase.co
-- ============================================================

-- 1. EXPENSES
create table if not exists expenses (
    id          bigserial primary key,
    date        date not null default current_date,
    description text not null,
    category    text not null default 'Other',
    amount      numeric(12,2) not null,
    notes       text,
    created_at  timestamptz default now()
);

-- 2. INCOME
create table if not exists income (
    id          bigserial primary key,
    date        date not null default current_date,
    description text not null,
    category    text not null default 'Salary',
    amount      numeric(12,2) not null,
    notes       text,
    created_at  timestamptz default now()
);

-- 3. BANK ACCOUNTS
create table if not exists bank_accounts (
    id        bigserial primary key,
    name      text not null,
    type      text not null default 'Savings',
    balance   numeric(12,2) not null default 0,
    note      text,
    updated_at timestamptz default now()
);

-- 4. INVESTMENTS
create table if not exists investments (
    id          bigserial primary key,
    description text not null,
    type        text not null default 'FD',
    amount      numeric(12,2) not null,
    rate        numeric(5,2) default 0,
    maturity    text,
    notes       text,
    created_at  timestamptz default now()
);

-- 5. HOME LOAN
create table if not exists home_loan (
    id          bigserial primary key,
    principal   numeric(12,2) not null,
    disbursed   text not null,
    total_emi   int not null,
    pending_emi int not null,
    rate        numeric(5,2) not null,
    monthly_emi numeric(12,2) not null,
    advance_paid numeric(12,2) default 0,
    updated_at  timestamptz default now()
);

-- 6. LOAN RATE HISTORY
create table if not exists loan_rate_history (
    id        bigserial primary key,
    date      text not null,
    rate      numeric(5,2) not null,
    remaining int not null
);

-- 7. DUES
create table if not exists dues (
    id        bigserial primary key,
    person    text not null,
    purpose   text not null,
    amount    numeric(12,2) not null,
    status    text not null default 'Pending',
    due_date  date,
    notes     text,
    created_at timestamptz default now()
);

-- ============================================================
-- SEED DATA (your actual data — runs once)
-- ============================================================

-- Bank accounts
insert into bank_accounts (name, type, balance, note) values
('HDFC Bank',        'Savings',     166205,  'Primary account'),
('Axis Bank',        'Savings',      62860,  'Min ₹12K balance'),
('Mehsana Bank',     'RD',            4000,  'Monthly RD'),
('CBI',              'Current',       1300,  'Petrol transfers'),
('M-8424 Portfolio', 'Mutual Fund',  59187,  'MF portfolio'),
('M-2111 Portfolio', 'Mutual Fund',   5197,  'MF portfolio'),
('M-SAURAS Portfolio','Mutual Fund', 42372,  'MF portfolio')
on conflict do nothing;

-- Home loan
insert into home_loan (principal, disbursed, total_emi, pending_emi, rate, monthly_emi, advance_paid) values
(2381324, 'May 2023', 240, 160, 7.15, 20000, 50000)
on conflict do nothing;

-- Loan rate history
insert into loan_rate_history (date, rate, remaining) values
('May 2023', 8.75, 240),
('Jan 2024', 8.40, 219),
('Mar 2025', 8.15, 208),
('Jun 2025', 7.40, 188),
('Dec 2025', 7.15, 160)
on conflict do nothing;

-- Investments
insert into investments (description, type, amount, rate, maturity) values
('Tejas GLS PF / PPF',       'PPF',      336311, 0,    'APR-2026'),
('Tejas PPF (Post IE)',       'PPF',      128955, 0,    'Ongoing'),
('Stocks — Mom Upstox',      'Stocks',   150000, 0,    'Liquid'),
('GLS Welfare Fund',          'Lock-in',  60000,  0,    'JUL-2025'),
('Ratnavatika Mandal',        'Mandal',   201400, 0,    'APR-2026'),
('Rajumama Mandal',           'Mandal',   61500,  0,    'APR-2026'),
('GLS Gratuity',              'Gratuity', 300000, 0,    'MAY-2026'),
('ELSS Mutual Fund',          'MF',       50000,  0,    '15-01-2027'),
('Prihaan HDFC FD (Dips)',    'FD',       75000,  7.25, '11-08-2026'),
('Prihaan HDFC FD (Dips)',    'FD',       125000, 5.50, '11-08-2026'),
('Prihaan HDFC FD (Dips)',    'FD',       35000,  4.25, '11-08-2026'),
('Saurashtra Mom FD',         'FD',       300000, 8.00, '09-02-2028'),
('Saurashtra Mom FD',         'FD',       50000,  8.00, '09-02-2028')
on conflict do nothing;

-- Dues
insert into dues (person, purpose, amount, status, due_date) values
('Dr. SS',      'IPO 1',              15000,  'Pending', '2024-01-01'),
('Dr. SS',      'IPO 2',              25000,  'Pending', '2024-01-01'),
('Yogeshbhai',  'Mobile EMI 2-6',     5500,   'Partial', '2025-11-25'),
('Secure Layer','Axis dues',          8000,   'Pending', '2025-01-01'),
('Bhargav',     'TV EMI 5-6',         7000,   'Pending', '2026-02-01')
on conflict do nothing;

-- Sample April 2026 expenses
insert into expenses (date, description, category, amount) values
('2026-04-10', 'Home Loan EMI (36)',        'Loan',          56100),
('2026-04-08', 'Honda Amaze EMI (62)',       'Loan',          9278),
('2026-04-01', 'Home — Viramgam',           'Home',          7000),
('2026-04-01', 'Mehsana Bank RD',           'Savings',       5000),
('2026-04-01', 'Petrol & Others (CBI)',     'Transport',     5000),
('2026-04-01', 'Credit Card Bill',          'Bills',         10500),
('2026-04-01', 'Netra Maintenance',         'Bills',         750),
('2026-04-03', 'Netflix',                   'Entertainment', 199),
('2026-04-01', 'Ratnavatika Mandal',        'Savings',       1000),
('2026-04-15', 'Rajumama Mandal',           'Savings',       500),
('2026-04-17', 'Amaze Petrol Viramgam',     'Transport',     1750),
('2026-04-20', 'Motorola TV Viramgam',      'Shopping',      10436),
('2026-04-22', 'Prihaan Education Fees',    'Education',     10000),
('2026-04-01', 'Torrent Power Bill',        'Bills',         1800),
('2026-04-18', 'Airtel Broadband',          'Bills',         234),
('2026-04-01', 'Dips Transfer',             'Family',        2500),
('2026-04-13', 'Car Washing',               'Transport',     550),
('2026-04-01', 'Variety Adda',              'Shopping',      300)
on conflict do nothing;

-- Sample income
insert into income (date, description, category, amount) values
('2026-04-01', 'GLS Salary — Q1 2026', 'Salary',   36990),
('2026-04-01', 'Nalco Dividend',        'Dividend',  3500)
on conflict do nothing;

-- Enable Row Level Security (optional but recommended)
alter table expenses         enable row level security;
alter table income           enable row level security;
alter table bank_accounts    enable row level security;
alter table investments      enable row level security;
alter table home_loan        enable row level security;
alter table loan_rate_history enable row level security;
alter table dues             enable row level security;

-- Allow all operations (since no auth — single user app)
create policy "allow all" on expenses          for all using (true) with check (true);
create policy "allow all" on income            for all using (true) with check (true);
create policy "allow all" on bank_accounts     for all using (true) with check (true);
create policy "allow all" on investments       for all using (true) with check (true);
create policy "allow all" on home_loan         for all using (true) with check (true);
create policy "allow all" on loan_rate_history for all using (true) with check (true);
create policy "allow all" on dues              for all using (true) with check (true);
