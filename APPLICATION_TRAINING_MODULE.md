# Novellus Quote Generator – End User Training Module

## 1. Getting Started

### 1.1 Access Requirements
- Confirm that your user account has been provisioned in the Novellus Loan Management application. Credentials are managed by administrators inside the platform.
- Launch the web application and authenticate via the **Login** page. Upon success you land on the **Home** (landing) screen.

### 1.2 Understanding the Interface
- A top navigation bar provides the refresh shortcut and context banner for every page.
- The hamburger icon on the top-left opens the collapsible side navigation menu. This sidebar houses links to every feature discussed in this module.
- Breadcrumb-like page headings appear next to the Novellus logo to confirm which workspace you are currently viewing.

## 2. Global Navigation Map
The sidebar contains the following destinations. Open the menu, then click the stated link to reach the page.

| Path | How to Reach It | Purpose |
| --- | --- | --- |
| **Home** | Sidebar → **Home** | Landing page with shortcuts and announcements. |
| **Calculator** | Sidebar → **Calculator** | Primary workspace for building bridge, term, and development loan calculations. |
| **Loan History** | Sidebar → **Loan History** | Table of saved calculations with search, filters, edit, and export actions. |
| **Scenario** | Sidebar → **Scenario** | One-click comparison tool that models multiple repayment options in parallel. |
| **Administration → Snowflake Config** | Sidebar → **Administration** → **Snowflake Config** | Manage credentials and sync status for the Snowflake data warehouse connection. |
| **Administration → Power BI Config** | Sidebar → **Administration** → **Power BI Config** | Configure scheduled refreshes and ad-hoc report links for Power BI datasets. |
| **Administration → User Manual** | Sidebar → **Administration** → **User Manual** | Embedded reference copy of the comprehensive user guide. |
| **Administration → Loan Notes** | Sidebar → **Administration** → **Loan Notes** | Create reusable note templates that appear in report exports and saved loan commentary. |

> Tip: The sidebar remains available on every screen, so you can always click the hamburger icon to jump directly to the module you need next.

## 3. Loan Calculator Workflows
All loan creation and recalculation tasks start inside the **Calculator** workspace. The panel is divided into collapsible accordions so you can work from top to bottom.

### 3.1 Launching a Calculation
1. Open the sidebar and click **Calculator**.
2. In the **Loan Overview** accordion, supply the required base information:
   - **Loan Name** (text field).
   - **Borrower Type**, **Loan Reference**, and optional **Notes**.
   - **Property Value** and **Currency** (GBP or EUR).
   - Choose between **Gross** or **Net** amount input, then enter either the fixed amount or the percentage of property value.
   - Set **Start Date**, **Loan Term** (or toggle to **End Date**) and opt into the 360-day interest basis if needed.
3. Expand **Repayment Profile** to choose how interest is captured and paid.
4. Complete **Fees & Costs** for arrangement fees, legal fees, site visit fees, title insurance, and any other adjustments.
5. When every required field is valid, the blue **Calculate** button is enabled at the bottom of the form. Click it to run the calculation.

### 3.2 Selecting Loan Types and Repayment Structures
The calculator supports four loan categories and five repayment styles. Use the radio-button groups at the top of the form to switch between them.

#### 3.2.1 Bridge Loans
1. Under **Loan Type**, click **Bridge**.
2. In **Repayment Profile → Interest Calculation Type**, click the desired option:
   - **Retained** – interest deducted up front.
   - **Service** – borrower services interest each period.
   - **Service + Capital** – combines interest servicing and capital amortisation.
   - **Capital** – capital-only repayments.
   - **Flexible** – custom payment amount per period.
3. After choosing the repayment style, confirm the following supporting fields:
   - **Interest Rate Input** (monthly or annual) and value.
   - **Interest Calculation** (Simple, Daily, Monthly, or Quarterly compounding).
   - **Payment Timing** (Advance or Arrears) and **Payment Frequency** (Monthly or Quarterly) when the repayment style requires scheduled servicing (Service, Service + Capital, Capital, or Flexible).
   - **Capital Repayment Amount** (for Capital) or **Flexible Payment per Period** (for Flexible).
4. Optionally enable **LTV Targeting Simulation** to work towards exit targets.

#### 3.2.2 Term Loans
1. Click **Term** in the **Loan Type** group.
2. Follow the same repayment selection steps as Bridge loans—the same five repayment options and supporting payment controls are available.
3. Enter term-specific data (e.g., longer loan term, frequency) before running the calculation.

#### 3.2.3 Development Loans (Development)
1. Click **Development** in the **Loan Type** picker. The calculator locks the gross input to prevent manual entry and expects you to work from a net requirement.
2. Provide the **Net Amount** and optional **Day 1 Advance**.
3. Use the **Development Loan Tranches** panel to define drawdown structure:
   - Pick **Manual Entry** and adjust tranche rows, or select **Auto Generate** to specify total tranche amount, number of tranches, and click **Generate Tranches**.
   - For manual tranches, click the amount cell to enter value and select the drawdown date for each tranche.
4. Populate the remaining repayment and fee fields as described for Bridge loans.
5. Run the calculation to produce the phased funding schedule.

#### 3.2.4 Development 2 Loan Template
1. Choose **Development 2** (labelled “Development” in the navigation but exposed as an additional radio option).
2. Provide the net requirement and configure tranches just like the primary Development workflow.
3. Use **Flexible Payment**, **Capital**, or **Service** repayment toggles to model hybrid structures during construction.
4. Click **Calculate** when ready.

### 3.3 Executing Each Interest Style
Use the following quick reference to ensure every repayment style is configured correctly regardless of loan type:

| Repayment Style | Required Actions |
| --- | --- |
| **Retained** | Select **Retained**; confirm **Payment Timing/Frequency** stay hidden. Enter rate and fees, then click **Calculate** to deduct interest up front. |
| **Service** | Select **Service**; set **Payment Timing** and **Payment Frequency**; enter rate; click **Calculate** to model periodic interest servicing. |
| **Service + Capital** | Select **Service + Capital**; set timing/frequency; supply **Capital Repayment Amount** for amortisation. |
| **Capital** | Select **Capital**; set timing/frequency; enter **Capital Repayment Amount** to repay principal only. |
| **Flexible** | Select **Flexible**; set timing/frequency; populate **Flexible Payment per Payment** with the custom amount. |

> Ensure the **Calculate** button is pressed after each configuration change so the results update with the latest inputs. The button becomes active automatically when all mandatory inputs are filled.

### 3.4 Reviewing Calculation Outputs
After clicking **Calculate**, the right-hand results column displays:
1. **Loan Summary card** – key figures such as Gross Amount, Net Advance, LTV, and interest components.
2. **Workflow buttons** – access to **Details**, **Save**, and **Report Fields**.
3. **Visualization buttons** below the summary:
   - **Detailed Payment Schedule** – opens a modal with period-by-period cashflows and an export option.
   - **Calculation Breakdown** – visible for Development loans to inspect tranche math.
   - **Loan Breakdown** – pie chart of fees, interest, and advances.
   - **Balance Over Time** – line chart of outstanding balance evolution.

Use these modals to validate and present the result to customers before exporting.

### 3.5 Saving Loans and Generating DOCX Reports
1. When satisfied with the calculation, click **Save** to store the loan. The system enables report downloads only after a loan record exists.
2. Click the **Report Fields** button to open the DOCX configuration modal:
   - Complete **Client/Broker**, **Property Address** entries, **Borrowing Entity**, **Corporate Guarantor**, broker details, maximum LTV, exit fee, and commitment fee.
   - Tick the checkboxes for the sections (valuation, planning appraisal, QS appraisal, due diligence, legals) you want to include.
   - Attach Loan Notes by ticking from the accordion list if needed.
   - Click **Save Report Fields** inside the modal.
3. Back in the summary card, open the download dropdown (displayed as **Quote** once the loan is saved) and select **Loan Summary (DOCX)** to export the Word document.
4. For branded quote layouts, use the **Download Professional Quote** button on the form footer (if enabled) to generate the alternative DOCX template.

## 4. Loan History and Report Review
### 4.1 Locating Saved Loans
1. Navigate to **Loan History** from the sidebar.
2. Use the search box, loan type filter, or organisation filter to narrow results.
3. Click a row to open the **Loan Details** modal. Review the calculation snapshot, payment tables, and any stored notes.

### 4.2 Editing or Exporting from History
- Click **Download DOCX** in the modal footer to export the saved Word summary again.
- Select **Edit & Recalculate** to reopen the loan in the Calculator with all data pre-populated for adjustments.
- Return to the table and use **Power BI Report** links to open embedded analytics configured for the loan.

## 5. Scenario Comparison Tool
1. Open **Scenario** from the sidebar.
2. Fill the **Base Parameters** with property value, amount input, rate, and fees—mirroring the calculator fields.
3. Choose up to four repayment templates (e.g., Retained, Service, Service + Capital, Capital) by toggling the scenario cards on the right.
4. Click **Generate Comparison** to produce side-by-side metrics including gross/net advance, interest totals, and breakeven analysis.
5. Use the **Best Scenario** highlight to identify the strongest option before returning to the calculator to build the final quote.

## 6. Administration Touchpoints
- **Snowflake Config**: Enter warehouse credentials, test the connection, and optionally trigger a manual data sync so downstream reporting remains up to date.
- **Power BI Config**: Supply dataset URL, credentials, and schedule interval to run the background refresh service.
- **Loan Notes**: Maintain standardised clauses that appear in both the calculator’s DOCX modal and the Loan History export modal.

Administrators should review these areas regularly to guarantee exports and reports reflect the latest content.

## 7. End-to-End Training Checklist
1. Login and open the sidebar navigation.
2. Practice building at least one Bridge, Term, Development, and Development 2 loan using each repayment style.
3. Save each loan, configure report fields, and download the DOCX export.
4. Verify the calculation using Loan Summary visuals and Payment Schedule modal.
5. Locate the saved loan in Loan History, re-open it, and export again.
6. Experiment with the Scenario Comparison tool to compare retained versus serviced structures.
7. Review Administration pages to understand where integrations and reusable notes are configured.

Completing this checklist ensures every trainee can confidently navigate the application, generate accurate loan calculations, export customer-ready documentation, and audit prior work.
