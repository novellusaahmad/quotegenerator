# Novellus Loan Management Application – Calculation & Integration Guide

## Overview
This document walks through the core features of the Novellus Loan Management application in everyday language.  It explains what each financial term means, shows the exact formulas used by the software, and provides step‑by‑step examples.  The second half of the guide demonstrates how to send the application’s data to Power BI for dashboards and to Snowflake for long‑term storage.

## Loan Calculation Formulas

### 1. Simple Interest Calculations
Simple interest is the easiest way to charge interest on a loan.  The loan balance does not grow; instead the lender just collects a fee for each day the money is outstanding.  This approach is used for **retained interest** (where interest is taken from the loan at the start) and for **interest‑only** monthly payments.

To work out the charge, the application follows three steps:
1. Convert the annual rate into a daily rate.
2. Count the exact number of days between the start and end dates.
3. Multiply the daily rate by the number of days and by the amount borrowed.

In formula form the calculation is:

\[
\text{Interest} = \frac{\text{Principal} \times \text{Annual Rate} \times \text{Days}}{\text{Days in Year} \times 100}
\]

Where:
- **Principal** – the amount you borrow.
- **Annual Rate** – the yearly interest rate as a percentage (for example, 12 means 12%).
- **Days** – how long you borrow the money.
- **Days in Year** – normally 365, or 366 in a leap year.

**Example** – Borrow £100,000 for 30 days at 12% per year:
1. Daily rate = 12 ÷ 365 = 0.0329% per day.
2. Interest = £100,000 × 0.0329% × 30 = **£986.30**.

The implementation performs these steps automatically, converting the annual rate to a daily rate and multiplying by the exact number of days in the term【F:calculations.py†L55-L61】.

### 2. Net‑to‑Gross Conversion
Borrowers often state how much cash they need **after** fees.  This is called the *net* amount.  The application must work backwards to find the *gross* amount that must be borrowed so that, after fees and interest are removed, the borrower still receives the desired net amount.

For simple interest the relationship is:

\[
\text{Gross} = \text{Net} \times (1 + r \times t)
\]

Where:
- \(r\) – annual interest rate expressed as a decimal (10% becomes 0.10).
- \(t\) – loan term in years (6 months is 0.5).

**Example** – The borrower needs £95,000 net, the annual rate is 10%, and the term is one year:
1. Factor = 1 + 0.10 × 1 = 1.10.
2. Gross = £95,000 × 1.10 = **£104,500**.

The code generalizes this for other interest types, including daily and monthly compounding【F:calculations.py†L191-L239】.

### 3. Amortizing (Capital + Interest) Payments
Some loans require the borrower to repay both the capital and interest over time.  Each payment is the same amount, making budgeting easier.  The application uses the standard amortization formula to work out this fixed payment for any combination of term and interest rate:

\[
\text{Payment} = P \times \frac{r(1+r)^n}{(1+r)^n - 1}
\]

Where:
- \(P\) – the amount borrowed.
- \(r\) – the interest rate for one period (for monthly payments this is annual rate ÷ 12).
- \(n\) – the total number of payments.

**Example** – Borrow £100,000 over two years at 8% per year with monthly payments:
1. Periodic rate \(r\) = 0.08 ÷ 12 = 0.006666...
2. Number of periods \(n\) = 24.
3. Payment = £100,000 × [0.006666 × (1 + 0.006666)^24] ÷ [(1 + 0.006666)^24 − 1] ≈ **£4,507.07** per month.

This logic appears in the amortizing term loan function【F:calculations.py†L2432-L2459】.

### 4. Development Loans
Property development often needs money in stages, called **tranches**, to match the construction schedule.  The calculator lets you enter each tranche with its own date and amount.  Interest is then calculated separately on each tranche from the day it is drawn until it is repaid or the loan completes.

The loan dispatcher links the tranches together, applies any fees, and totals the interest so you can see the full cost of the project【F:calculations.py†L1312-L1360】.

**Example** – Borrow £50,000 on 1 January and a further £20,000 on 1 April.  Interest on the first tranche runs for the full term, while interest on the second tranche only accrues from April onwards.  The application keeps track of these timings automatically.

### 5. Fee Structures and Net Advance Impact
The application accounts for several fee types when deriving both gross and net amounts:

- **Arrangement Fee** – a percentage charged by the lender for setting up the loan.
- **Legal Fees** – cash paid to lawyers for preparing documents.
- **Site Visit Fee** – a fixed charge for any property inspection.
- **Title Insurance** – a percentage that protects the lender against title defects.
- **Exit Fee** – a percentage charged when the loan is repaid.

The first four fees are taken at the start of the loan.  The exit fee is calculated up front but only paid at the end.

All fees are computed in a dedicated helper which returns each component and a combined legal fee total:

\[
\begin{aligned}
\text{Arrangement Fee} &= \text{Gross} \times \frac{\text{Arrangement %}}{100} \\
\text{Title Insurance} &= \text{Gross} \times \frac{\text{Title %}}{100} \\
\text{Exit Fee} &= \text{Gross} \times \frac{\text{Exit %}}{100} \\
\text{Total Legal Fees} &= \text{Legal Fees} + \text{Site Visit Fee} + \text{Title Insurance}
\end{aligned}
\]【F:calculations.py†L2685-L2701】

These fees influence available funds differently depending on the repayment structure:

- **Interest Retained** – net advance deducts all fees and the calculated interest:
  \[\text{Net} = \text{Gross} - \text{Arrangement Fee} - \text{Total Legal Fees} - \text{Interest}\]【F:calculations.py†L1852-L1860】
- **Serviced Options** – only upfront fees reduce the advance, while interest is paid periodically:
  \[\text{Net} = \text{Gross} - \text{Arrangement Fee} - \text{Total Legal Fees}\]【F:calculations.py†L2069-L2073】

When solving gross from a desired net amount, fixed fees are added to the numerator and percentage‑based fees are included with the interest factor in the denominator:

\[
\text{Gross} = \frac{\text{Net} + \text{Legal Fees} + \text{Site Visit Fee}}{1 - (r \times t + \text{Arrangement %} + \text{Title %})}
\]【F:calculations.py†L2721-L2734】

**Worked Example** – Suppose the gross loan is £100,000 with 2% arrangement fee, £1,000 legal fees, £500 site visit fee, 0.5% title insurance and 1% exit fee.

1. Arrangement fee = £100,000 × 2% = £2,000.
2. Title insurance = £100,000 × 0.5% = £500.
3. Total legal fees = £1,000 + £500 (site) + £500 (title) = £2,000.
4. Exit fee = £100,000 × 1% = £1,000 (paid later).

**Net Advance (Interest Retained)** – subtract arrangement, legal fees and interest from the gross to find the amount released to the borrower.

**Net Advance (Serviced)** – subtract only arrangement and legal fees; interest and exit fee are paid separately.

Exit fees are calculated but not deducted upfront; they are applied when the loan is repaid.

## Integration with Power BI
The application stores data in a PostgreSQL database.  A helper script called `start.sh` prepares this database and prints out the connection details you need.  You do not need any prior knowledge of databases to follow the steps:

1. In a terminal, run `./start.sh` and wait until it says the server is ready.
2. The script displays the **server name**, **database**, **username** and **password**.  Leave this window open so you can copy the values.
3. Open **Power BI Desktop** and choose **Get Data → PostgreSQL database**.
4. Enter the server and database details from step 2.  When prompted for credentials, pick **Basic** and type the username and password.
5. Select the tables you want, such as `loan_summary` or `payment_schedule`, and click **Load**.
6. Create visuals as required.  You can later publish the report to Power BI Service and schedule automatic refreshes using the same connection details.

If you host the application on‑premises, an optional Data Gateway can be configured for cloud refreshes【F:ONPREMISE_POWERBI_SETUP.md†L41-L65】.

## Integration with Snowflake
Snowflake is a cloud data warehouse that can store large amounts of information for reporting or sharing with other systems.  The application includes a helper module to send data to Snowflake without writing any SQL.

1. **Configure the Connection**
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
   The function saves the details so they are remembered next time【F:snowflake_utils.py†L20-L37】.

2. **Test the Connection**
   ```python
   from snowflake_utils import test_snowflake_connection
   test_snowflake_connection()
   ```
   If the credentials are correct it prints a success message【F:snowflake_utils.py†L93-L104】.

3. **Send Data**
   ```python
   from snowflake_utils import sync_data_to_snowflake
   sync_data_to_snowflake("loan_summary", [loan.__dict__])
   ```
   This converts the loan object into a dictionary and inserts it into the `loan_summary` table【F:snowflake_utils.py†L107-L156】.

Once configured, loan records can be pushed to Snowflake for advanced analytics or to share with other teams.

## Summary
You now have a plain‑English reference for how the application calculates interest, fees and repayments, plus hands‑on steps for connecting the results to Power BI and Snowflake.  Armed with these details, even a first‑time user can follow the calculations and build reports without needing to understand the underlying code.

