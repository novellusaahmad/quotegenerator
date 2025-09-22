# Change Request Document


| Branch | Description | Files | Time Spent | Deployment |
| --- | --- | --- | --- | --- |
| `add-dynamic-interest-calculation-for-loans` | Compute periodic interest by payment frequency to support varied loan schedules. | calculations.py, calculatordev.js | 3.0h | Completed |
| `add-dynamic-interest-calculation-logic` | Add reusable logic for dynamic periodic interest, covering different term structures. | calculations.py, static/js/calculator.js | 3.0h | Completed |
| `fix-loan-save-behavior` | Allow updating existing loans so edits persist and records remain accurate. | routes.py, templates/calculator.html | 2.5h | Completed |
| `fix-loan-edit-input-value-updates` | Ensure edit mode populates fields and toggles to reflect current loan state. | templates/calculator.html, templates/loan_history.html | 2.5h | Completed |
| `fix-loan-editing-fields-update` | Fix loan edit form population, preventing stale values from appearing. | templates/calculator.html | 2.0h | Completed |
| `fix-undefined-values-in-payment-schedule-report` | Fix service+capital schedule and net/gross calculations to avoid undefined values in reports. | calculations.py | 2.0h | Completed |
| `amend-loan-payment-schedule-details` | Refine serviced loan schedule for clearer period breakdowns and interest visibility. | static/js/calculator.js | 2.0h | Completed |
| `fix-javascript-error-for-interest-calculations` | Fix end-date recalculation bug and update day count to prevent JavaScript errors. | templates/calculator.html | 2.0h | Completed |
| `adjust-monthly-interest-calculation-in-summary` | Correct monthly interest calculation for service-only loans. | calculatordev.js, static/js/calculator.js | 2.5h | Completed |
| `fix-detailed-payment-schedule-data-population` | Include period details for service-only schedules and calculate monthly interest locally. | calculations.py, calculatordev.js, static/js/calculator.js | 3.0h | Completed |
| `amend-payment-schedule-for-interest-serviced-loan` | Include period dates for serviced loans to improve reporting. | calculations.py, static/js/calculator.js | 2.5h | Completed |
| `fix-calculate-button-functionality` | Trigger recalculation when interest type changes so output stays accurate. | static/js/calculator.js | 2.0h | Completed |
| `fix-total-interest-calculation-discrepancy` | Use daily calculation for service-only interest schedules to align totals. | calculations.py | 2.0h | Completed |
| `fix-interest-calculation-for-repayment-types` | Use actual day counts for bridge non-retained interest, improving accuracy. | calculations.py, test_bridge_day_count_non_retained.py | 2.5h | Completed |
| `revert-last-change` | Revert `ensure-repayment-options-use-exact-days` to resolve regression. | calculations.py, test_service_only_schedule_day_count.py | 2.0h | Completed |
| `ensure-repayment-options-use-exact-days` | Ensure service-only schedules use calendar days for precise computations. | calculations.py, test_service_only_schedule_day_count.py | 2.0h | Completed |
| `implement-exact-month-calculation-for-loan-repayments` | Refine serviced net-to-gross monthly factor for accurate repayment plans. | calculations.py, calculatordev.html, static/js/calculator_backup.js, templates/calculator.html | 4.0h | Completed |
| `fix-calculation-for-15-months` | Add calendar-based term day calculation covering 15-month loans. | calculations.py, test_interest_day_count.py | 2.5h | Completed |
| `implement-interest-calculation-for-loans` | Use daily interest calculation for bridge and term loans to improve precision. | calculations.py | 2.5h | Completed |
| `calculate-interest-for-bridge-and-term-loan` | Adopt yearly-to-daily method for interest calculations across products. | calculations.py | 2.5h | Completed |
| `add-loan-calculation-summary-modal` | Introduce a modal summarizing loan calculations, including interest, fees, and totals for transparency. | static/js/calculator.js, templates/calculator.html | 3.0h | Completed |
| `update-calculation-display-logic` | Explain how fees impact loan amounts by updating display logic and messaging. | static/js/calculator.js | 2.0h | Completed |
| `display-interest-rates-as-daily,-monthly,-yearly` | Show equivalent daily, monthly, and annual interest rates for user comparison. | templates/quotes.html | 1.5h | Completed |
| `add-footnote-for-rate-equivalencies` | Display the equivalent rate when monthly or annual selections are made to guide users. | static/js/calculator.js | 2.5h | Completed |
| `optimize-tranche-input-space-usage` | Compact the tranche input area and move editing into a modal to save space. | static/js/calculator.js, templates/calculator.html | 2.5h | Completed |
| `fix-overlapping-sections-on-small-screens` | Resolve layout overlaps on small screens with a targeted hotfix. | static/css/layout-hotfix.css, static/js/layout-hotfix.js, templates/base.html | 3.0h | Completed |
| `merge-layout-from-calculator_working11082025.html` | Align the calculator layout with the working HTML version for consistency. | templates/calculator.html | 2.0h | Completed |
| `fix-tranches-input-and-calculation-issues` | Improve tranche input handling and correct related calculation errors. | static/js/calculator.js, templates/calculator.html | 2.5h | Completed |
| `revert-last-change-and-fix-tranche-calculations` | Parse tranche amounts accurately and ensure calculations use the parsed values. | calculations.py, routes.py, static/js/calculator.js, templates/calculator.html | 3.0h | Completed |
| `fix-generate-tranches-button-functionality` | Enable automatic generation of development tranches through the button. | static/js/calculator.js | 2.0h | Completed |
| `update-loan-tranche-calculations-in-files` | Enhance development tranche handling across relevant files. | calculatordev.html, calculatordev.js | 2.5h | Completed |
| `reduce-spacing-for-tranche-display` | Decrease spacing and streamline tranche controls for a cleaner UI. | static/js/calculator.js, templates/calculator_working11082025.html | 2.0h | Completed |
| `adjust-spacing-for-generated-tranches` | Reduce spacing and add edit/delete modals for generated tranches. | static/js/calculator.js, templates/calculator.html | 2.5h | Completed |
| `fix-payment-schedule-and-end-date-calculations` | Correct tranche schedule creation and end-date calculations. | calculations.py | 2.0h | Completed |
| `fix-payment-schedule-tranches-count` | Filter day-one tranches from the detailed payment schedule to avoid duplication. | calculations.py | 2.0h | Completed |
| `remove-tranche-limits-for-development-loan` | Remove limits on development tranches, allowing more flexibility. | calculations.py, static/js/calculator.js, templates/calculator.html | 2.5h | Completed |
| `set-remaining_advance-as-default-value` | Default development tranche amount to the remaining advance. | calculatordev.html, static/js/calculator.js, templates/calculator.html | 2.5h | Completed |
| `fix-tranche-population-count-issue` | Resolve month-offset issues in tranche population breakdown. | calculations.py, test_payment_schedule_consistency.py, test_tranche_generation.py | 3.0h | Completed |
| `fix-auto-tranche-start-date` | Start automatically generated tranches in the second month for accuracy. | static/js/calculator.js, test_tranche_generation.py | 2.5h | Completed |
| `convert-tranche-layout-to-table-format` | Refactor tranche inputs into an editable table layout. | static/js/calculator.js, templates/calculator.html | 3.0h | Completed |
| `fix-column-header-alignment` | Specify CSV delimiters to keep column headers aligned properly. | utils.py | 2.0h | Completed |
| `fix-euro-symbol-display-for-loans` | Correct incorrect Euro symbol rendering in loan outputs. | static/js/calculator.js, templates/calculator.html, utils.py | 3.0h | Completed |
| `update-visualizations-to-button-and-modal` | Move charts into modals and trigger them with buttons for cleaner UI. | static/js/calculator.js, templates/calculator.html | 2.5h | Completed |
| `add-ltv-targeting-simulation-option` | Introduce LTV targeting simulations for both bridge and term loans. | static/js/calculator.js, templates/calculator.html | 3.0h | Completed |
| `fix-end-ltv-calculation-for-payments` | Fix the end LTV calculation for bridge loans to show accurate values. | calculations.py, test_end_ltv.py | 2.5h | Completed |
| `fix-end-ltv-calculation-for-flexible-payments` | Update LTV metrics and add aliases for flexible payment scenarios. | calculations.py, test_end_ltv.py | 2.5h | Completed |
| `fix-end-ltv-for-capital-repayment-option` | Correct end LTV calculation when capital repayments are used. | calculations.py, static/js/calculator.js, test_end_ltv.py | 3.0h | Completed |
| `fix-incorrect-end-ltv-calculation` | Auto-fill capital repayment based on the LTV target to prevent errors. | static/js/calculator.js | 2.0h | Completed |
| `fix-flexible-payment-schedule-calculation` | Generate flexible payment schedules and update LTV targeting logic. | static/js/calculator.js | 2.0h | Completed |
| `fix-flexible-payment-schedule-calculations` | Refine LTV target handling for flexible payment cases. | static/js/calculator.js | 2.0h | Completed |
| `fix-end-ltv-calculation-for-loans` | Test LTV targeting for capital repayment to validate logic. | static/js/calculator.js, test_ltv_target.py | 2.5h | Completed |
| `propose-ui-wizard-for-user-input` | Convert the quote form into a multi-step wizard to simplify data entry. | templates/quote_form.html, static/js/calculator.js, test_ltv_target.py | 3.5h | Completed |
| `fix-loan-calculator-wizard-form-display` | Ensure the wizard-style loan calculator form displays correctly. | routes.py, static/js/calculator_wizard.js, templates/calculator_wizard.html | 3.0h | Completed |
| `duplicate-calculator-page-and-modify-layout` | Add a compact loan calculator template with adjusted layout. | routes.py, templates/calculator_compact.html | 3.0h | Completed |
| `add-mapping-for-calculator-to-calculator-compact` | Align the compact calculator’s color scheme with the main theme. | templates/calculator_compact.html | 2.5h | Completed |
| `make-chart-modal-fullscreen-with-close-option` | Make chart modals fullscreen and add a refresh button and close control. | templates/calculator.html | 2.0h | Completed |
| `add-close-button-to-tabular-report` | Add a close button to the payment schedule modal for improved UX. | templates/calculator.html | 2.5h | Completed |
| `fix-power-bi-postgres-connection-error` | Set up PostgreSQL SSL for Power BI connections to resolve errors. | install.sh, start.sh | 2.5h | Completed |
| `fix-postgresql-ssl-certificate-issue-for-power-bi` | Automatically configure SSL mode for Power BI to avoid certificate issues. | POWERBI_SSL_TROUBLESHOOTING.md, start.sh | 2.5h | Completed |
| `enable-ssl-mode-for-database-connection` | Enable PostgreSQL SSL mode in the application configuration. | install.sh | 1.5h | Completed |
| `o6u515-enable-ssl-mode-for-database-connection` | Handle long hostnames when generating PostgreSQL SSL certificates. | install.sh | 1.5h | Completed |
| `add-snowflake-db-connection-option` | Add helper utilities for Snowflake database integration. | README.md, templates/powerbi_config.html, test_database_url.py, test_powerbi_ssl_connection.py, test_tranche_generation.py | 4.5h | Completed |
| `w73xzn-add-snowflake-db-connection-option` | Synchronize the Snowflake DB connection branch with `main`. | README.md, templates/powerbi_config.html, test_database_url.py, test_powerbi_ssl_connection.py, test_tranche_generation.py | 3.5h | Completed |
| `add-snowflake-connection-test-option` | Provide a Snowflake connection test endpoint for validation. | README.md, routes.py, snowflake_utils.py | 3.5h | Completed |
| `0mai2s-add-snowflake-connection-test-option` | Install the Snowflake connector to support connection tests. | install.sh | 1.5h | Completed |
| `c75cd1-add-snowflake-connection-test-option` | Sync the Snowflake connection test branch with `main`. | README.md, routes.py, snowflake_utils.py | 2.5h | Completed |
| `update-code-for-snowflake-sync` | Import `model_to_dict` and other helpers for Snowflake synchronization. | routes.py | 2.0h | Completed |
| `add-snowflake-connection-options` | Add Snowflake token authentication and configuration management. | routes.py, snowflake_utils.py, templates/powerbi_config.html | 3.5h | Completed |
| `remove-table-creation-option-in-snowflake-sync` | Remove automatic table creation in Snowflake sync routines. | snowflake_utils.py | 1.5h | Completed |
| `update-theme-on-powerbi-config-page` | Align PowerBI configuration theme with the loan calculator design. | templates/powerbi_config.html | 2.0h | Completed |
| `rewrite-user-manual-with-professional-formatting` | Rewrite the user manual with professional formatting and structure. | USER_MANUAL.md | 2.5h | Completed |
| `fix-loan-edit-values-on-history-page` | Preserve zero values when editing loans from the history page. | templates/loan_history.html | 2.0h | Completed |
| `create-business-requirement-document-with-features` | Expand the BRD with formulas and visual examples. | Novellus_BRD.md | 2.5h | Completed |
| `update-scenario-comparison-page-calculation-engine` | Use the base layout for scenario comparisons, reducing duplication. | scenario_comparison.py, templates/scenario_comparison.html | 2.5h | Completed |
| `configure-docker-compose-for-windows-and-ubuntu` | Ensure Docker Compose works consistently on Windows and Ubuntu. | docker-compose.yml | 2.0h | Completed |
| `fix-dynamic-display-of-insurance-row` | Fix dynamic percentage display for fee inputs in the insurance row. | static/js/calculator.js | 2.0h | Completed |
| `fix-dynamic-display-of-insurance-row-3s56yp` | Sync the dynamic insurance row fix with `main`. | static/js/calculator.js | 2.0h | Completed |
| `fix-javascript-errors-in-calculator.js` | Handle canvas fallback in calculator labels to avoid script errors. | static/js/calculator.js | 2.0h | Completed |
| `fix-javascript-network-processing-errors` | Correct fee display variable names to prevent network processing errors. | static/js/calculator.js | 2.0h | Completed |
| `fix-title-insurance-summary-display` | Treat blank fee inputs as zero to fix insurance summary display. | calculations.py, calculatordev.html, calculatordev.js, static/js/calculator.js, templates/calculator.html | 4.0h | Completed |
| `hide-buttons-and-remove-payment-schedule` | Hide charts and schedules for bridge retained interest loans. | static/js/calculator.js | 1.5h | Completed |
| `enhance-loan-details-modal-formatting` | Improve gross-to-net breakdown formatting in the loan details modal. | static/js/calculator.js | 2.0h | Completed |
| `allow-decimal-input-in-calculator.html` | Permit decimal inputs across calculator fields for precision. | templates/calculator.html | 1.5h | Completed |
| `fix-calculation-for-gross-amount-percentage` | Correct percentage-based gross amount calculations. | static/js/calculator.js | 2.0h | Completed |
| `calculate-interest-for-bridge-and-term-loan` | Adopt yearly-to-daily method for interest calculations across products. | calculations.py | 2.5h | Completed |
| `implement-interest-calculation-for-loans` | Use daily interest calculation for bridge and term loans to improve precision. | calculations.py | 2.5h | Completed |
| `fix-calculation-for-15-months` | Add calendar-based term day calculation covering 15-month loans. | calculations.py, test_interest_day_count.py | 2.5h | Completed |
| `implement-exact-month-calculation-for-loan-repayments` | Refine serviced net-to-gross monthly factor for accurate repayment plans. | calculations.py, calculatordev.html, static/js/calculator_backup.js, templates/calculator.html | 4.0h | Completed |
| `ensure-repayment-options-use-exact-days` | Ensure service-only schedules use calendar days for precise computations. | calculations.py, test_service_only_schedule_day_count.py | 2.0h | Completed |
| `revert-last-change` | Revert `ensure-repayment-options-use-exact-days` to resolve regression. | calculations.py, test_service_only_schedule_day_count.py | 2.0h | Completed |
| `fix-interest-calculation-for-repayment-types` | Use actual day counts for bridge non-retained interest, improving accuracy. | calculations.py, test_bridge_day_count_non_retained.py | 2.5h | Completed |
| `fix-total-interest-calculation-discrepancy` | Use daily calculation for service-only interest schedules to align totals. | calculations.py | 2.0h | Completed |
| `fix-calculate-button-functionality` | Trigger recalculation when interest type changes so output stays accurate. | static/js/calculator.js | 2.0h | Completed |
| `amend-payment-schedule-for-interest-serviced-loan` | Include period dates for serviced loans to improve reporting. | calculations.py, static/js/calculator.js | 2.5h | Completed |
| `fix-detailed-payment-schedule-data-population` | Include period details for service-only schedules and calculate monthly interest locally. | calculations.py, calculatordev.js, static/js/calculator.js | 3.0h | Completed |
| `adjust-monthly-interest-calculation-in-summary` | Correct monthly interest calculation for service-only loans. | calculatordev.js, static/js/calculator.js | 2.5h | Completed |
| `fix-javascript-error-for-interest-calculations` | Fix end-date recalculation bug and update day count to prevent JavaScript errors. | templates/calculator.html | 2.0h | Completed |
| `amend-loan-payment-schedule-details` | Refine serviced loan schedule for clearer period breakdowns and interest visibility. | static/js/calculator.js | 2.0h | Completed |
| `fix-undefined-values-in-payment-schedule-report` | Fix service+capital schedule and net/gross calculations to avoid undefined values in reports. | calculations.py | 2.0h | Completed |
| `fix-loan-editing-fields-update` | Fix loan edit form population, preventing stale values from appearing. | templates/calculator.html | 2.0h | Completed |
| `fix-loan-edit-input-value-updates` | Ensure edit mode populates fields and toggles to reflect current loan state. | templates/calculator.html, templates/loan_history.html | 2.5h | Completed |
| `fix-loan-save-behavior` | Allow updating existing loans so edits persist and records remain accurate. | routes.py, templates/calculator.html | 2.5h | Completed |
| `add-dynamic-interest-calculation-logic` | Add reusable logic for dynamic periodic interest, covering different term structures. | calculations.py, static/js/calculator.js | 3.0h | Completed |
| `add-dynamic-interest-calculation-for-loans` | Compute periodic interest by payment frequency to support varied loan schedules. | calculations.py, calculatordev.js | 3.0h | Completed |
