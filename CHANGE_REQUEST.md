# Change Request Document

This document summarizes the updates in each branch of the repository.

## Branch: main
Currently aligned with `work`; no unique changes.

## Branch: work
The following branches have been merged into `work` along with their main contributions:

- **codex/add-dynamic-interest-calculation-for-loans**: Compute periodic interest by payment frequency to support varied loan schedules.
- **codex/add-dynamic-interest-calculation-logic**: Add reusable logic for dynamic periodic interest, covering different term structures.
- **codex/fix-loan-save-behavior**: Allow updating existing loans so edits persist and records remain accurate.
- **codex/fix-loan-edit-input-value-updates**: Ensure edit mode populates fields and toggles to reflect current loan state.
- **codex/fix-loan-editing-fields-update**: Fix loan edit form population, preventing stale values from appearing.
- **codex/fix-undefined-values-in-payment-schedule-report**: Fix service+capital schedule and net/gross calculations to avoid undefined values in reports.
- **codex/amend-loan-payment-schedule-details**: Refine serviced loan schedule for clearer period breakdowns and interest visibility.
- **codex/fix-javascript-error-for-interest-calculations**: Fix end-date recalculation bug and update day count to prevent JavaScript errors.
- **codex/adjust-monthly-interest-calculation-in-summary**: Correct monthly interest calculation for service-only loans.
- **codex/fix-detailed-payment-schedule-data-population**: Include period details for service-only schedules and calculate monthly interest locally.
- **codex/amend-payment-schedule-for-interest-serviced-loan**: Include period dates for serviced loans to improve reporting.
- **codex/fix-calculate-button-functionality**: Trigger recalculation when interest type changes so output stays accurate.
- **codex/fix-total-interest-calculation-discrepancy**: Use daily calculation for service-only interest schedules to align totals.
- **codex/fix-interest-calculation-for-repayment-types**: Use actual day counts for bridge non-retained interest, improving accuracy.
- **codex/revert-last-change**: Revert `ensure-repayment-options-use-exact-days` to resolve regression.
- **codex/ensure-repayment-options-use-exact-days**: Ensure service-only schedules use calendar days for precise computations.
- **codex/implement-exact-month-calculation-for-loan-repayments**: Refine serviced net-to-gross monthly factor for accurate repayment plans.
- **codex/fix-calculation-for-15-months**: Add calendar-based term day calculation covering 15-month loans.
- **codex/implement-interest-calculation-for-loans**: Use daily interest calculation for bridge and term loans to improve precision.
- **codex/calculate-interest-for-bridge-and-term-loan**: Adopt yearly-to-daily method for interest calculations across products.

## Branch History
The following branches have been created since the project's inception and their primary contributions when they were merged:

- **codex/add-loan-calculation-summary-modal**: Introduce a modal summarizing loan calculations, including interest, fees, and totals for transparency.
- **codex/update-calculation-display-logic**: Explain how fees impact loan amounts by updating display logic and messaging.
- **codex/display-interest-rates-as-daily,-monthly,-yearly**: Show equivalent daily, monthly, and annual interest rates for user comparison.
- **codex/add-footnote-for-rate-equivalencies**: Display the equivalent rate when monthly or annual selections are made to guide users.
- **codex/optimize-tranche-input-space-usage**: Compact the tranche input area and move editing into a modal to save space.
- **codex/fix-overlapping-sections-on-small-screens**: Resolve layout overlaps on small screens with a targeted hotfix.
- **codex/merge-layout-from-calculator_working11082025.html**: Align the calculator layout with the working HTML version for consistency.
- **codex/fix-tranches-input-and-calculation-issues**: Improve tranche input handling and correct related calculation errors.
- **codex/revert-last-change-and-fix-tranche-calculations**: Parse tranche amounts accurately and ensure calculations use the parsed values.
- **codex/fix-generate-tranches-button-functionality**: Enable automatic generation of development tranches through the button.
- **codex/update-loan-tranche-calculations-in-files**: Enhance development tranche handling across relevant files.
- **codex/reduce-spacing-for-tranche-display**: Decrease spacing and streamline tranche controls for a cleaner UI.
- **codex/adjust-spacing-for-generated-tranches**: Reduce spacing and add edit/delete modals for generated tranches.
- **codex/fix-payment-schedule-and-end-date-calculations**: Correct tranche schedule creation and end-date calculations.
- **codex/fix-payment-schedule-tranches-count**: Filter day-one tranches from the detailed payment schedule to avoid duplication.
- **codex/remove-tranche-limits-for-development-loan**: Remove limits on development tranches, allowing more flexibility.
- **codex/set-remaining_advance-as-default-value**: Default development tranche amount to the remaining advance.
- **codex/fix-tranche-population-count-issue**: Resolve month-offset issues in tranche population breakdown.
- **codex/fix-auto-tranche-start-date**: Start automatically generated tranches in the second month for accuracy.
- **codex/convert-tranche-layout-to-table-format**: Refactor tranche inputs into an editable table layout.
- **codex/fix-column-header-alignment**: Specify CSV delimiters to keep column headers aligned properly.
- **codex/fix-euro-symbol-display-for-loans**: Correct incorrect Euro symbol rendering in loan outputs.
- **codex/update-visualizations-to-button-and-modal**: Move charts into modals and trigger them with buttons for cleaner UI.
- **codex/add-ltv-targeting-simulation-option**: Introduce LTV targeting simulations for both bridge and term loans.
- **codex/fix-end-ltv-calculation-for-payments**: Fix the end LTV calculation for bridge loans to show accurate values.
- **codex/fix-end-ltv-calculation-for-flexible-payments**: Update LTV metrics and add aliases for flexible payment scenarios.
- **codex/fix-end-ltv-for-capital-repayment-option**: Correct end LTV calculation when capital repayments are used.
- **codex/fix-incorrect-end-ltv-calculation**: Auto-fill capital repayment based on the LTV target to prevent errors.
- **codex/fix-flexible-payment-schedule-calculation**: Generate flexible payment schedules and update LTV targeting logic.
- **codex/fix-flexible-payment-schedule-calculations**: Refine LTV target handling for flexible payment cases.
- **codex/fix-end-ltv-calculation-for-loans**: Test LTV targeting for capital repayment to validate logic.
- **codex/propose-ui-wizard-for-user-input**: Convert the quote form into a multi-step wizard to simplify data entry.
- **codex/fix-loan-calculator-wizard-form-display**: Ensure the wizard-style loan calculator form displays correctly.
- **codex/duplicate-calculator-page-and-modify-layout**: Add a compact loan calculator template with adjusted layout.
- **codex/add-mapping-for-calculator-to-calculator-compact**: Align the compact calculator’s color scheme with the main theme.
- **codex/make-chart-modal-fullscreen-with-close-option**: Make chart modals fullscreen and add a refresh button and close control.
- **codex/add-close-button-to-tabular-report**: Add a close button to the payment schedule modal for improved UX.
- **codex/fix-power-bi-postgres-connection-error**: Set up PostgreSQL SSL for Power BI connections to resolve errors.
- **codex/fix-postgresql-ssl-certificate-issue-for-power-bi**: Automatically configure SSL mode for Power BI to avoid certificate issues.
- **codex/enable-ssl-mode-for-database-connection**: Enable PostgreSQL SSL mode in the application configuration.
- **o6u515-codex/enable-ssl-mode-for-database-connection**: Handle long hostnames when generating PostgreSQL SSL certificates.
- **codex/add-snowflake-db-connection-option**: Add helper utilities for Snowflake database integration.
- **w73xzn-codex/add-snowflake-db-connection-option**: Synchronize the Snowflake DB connection branch with `main`.
- **codex/add-snowflake-connection-test-option**: Provide a Snowflake connection test endpoint for validation.
- **0mai2s-codex/add-snowflake-connection-test-option**: Install the Snowflake connector to support connection tests.
- **c75cd1-codex/add-snowflake-connection-test-option**: Sync the Snowflake connection test branch with `main`.
- **codex/update-code-for-snowflake-sync**: Import `model_to_dict` and other helpers for Snowflake synchronization.
- **codex/add-snowflake-connection-options**: Add Snowflake token authentication and configuration management.
- **codex/remove-table-creation-option-in-snowflake-sync**: Remove automatic table creation in Snowflake sync routines.
- **codex/update-theme-on-powerbi-config-page**: Align PowerBI configuration theme with the loan calculator design.
- **codex/rewrite-user-manual-with-professional-formatting**: Rewrite the user manual with professional formatting and structure.
- **codex/fix-loan-edit-values-on-history-page**: Preserve zero values when editing loans from the history page.
- **codex/create-business-requirement-document-with-features**: Expand the BRD with formulas and visual examples.
- **codex/update-scenario-comparison-page-calculation-engine**: Use the base layout for scenario comparisons, reducing duplication.
- **codex/configure-docker-compose-for-windows-and-ubuntu**: Ensure Docker Compose works consistently on Windows and Ubuntu.
- **codex/fix-dynamic-display-of-insurance-row**: Fix dynamic percentage display for fee inputs in the insurance row.
- **codex/fix-dynamic-display-of-insurance-row-3s56yp**: Sync the dynamic insurance row fix with `main`.
- **codex/fix-javascript-errors-in-calculator.js**: Handle canvas fallback in calculator labels to avoid script errors.
- **codex/fix-javascript-network-processing-errors**: Correct fee display variable names to prevent network processing errors.
- **codex/fix-title-insurance-summary-display**: Treat blank fee inputs as zero to fix insurance summary display.
- **codex/hide-buttons-and-remove-payment-schedule**: Hide charts and schedules for bridge retained interest loans.
- **codex/enhance-loan-details-modal-formatting**: Improve gross-to-net breakdown formatting in the loan details modal.
- **codex/allow-decimal-input-in-calculator.html**: Permit decimal inputs across calculator fields for precision.
- **codex/fix-calculation-for-gross-amount-percentage**: Correct percentage-based gross amount calculations.
- **codex/calculate-interest-for-bridge-and-term-loan**: Adopt yearly-to-daily interest methodology for both loan types.
- **codex/implement-interest-calculation-for-loans**: Introduce daily interest calculations for bridge and term loans.
- **codex/fix-calculation-for-15-months**: Add calendar-based term day calculations for fifteen-month loans.
- **codex/implement-exact-month-calculation-for-loan-repayments**: Adjust monthly net-to-gross factor for serviced loan repayment plans.
- **codex/ensure-repayment-options-use-exact-days**: Ensure service-only schedules rely on exact calendar day counts.
- **codex/revert-last-change**: Revert the merge of `codex/ensure-repayment-options-use-exact-days` after issues arose.
- **codex/fix-interest-calculation-for-repayment-types**: Use actual day counts for bridge non-retained interest computations.
- **codex/fix-total-interest-calculation-discrepancy**: Force daily calculations for service-only interest schedules.
- **codex/fix-calculate-button-functionality**: Recalculate outputs whenever interest type changes, ensuring accuracy.
- **codex/amend-payment-schedule-for-interest-serviced-loan**: Include detailed period dates for serviced loans in schedules.
- **codex/fix-detailed-payment-schedule-data-population**: Include period-level data for service-only schedules with local interest calc.
- **codex/adjust-monthly-interest-calculation-in-summary**: Correct monthly interest summaries for service-only loans.
- **codex/fix-javascript-error-for-interest-calculations**: Resolve end-date recalculation bugs and day-count issues.
- **codex/amend-loan-payment-schedule-details**: Refine service loan schedule details for better clarity.
- **codex/fix-undefined-values-in-payment-schedule-report**: Resolve undefined values in payment schedules and net/gross calculations.
- **codex/fix-loan-editing-fields-update**: Populate edit form fields properly to avoid stale data.
- **codex/fix-loan-edit-input-value-updates**: Ensure edit mode populates input values and toggle states accurately.
- **codex/fix-loan-save-behavior**: Allow existing loans to be updated while preserving data integrity.
- **codex/add-dynamic-interest-calculation-logic**: Add shared logic for dynamic periodic interest.
- **codex/add-dynamic-interest-calculation-for-loans**: Compute periodic interest by payment frequency across loan types.

