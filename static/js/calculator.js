/**
 * Novellus Loan Calculator JavaScript - Enhanced Version
 * Handles loan summary display with comprehensive visualizations
 */

class LoanCalculator {
    constructor() {
        this.form = document.getElementById('calculatorForm');
        this.resultsSection = document.getElementById('resultsSection');
        this.noResults = document.getElementById('noResults');
        this.currentResults = null;
        this.charts = {}; // Store chart instances for proper cleanup
        this.chartGenerationInProgress = false; // Prevent concurrent chart generation
        
        // Only initialize if required elements exist
        if (this.form) {
            this.initializeEventListeners();
            this.setDefaultDate();
            this.updateCurrencySymbols();
            this.updateGBPQuoteButtonVisibility();
            // Initialize dynamic dropdowns and sections on page load
            this.updateRepaymentOptions();
            this.updateAdditionalParams();
            // Calculate initial end date based on default values
            setTimeout(() => calculateEndDate(), 100);
            // Check for existing calculation data and display charts on page load
            setTimeout(() => this.loadExistingResults(), 500);
            // Update percentage displays on page load
            setTimeout(() => this.updatePercentageDisplays(), 100);
            // Initialize currency theme based on default currency
            setTimeout(() => {
                const currencySelect = document.getElementById('currency');
                if (currencySelect && window.currencyThemeManager) {
                    const currentCurrency = currencySelect.value || 'GBP';
                    window.currencyThemeManager.updateTheme(currentCurrency);
                    console.log(`Initialized currency theme: ${currentCurrency}`);
                }
            }, 200);
        }
        
        // Make calculator instance globally accessible for theme updates
        window.loanCalculator = this;
    }

    initializeEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateLoan();
        });

        // Loan type and repayment option changes with error handling
        document.getElementById('loanType').addEventListener('change', () => {
            try {
                console.log('Loan type changed');
                this.updateRepaymentOptions();
                this.updateAdditionalParams();
            } catch (error) {
                console.error('Error updating loan type:', error);
            }
        });

        document.getElementById('repaymentOption').addEventListener('change', () => {
            try {
                console.log('Repayment option changed');
                this.updateAdditionalParams();
            } catch (error) {
                console.error('Error updating repayment option:', error);
            }
        });

        // Currency changes
        document.getElementById('currency').addEventListener('change', (e) => {
            const selectedCurrency = e.target.value;
            this.updateCurrencySymbols();
            this.updateGBPQuoteButtonVisibility();
            
            // Update currency theme
            if (window.currencyThemeManager) {
                window.currencyThemeManager.updateTheme(selectedCurrency);
            }
            
            // Regenerate charts with new colors if we have existing results
            if (this.currentResults) {
                setTimeout(() => {
                    this.generateCharts(this.currentResults);
                }, 100);
            }
            
            // Dispatch currency change event for other components
            document.dispatchEvent(new CustomEvent('currencyChanged', {
                detail: { currency: selectedCurrency }
            }));
            
            // If we have existing results, update the detailed payment schedule with new currency symbols
            if (this.currentResults && this.currentResults.detailed_payment_schedule) {
                this.displayDetailedPaymentSchedule(this.currentResults);
            }
        });

        // Amount input type toggles
        document.querySelectorAll('input[name="amount_input_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.toggleAmountInputSections();
            });
        });

        // Gross amount type toggles
        document.querySelectorAll('input[name="gross_amount_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.toggleGrossAmountInputs();
            });
        });

        // Rate input type toggles
        document.querySelectorAll('input[name="rate_input_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.toggleRateInputs();
            });
        });

        // Property value changes for percentage calculation
        document.getElementById('propertyValue').addEventListener('input', () => {
            this.updateGrossAmountFromPercentage();
        });

        document.getElementById('grossAmountPercentage').addEventListener('input', () => {
            this.updateGrossAmountFromPercentage();
        });

        // Start date changes - trigger automatic end date calculation
        document.getElementById('startDate').addEventListener('change', () => {
            calculateEndDate(); // Global function defined in calculator.html
        });

        // Loan term changes - trigger automatic end date calculation
        document.getElementById('loanTerm').addEventListener('change', () => {
            calculateEndDate(); // Global function defined in calculator.html
        });

        // End date changes - trigger automatic loan term recalculation
        document.getElementById('endDate').addEventListener('change', () => {
            recalculateLoanTerm(); // Global function defined in calculator.html
        });

        // Tranche mode toggles
        document.querySelectorAll('input[name="tranche_mode"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.toggleTrancheMode();
            });
        });

        // Update percentage displays when input values change
        const updatePercentageFields = ['arrangementFeeRate', 'titleInsuranceRate', 'annualRateValue', 'monthlyRateValue'];
        updatePercentageFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', () => {
                    this.updatePercentageDisplays();
                });
            }
        });

        // Update percentage displays when rate input type changes
        document.querySelectorAll('input[name="rate_input_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.updatePercentageDisplays();
            });
        });

        // Auto generate tranches button
        const generateButton = document.getElementById('generateTranches');
        if (generateButton) {
            generateButton.addEventListener('click', () => {
                this.generateTranches();
            });
        }

        // Manual tranche controls
        const increaseButton = document.getElementById('increaseTranches');
        const decreaseButton = document.getElementById('decreaseTranches');
        if (increaseButton) {
            increaseButton.addEventListener('click', () => {
                this.increaseTranches();
            });
        }
        if (decreaseButton) {
            decreaseButton.addEventListener('click', () => {
                this.decreaseTranches();
            });
        }

        // Initialize toggles on page load - ensure DOM is fully loaded
        setTimeout(() => {
            try {
                this.toggleAmountInputSections();
                this.toggleGrossAmountInputs();
                this.toggleRateInputs();
                this.updateRepaymentOptions();
                this.updateAdditionalParams();
                this.toggleTrancheMode();
            } catch (error) {
                console.error('Error during initialization:', error);
            }
        }, 100);
    }

    async calculateLoan(skipValidation = false) {
        console.log('Calculate button clicked');
        
        // Check loan name is provided and not empty (unless skipped for auto-calculation)
        if (!skipValidation) {
            const loanName = document.getElementById('loanName').value.trim();
            if (!loanName) {
                window.notifications.warning('Please enter a loan name before calculating.');
                document.getElementById('loanName').focus();
                return;
            }
        }
        
        const submitButton = this.form.querySelector('button[type="submit"]');
        
        // Show loading state
        submitButton.disabled = true;
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calculating...';
        
        try {
            const formData = this.collectFormData();
            console.log('Form data collected:', formData);
            
            const response = await fetch('/api/calculate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Calculation failed');
            }
            
            const results = await response.json();
            console.log('Results received:', results);
            
            // Validate that we have essential calculation results
            if (!results || typeof results !== 'object') {
                throw new Error('Invalid response format from server');
            }
            
            // Check for required fields for Development 2
            if (results.loan_type === 'development2') {
                if (!results.grossAmount && !results.gross_amount) {
                    throw new Error('Missing gross amount in Development 2 calculation result');
                }
            }
            
            this.currentResults = results;
            
            // Store results globally for download functions
            window.calculatorResults = results;
            
            // Show success notification if loan was auto-saved
            if (results.saved_loan_id && results.saved_loan_version) {
                const loanName = document.getElementById('loanName').value.trim();
                window.notifications.success(`Loan "${loanName}" automatically saved as version ${results.saved_loan_version}`);
            }
            
            this.displayResults(results);
            
        } catch (error) {
            console.error('Calculation error details:', {
                error: error,
                message: error.message,
                stack: error.stack,
                response: error.response
            });
            
            // Enhanced error message for Development 2
            let errorMessage = error.message;
            if (errorMessage.includes('Calculation failed')) {
                errorMessage = 'Calculation completed but there was an issue displaying results. Please try again.';
            }
            
            window.notifications.error(`Calculation failed: ${errorMessage}`);
        } finally {
            // Hide loading state
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fas fa-calculator me-2"></i>Calculate';
        }
    }

    collectFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        // Convert FormData to regular object
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Handle special cases for amount input
        const amountInputType = document.querySelector('input[name="amount_input_type"]:checked').value;
        data.amount_input_type = amountInputType;
        
        // Handle checkbox for daily rate calculation (unchecked checkboxes don't appear in FormData)
        const use360DaysCheckbox = document.getElementById('use360Days');
        data.use_360_days = use360DaysCheckbox ? use360DaysCheckbox.checked.toString() : 'false';
        
        if (amountInputType === 'gross') {
            const grossAmountType = document.querySelector('input[name="gross_amount_type"]:checked').value;
            data.gross_amount_type = grossAmountType;
            
            if (grossAmountType === 'percentage') {
                const propertyValue = parseFloat(data.property_value) || 0;
                const percentage = parseFloat(data.gross_amount_percentage) || 0;
                data.gross_amount = propertyValue * (percentage / 100);
            } else {
                data.gross_amount = data.gross_amount || 0;
            }
        }
        
        // Handle rate input type
        const rateInputType = document.querySelector('input[name="rate_input_type"]:checked').value;
        data.rate_input_type = rateInputType;
        
        // Handle interest type
        data.interest_type = document.getElementById('interestType').value;
        
        // Handle end date if provided
        const endDateInput = document.getElementById('endDate');
        if (endDateInput && endDateInput.value) {
            data.end_date = endDateInput.value;
        }
        
        // Handle tranches for development loans (both development and development2)
        if (data.loan_type === 'development' || data.loan_type === 'development2') {
            const tranches = [];
            const trancheContainer = document.getElementById('tranchesContainer');
            
            if (trancheContainer) {
                const trancheInputs = trancheContainer.querySelectorAll('.tranche-item');
                
                trancheInputs.forEach((trancheItem, index) => {
                    const amountInput = trancheItem.querySelector('.tranche-amount');
                    const dateInput = trancheItem.querySelector('.tranche-date');
                    const rateInput = trancheItem.querySelector('.tranche-rate');
                    const descriptionInput = trancheItem.querySelector('.tranche-description');
                    
                    if (amountInput && dateInput && parseFloat(amountInput.value) > 0) {
                        tranches.push({
                            amount: parseFloat(amountInput.value),
                            date: dateInput.value,
                            rate: parseFloat(rateInput.value) || parseFloat(data.annual_rate) || 12,
                            description: descriptionInput.value || `Tranche ${index + 1}`
                        });
                    }
                });
            }
            
            if (tranches.length > 0) {
                data.tranches = tranches;
            }
        }
        
        return data;
    }

    displayResults(results) {
        try {
            console.log('Starting displayResults for loan type:', results.loan_type, 'with grossAmount:', results.grossAmount);
            
            // Store results for potential re-display with currency changes
            this.currentResults = results;
            
            const currency = this.getCurrencySymbol(results.currency);
            
            // Show results section and hide no results message
            if (this.resultsSection) {
                this.resultsSection.style.display = 'block';
            }
            if (this.noResults) {
                this.noResults.style.display = 'none';
            }
            
            // Show download options
            const downloadOptionsCard = document.getElementById('downloadOptionsCard');
            if (downloadOptionsCard) {
                downloadOptionsCard.style.display = 'block';
            }
            
            // Update calculation results table
            console.log('Updating calculation results...');
            this.updateCalculationResults(results);
            
            // Generate charts based on loan type and results
            console.log('Generating charts...');
            this.generateCharts(results);
            
            // Update percentage displays after results are shown
            console.log('Updating percentage displays...');
            this.updatePercentageDisplays();
            
            // Scroll to results
            if (this.resultsSection) {
                this.resultsSection.scrollIntoView({ behavior: 'smooth' });
            }
            
            console.log('displayResults completed successfully');
        } catch (error) {
            console.error('Error in displayResults:', error);
            throw error;  // Re-throw so the main catch block can handle it
        }
        
        // Enable save button after successful calculation
        const saveLoanBtn = document.getElementById('saveLoanBtn');
        if (saveLoanBtn) {
            saveLoanBtn.disabled = false;
            saveLoanBtn.classList.remove('btn-secondary');
            saveLoanBtn.classList.add('btn-success');
            console.log('Save button enabled after successful calculation');
        }
    }

    updateCalculationResults(results) {
        const currency = this.getCurrencySymbol(results.currency);
        
        // Update currency theme based on selected currency
        if (window.currencyThemeManager) {
            const currencyCode = results.currency || 'GBP';
            window.currencyThemeManager.updateTheme(currencyCode);
        }
        
        // Update all currency symbols on the page to match selected currency
        this.updateCurrencySymbols();
        
        // Get all the result elements
        const grossAmountEl = document.getElementById('grossAmountResult');
        const startDateEl = document.getElementById('startDateResult');
        const endDateEl = document.getElementById('endDateResult');
        const loanTermEl = document.getElementById('loanTermResult');
        const loanTermDaysEl = document.getElementById('loanTermDaysResult');
        const arrangementFeeEl = document.getElementById('arrangementFeeResult');
        const legalCostsEl = document.getElementById('legalCostsResult');
        const siteVisitFeeEl = document.getElementById('siteVisitFeeResult');
        const titleInsuranceEl = document.getElementById('titleInsuranceResult');
        const totalInterestEl = document.getElementById('totalInterestResult');
        const netDay1AdvanceEl = document.getElementById('netDay1AdvanceResult');
        const ltvRatioEl = document.getElementById('ltvRatioResult');
        const totalNetAdvanceEl = document.getElementById('totalNetAdvanceResult');
        const valuationEl = document.getElementById('propertyValueResult');
        const endLTVEl = document.getElementById('endLTVResult');
        
        // Extract values from results
        const grossAmount = results.grossAmount || 0;
        const propertyValue = results.propertyValue || 0;
        const startDate = results.start_date || results.startDate || '';
        const endDate = results.end_date || results.endDate || '';
        const loanTerm = results.loanTerm || results.loan_term || 0;
        const loanTermDays = results.loanTermDays || results.loan_term_days || 0;
        const arrangementFee = results.arrangementFee || 0;
        const legalCosts = results.legalCosts || results.legalFees || 0;
        const siteVisitFee = results.siteVisitFee || 0;
        const titleInsurance = results.titleInsurance || 0;
        const totalInterest = results.totalInterest || 0;
        const day1Advance = results.day1Advance || results.netDay1Advance || 0;
        
        // Update the display elements
        if (valuationEl) valuationEl.textContent = propertyValue.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (grossAmountEl) grossAmountEl.textContent = grossAmount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (startDateEl) startDateEl.textContent = this.formatDate(startDate);
        if (endDateEl) endDateEl.textContent = this.formatDate(endDate);
        if (loanTermEl) loanTermEl.textContent = loanTerm.toFixed(2);
        if (loanTermDaysEl) loanTermDaysEl.textContent = loanTermDays;
        if (arrangementFeeEl) arrangementFeeEl.textContent = arrangementFee.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (legalCostsEl) legalCostsEl.textContent = legalCosts.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (siteVisitFeeEl) siteVisitFeeEl.textContent = siteVisitFee.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (titleInsuranceEl) titleInsuranceEl.textContent = titleInsurance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (totalInterestEl) totalInterestEl.textContent = totalInterest.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        // For development loans, show user input Day 1 advance for display purposes
        if (netDay1AdvanceEl) {
            // Priority: Use userInputDay1Advance from backend, then user form input, then calculated
            const userInputFromBackend = results.userInputDay1Advance;
            const day1AdvanceInput = document.querySelector('input[name="day1_advance"]');
            const userInputFromForm = day1AdvanceInput ? parseFloat(day1AdvanceInput.value) || 0 : 0;
            
            // Use user input value for display, fallback to calculated if no user input
            const displayDay1Advance = userInputFromBackend || userInputFromForm || results.day1NetAdvance || results.day1Advance || day1Advance || 0;
            netDay1AdvanceEl.textContent = displayDay1Advance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
        
        // Calculate and display LTV ratio (use backend values if available)
        if (ltvRatioEl && propertyValue > 0) {
            const ltvRatio = results.ltv || (grossAmount / propertyValue * 100);
            ltvRatioEl.textContent = ltvRatio.toFixed(2) + '%';
        } else if (ltvRatioEl) {
            ltvRatioEl.textContent = '0.00%';
        }
        
        // Display End LTV based on closing balance of last month from payment schedule
        if (endLTVEl && propertyValue > 0) {
            let endLTV = 0;
            
            // Try to get the closing balance from the last month of the payment schedule for final remaining balance
            if (results.detailed_payment_schedule && results.detailed_payment_schedule.length > 0) {
                const lastScheduleEntry = results.detailed_payment_schedule[results.detailed_payment_schedule.length - 1];
                const closingBalanceRaw = lastScheduleEntry.closing_balance;
                
                // Handle both string and numeric closing balance values
                let closingBalanceValue = 0;
                console.log('End LTV closing balance debug:', {
                    type: typeof closingBalanceRaw,
                    value: closingBalanceRaw
                });
                
                if (typeof closingBalanceRaw === 'number') {
                    closingBalanceValue = closingBalanceRaw;
                } else if (typeof closingBalanceRaw === 'string') {
                    // Extract numeric value from closing balance string (remove currency symbols and commas)
                    const closingBalanceMatch = closingBalanceRaw.match(/[\d,]+\.?\d*/);
                    if (closingBalanceMatch) {
                        closingBalanceValue = parseFloat(closingBalanceMatch[0].replace(/,/g, ''));
                    }
                } else {
                    console.warn('End LTV: Unexpected closing balance type:', typeof closingBalanceRaw, closingBalanceRaw);
                }
                
                if (closingBalanceValue > 0) {
                    endLTV = (closingBalanceValue / propertyValue) * 100;
                    console.log(`End LTV calculation: Final balance £${closingBalanceValue.toLocaleString()} / Property value £${propertyValue.toLocaleString()} = ${endLTV.toFixed(2)}%`);
                }
            } else {
                // Fallback to gross amount if no payment schedule available
                endLTV = (grossAmount / propertyValue) * 100;
                console.log(`End LTV fallback: Gross amount £${grossAmount.toLocaleString()} / Property value £${propertyValue.toLocaleString()} = ${endLTV.toFixed(2)}%`);
            }
            
            endLTVEl.textContent = endLTV.toFixed(2) + '%';
        } else if (endLTVEl) {
            endLTVEl.textContent = '0.00%';
        }
        
        // Total Net Advance
        if (totalNetAdvanceEl) {
            // Use the corrected totalNetAdvance from the backend (Gross - Arrangement Fee - Legal Costs)
            const totalNetAdvance = results.totalNetAdvance || 0;
            totalNetAdvanceEl.textContent = totalNetAdvance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
        
        // Get loan type and repayment option for multiple uses
        const loanType = document.getElementById('loanType').value;
        const repaymentOption = document.getElementById('repaymentOption').value;
        const paymentFrequency = document.querySelector('input[name="payment_frequency"]:checked')?.value || 'monthly';
        
        // Show interest-only total and savings if available (for flexible payment options)
        const interestOnlyTotalRow = document.getElementById('interestOnlyTotalRow');
        const interestOnlyTotalEl = document.getElementById('interestOnlyTotalResult');
        const interestSavingsRow = document.getElementById('interestSavingsRow');
        const interestSavingsEl = document.getElementById('interestSavingsResult');
        const savingsPercentageEl = document.getElementById('savingsPercentageResult');
        
        // Check if we should show interest savings comparison
        const shouldShowInterestComparison = (
            (results.interestSavings !== undefined && results.interestSavings > 0) ||
            (results.interestOnlyTotal !== undefined && results.interestOnlyTotal > 0) ||
            (repaymentOption === 'service_and_capital' || repaymentOption === 'capital_payment_only' || repaymentOption === 'flexible_payment')
        );
        
        if (shouldShowInterestComparison) {
            // Show interest-only total row
            if (interestOnlyTotalRow) interestOnlyTotalRow.style.display = 'table-row';
            if (interestOnlyTotalEl) {
                const interestOnlyTotal = results.interestOnlyTotal || 0;
                interestOnlyTotalEl.textContent = interestOnlyTotal.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }
            
            // Show interest savings row only if there are actual savings
            const interestSavings = results.interestSavings || 0;
            if (interestSavings > 0 && interestSavingsRow) {
                interestSavingsRow.style.display = 'table-row';
                if (interestSavingsEl) {
                    interestSavingsEl.textContent = currency + interestSavings.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }
                if (savingsPercentageEl) {
                    const percentage = results.savingsPercentage || 0;
                    savingsPercentageEl.textContent = percentage.toFixed(1) + '% savings';
                }
            } else {
                // Hide savings row if no savings (e.g., for capital_payment_only where interest is retained)
                if (interestSavingsRow) interestSavingsRow.style.display = 'none';
            }
        } else {
            // Hide both rows if not applicable
            if (interestOnlyTotalRow) interestOnlyTotalRow.style.display = 'none';
            if (interestSavingsRow) interestSavingsRow.style.display = 'none';
        }
        
        // Show/hide periodic interest payment for term loans with service only
        const periodicInterestRow = document.getElementById('periodicInterestRow');
        const periodicInterestEl = document.getElementById('periodicInterestResult');
        const periodicInterestLabel = document.getElementById('periodicInterestLabel');
        
        console.log(`Periodic interest check: loanType=${loanType}, repaymentOption=${repaymentOption}, periodicInterest=${results.periodicInterest}`);
        if ((loanType === 'term' || loanType === 'bridge') && repaymentOption === 'service_only' && results.periodicInterest) {
            console.log('Showing periodic interest row');
            if (periodicInterestRow) periodicInterestRow.style.display = 'table-row';
            if (periodicInterestEl) {
                periodicInterestEl.textContent = results.periodicInterest.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }
            
            // Update label based on payment frequency
            if (periodicInterestLabel) {
                const label = paymentFrequency === 'quarterly' ? 'Quarterly Interest Payment' : 'Monthly Interest Payment';
                periodicInterestLabel.textContent = label;
            }
        } else {
            if (periodicInterestRow) periodicInterestRow.style.display = 'none';
        }
        
        // Display detailed payment schedule if available (for all loan types)
        this.displayDetailedPaymentSchedule(results);
        
        // Display tranche breakdown for development loans
        if (results.tranche_breakdown && results.tranche_breakdown.length > 0) {
            this.displayTrancheBreakdown(results.tranche_breakdown, currency);
        }
        
        // Update percentage displays with actual user input values
        this.updatePercentageDisplays();
    }

    displayDetailedPaymentSchedule(results) {
        const scheduleContainer = document.getElementById('detailedPaymentScheduleCard');
        const scheduleBody = document.getElementById('detailedPaymentScheduleBody');
        
        if (!scheduleContainer || !scheduleBody || !results.detailed_payment_schedule) {
            // Hide the schedule table if no data available
            if (scheduleContainer) {
                scheduleContainer.style.display = 'none';
            }
            return;
        }
        
        // Show the schedule table
        scheduleContainer.style.display = 'block';
        
        // Clear existing rows
        scheduleBody.innerHTML = '';
        
        // Get current currency symbol
        const currency = document.getElementById('currency').value;
        const currentSymbol = this.getCurrencySymbol(currency);
        
        // Populate rows from detailed payment schedule
        results.detailed_payment_schedule.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.style.border = '1px solid #000';
            tr.style.background = index % 2 === 0 ? '#f8f9fa' : 'white';
            
            // Replace currency symbols in the row data to match current selection
            const fixedRow = {
                payment_date: row.payment_date,
                opening_balance: String(row.opening_balance || '').replace(/[£€]/g, currentSymbol),
                tranche_release: String(row.tranche_release || '').replace(/[£€]/g, currentSymbol),
                interest_calculation: String(row.interest_calculation || '').replace(/[£€]/g, currentSymbol),
                interest_amount: String(row.interest_amount || '').replace(/[£€]/g, currentSymbol),
                principal_payment: String(row.principal_payment || '').replace(/[£€]/g, currentSymbol),
                total_payment: String(row.total_payment || '').replace(/[£€]/g, currentSymbol),
                closing_balance: String(row.closing_balance || '').replace(/[£€]/g, currentSymbol),
                balance_change: row.balance_change
            };
            
            // Debug log to check currency replacement
            if (index === 0) {
                console.log('Currency replacement debug:', {
                    currentSymbol: currentSymbol,
                    originalOpening: row.opening_balance,
                    fixedOpening: fixedRow.opening_balance,
                    originalInterest: row.interest_calculation,
                    fixedInterest: fixedRow.interest_calculation
                });
            }
            
            tr.innerHTML = `
                <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.payment_date}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.opening_balance}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.tranche_release}</td>
                <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_calculation}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_amount}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.principal_payment}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.total_payment}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.closing_balance}</td>
                <td class="py-1 px-2 text-center" style="color: #000; font-size: 0.875rem;">${fixedRow.balance_change}</td>
            `;
            
            scheduleBody.appendChild(tr);
        });
        
        console.log('Detailed payment schedule displayed with', results.detailed_payment_schedule.length, 'rows');
    }

    formatDate(dateString) {
        if (!dateString) return '00/01/1900';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-GB');
        } catch (e) {
            return dateString;
        }
    }

    getCurrencySymbol(currency) {
        return currency === 'EUR' ? '€' : '£';
    }

    updateGBPQuoteButtonVisibility() {
        const currency = document.getElementById('currency').value;
        const gbpQuoteBtn = document.getElementById('downloadGBPBtn');
        
        if (gbpQuoteBtn) {
            if (currency === 'GBP') {
                gbpQuoteBtn.style.display = 'inline-block';
            } else {
                gbpQuoteBtn.style.display = 'none';
            }
        }
    }

    showError(message) {
        alert('Error: ' + message);
    }

    // All other UI helper methods remain the same...
    updateRepaymentOptions() {
        try {
            const loanTypeElement = document.getElementById('loanType');
            const repaymentSelect = document.getElementById('repaymentOption');
            
            if (!loanTypeElement || !repaymentSelect) {
                console.warn('Loan type or repayment option elements not found');
                return;
            }
            
            const loanType = loanTypeElement.value;
            console.log('Updating repayment options for loan type:', loanType);
            
            // Store current selection to preserve it if possible
            const currentValue = repaymentSelect.value;
            
            // Clear existing options
            repaymentSelect.innerHTML = '';
            
            let options = [];
            
            if (loanType === 'bridge') {
                options = [
                    { value: 'none', text: 'Retained Interest (Interest Only)' },
                    { value: 'service_only', text: 'Service Only (Interest Payments)' },
                    { value: 'service_and_capital', text: 'Service + Capital (Principal & Interest)' },
                    { value: 'capital_payment_only', text: 'Capital Payment Only (Interest Retained)' },
                    { value: 'flexible_payment', text: 'Flexible Payment Schedule' }
                ];
            } else if (loanType === 'term') {
                options = [
                    { value: 'none', text: 'Retained Interest (Interest Only)' },
                    { value: 'service_only', text: 'Service Only (Interest Payments)' },
                    { value: 'service_and_capital', text: 'Service + Capital (Principal & Interest)' },
                    { value: 'capital_payment_only', text: 'Capital Payment Only (Interest Retained)' },
                    { value: 'flexible_payment', text: 'Flexible Payment Schedule' }
                ];
            } else if (loanType === 'development') {
                options = [
                    { value: 'none', text: 'Retained Interest (Interest Only)' }
                ];
            } else if (loanType === 'development2') {
                options = [
                    { value: 'none', text: 'Retained Interest (Excel Goal Seek)' }
                ];
            }
            
            // Add options to select
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option.value;
                optionElement.textContent = option.text;
                repaymentSelect.appendChild(optionElement);
            });
            
            // Try to preserve the previous selection if it exists in new options
            const validOption = options.find(opt => opt.value === currentValue);
            if (validOption) {
                repaymentSelect.value = currentValue;
            } else {
                repaymentSelect.value = options[0].value; // Default to first option
            }
            
            console.log('Repayment options updated successfully');
        } catch (error) {
            console.error('Error in updateRepaymentOptions:', error);
        }
    }

    updateAdditionalParams() {
        try {
            const loanTypeElement = document.getElementById('loanType');
            const repaymentOptionElement = document.getElementById('repaymentOption');
            
            if (!loanTypeElement || !repaymentOptionElement) {
                console.warn('Required elements not found for updateAdditionalParams');
                return;
            }
            
            const loanType = loanTypeElement.value;
            const repaymentOption = repaymentOptionElement.value;
            
            console.log('Updating additional params for:', loanType, repaymentOption);
            
            // Show/hide sections based on loan type and repayment option
            const additionalParamsContainer = document.getElementById('additionalParams');
            const paymentTimingSection = document.getElementById('paymentTimingSection');
            const trancheSection = document.getElementById('developmentTrancheSection');
            const day1AdvanceSection = document.getElementById('day1AdvanceSection');
            
            let showAdditionalParams = false;
            
            if (paymentTimingSection) {
                // Show payment timing for service only, capital+interest, capital payment only, and flexible payment options
                if (repaymentOption === 'service_only' || repaymentOption === 'service_and_capital' || repaymentOption === 'capital_payment_only' || repaymentOption === 'flexible_payment') {
                    paymentTimingSection.style.display = 'block';
                    showAdditionalParams = true;
                } else {
                    paymentTimingSection.style.display = 'none';
                }
            }
            
            // Show capital repayment section for service + capital and capital payment only options
            const capitalRepaymentSection = document.getElementById('capitalRepaymentSection');
            if (capitalRepaymentSection) {
                if (repaymentOption === 'service_and_capital' || repaymentOption === 'capital_payment_only') {
                    capitalRepaymentSection.style.display = 'block';
                    showAdditionalParams = true;
                } else {
                    capitalRepaymentSection.style.display = 'none';
                }
            }
            
            // Show flexible payment section for flexible payment option
            const flexiblePaymentSection = document.getElementById('flexiblePaymentSection');
            if (flexiblePaymentSection) {
                if (repaymentOption === 'flexible_payment') {
                    flexiblePaymentSection.style.display = 'block';
                    showAdditionalParams = true;
                } else {
                    flexiblePaymentSection.style.display = 'none';
                }
            }
            
            if (trancheSection) {
                // Show tranche section only for development loans
                if (loanType === 'development' || loanType === 'development2') {
                    trancheSection.style.display = 'block';
                } else {
                    trancheSection.style.display = 'none';
                }
            }
            
            if (day1AdvanceSection) {
                // Show Day 1 advance section only for development loans
                if (loanType === 'development' || loanType === 'development2') {
                    day1AdvanceSection.style.display = 'block';
                } else {
                    day1AdvanceSection.style.display = 'none';
                }
            }
            
            // Show/hide amount input section based on loan type
            const netAmountSection = document.getElementById('netAmountSection');
            const grossAmountSection = document.getElementById('grossAmountSection');
            
            if (loanType === 'development' || loanType === 'development2') {
                // Development loans default to net amount input
                document.getElementById('netAmount').checked = true;
                document.getElementById('grossAmount').checked = false;
                if (netAmountSection) netAmountSection.style.display = 'block';
                if (grossAmountSection) grossAmountSection.style.display = 'none';
                
                // Set interest calculation type to compound daily for development loans
                const interestTypeSelect = document.getElementById('interestType');
                if (interestTypeSelect) {
                    interestTypeSelect.value = 'compound_daily';
                    interestTypeSelect.disabled = true;
                }
            } else {
                // Bridge and term loans default to gross amount input
                document.getElementById('grossAmount').checked = true;
                document.getElementById('netAmount').checked = false;
                if (grossAmountSection) grossAmountSection.style.display = 'block';
                if (netAmountSection) netAmountSection.style.display = 'none';
                
                // Enable interest calculation type selection for non-development loans
                const interestTypeSelect = document.getElementById('interestType');
                if (interestTypeSelect) {
                    interestTypeSelect.disabled = false;
                }
            }
            
            // Show/hide additional params container
            if (additionalParamsContainer) {
                if (showAdditionalParams || loanType === 'development' || loanType === 'development2') {
                    additionalParamsContainer.style.display = 'block';
                } else {
                    additionalParamsContainer.style.display = 'none';
                }
            }
            
            console.log('Additional params updated successfully');
        } catch (error) {
            console.error('Error in updateAdditionalParams:', error);
        }
    }

    updateCurrencySymbols() {
        const currency = document.getElementById('currency').value;
        const symbol = this.getCurrencySymbol(currency);
        
        // Update all currency symbols on the page
        document.querySelectorAll('.currency-symbol').forEach(el => {
            el.textContent = symbol;
        });
    }

    toggleAmountInputSections() {
        const amountInputType = document.querySelector('input[name="amount_input_type"]:checked').value;
        const netAmountSection = document.getElementById('netAmountSection');
        const grossAmountSection = document.getElementById('grossAmountSection');
        
        if (netAmountSection && grossAmountSection) {
            if (amountInputType === 'net') {
                netAmountSection.style.display = 'block';
                grossAmountSection.style.display = 'none';
            } else {
                netAmountSection.style.display = 'none';
                grossAmountSection.style.display = 'block';
                this.toggleGrossAmountInputs();
            }
        }
    }

    toggleGrossAmountInputs() {
        const grossAmountTypeRadio = document.querySelector('input[name="gross_amount_type"]:checked');
        if (!grossAmountTypeRadio) return;
        
        const grossAmountType = grossAmountTypeRadio.value;
        const grossFixedInput = document.getElementById('grossFixedInput');
        const grossPercentageInput = document.getElementById('grossPercentageInput');
        
        console.log('Toggle gross amount inputs:', grossAmountType);
        
        if (grossFixedInput && grossPercentageInput) {
            if (grossAmountType === 'fixed') {
                grossFixedInput.style.setProperty('display', 'flex', 'important');
                grossPercentageInput.style.setProperty('display', 'none', 'important');
                console.log('Showing fixed input, hiding percentage input');
            } else {
                grossFixedInput.style.setProperty('display', 'none', 'important');
                grossPercentageInput.style.setProperty('display', 'flex', 'important');
                console.log('Hiding fixed input, showing percentage input');
                this.updateGrossAmountFromPercentage();
            }
        }
    }

    toggleRateInputs() {
        const rateInputTypeRadio = document.querySelector('input[name="rate_input_type"]:checked');
        if (!rateInputTypeRadio) return;
        
        const rateInputType = rateInputTypeRadio.value;
        const monthlyRateInput = document.getElementById('monthlyRateInput');
        const annualRateInput = document.getElementById('annualRateInput');
        
        console.log('Toggle rate inputs:', rateInputType);
        
        if (monthlyRateInput && annualRateInput) {
            if (rateInputType === 'monthly') {
                monthlyRateInput.style.setProperty('display', 'flex', 'important');
                annualRateInput.style.setProperty('display', 'none', 'important');
                console.log('Showing monthly input, hiding annual input');
            } else {
                monthlyRateInput.style.setProperty('display', 'none', 'important');
                annualRateInput.style.setProperty('display', 'flex', 'important');
                console.log('Hiding monthly input, showing annual input');
            }
        }
    }

    updateGrossAmountFromPercentage() {
        const grossAmountType = document.querySelector('input[name="gross_amount_type"]:checked');
        if (grossAmountType && grossAmountType.value === 'percentage') {
            const propertyValue = parseFloat(document.getElementById('propertyValue').value) || 0;
            const percentage = parseFloat(document.getElementById('grossAmountPercentage').value) || 0;
            const grossAmount = propertyValue * (percentage / 100);
            
            // Update a hidden field or display for reference
            // This will be used in form submission
        }
    }

    setDefaultDate() {
        const startDateInput = document.getElementById('startDate');
        const autoStartDateInput = document.getElementById('autoStartDate');
        const today = new Date().toISOString().split('T')[0];
        
        if (startDateInput && !startDateInput.value) {
            startDateInput.value = today;
        }
        
        if (autoStartDateInput && !autoStartDateInput.value) {
            autoStartDateInput.value = today;
        }
    }

    toggleTrancheMode() {
        const manualMode = document.getElementById('manual_tranches');
        const autoSettings = document.getElementById('autoTrancheSettings');
        const manualControls = document.getElementById('manualTrancheControls');
        const tranchesContainer = document.getElementById('tranchesContainer');

        if (manualMode && manualMode.checked) {
            // Show manual controls
            if (autoSettings) autoSettings.style.display = 'none';
            if (manualControls) manualControls.style.display = 'flex';
            if (tranchesContainer) tranchesContainer.style.display = 'block';
        } else {
            // Show auto generation settings
            if (autoSettings) autoSettings.style.display = 'block';
            if (manualControls) manualControls.style.display = 'none';
            if (tranchesContainer) tranchesContainer.style.display = 'none';
        }
    }

    generateTranches() {
        try {
            console.log('Generate tranches button clicked');
            
            // Get form values - with fallback to form elements
            let totalAmount = parseFloat(document.getElementById('autoTotalAmount')?.value) || 0;
            let startDate = document.getElementById('autoStartDate')?.value;
            let loanPeriod = parseInt(document.getElementById('autoLoanPeriod')?.value) || 12;
            let interestRate = parseFloat(document.getElementById('autoInterestRate')?.value) || 12;
            let trancheCount = parseInt(document.getElementById('autoTrancheCount')?.value) || 6;
            
            // Fallback to main form values if auto fields don't exist
            if (totalAmount === 0) {
                const netAmountInput = document.getElementById('netAmountInput');
                totalAmount = parseFloat(netAmountInput?.value) || 0;
                console.log('Using net amount from main form:', totalAmount);
            }
            
            if (!startDate) {
                const startDateInput = document.getElementById('startDate');
                startDate = startDateInput?.value;
                console.log('Using start date from main form:', startDate);
            }
            
            if (loanPeriod === 12) {
                const loanTermInput = document.getElementById('loanTerm');
                loanPeriod = parseInt(loanTermInput?.value) || 12;
                console.log('Using loan term from main form:', loanPeriod);
            }
            
            if (interestRate === 12) {
                const annualRateInput = document.getElementById('annualRateValue');
                interestRate = parseFloat(annualRateInput?.value) || 12;
                console.log('Using interest rate from main form:', interestRate);
            }

            console.log('Tranche generation parameters:', {
                totalAmount,
                startDate,
                loanPeriod,
                interestRate,
                trancheCount
            });

            if (totalAmount <= 0) {
                alert('Please enter a valid total loan amount');
                return;
            }

            if (!startDate) {
                alert('Please select a start date');
                return;
            }

            // Calculate equal tranche amounts
            const trancheAmount = totalAmount / trancheCount;
            console.log('Calculated tranche amount:', trancheAmount);

            // Clear existing tranches
            this.clearTranches();

            // Set tranche count
            const trancheCountElement = document.getElementById('trancheCount');
            if (trancheCountElement) {
                trancheCountElement.textContent = trancheCount;
            }

            // Generate tranche dates (monthly intervals)
            const start = new Date(startDate);
            const monthInterval = Math.max(1, Math.floor(loanPeriod / trancheCount));

            console.log('Generating', trancheCount, 'tranches with', monthInterval, 'month intervals');

            // Create tranches
            for (let i = 0; i < trancheCount; i++) {
                const releaseDate = new Date(start);
                releaseDate.setMonth(releaseDate.getMonth() + (i * monthInterval));
                
                console.log(`Creating tranche ${i + 1}:`, {
                    amount: trancheAmount,
                    date: releaseDate.toISOString().split('T')[0],
                    rate: interestRate
                });
                
                this.createTrancheItem(i + 1, trancheAmount, releaseDate.toISOString().split('T')[0], interestRate, `Tranche ${i + 1}`);
            }

            // Switch to manual mode to show generated tranches
            const manualRadio = document.getElementById('manual_tranches');
            if (manualRadio) {
                manualRadio.checked = true;
                this.toggleTrancheMode();
                console.log('Switched to manual tranche mode');
            } else {
                console.error('Could not find manual_tranches radio button');
            }
            
            console.log('Tranche generation completed successfully');
            
        } catch (error) {
            console.error('Error in generateTranches:', error);
            alert('Error generating tranches: ' + error.message);
        }
    }

    increaseTranches() {
        const countElement = document.getElementById('trancheCount');
        const currentCount = parseInt(countElement.textContent);
        const newCount = currentCount + 1;
        
        if (newCount <= 20) {
            countElement.textContent = newCount;
            this.createTrancheItem(newCount, 0, '', 12, `Tranche ${newCount}`);
        }
    }

    decreaseTranches() {
        const countElement = document.getElementById('trancheCount');
        const currentCount = parseInt(countElement.textContent);
        
        if (currentCount > 1) {
            const newCount = currentCount - 1;
            countElement.textContent = newCount;
            
            // Remove the last tranche
            const container = document.getElementById('tranchesContainer');
            const lastTranche = container.querySelector(`[data-tranche="${currentCount}"]`);
            if (lastTranche) {
                lastTranche.remove();
            }
        }
    }

    clearTranches() {
        const container = document.getElementById('tranchesContainer');
        if (container) {
            container.innerHTML = '';
        }
    }

    createTrancheItem(number, amount = 0, date = '', rate = 12, description = '') {
        const container = document.getElementById('tranchesContainer');
        if (!container) {
            console.error('Could not find tranchesContainer element');
            return;
        }

        console.log(`Creating tranche item ${number} in container`, container);

        const trancheHtml = `
            <div class="tranche-item mb-3" data-tranche="${number}">
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Tranche ${number}</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">Tranche Amount</label>
                                <div class="input-group">
                                    <span class="input-group-text currency-symbol">£</span>
                                    <input type="number" class="form-control tranche-amount" 
                                           name="tranche_amounts[]" min="0" step="0.0001" 
                                           value="${amount}" placeholder="0">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Release Date</label>
                                <input type="date" class="form-control tranche-date" 
                                       name="tranche_dates[]" value="${date}">
                            </div>
                        </div>
                        <div class="row mt-2">
                            <div class="col-md-6">
                                <label class="form-label">Interest Rate (%)</label>
                                <input type="number" class="form-control tranche-rate" 
                                       name="tranche_rates[]" min="0" max="50" step="0.0001" 
                                       value="${rate}" placeholder="Annual rate">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Description</label>
                                <input type="text" class="form-control tranche-description" 
                                       name="tranche_descriptions[]" value="${description}" 
                                       placeholder="e.g., Land Purchase">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', trancheHtml);
        console.log(`Tranche item ${number} created successfully`);
        
        // Make sure the container is visible after adding content
        container.style.display = 'block';
    }

    // Additional helper methods for form handling
    toggleAmountInputSections() {
        const grossSection = document.getElementById('grossAmountSection');
        const netSection = document.getElementById('netAmountSection');
        const grossRadio = document.getElementById('grossAmount');
        const netRadio = document.getElementById('netAmount');
        
        if (grossRadio && grossRadio.checked && grossSection) {
            grossSection.style.display = 'block';
            console.log('Showing gross amount section');
        } else if (grossSection) {
            grossSection.style.display = 'none';
        }
        
        if (netRadio && netRadio.checked && netSection) {
            netSection.style.display = 'block';
            console.log('Showing net amount section');
        } else if (netSection) {
            netSection.style.display = 'none';
        }
    }
    
    toggleGrossAmountInputs() {
        const fixedInput = document.getElementById('grossFixedInput');
        const percentageInput = document.getElementById('grossPercentageInput');
        const fixedRadio = document.getElementById('grossFixed');
        
        if (fixedRadio && fixedRadio.checked) {
            console.log('Toggle gross amount inputs:', 'fixed');
            if (fixedInput) {
                fixedInput.style.setProperty('display', 'flex', 'important');
                console.log('Showing fixed input, hiding percentage input');
            }
            if (percentageInput) {
                percentageInput.style.setProperty('display', 'none', 'important');
            }
        } else {
            console.log('Toggle gross amount inputs:', 'percentage');
            if (fixedInput) {
                fixedInput.style.setProperty('display', 'none', 'important');
            }
            if (percentageInput) {
                percentageInput.style.setProperty('display', 'flex', 'important');
                console.log('Showing percentage input, hiding fixed input');
            }
        }
    }
    
    toggleRateInputs() {
        const monthlyInput = document.getElementById('monthlyRateInput');
        const annualInput = document.getElementById('annualRateInput');
        const monthlyRadio = document.getElementById('monthlyRate');
        
        if (monthlyRadio && monthlyRadio.checked) {
            console.log('Toggle rate inputs:', 'monthly');
            if (monthlyInput) {
                monthlyInput.style.setProperty('display', 'flex', 'important');
                console.log('Showing monthly input, hiding annual input');
            }
            if (annualInput) {
                annualInput.style.setProperty('display', 'none', 'important');
            }
        } else {
            console.log('Toggle rate inputs:', 'annual');
            if (monthlyInput) {
                monthlyInput.style.setProperty('display', 'none', 'important');
            }
            if (annualInput) {
                annualInput.style.setProperty('display', 'flex', 'important');
                console.log('Hiding monthly input, showing annual input');
            }
        }
    }

    toggleTrancheMode() {
        try {
            console.log('Toggling tranche mode');
            
            // Get correct element IDs from HTML
            const manualTrancheControls = document.getElementById('manualTrancheControls');
            const tranchesContainer = document.getElementById('tranchesContainer');
            const autoTrancheSettings = document.getElementById('autoTrancheSettings');
            const manualRadio = document.getElementById('manual_tranches'); // Note: underscore, not camelCase
            const autoRadio = document.getElementById('auto_tranches');
            
            console.log('Radio button states:', {
                manual: manualRadio?.checked,
                auto: autoRadio?.checked
            });
            
            if (manualRadio && manualRadio.checked) {
                console.log('Switching to manual tranche mode');
                // Show manual controls and tranche container
                if (manualTrancheControls) {
                    manualTrancheControls.style.display = 'flex';
                }
                if (tranchesContainer) {
                    tranchesContainer.style.display = 'block';
                }
                if (autoTrancheSettings) {
                    autoTrancheSettings.style.display = 'none';
                }
            } else if (autoRadio && autoRadio.checked) {
                console.log('Switching to auto tranche mode');
                // Show auto generation settings, hide manual controls
                if (manualTrancheControls) {
                    manualTrancheControls.style.display = 'none';
                }
                if (tranchesContainer) {
                    tranchesContainer.style.display = 'none';
                }
                if (autoTrancheSettings) {
                    autoTrancheSettings.style.display = 'block';
                }
            }
            
            console.log('Tranche mode toggle completed');
            
        } catch (error) {
            console.error('Error in toggleTrancheMode:', error);
        }
    }

    updateCurrencySymbols() {
        const currency = document.getElementById('currency').value;
        const symbol = currency === 'EUR' ? '€' : '£';
        document.querySelectorAll('.currency-symbol').forEach(el => {
            el.textContent = symbol;
        });
    }

    setDefaultDate() {
        const startDateInput = document.getElementById('startDate');
        if (startDateInput && !startDateInput.value) {
            const today = new Date().toISOString().split('T')[0];
            startDateInput.value = today;
            // Calculate end date after setting default start date
            setTimeout(() => calculateEndDate(), 50);
        }
    }

    updateGrossAmountFromPercentage() {
        const propertyValue = parseFloat(document.getElementById('propertyValue').value) || 0;
        const percentage = parseFloat(document.getElementById('grossAmountPercentage').value) || 0;
        const grossFixedInput = document.getElementById('grossAmountFixed');
        
        if (propertyValue > 0 && percentage > 0 && grossFixedInput) {
            const grossAmount = (propertyValue * percentage / 100).toFixed(2);
            grossFixedInput.value = grossAmount;
        }
    }

    // Clear existing charts before creating new ones
    clearExistingCharts() {
        try {
            // Destroy all stored chart instances
            Object.values(this.charts).forEach(chart => {
                if (chart && typeof chart.destroy === 'function') {
                    try {
                        chart.destroy();
                    } catch (e) {
                        console.log('Error destroying chart:', e);
                    }
                }
            });
            this.charts = {};
            
            // Also clear any Chart.js instances that might exist on canvas elements
            const canvasElements = document.querySelectorAll('canvas[id*="Chart"]');
            canvasElements.forEach(canvas => {
                const chartInstance = Chart.getChart(canvas);
                if (chartInstance) {
                    try {
                        chartInstance.destroy();
                    } catch (e) {
                        console.log('Error destroying canvas chart:', e);
                    }
                }
            });
        } catch (error) {
            console.log('Error in clearExistingCharts:', error);
        }
    }

    displayTrancheBreakdown(trancheData, currency) {
        console.log('Displaying tranche breakdown:', trancheData);
        
        // Find or create tranche breakdown table container
        let trancheContainer = document.getElementById('trancheBreakdownContainer');
        if (!trancheContainer) {
            // Create container if it doesn't exist
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) {
                trancheContainer = document.createElement('div');
                trancheContainer.id = 'trancheBreakdownContainer';
                trancheContainer.className = 'card mt-3';
                resultsSection.appendChild(trancheContainer);
            } else {
                console.error('Results section not found');
                return;
            }
        }
        
        // Build tranche breakdown table
        const tableHtml = `
            <div class="card-header">
                <h5 class="mb-0">Tranche Release Schedule</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Tranche</th>
                                <th>Release Date</th>
                                <th>Amount</th>
                                <th>Description</th>
                                <th>Cumulative</th>
                                <th>Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${trancheData.map(tranche => `
                                <tr>
                                    <td>${tranche.tranche_number}</td>
                                    <td>${this.formatDate(tranche.release_date)}</td>
                                    <td>${currency}${tranche.amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td>${tranche.description}</td>
                                    <td>${currency}${tranche.cumulative_amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td>${tranche.interest_rate.toFixed(2)}%</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        
        trancheContainer.innerHTML = tableHtml;
        trancheContainer.style.display = 'block';
    }

    // Load existing results from session storage or page data
    loadExistingResults() {
        console.log('Checking for existing calculation results on page load');
        
        // Check if loan summary table has data (indicating a previous calculation)
        const loanSummaryBody = document.getElementById('loanSummaryBody');
        if (loanSummaryBody && loanSummaryBody.children.length > 0) {
            console.log('Found existing loan summary data, attempting to display charts');
            
            // Extract payment schedule data from the detailed table
            const scheduleTable = document.getElementById('detailedPaymentScheduleBody');
            
            if (scheduleTable && scheduleTable.children.length > 0) {
                // Extract payment schedule data from the table
                const schedule = [];
                for (let row of scheduleTable.children) {
                    const cells = row.children;
                    if (cells.length >= 8) {
                        schedule.push({
                            payment_date: cells[0].textContent.trim(),
                            opening_balance: cells[1].textContent.trim(),
                            tranche_release: cells[2].textContent.trim(),
                            interest_calculation: cells[3].textContent.trim(),
                            interest_amount: cells[4].textContent.trim(),
                            principal_payment: cells[5].textContent.trim(),
                            total_payment: cells[6].textContent.trim(),
                            closing_balance: cells[7].textContent.trim(),
                            balance_change: cells[8] ? cells[8].textContent.trim() : ''
                        });
                    }
                }
                
                if (schedule.length > 0) {
                    // Extract additional data from loan summary table
                    const grossAmountRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Gross Amount'));
                    const totalInterestRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Total Interest'));
                    const arrangementFeeRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Arrangement Fee'));
                    const netAdvanceRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Net Advance'));
                    
                    // Create a mock results object for chart generation
                    const mockResults = {
                        detailed_payment_schedule: schedule,
                        loan_type: 'bridge', // Default assumption
                        currencySymbol: '£', // Default to GBP
                        grossAmount: grossAmountRow ? parseFloat(grossAmountRow.children[1].textContent.replace(/[£,]/g, '')) : 0,
                        totalInterest: totalInterestRow ? parseFloat(totalInterestRow.children[1].textContent.replace(/[£,]/g, '')) : 0,
                        arrangementFee: arrangementFeeRow ? parseFloat(arrangementFeeRow.children[1].textContent.replace(/[£,]/g, '')) : 0,
                        netAdvance: netAdvanceRow ? parseFloat(netAdvanceRow.children[1].textContent.replace(/[£,]/g, '')) : 0
                    };
                    
                    console.log('Creating charts from existing payment schedule data with', schedule.length, 'entries');
                    this.generateCharts(mockResults);
                }
            }
        }
    }

    // Load existing results from session storage or page data
    loadExistingResults() {
        console.log('Checking for existing calculation results on page load');
        
        // Check if loan summary table has data (indicating a previous calculation)
        const loanSummaryBody = document.getElementById('loanSummaryBody');
        if (loanSummaryBody && loanSummaryBody.children.length > 0) {
            console.log('Found existing loan summary data, attempting to display charts');
            
            // Try to extract payment schedule data from the detailed payment schedule table
            const scheduleTable = document.getElementById('detailedPaymentScheduleBody');
            
            if (scheduleTable && scheduleTable.children.length > 0) {
                console.log('Found existing payment schedule with', scheduleTable.children.length, 'rows');
                
                // Extract payment schedule data from the table
                const schedule = [];
                for (let row of scheduleTable.children) {
                    const cells = row.children;
                    if (cells.length >= 8) {
                        schedule.push({
                            payment_date: cells[0].textContent.trim(),
                            opening_balance: cells[1].textContent.trim(),
                            tranche_release: cells[2].textContent.trim(),
                            interest_calculation: cells[3].textContent.trim(),
                            interest_amount: cells[4].textContent.trim(),
                            principal_payment: cells[5].textContent.trim(),
                            total_payment: cells[6].textContent.trim(),
                            closing_balance: cells[7].textContent.trim(),
                            balance_change: cells[8] ? cells[8].textContent.trim() : ''
                        });
                    }
                }
                
                if (schedule.length > 0) {
                    // Extract additional data from loan summary table
                    const grossAmountRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Gross Amount'));
                    const totalInterestRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Total Interest'));
                    const arrangementFeeRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Arrangement Fee'));
                    const netAdvanceRow = Array.from(loanSummaryBody.children).find(row => 
                        row.children[0].textContent.includes('Net Advance'));
                    
                    // Get loan type from page data or default to bridge
                    const loanTypeInput = document.getElementById('loanType');
                    const loanType = loanTypeInput ? loanTypeInput.value : 'bridge';
                    
                    // Get currency symbol from page or default to GBP
                    const currencyInput = document.getElementById('currency');
                    const currency = currencyInput ? currencyInput.value : 'GBP';
                    const currencySymbol = currency === 'EUR' ? '€' : '£';
                    
                    // Create a results object for chart generation
                    const mockResults = {
                        detailed_payment_schedule: schedule,
                        loan_type: loanType,
                        currency: currency,
                        currencySymbol: currencySymbol,
                        currency_symbol: currencySymbol,
                        grossAmount: grossAmountRow ? parseFloat(grossAmountRow.children[1].textContent.replace(/[£€,]/g, '')) : 0,
                        totalInterest: totalInterestRow ? parseFloat(totalInterestRow.children[1].textContent.replace(/[£€,]/g, '')) : 0,
                        arrangementFee: arrangementFeeRow ? parseFloat(arrangementFeeRow.children[1].textContent.replace(/[£€,]/g, '')) : 0,
                        netAdvance: netAdvanceRow ? parseFloat(netAdvanceRow.children[1].textContent.replace(/[£€,]/g, '')) : 0
                    };
                    
                    console.log('Creating charts from existing payment schedule data with', schedule.length, 'entries');
                    console.log('Mock results object:', mockResults);
                    this.currentResults = mockResults;
                    this.generateCharts(mockResults);
                } else {
                    console.log('No payment schedule data found in table');
                }
            } else {
                console.log('No payment schedule table found or table is empty');
            }
        } else {
            console.log('No existing loan summary data found');
        }
    }

    // Generate all charts based on loan type and results
    generateCharts(results) {
        // Prevent concurrent chart generation
        if (this.chartGenerationInProgress) {
            console.log('Chart generation already in progress, skipping...');
            return;
        }
        
        try {
            this.chartGenerationInProgress = true;
            console.log('Starting chart generation for loan type:', results.loan_type);
            
            // Clear any existing charts first
            this.clearExistingCharts();
            
            // Add small delay to ensure canvas elements are ready
            setTimeout(() => {
                try {
                    console.log('Setting up chart containers...');
                    
                    // Hide all chart rows initially
                    const chartRows = ['topChartsRow', 'balanceChartRow', 'developmentChartsRow', 'trancheChartsRow'];
                    chartRows.forEach(rowId => {
                        const row = document.getElementById(rowId);
                        if (row) {
                            row.style.display = 'none';
                            console.log(`Hidden chart row: ${rowId}`);
                        }
                    });

                    // Check if we have the necessary chart containers
                    const loanBreakdownCanvas = document.getElementById('loanBreakdownChart');
                    if (!loanBreakdownCanvas) {
                        console.error('Loan breakdown chart canvas not found');
                        this.chartGenerationInProgress = false;
                        return;
                    }

                    // Generate basic loan breakdown chart for all loan types
                    console.log('Creating loan breakdown chart...');
                    this.createLoanBreakdownChart(results);

                    // Show top charts row (always visible for all loan types)
                    const topChartsRow = document.getElementById('topChartsRow');
                    if (topChartsRow) {
                        topChartsRow.style.display = 'flex';
                        console.log('Showing top charts row');
                    }

                    // Always show balance chart if we have payment schedule data
                    console.log('Checking for payment schedule data...');
                    const balanceChartRow = document.getElementById('balanceChartRow');
                    if (balanceChartRow && results.detailed_payment_schedule && results.detailed_payment_schedule.length > 0) {
                        balanceChartRow.style.display = 'block';
                        console.log('Balance chart row forced to display - schedule has', results.detailed_payment_schedule.length, 'entries');
                    }

                    // Generate loan-type specific charts
                    if (results.loan_type === 'development' || results.loan_type === 'development2') {
                        this.createDevelopmentLoanCharts(results);
                    } else {
                        this.createBridgeTermLoanCharts(results);
                    }

                    console.log('All charts generated successfully');
                } catch (delayedError) {
                    console.error('Error in delayed chart generation:', delayedError);
                } finally {
                    this.chartGenerationInProgress = false;
                }
            }, 50); // Small delay to ensure canvas cleanup
        } catch (error) {
            console.error('Error generating charts:', error);
            this.chartGenerationInProgress = false;
        }
    }

    // Create loan breakdown pie chart showing gross amount, fees, and net advance
    createLoanBreakdownChart(results) {
        const ctx = document.getElementById('loanBreakdownChart');
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts.loanBreakdown) {
            try {
                this.charts.loanBreakdown.destroy();
            } catch (e) {
                console.log('Error destroying existing loan breakdown chart:', e);
            }
            this.charts.loanBreakdown = null;
        }
        
        // Also check for any existing Chart.js instance on this canvas
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            try {
                existingChart.destroy();
            } catch (e) {
                console.log('Error destroying canvas chart:', e);
            }
        }

        const grossAmount = results.grossAmount || 0;
        const arrangementFee = results.arrangementFee || 0;
        const legalFees = results.legalCosts || results.legalFees || 0;
        const siteVisitFee = results.siteVisitFee || 0;
        const titleInsurance = results.titleInsurance || 0;
        const totalInterest = results.totalInterest || 0;
        const totalNetAdvance = results.totalNetAdvance || 0;

        const data = {
            labels: ['Total Net Advance', 'Arrangement Fee', 'Legal Costs', 'Site Visit Fee', 'Title Insurance', 'Total Interest'],
            datasets: [{
                data: [totalNetAdvance, arrangementFee, legalFees, siteVisitFee, titleInsurance, totalInterest],
                backgroundColor: this.getCurrentThemeColors(results.currency).gradient,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        };

        let chartConfig = {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: 'Loan Amount Breakdown',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                const currency = results.currencySymbol || '£';
                                return `${label}: ${currency}${value.toLocaleString('en-GB')} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        };

        // Add enhanced data labels for better visibility
        if (typeof window.ChartDataLabelsEnhancer !== 'undefined') {
            chartConfig = window.ChartDataLabelsEnhancer.enhancePieChart(chartConfig, {
                currency: results.currencySymbol || '£',
                baseFontSize: 20 // Increased to 20 for much better visibility
            });
        }

        this.charts.loanBreakdown = new Chart(ctx, chartConfig);
    }



    // Create charts specific to development loans
    createDevelopmentLoanCharts(results) {
        try {
            console.log('Creating development loan charts');
            
            const developmentChartsRow = document.getElementById('developmentChartsRow');
            const balanceChartRow = document.getElementById('balanceChartRow');
            
            if (developmentChartsRow) {
                developmentChartsRow.style.display = 'block';
                console.log('Development charts row displayed');
            } else {
                console.log('Development charts row not found');
            }
            
            if (balanceChartRow) {
                balanceChartRow.style.display = 'block';
                console.log('Balance chart row displayed for development loan');
            } else {
                console.log('Balance chart row not found for development loan');
            }
            
            // Create charts with error handling
            try {
                this.createMonthlyBreakdownChart(results);
            } catch (error) {
                console.error('Error creating monthly breakdown chart:', error);
            }
            
            try {
                this.createBalanceOverTimeChart(results);
            } catch (error) {
                console.error('Error creating balance over time chart:', error);
            }
            
            // Debug compound interest chart
            console.log('Creating compound interest chart with data:', {
                monthly_breakdown: results.monthly_breakdown,
                detailed_payment_schedule: results.detailed_payment_schedule ? results.detailed_payment_schedule.length + ' entries' : 'none'
            });
            
            try {
                this.createCompoundInterestChart(results);
            } catch (error) {
                console.error('Error creating compound interest chart:', error);
            }
            
            // Show tranche charts if tranche data is available
            if (results.tranche_release_schedule || (results.detailed_payment_schedule && 
                results.detailed_payment_schedule.some(entry => {
                    if (!entry.tranche_release) return false;
                    const trancheValue = typeof entry.tranche_release === 'number' ? 
                        entry.tranche_release : 
                        parseFloat(String(entry.tranche_release).replace(/[£€,]/g, '')) || 0;
                    return trancheValue > 0;
                }))) {
                
                const trancheChartsRow = document.getElementById('trancheChartsRow');
                if (trancheChartsRow) {
                    trancheChartsRow.style.display = 'block';
                    console.log('Creating tranche release chart with schedule entries:', 
                        results.detailed_payment_schedule ? results.detailed_payment_schedule.length : 'none');
                    
                    try {
                        this.createTrancheReleaseChart(results);
                    } catch (error) {
                        console.error('Error creating tranche release chart:', error);
                    }
                }
            }
        } catch (error) {
            console.error('Error in createDevelopmentLoanCharts:', error);
        }
    }

    // Create charts specific to bridge and term loans
    createBridgeTermLoanCharts(results) {
        try {
            console.log('Creating bridge/term loan charts');
            
            // Show balance chart row for bridge and term loans
            const balanceChartRow = document.getElementById('balanceChartRow');
            if (balanceChartRow) {
                balanceChartRow.style.display = 'block';
                console.log('Balance chart row displayed');
            }
            
            // Create charts with error handling
            try {
                this.createBalanceOverTimeChart(results);
            } catch (error) {
                console.error('Error creating balance over time chart for bridge/term loan:', error);
            }
            
        } catch (error) {
            console.error('Error in createBridgeTermLoanCharts:', error);
        }
    }

    // Create monthly payment breakdown chart
    createMonthlyBreakdownChart(results) {
        const ctx = document.getElementById('monthlyBreakdownChart');
        if (!ctx) return;

        const schedule = results.detailed_payment_schedule || [];
        if (schedule.length === 0) return;

        const labels = schedule.map(entry => {
            // Use actual payment dates from the schedule
            const dateStr = entry.payment_date || '';
            if (dateStr) {
                // Parse the date format (e.g., "22/07/2025") and format it nicely
                const parts = dateStr.split('/');
                if (parts.length === 3) {
                    const day = parts[0];
                    const month = parts[1];
                    const year = parts[2].slice(-2); // Last 2 digits of year
                    return `${day}/${month}/${year}`;
                }
            }
            return dateStr || `Month ${schedule.indexOf(entry) + 1}`;
        });
        const interestData = schedule.map(entry => {
            const interestRaw = entry.interest_amount || 0;
            if (typeof interestRaw === 'number') {
                return interestRaw;
            } else if (typeof interestRaw === 'string') {
                return parseFloat(interestRaw.replace(/[£€,]/g, '')) || 0;
            }
            return 0;
        });
        
        const principalData = schedule.map(entry => {
            const principalRaw = entry.principal_payment || 0;
            if (typeof principalRaw === 'number') {
                return principalRaw;
            } else if (typeof principalRaw === 'string') {
                return parseFloat(principalRaw.replace(/[£€,]/g, '')) || 0;
            }
            return 0;
        });

        const themeColors = this.getCurrentThemeColors(results.currency);
        
        const data = {
            labels: labels,
            datasets: [{
                label: 'Interest',
                data: interestData,
                backgroundColor: this.hexToRgba(themeColors.primary, 0.7),
                borderColor: themeColors.primary,
                borderWidth: 1,
                pointRadius: 4,
                pointHoverRadius: 6
            }, {
                label: 'Principal',
                data: principalData,
                backgroundColor: this.hexToRgba(themeColors.secondary, 0.7),
                borderColor: themeColors.secondary,
                borderWidth: 1,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        };

        let chartConfig = {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        title: {
                            display: true,
                            text: 'Payment Period'
                        }
                    },
                    y: {
                        stacked: true,
                        title: {
                            display: true,
                            text: `Amount (${results.currencySymbol || results.currency_symbol || '£'})`
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Interest vs Principal Payments',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                const currency = results.currencySymbol || results.currency_symbol || '£';
                                return `${context.dataset.label}: ${currency}${context.parsed.y.toLocaleString('en-GB')}`;
                            }
                        }
                    }
                }
            }
        };

        // Add data labels if ChartEnhancer is available
        if (typeof window.ChartEnhancer !== 'undefined') {
            chartConfig = window.ChartEnhancer.enhanceBarChart(chartConfig, results);
        }

        this.charts.monthlyBreakdown = new Chart(ctx, chartConfig);
    }

    // Create remaining balance over time chart
    createBalanceOverTimeChart(results) {
        const ctx = document.getElementById('balanceOverTimeChart');
        if (!ctx) {
            console.log('Balance Over Time chart canvas not found');
            return false;
        }

        // Destroy existing chart if it exists before creating new one
        if (this.charts.balanceOverTime) {
            try {
                this.charts.balanceOverTime.destroy();
            } catch (e) {
                console.log('Error destroying existing balance chart:', e);
            }
            this.charts.balanceOverTime = null;
        }
        
        // Also check for any existing Chart.js instance on this canvas
        const existingChart = Chart.getChart(ctx);
        if (existingChart) {
            try {
                existingChart.destroy();
            } catch (e) {
                console.log('Error destroying canvas chart:', e);
            }
        }
        
        // Ensure parent container is visible
        const balanceChartRow = document.getElementById('balanceChartRow');
        if (balanceChartRow) {
            balanceChartRow.style.display = 'block';
        }

        const schedule = results.detailed_payment_schedule || [];
        console.log('Balance Over Time chart - schedule length:', schedule.length);
        if (schedule.length === 0) {
            console.log('Balance Over Time chart - no schedule data available');
            return;
        }

        const labels = schedule.map(entry => {
            // Use actual payment dates from the schedule
            const dateStr = entry.payment_date || '';
            if (dateStr) {
                // Parse the date format (e.g., "22/07/2025") and format it nicely
                const parts = dateStr.split('/');
                if (parts.length === 3) {
                    const day = parts[0];
                    const month = parts[1];
                    const year = parts[2].slice(-2); // Last 2 digits of year
                    return `${day}/${month}/${year}`;
                }
            }
            return dateStr || `Month ${schedule.indexOf(entry) + 1}`;
        });
        const balanceData = schedule.map(entry => {
            const balanceRaw = entry.closing_balance || 0;
            if (typeof balanceRaw === 'number') {
                return balanceRaw;
            } else if (typeof balanceRaw === 'string') {
                return parseFloat(balanceRaw.replace(/[£€,]/g, '')) || 0;
            }
            return 0;
        });

        const data = {
            labels: labels,
            datasets: [{
                label: 'Remaining Balance',
                data: balanceData,
                borderColor: 'rgba(184, 134, 11, 1)', // Novellus gold
                backgroundColor: 'rgba(184, 134, 11, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointRadius: 3,
                pointHoverRadius: 6,
                pointBackgroundColor: 'rgba(184, 134, 11, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        };

        console.log('Creating Balance Over Time chart with', balanceData.length, 'data points');
        
        // Ensure canvas is ready and visible before creating chart
        const createChart = () => {
            try {
                // Force canvas visibility
                ctx.style.display = 'block';
                ctx.parentElement.style.display = 'block';
                
                let chartConfig = {
                    type: 'line',
                    data: data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: {
                            duration: 0 // Disable animation for faster rendering
                        },
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Payment Period'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: `Balance (${results.currencySymbol || results.currency_symbol || '£'})`
                                },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: 'Loan Balance Over Time',
                                font: {
                                    size: 14,
                                    weight: 'bold'
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const currency = results.currencySymbol || results.currency_symbol || '£';
                                        return `${context.dataset.label}: ${currency}${context.parsed.y.toLocaleString('en-GB')}`;
                                    }
                                }
                            }
                        }
                    }
                };

                // Add data labels if ChartEnhancer is available
                if (typeof window.ChartEnhancer !== 'undefined') {
                    chartConfig = window.ChartEnhancer.enhanceLineChart(chartConfig, results);
                }

                this.charts.balanceOverTime = new Chart(ctx, chartConfig);
                console.log('Balance Over Time chart created successfully');
                return true;
            } catch (error) {
                console.error('Error creating Balance Over Time chart:', error);
                return false;
            }
        };
        
        // Try creating chart immediately
        if (!createChart()) {
            // If immediate creation fails, retry with delay
            setTimeout(() => {
                console.log('Retrying Balance Over Time chart creation');
                createChart();
            }, 100);
        }
    }

    // Create compound interest breakdown chart for development loans
    createCompoundInterestChart(results) {
        const ctx = document.getElementById('compoundInterestChart');
        if (!ctx) {
            console.error('Compound interest chart canvas not found');
            return;
        }

        // Use detailed_payment_schedule if monthly_breakdown is not available (Development 2)
        const monthlyBreakdown = results.monthly_breakdown || results.detailed_payment_schedule || [];
        console.log('Compound interest chart data source:', {
            monthly_breakdown_length: results.monthly_breakdown ? results.monthly_breakdown.length : 0,
            detailed_schedule_length: results.detailed_payment_schedule ? results.detailed_payment_schedule.length : 0,
            using_data_length: monthlyBreakdown.length
        });
        
        if (monthlyBreakdown.length === 0) {
            console.warn('No data available for compound interest chart');
            return;
        }

        const labels = monthlyBreakdown.map(entry => {
            // Use actual dates if available
            const dateStr = entry.date || entry.payment_date || entry.month || 'N/A';
            if (dateStr && dateStr.includes('-')) {
                // Parse ISO date format and convert to DD/MM/YY
                const date = new Date(dateStr);
                if (!isNaN(date.getTime())) {
                    const day = date.getDate().toString().padStart(2, '0');
                    const month = (date.getMonth() + 1).toString().padStart(2, '0');
                    const year = date.getFullYear().toString().slice(-2);
                    return `${day}/${month}/${year}`;
                }
            }
            return dateStr;
        });
        
        const interestData = monthlyBreakdown.map(entry => {
            // Handle both monthly_breakdown format and detailed_payment_schedule format
            const interest = entry.interest || entry.interest_amount || 0;
            if (typeof interest === 'number') {
                return interest;
            } else if (typeof interest === 'string') {
                return parseFloat(interest.replace(/[£€,]/g, '')) || 0;
            }
            return 0;
        });
        
        const principalData = monthlyBreakdown.map(entry => {
            // Handle both formats
            const principal = entry.principal || entry.principal_payment || entry.tranche_release || 0;
            if (typeof principal === 'number') {
                return principal;
            } else if (typeof principal === 'string') {
                return parseFloat(principal.replace(/[£€,]/g, '')) || 0;
            }
            return 0;
        });

        const data = {
            labels: labels,
            datasets: [{
                label: 'Monthly Interest',
                data: interestData,
                backgroundColor: 'rgba(30, 43, 58, 0.7)', // Novellus navy
                borderColor: 'rgba(30, 43, 58, 1)',
                borderWidth: 1,
                pointRadius: 4,
                pointHoverRadius: 6
            }, {
                label: 'Principal Amount',
                data: principalData,
                backgroundColor: 'rgba(184, 134, 11, 0.7)', // Novellus gold
                borderColor: 'rgba(184, 134, 11, 1)',
                borderWidth: 1,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        };

        this.charts.compoundInterest = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Month'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `Amount (${results.currencySymbol || results.currency_symbol || '£'})`
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Compound Interest Breakdown',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const currency = results.currencySymbol || results.currency_symbol || '£';
                                return `${context.dataset.label}: ${currency}${context.parsed.y.toLocaleString('en-GB')}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Create tranche release schedule chart
    createTrancheReleaseChart(results) {
        const ctx = document.getElementById('trancheReleaseChart');
        if (!ctx) return;

        const schedule = results.detailed_payment_schedule || [];
        const trancheData = schedule.filter(entry => {
            const trancheValue = entry.tranche_release || 0;
            if (typeof trancheValue === 'number') {
                return trancheValue > 0;
            } else if (typeof trancheValue === 'string') {
                return parseFloat(trancheValue.replace(/[£€,]/g, '')) > 0;
            }
            return false;
        });

        if (trancheData.length === 0) return;

        const labels = trancheData.map(entry => {
            const dateStr = entry.payment_date || 'N/A';
            if (dateStr && dateStr.includes('-')) {
                // Parse ISO date format and convert to DD/MM/YY
                const date = new Date(dateStr);
                if (!isNaN(date.getTime())) {
                    const day = date.getDate().toString().padStart(2, '0');
                    const month = (date.getMonth() + 1).toString().padStart(2, '0');
                    const year = date.getFullYear().toString().slice(-2);
                    return `${day}/${month}/${year}`;
                }
            }
            return dateStr;
        });
        
        const amounts = trancheData.map(entry => {
            const trancheValue = entry.tranche_release || 0;
            if (typeof trancheValue === 'number') {
                return trancheValue;
            } else if (typeof trancheValue === 'string') {
                return parseFloat(trancheValue.replace(/[£€,]/g, '')) || 0;
            }
            return 0;
        });

        const data = {
            labels: labels,
            datasets: [{
                label: 'Tranche Release Amount',
                data: amounts,
                backgroundColor: 'rgba(184, 134, 11, 0.7)', // Novellus gold
                borderColor: 'rgba(184, 134, 11, 1)',
                borderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        };

        this.charts.trancheRelease = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Release Date'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: `Amount (${results.currencySymbol || '£'})`
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Tranche Release Schedule',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const currency = results.currencySymbol || '£';
                                return `${context.dataset.label}: ${currency}${context.parsed.y.toLocaleString('en-GB')}`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Update percentage displays with actual user input values
    updatePercentageDisplays() {
        console.log('Updating percentage displays...');
        
        // Update arrangement fee percentage
        const arrangementFeePercentageEl = document.getElementById('arrangementFeePercentageDisplay');
        const arrangementFeeInput = document.getElementById('arrangementFeeRate');
        console.log('Arrangement fee elements found:', !!arrangementFeePercentageEl, !!arrangementFeeInput);
        if (arrangementFeePercentageEl && arrangementFeeInput) {
            const arrangementFeeRate = parseFloat(arrangementFeeInput.value) || 2.0;
            const newText = arrangementFeeRate.toFixed(2) + '%';
            arrangementFeePercentageEl.textContent = newText;
            console.log('Updated arrangement fee percentage from', arrangementFeePercentageEl.textContent, 'to:', newText);
        } else {
            console.error('Arrangement fee percentage elements not found');
        }
        
        // Update title insurance percentage  
        const titleInsurancePercentageEl = document.getElementById('titleInsurancePercentageDisplay');
        const titleInsuranceInput = document.getElementById('titleInsuranceRate');
        console.log('Title insurance elements found:', !!titleInsurancePercentageEl, !!titleInsuranceInput);
        if (titleInsurancePercentageEl && titleInsuranceInput) {
            const titleInsuranceRate = parseFloat(titleInsuranceInput.value) || 0.01;
            // Fix rounding issue by using proper decimal precision
            const newText = titleInsuranceRate.toFixed(3) + '%';
            titleInsurancePercentageEl.textContent = newText;
            console.log('Updated title insurance percentage to:', newText, 'from input value:', titleInsuranceInput.value);
        } else {
            console.error('Title insurance percentage elements not found');
        }
        
        // Update interest rate percentage
        const interestRatePercentageEl = document.getElementById('interestRatePercentageDisplay');
        console.log('Interest rate element found:', !!interestRatePercentageEl);
        if (interestRatePercentageEl) {
            const rateInputType = document.querySelector('input[name="rate_input_type"]:checked')?.value || 'annual';
            let interestRate = 0;
            
            if (rateInputType === 'annual') {
                const annualRateInput = document.getElementById('annualRateValue');
                interestRate = parseFloat(annualRateInput?.value) || 12.0;
                console.log('Reading annual rate from input:', annualRateInput?.value, 'parsed as:', interestRate);
            } else {
                const monthlyRateInput = document.getElementById('monthlyRateValue');
                interestRate = parseFloat(monthlyRateInput?.value) || 1.0;
                interestRate = interestRate * 12; // Convert monthly to annual for display
                console.log('Reading monthly rate from input:', monthlyRateInput?.value, 'annual equivalent:', interestRate);
            }
            
            const newText = interestRate.toFixed(2) + '%';
            interestRatePercentageEl.textContent = newText;
            console.log('Updated interest rate percentage to:', newText);
        } else {
            console.error('Interest rate percentage element not found');
        }
        
        console.log('Percentage displays update completed');
    }

    // Helper method to get current theme colors based on currency
    getCurrentThemeColors(currency) {
        const currentCurrency = currency || document.getElementById('currency')?.value || 'GBP';
        
        if (currentCurrency === 'EUR') {
            // Teal palette for EUR
            return {
                primary: '#42B89A',
                secondary: '#20B2AA',
                tertiary: '#5CC9B0',
                quaternary: '#76DAC6',
                quinary: '#B8F0E5',
                success: '#359677',
                warning: '#00CED1',
                gradient: ['#42B89A', '#20B2AA', '#5CC9B0', '#76DAC6', '#B8F0E5', '#359677']
            };
        } else {
            // Gold palette for GBP (default)
            return {
                primary: '#B8860B',
                secondary: '#DAA520',
                tertiary: '#CDA44C',
                quaternary: '#E6C547',
                quinary: '#F2E185',
                success: '#8B6914',
                warning: '#FFD700',
                gradient: ['#B8860B', '#DAA520', '#CDA44C', '#E6C547', '#F2E185', '#8B6914']
            };
        }
    }

    // Helper method to darken a color
    darkenColor(color, percent) {
        const num = parseInt(color.replace("#", ""), 16);
        const amt = Math.round(2.55 * percent);
        const R = (num >> 16) - amt;
        const G = (num >> 8 & 0x00FF) - amt;
        const B = (num & 0x0000FF) - amt;
        return "#" + (0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)).toString(16).slice(1);
    }

    // Helper method to convert hex color to rgba
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
}

// Fullscreen toggle functionality
function toggleFullscreen(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (container.classList.contains('fullscreen')) {
        // Exit fullscreen
        container.classList.remove('fullscreen');
        document.body.classList.remove('no-scroll');
        
        // Update button text
        const button = container.querySelector('.expand-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-expand me-1"></i>View Full Chart';
        }
        
        // Resize chart
        const canvas = container.querySelector('canvas');
        if (canvas && window.loanCalculator && window.loanCalculator.charts) {
            const chart = Object.values(window.loanCalculator.charts).find(c => 
                c.canvas.id === canvas.id
            );
            if (chart) {
                setTimeout(() => chart.resize(), 100);
            }
        }
    } else {
        // Enter fullscreen
        container.classList.add('fullscreen');
        document.body.classList.add('no-scroll');
        
        // Update button text
        const button = container.querySelector('.expand-btn');
        if (button) {
            button.innerHTML = '<i class="fas fa-compress me-1"></i>Exit Fullscreen';
        }
        
        // Resize chart and update data points
        const canvas = container.querySelector('canvas');
        if (canvas && window.loanCalculator && window.loanCalculator.charts) {
            const chart = Object.values(window.loanCalculator.charts).find(c => 
                c.canvas.id === canvas.id
            );
            if (chart) {
                // Enhanced data points for fullscreen view
                if (chart.data.datasets) {
                    chart.data.datasets.forEach(dataset => {
                        if (dataset.pointRadius !== undefined) {
                            dataset.pointRadius = 6;
                            dataset.pointHoverRadius = 8;
                        }
                    });
                    chart.update('none');
                }
                setTimeout(() => chart.resize(), 100);
            }
        }
    }
}

// Close fullscreen on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const fullscreenChart = document.querySelector('.chart-container.fullscreen');
        if (fullscreenChart) {
            toggleFullscreen(fullscreenChart.id);
        }
    }
});

// Auto-update functionality for charts
function addAutoUpdateListeners() {
    const watchedInputs = [
        'grossAmount', 'netAmount', 'interestRate', 'loanTerm', 'propertyValue',
        'arrangementFeeRate', 'legalCosts', 'siteVisitFee', 'titleInsurance',
        'startDate', 'endDate', 'capitalRepayment', 'flexiblePayment'
    ];
    
    watchedInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('input', debounce(() => {
                autoUpdateCharts();
            }, 800));
        }
    });
    
    // Watch dropdown changes immediately
    const watchedSelects = ['loanType', 'repaymentOption', 'paymentTiming', 'paymentFrequency', 'loanTerm'];
    watchedSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.addEventListener('change', () => {
                setTimeout(() => autoUpdateCharts(), 300);
            });
        }
    });
    
    // Watch currency changes
    const currencyRadios = document.querySelectorAll('input[name="currency"]');
    currencyRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            setTimeout(() => autoUpdateCharts(), 200);
        });
    });
}

function addAutoUpdateListeners() {
    // Only add listeners if the calculator is initialized
    if (!window.loanCalculator) {
        console.warn('Loan calculator not initialized, skipping auto-update listeners');
        return;
    }
    
    // Get form inputs for auto-update
    const inputSelectors = [
        '#grossAmount', '#netAmount', '#annual_rate', '#monthly_rate', '#property_value',
        '#arrangement_fee_percentage', '#legal_fees', '#site_visit_fee', '#title_insurance_rate',
        '#loan_term', '#start_date', '#end_date', '#day1_advance', 
        '#capital_repayment', '#flexible_payment'
    ];
    
    // Add debounced change listeners to inputs
    inputSelectors.forEach(selector => {
        const element = document.querySelector(selector);
        if (element) {
            const debouncedUpdate = debounce(() => {
                if (window.loanCalculator && window.loanCalculator.currentResults) {
                    setTimeout(() => autoUpdateCharts(), 300);
                }
            }, 500);
            
            element.addEventListener('input', debouncedUpdate);
            element.addEventListener('change', debouncedUpdate);
        }
    });
    
    // Watch dropdown changes immediately
    const watchedSelects = ['loanType', 'repaymentOption', 'paymentTiming', 'paymentFrequency', 'loanTerm'];
    watchedSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (select) {
            select.addEventListener('change', () => {
                setTimeout(() => autoUpdateCharts(), 300);
            });
        }
    });
    
    // Watch currency changes
    const currencyRadios = document.querySelectorAll('input[name="currency"]');
    currencyRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            setTimeout(() => autoUpdateCharts(), 200);
        });
    });
}

// Debounce function to prevent too many rapid updates
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Auto-update charts when form data changes
function autoUpdateCharts() {
    const loanSummaryTable = document.querySelector('#loanSummaryTable tbody');
    if (!loanSummaryTable || loanSummaryTable.children.length === 0) {
        return; // No existing results to update
    }
    
    // Only auto-update if user isn't actively typing
    const activeElement = document.activeElement;
    if (activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'SELECT')) {
        return;
    }
    
    // Destroy existing charts to prevent conflicts
    if (window.loanCalculator && window.loanCalculator.charts) {
        Object.values(window.loanCalculator.charts).forEach(chart => {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        });
        window.loanCalculator.charts = {};
    }
    
    // Trigger calculation which will update charts
    if (window.loanCalculator) {
        console.log('Auto-updating charts based on form changes');
        window.loanCalculator.calculateLoan();
    }
}

// Initialize calculator when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.loanCalculator = new LoanCalculator();
    
    // Add auto-update listeners after calculator is ready
    setTimeout(() => {
        addAutoUpdateListeners();
        console.log('Auto-update listeners added for chart synchronization');
    }, 500);
});