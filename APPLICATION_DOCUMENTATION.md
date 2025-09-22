# Novellus Loan Management Application – Calculation & Integration Guide

## 1. Introduction
The guide explains the main calculations in the Novellus Loan Management application and shows how to connect its data to Power BI and Snowflake. Each section uses everyday language, examples, and references to the matching code.

## 2. Loan Calculations
### 2.1 Simple Interest
Simple interest charges a daily fee on the amount borrowed. The balance itself does not increase.

Steps:
1. Convert the annual rate to a daily rate.
2. Count the exact number of days between start and end dates.
3. Multiply the daily rate by the number of days and the principal.

**Formula**

`Interest = (Principal × Annual Rate × Days) / (Days in Year × 100)`

Where:
- Principal – amount borrowed.
- Annual Rate – yearly percentage rate (e.g., 12 means 12%).
- Days – number of days the money is borrowed.
- Days in Year – usually 365, or 366 in a leap year.

**Example**

Borrow £100,000 for 30 days at 12% per year.

1. Daily rate = 12 ÷ 365 = 0.0329% per day.
2. Interest = £100,000 × 0.0329% × 30 = £986.30.

The application automates these steps【F:calculations.py†L55-L61】.

### 2.2 Net-to-Gross Conversion
Borrowers normally specify the cash they need after fees (net). The application works backwards to find the gross amount that delivers the required net once fees and interest are deducted.

**Formula**

`Gross = Net × (1 + r × t)`

Where:
- r – annual interest rate as a decimal (10% becomes 0.10).
- t – loan term in years (6 months is 0.5).

**Example**

Need £95,000 net, annual rate 10%, term 1 year:
1. Factor = 1 + 0.10 × 1 = 1.10.
2. Gross = £95,000 × 1.10 = £104,500.

The code also handles daily and monthly compounding【F:calculations.py†L191-L239】.

### 2.3 Amortizing Payments
Some loans repay capital and interest through equal instalments.

**Formula**

`Payment = P × [r(1 + r)^n] / [(1 + r)^n − 1]`

Where:
- P – principal.
- r – periodic interest rate (annual rate ÷ 12 for monthly payments).
- n – number of payments.

**Example**

Borrow £100,000 over two years at 8% with monthly payments:
1. r = 0.08 ÷ 12 = 0.006666...
2. n = 24.
3. Payment ≈ £4,507.07 per month.

Implemented in the amortizing loan function【F:calculations.py†L2432-L2459】.

### 2.4 Development Loans
Development finance often releases funds in tranches. Each tranche accrues interest from its own draw date until repayment.

The dispatcher ties tranches together, adds fees, and totals interest for the full project cost【F:calculations.py†L1312-L1360】.

**Example**

Borrow £50,000 on 1 January and £20,000 on 1 April. The first tranche accrues interest for the full term; the second only from April. The application tracks each automatically.

### 2.5 Fees and Net Advance
Fees applied at the start of a loan affect the amount available to the borrower.

Common fees:
- Arrangement Fee – percentage of the gross amount.
- Legal Fees – fixed legal costs.
- Site Visit Fee – fixed inspection charge.
- Title Insurance – percentage for title protection.
- Exit Fee – percentage paid when the loan is repaid.

**Fee Formulas**

```
Arrangement Fee = Gross × (Arrangement % / 100)
Title Insurance = Gross × (Title % / 100)
Exit Fee        = Gross × (Exit % / 100)
Total Legal Fees = Legal Fees + Site Visit Fee + Title Insurance
```
【F:calculations.py†L2685-L2701】

**Impact on Net Advance**

- Interest Retained:

  `Net = Gross − Arrangement Fee − Total Legal Fees − Interest`【F:calculations.py†L1852-L1860】

- Serviced Options:

  `Net = Gross − Arrangement Fee − Total Legal Fees`【F:calculations.py†L2069-L2073】

To determine the gross amount from a desired net:

`Gross = (Net + Legal Fees + Site Visit Fee) / [1 − (r × t + Arrangement % + Title %)]`
【F:calculations.py†L2721-L2734】

**Worked Example**

Gross loan £100,000 with 2% arrangement fee, £1,000 legal fees, £500 site visit fee, 0.5% title insurance and 1% exit fee:

1. Arrangement fee = £100,000 × 2% = £2,000  
2. Title insurance = £100,000 × 0.5% = £500  
3. Total legal fees = £1,000 + £500 + £500 = £2,000  
4. Exit fee = £100,000 × 1% = £1,000 (paid at the end)

For interest-retained loans, subtract fees and interest from the gross to obtain the net. For serviced loans, deduct only the upfront fees; interest and exit fee are paid later.

## 3. Power BI Integration
The application stores data in PostgreSQL. A helper script (`start.sh`) prepares the database and shows the connection settings.

Steps:
1. Run `./start.sh` and wait until the server is ready.
2. Note the server name, database, username and password displayed.
3. In Power BI Desktop choose **Get Data → PostgreSQL database**.
4. Enter the connection details. Select **Basic** authentication and supply the username and password.
5. Choose tables such as `loan_summary` or `payment_schedule` and click **Load**.
6. Build visuals. You can publish the report and schedule refreshes with the same credentials.

For on‑premises hosting, configure a Data Gateway for cloud refreshes【F:ONPREMISE_POWERBI_SETUP.md†L41-L65】.

## 4. Snowflake Integration
Snowflake is a cloud data warehouse. The application includes helpers so you can send data without writing SQL.

1. **Configure the connection**

```python
from snowflake_utils import set_snowflake_config
set_snowflake_config({
    "account": "your_account",
    "user": "your_username",
    "password": "your_password",
    "warehouse": "COMPUTE_WH",
    "database": "NOVELLUS",
    "schema": "PUBLIC"
})
```
The configuration is saved for reuse【F:snowflake_utils.py†L20-L37】.

2. **Test the connection**

```python
from snowflake_utils import test_snowflake_connection
test_snowflake_connection()
```
Displays a success message if credentials are valid【F:snowflake_utils.py†L93-L104】.

3. **Send data**

```python
from snowflake_utils import sync_data_to_snowflake
sync_data_to_snowflake("loan_summary", [loan.__dict__])
```
Inserts a loan record into the `loan_summary` table【F:snowflake_utils.py†L107-L156】.


