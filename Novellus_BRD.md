![Novellus Logo](static/novellus_logo.png)

# Novellus Loan Management System - Business Requirements

**Version:** 1.2
**Date:** 16 August 2025

## 1. System Overview
The Novellus Loan Management System is a Flask-based web application supporting Bridge, Term, and Development loans with precise decimal calculations, multi-currency support, and flexible payment options.

## 2. Key Features
- Dual authentication using sessions and JWT tokens.
- Role-based access control for borrowers and lenders.
- Comprehensive loan calculation engine covering interest, fees, payment schedules, and LTV metrics.
- Professional document generation in PDF and Excel formats.
- Interactive charts and responsive user interface with Novellus branding.
- Database models for users, applications, quotes, payments, and communications.

## 3. Loan Types
- **Bridge Loans:** Retained, interest-only, service + capital, capital-only, and flexible-payment options with daily interest and net-to-gross conversion.
- **Term Loans:** Interest-only or amortizing structures with advance or arrears timing.
- **Development Loans:** Multiple tranches with staggered releases and per‑tranche rates, supporting day‑1 advances.

## 4. User Management
- Secure registration and login with password hashing.
- Role-based dashboards and permissions.
- JWT tokens for API access.

## 5. Document Generation
- PDF quotes with branding, payment schedules, and fee breakdowns.
- Excel exports with summary, schedule, and fees worksheets.

## 6. Configuration and Deployment
- Environment-based settings for development and production.
- Docker and Azure deployment scripts.

## 7. Non-Functional Requirements
- **Security:** CSRF protection, session management, and role validation.
- **Performance:** Optimized calculation engine and database indexing.
- **Maintainability:** Modular architecture and comprehensive documentation.

## 8. Calculation Logic
The `calculations.py` module provides an auditable engine for all loan types.

### 8.1 Bridge Loan Calculations
`calculate_bridge_loan` normalizes inputs, converts net requests to gross when needed, and dispatches to repayment strategies based on `repayment_option`【F:calculations.py†L116-L161】【F:calculations.py†L210-L323】. The function supports a 360/365 day-count switch and records payment timing/frequency for schedule generation and LTV reporting【F:calculations.py†L202-L209】【F:calculations.py†L343-L379】.

#### 8.1.1 Gross to Net
- **Retained Interest** – `_calculate_bridge_retained` deducts all interest at drawdown, reducing the net advance【F:calculations.py†L1633-L1663】.  
  Formula: `interest = gross × rate × term_years`; `net = gross − interest − fees`【F:calculations.py†L1670-L1676】【F:calculations.py†L1661】
- **Service Only** – `_calculate_bridge_interest_only` charges periodic interest, extracting actual totals from the detailed schedule for accuracy【F:calculations.py†L1713-L1761】.  
  Formula: `interest_i = balance_i × rate × days_i / basis`; `payment_i = interest_i` for each period【F:calculations.py†L1750-L1757】
- **Service + Capital** – `_calculate_bridge_service_capital` applies user-defined capital repayments on a declining balance【F:calculations.py†L1811-L1848】.  
  Formula: `interest_i = balance_i × rate / 12`; `balance_{i+1} = balance_i + interest_i − capital_payment`【F:calculations.py†L1815-L1837】
- **Capital Only** – `_calculate_bridge_capital_payment_only` retains interest up front and reduces balance with capital payments, crediting interest savings【F:calculations.py†L6216-L6250】.  
  Formula: `retained_interest = gross × rate × term_years`; `net = gross − retained_interest − fees`【F:calculations.py†L6228-L6233】
- **Flexible Payment** – `_calculate_bridge_flexible` accepts arbitrary payment amounts and recomputes residual interest each period【F:calculations.py†L1928-L1963】.  
  Formula: `balance_{i+1} = balance_i + interest_i − payment_i`, where `interest_i = balance_i × rate / 12`【F:calculations.py†L1950-L1967】

#### 8.1.2 Net to Gross
For net inputs, `_calculate_gross_from_net_bridge` iteratively solves the Excel-style `net = gross − interest − fees` equation, applying 365/360 adjustments when requested【F:calculations.py†L2497-L2595】.  
Formula: `gross = (net + fixed_fees) / (1 − (rate × term/12 + arrangement% + title%))`【F:calculations.py†L2497-L2531】【F:calculations.py†L2538-L2546】.  
Each repayment option then reuses the corresponding gross-to-net routine with the solved gross amount【F:calculations.py†L210-L323】.

#### 8.1.3 Additional Bridge Controls
Bridge loans support 360-day loans, monthly or quarterly payments in advance or arrears, and compute start/end LTVs to facilitate exit targeting. Automated tests verify LTV targeting by matching end LTVs to requested percentages【F:calculations.py†L202-L209】【F:calculations.py†L343-L379】【F:test_ltv_target.py†L50-L56】.

### 8.2 Term Loan Calculations
`calculate_term_loan` mirrors bridge processing but defaults to interest-only payments; it supports 360/365 day-count logic and converts net requests to gross amounts【F:calculations.py†L449-L458】【F:calculations.py†L500-L560】.

#### 8.2.1 Gross to Net
- **Retained Interest** – `_calculate_term_retained_interest` deducts interest at inception using actual day counts when available【F:calculations.py†L2172-L2204】.  
  Formula: `interest = gross × rate × term_years`; `net = gross − interest − fees`【F:calculations.py†L2187-L2195】
- **Service Only** – `_calculate_term_interest_only` computes periodic interest and aligns totals with the detailed schedule【F:calculations.py†L2067-L2106】.  
  Formula: `interest_i = balance_i × rate × days_i / basis`; `payment_i = interest_i` for each period【F:calculations.py†L2091-L2101】

#### 8.2.2 Net to Gross
`_calculate_gross_from_net_term` provides Excel-compatible formulas. The retained-interest path iterates until `gross − interest − fees = net`, while the serviced path removes only the monthly interest factor from the denominator【F:calculations.py†L2717-L2797】【F:calculations.py†L2825-L2869】.  
Formula (retained): `gross = (net + fixed_fees) / (1 − (rate × term/12 + arrangement% + title%))`【F:calculations.py†L2717-L2757】.

#### 8.2.3 Additional Term Controls
Term loans accept 360-day calculations, payment timing in advance or arrears, and monthly or quarterly frequency while tracking start and end LTVs for exit planning【F:calculations.py†L449-L458】【F:calculations.py†L658-L688】.

### 8.3 Development Loan Calculations
`calculate_development_loan` manages multi-tranche projects and defaults to net inputs. It captures parameters including `use_360_days` and per‑tranche rates before choosing net-to-gross or gross-to-net flows【F:calculations.py†L1191-L1212】.

#### 8.3.1 Net to Gross
For net requests, `_calculate_development_excel_methodology` reverse-engineers the gross amount using compound daily interest to match Excel outputs. Loan term days come from actual start/end dates, and fees are recomputed on the solved gross amount【F:calculations.py†L1217-L1288】.  
Formula: for each tranche `j`, `interest_j = tranche_j × rate_j × days_j / basis`; `gross = net + Σ interest_j + fees`.  Day‑1 advances are added to user-specified tranche lists without generating extra tranches【F:calculations.py†L1260-L1283】.

#### 8.3.2 Gross to Net
When gross is supplied, user tranches are processed directly. Legacy array formats are normalized, and if a Day‑1 advance exists the remaining tranche amounts are scaled and dates shifted to start from month two【F:calculations.py†L1303-L1343】【F:calculations.py†L1345-L1386】.  
Formula: `net = gross − Σ interest_j − fees`, where each `interest_j` is computed on its tranche balance as above.

#### 8.3.3 Additional Development Controls
The resulting quote records loan term in days, supports 360-day interest, honours payment timing/frequency, and exposes overall LTV calculated from the aggregated tranche advances【F:calculations.py†L1594-L1616】.

## 9. Calculator Visualizations and Reports
The calculator page augments numeric outputs with modals and charts that explain the quote.

- **Detailed Payment Schedule** – Tabular report listing period, opening balance, tranche release, interest calculation, interest amount, principal payment, total payment, closing balance, and balance change【F:templates/calculator.html†L974-L1005】.
- **Loan Breakdown Chart** – Doughnut visual showing net advance, arrangement fee, legal costs, site visit fee, title insurance, and total interest【F:templates/calculator.html†L1013-L1022】【F:static/js/calculator.js†L2368-L2384】.
- **Balance Over Time Chart** – Line chart plotting the declining loan balance across payment dates【F:templates/calculator.html†L1030-L1039】【F:static/js/calculator.js†L2660-L2741】.
- **Compound Interest Chart** – Bar chart for development loans comparing monthly interest and principal amounts to highlight compounding effects【F:templates/calculator.html†L1047-L1056】【F:static/js/calculator.js†L2842-L2904】.
- **Tranche Release Chart** – Bar chart tracking the timing and amount of each tranche drawdown in development scenarios【F:templates/calculator.html†L1064-L1072】【F:static/js/calculator.js†L2944-L3004】.

---

This document captures the detailed calculation pathways for all Novellus loan products, ensuring every financial result is transparent and reproducible.
