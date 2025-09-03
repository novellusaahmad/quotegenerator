/**
 * Novellus Loan Calculator JavaScript - Enhanced Version
 * Handles loan summary display with comprehensive visualizations
 */


// --- Custom plugin to draw value (currency) and % on donut slices ---
const loanDonutLabels = {
    id: 'loanDonutLabels',
    afterDatasetsDraw(chart, args, pluginOptions) {
        const {ctx, chartArea, data} = chart;
        const ds = chart.data.datasets[0];
        if (!ds || !ds.data || !ds.data.length) return;
        const meta = chart.getDatasetMeta(0);
        const total = ds.data.reduce((a, b) => a + (parseFloat(b) || 0), 0);
        if (!total) return;

        // Determine currency symbol from UI
        let symbol = '£';
        try {
            const cur = document.getElementById('currency')?.value || 'GBP';
            symbol = (cur === 'EUR') ? '€' : '£';
        } catch(e) {}

        ctx.save();
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = '12px sans-serif';

        meta.data.forEach((arc, i) => {
            const val = parseFloat(ds.data[i]) || 0;
            if (val <= 0) return;

            const p = arc.getProps(['x', 'y', 'startAngle', 'endAngle', 'outerRadius', 'innerRadius'], true);
            // angle at the middle of the arc
            const angle = (p.startAngle + p.endAngle) / 2;
            // position slightly inside the outer edge
            const r = (p.innerRadius + p.outerRadius) / 2;
            const x = p.x + Math.cos(angle) * r;
            const y = p.y + Math.sin(angle) * r;

            const pct = total ? (val / total * 100) : 0;
            const valueStr = symbol + val.toLocaleString('en-GB', {minimumFractionDigits: 0, maximumFractionDigits: 0});
            const label = `${valueStr} (${pct.toFixed(1)}%)`;

            // Only draw if there is enough arc span
            const span = p.endAngle - p.startAngle;
            if (span < 0.15) return; // skip very tiny slices to avoid clutter

            // White rounded background for readability
            const padding = 4;
            const textWidth = ctx.measureText(label).width;
            const boxW = textWidth + padding * 2;
            const boxH = 18;

            ctx.fillStyle = 'rgba(255,255,255,0.85)';
            ctx.beginPath();
            if (typeof ctx.roundRect === 'function') {
                ctx.roundRect(x - boxW / 2, y - boxH / 2, boxW, boxH, 6);
            } else {
                ctx.rect(x - boxW / 2, y - boxH / 2, boxW, boxH);
            }
            ctx.fill();

            ctx.fillStyle = '#333';
            ctx.fillText(label, x, y);
        });

        ctx.restore();
    }
};
if (typeof Chart !== 'undefined') {
    Chart.register(loanDonutLabels);
}

class LoanCalculator {
    constructor() {
        try {
            this.form = document.getElementById('calculatorForm');
            this.resultsSection = document.getElementById('resultsSection');
            this.noResults = document.getElementById('noResults');
            this.currentResults = null;
            this.charts = {}; // Store chart instances for proper cleanup
            this.chartGenerationInProgress = false; // Prevent concurrent chart generation
            this.currentTrancheIndex = null;
            this.trancheBreakdownData = [];
            this.trancheCurrency = '£';
            this.editContext = 'breakdown';
            
            // Check if required elements exist
            if (!this.form) {
                console.error('Calculator form not found - calculator functionality will be limited');
                return;
            }
            
            // Only initialize if required elements exist
            this.initializeEventListeners();
            // Enable blur-based comma formatting on monetary fields
            this.setupImprovedInputFormatting();
            this.setDefaultDate();
            this.updateCurrencySymbols();
            this.updateGBPQuoteButtonVisibility();
            // Initialize dynamic dropdowns and sections on page load
            this.updateRepaymentOptions();
            this.updateAdditionalParams();
            this.updateAutoTotalAmount();
            this.initializeLTVTargetControls();
            // Calculate initial end date based on default values
            setTimeout(() => {
                try {
                    if (typeof calculateEndDate === 'function') {
                        calculateEndDate();
                    }
                } catch (error) {
                    console.error('Error calculating end date:', error);
                }
            }, 100);
            // Check for existing calculation data and display charts on page load
            setTimeout(() => {
                try {
                    this.loadExistingResults();
                } catch (error) {
                    console.error('Error loading existing results:', error);
                }
            }, 500);
            // Update percentage displays on page load
            setTimeout(() => {
                try {
                    this.updatePercentageDisplays();
                    this.updateRateEquivalenceNote();
                } catch (error) {
                    console.error('Error updating percentage displays:', error);
                }
            }, 100);
            // Initialize currency theme based on default currency
            setTimeout(() => {
                try {
                    const currencySelect = document.getElementById('currency');
                    if (currencySelect && window.currencyThemeManager) {
                        const currentCurrency = currencySelect.value || 'GBP';
                        window.currencyThemeManager.updateTheme(currentCurrency);
                        console.log(`Initialized currency theme: ${currentCurrency}`);
                    }
                } catch (error) {
                    console.error('Error initializing currency theme:', error);
                }
            }, 200);
            
            // Make calculator instance globally accessible for theme updates
            window.loanCalculator = this;
            this.setupModalResizeHandlers();
            console.log('Loan calculator initialized successfully');
            
        } catch (error) {
            console.error('Error initializing LoanCalculator:', error);
            // Still make a basic calculator instance available
            window.loanCalculator = this;
        }
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

        // Sync radio toggle inputs with hidden fields
        document.querySelectorAll('input[name="loanTypeToggle"]').forEach(radio => {
            radio.addEventListener('change', () => {
                const hidden = document.getElementById('loanType');
                if (hidden) {
                    hidden.value = radio.value;
                    hidden.dispatchEvent(new Event('change'));
                }
            });
        });

        document.querySelectorAll('input[name="repaymentOptionToggle"]').forEach(radio => {
            radio.addEventListener('change', () => {
                const hidden = document.getElementById('repaymentOption');
                if (hidden) {
                    hidden.value = radio.value;
                    hidden.dispatchEvent(new Event('change'));
                }
            });
        });

        document.querySelectorAll('input[name="currency"]').forEach(radio => {
            radio.addEventListener('change', () => {
                const hidden = document.getElementById('currency');
                if (hidden) {
                    hidden.value = radio.value;
                    hidden.dispatchEvent(new Event('change'));
                }
            });
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

        // Update Total Development Tranche when net amount or Day 1 advance changes
        const netAmountField = document.getElementById('netAmountInput');
        const day1AdvanceField = document.getElementById('day1Advance');
        if (netAmountField) {
            netAmountField.addEventListener('input', () => this.updateAutoTotalAmount());
        }
        if (day1AdvanceField) {
            day1AdvanceField.addEventListener('input', () => this.updateAutoTotalAmount());
        }

        // Start/end date or term changes - update loan end synchronization
        document.getElementById('startDate').addEventListener('change', () => {
            calculateEndDate();
        });
        const endDateField = document.getElementById('endDate');
        if (endDateField) {
            endDateField.addEventListener('change', () => {
                calculateEndDate();
            });
        }
        const loanTermField = document.getElementById('loanTerm');
        if (loanTermField) {
            loanTermField.addEventListener('input', () => {
                calculateEndDate();
            });
        }
        const loanEndRadios = document.querySelectorAll('input[name="loan_end_type"]');
        if (loanEndRadios.length > 0) {
            loanEndRadios.forEach(radio => radio.addEventListener('change', () => {
                calculateEndDate();
            }));
        }

        // 360-day checkbox changes - trigger automatic recalculation
        const use360DaysCheckbox = document.getElementById('use360Days');
        if (use360DaysCheckbox) {
            use360DaysCheckbox.addEventListener('change', () => {
                console.log('360-day calculation method changed');
                // If we have existing results, automatically recalculate
                if (this.currentResults) {
                    this.calculateLoan();
                }
            });
        }

        // Interest calculation type changes (toggle buttons)
        const interestTypeRadios = document.querySelectorAll('input[name="interestTypeToggle"]');
        interestTypeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                const hidden = document.getElementById('interestType');
                if (hidden) {
                    hidden.value = radio.value;
                    hidden.dispatchEvent(new Event('change'));
                }
                try {
                    console.log('Interest calculation type changed');
                    // Recalculate automatically if we already have results
                    if (this.currentResults) {
                        this.calculateLoan(true);
                    }
                } catch (error) {
                    console.error('Error handling interest type change:', error);
                }
            });
        });

        // Input formatting disabled to prevent field clearing issues

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
                    if (fieldId === 'annualRateValue' || fieldId === 'monthlyRateValue') {
                        this.updateRateEquivalenceNote();
                    }
                });
            }
        });

        // Update percentage displays when rate input type changes
        document.querySelectorAll('input[name="rate_input_type"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.updatePercentageDisplays();
                this.updateRateEquivalenceNote();
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

        // View calculation breakdown
        const breakdownBtn = document.getElementById('viewBreakdownBtn');
        if (breakdownBtn) {
            breakdownBtn.addEventListener('click', () => {
                this.populateBreakdownModal();
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
        
        // General sanitization: strip commas from any numeric-looking string
        Object.keys(data).forEach((k) => {
            if (typeof data[k] === 'string' && /[0-9],[0-9]/.test(data[k])) {
                data[k] = data[k].replace(/,/g, '');
            }
        });
        // Remove commas from monetary fields for calculation
        const monetaryFieldNames = [
            'property_value', 'gross_amount', 'net_amount', 
            'day1_advance', 'legal_fees', 'site_visit_fee', 
            'capital_repayment', 'flexible_payment'
        ];
        
        monetaryFieldNames.forEach(fieldName => {
            if (data[fieldName] && typeof data[fieldName] === 'string') {
                data[fieldName] = data[fieldName].replace(/,/g, '');
            }
        });
        
        // Handle special cases for amount input
        const amountInputType = document.querySelector('input[name="amount_input_type"]:checked').value;
        data.amount_input_type = amountInputType;
        
        // Handle payment timing and frequency explicitly
        const paymentTimingElement = document.querySelector('input[name="payment_timing"]:checked');
        if (paymentTimingElement) {
            data.payment_timing = paymentTimingElement.value;
        }
        
        const paymentFrequencyElement = document.querySelector('input[name="payment_frequency"]:checked');
        if (paymentFrequencyElement) {
            data.payment_frequency = paymentFrequencyElement.value;
        }
        
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
            const startDateValue = document.getElementById('startDate')?.value;

            if (trancheContainer) {
                const trancheInputs = trancheContainer.querySelectorAll('.tranche-item');

                trancheInputs.forEach((trancheItem, index) => {
                    const amountInput = trancheItem.querySelector('.tranche-amount');
                    const dateInput = trancheItem.querySelector('.tranche-date');
                    const rateInput = trancheItem.querySelector('.tranche-rate');
                    const descriptionInput = trancheItem.querySelector('.tranche-description');

                    if (amountInput && dateInput && parseFloat(amountInput.value) > 0) {
                        // The calculation engine expects a month index to align each tranche
                        // with the loan schedule. Derive it from the release date when available
                        // or fall back to sequential months starting at 2 (post Day 1 advance).
                        let month = index + 2;
                        if (dateInput.value && startDateValue) {
                            const start = new Date(startDateValue);
                            const release = new Date(dateInput.value);
                            month = (release.getFullYear() - start.getFullYear()) * 12 +
                                    (release.getMonth() - start.getMonth()) + 1;
                            if (month < 2) month = 2;
                        }

                        const rawRate = parseFloat(rateInput.value);
                        let rate = rawRate;
                        if (isNaN(rate)) {
                            rate = parseFloat(data.annual_rate);
                            if (isNaN(rate)) rate = 0;
                        }

                        tranches.push({
                            amount: parseFloat(amountInput.value),
                            date: dateInput.value,
                            rate: rate,
                            description: descriptionInput.value || `Tranche ${index + 1}`,
                            month: month
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

            // Update visualization button visibility based on loan type and repayment option
            this.updateVisualizationButtonsVisibility(results);
            
            // Update percentage displays after results are shown
            console.log('Updating percentage displays...');
            this.updatePercentageDisplays();

            const targetExitInput = document.getElementById('targetLTVExit');
            if (targetExitInput && typeof results.endLTV !== 'undefined') {
                targetExitInput.value = Number(results.endLTV).toFixed(2);
            }
            this.calculateLTVSimulation(results);
            
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
        const netDay1AdvanceRow = netDay1AdvanceEl ? netDay1AdvanceEl.closest('tr') : null;
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
        const loanTermDays = results.loanTermDays || 0; // normalized by backend
        const arrangementFee = results.arrangementFee || 0;
        const legalCosts = results.legalCosts || results.legalFees || 0;
        const siteVisitFee = results.siteVisitFee || 0;
        const titleInsurance = results.titleInsurance || 0;
        const totalInterest = results.totalInterest || 0;
        const day1Advance = results.day1Advance || results.netDay1Advance || 0;
        
        // Determine loan type and repayment option early for conditional displays
        const loanType = document.getElementById('loanType').value;
        const repaymentOption = document.getElementById('repaymentOption').value;
        const isBridgeRetainedOnly = loanType === 'bridge' && repaymentOption === 'retained';
        const isBridgeServicedOnly = loanType === 'bridge' && repaymentOption === 'service_only';
        const paymentFrequency = document.querySelector('input[name="payment_frequency"]:checked')?.value || 'monthly';
        const paymentTiming = document.querySelector('input[name="payment_timing"]:checked')?.value || 'advance';

        // Update the display elements
        const moneyFormat = {minimumFractionDigits: 2, maximumFractionDigits: 2};
        if (valuationEl) valuationEl.textContent = propertyValue.toLocaleString('en-GB', moneyFormat);
        if (grossAmountEl) grossAmountEl.textContent = grossAmount.toLocaleString('en-GB', moneyFormat);
        if (startDateEl) startDateEl.textContent = this.formatDate(startDate);
        if (endDateEl) endDateEl.textContent = this.formatDate(endDate);
        if (loanTermEl) loanTermEl.textContent = loanTerm.toFixed(2);
        if (loanTermDaysEl) loanTermDaysEl.textContent = loanTermDays;
        if (arrangementFeeEl) arrangementFeeEl.textContent = arrangementFee.toLocaleString('en-GB', moneyFormat);
        if (legalCostsEl) legalCostsEl.textContent = legalCosts.toLocaleString('en-GB', moneyFormat);
        if (siteVisitFeeEl) siteVisitFeeEl.textContent = siteVisitFee.toLocaleString('en-GB', moneyFormat);
        if (titleInsuranceEl) titleInsuranceEl.textContent = titleInsurance.toLocaleString('en-GB', moneyFormat);
        if (totalInterestEl) totalInterestEl.textContent = totalInterest.toLocaleString('en-GB', moneyFormat);

        // For development loans, show user input Day 1 advance for display purposes
        if (netDay1AdvanceRow) {
            if (repaymentOption === 'service_and_capital') {
                netDay1AdvanceRow.style.display = 'none';
            } else {
                netDay1AdvanceRow.style.display = '';
                const userInputFromBackend = results.userInputDay1Advance;
                const day1AdvanceInput = document.querySelector('input[name="day1_advance"]');
                const userInputFromForm = day1AdvanceInput ? parseFloat(day1AdvanceInput.value) || 0 : 0;
                const displayDay1Advance = userInputFromBackend || userInputFromForm || results.day1NetAdvance || results.day1Advance || day1Advance || 0;
                netDay1AdvanceEl.textContent = displayDay1Advance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }
        }
        
        // Calculate and display LTV ratio (use backend values if available)
        if (ltvRatioEl && propertyValue > 0) {
            const ltvRatio = results.ltv || (grossAmount / propertyValue * 100);
            ltvRatioEl.textContent = ltvRatio.toFixed(2) + '%';
        } else if (ltvRatioEl) {
            ltvRatioEl.textContent = '0.00%';
        }
        
        // Display End LTV based on closing balance of last month from payment schedule
        const endLTVRow = endLTVEl ? endLTVEl.closest('tr') : null;
        if (isBridgeRetainedOnly || isBridgeServicedOnly) {
            if (endLTVRow) endLTVRow.style.display = 'none';
        } else if (endLTVEl && propertyValue > 0) {
            let endLTV = 0;
            
            // Try to get the closing balance from the last month of the payment schedule for final remaining balance
            if (results.detailed_payment_schedule && results.detailed_payment_schedule.length > 0) {
                const schedule = results.detailed_payment_schedule;
                const lastScheduleEntry = schedule[schedule.length - 1];
                let closingBalanceRaw = lastScheduleEntry.closing_balance;

                // Handle both string and numeric closing balance values
                let closingBalanceValue = 0;
                if (typeof closingBalanceRaw === 'number') {
                    closingBalanceValue = closingBalanceRaw;
                } else if (typeof closingBalanceRaw === 'string') {
                    const match = closingBalanceRaw.match(/[\d,]+\.?\d*/);
                    if (match) closingBalanceValue = parseFloat(match[0].replace(/,/g, ''));
                }

                if (closingBalanceValue <= 0 && schedule.length > 1) {
                    const secondLast = schedule[schedule.length - 2];
                    const secondRaw = secondLast.closing_balance || secondLast.capital_outstanding;
                    if (typeof secondRaw === 'number') {
                        closingBalanceValue = secondRaw;
                    } else if (typeof secondRaw === 'string') {
                        const match = secondRaw.match(/[\d,]+\.?\d*/);
                        if (match) closingBalanceValue = parseFloat(match[0].replace(/,/g, ''));
                    }
                }

                if (closingBalanceValue <= 0 && (results.repayment_option === 'capital_payment_only' || results.repaymentOption === 'capital_payment_only') && lastScheduleEntry.opening_balance) {
                    const openingRaw = lastScheduleEntry.opening_balance;
                    if (typeof openingRaw === 'number') {
                        closingBalanceValue = openingRaw;
                    } else if (typeof openingRaw === 'string') {
                        const match = openingRaw.match(/[\d,]+\.?\d*/);
                        if (match) closingBalanceValue = parseFloat(match[0].replace(/,/g, ''));
                    }
                }

                if (closingBalanceValue > 0) {
                    endLTV = (closingBalanceValue / propertyValue) * 100;
                    console.log(`End LTV calculation: balance £${closingBalanceValue.toLocaleString()} / Property value £${propertyValue.toLocaleString()} = ${endLTV.toFixed(2)}%`);
                }
            }

            if (!endLTV) {
                // Fallback to gross amount if no payment schedule available or balance couldn't be determined
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
        
        // Retained interest and refund
        const retainedInterestRow = document.getElementById('retainedInterestRow');
        const retainedInterestEl = document.getElementById('retainedInterestResult');
        const interestRefundRow = document.getElementById('interestRefundRow');
        const interestRefundEl = document.getElementById('interestRefundResult');

        const retainedInterestVal = parseFloat(results.retainedInterest ?? results.retained_interest ?? 0);
        const interestRefundVal = parseFloat(results.interestRefund ?? results.interest_refund ?? 0);
        const isServiceAndCapital = repaymentOption === 'service_and_capital';

        if (retainedInterestRow) {
            if (isServiceAndCapital) {
                retainedInterestRow.style.display = 'none';
            } else if (retainedInterestVal > 0) {
                retainedInterestRow.style.display = 'table-row';
                if (retainedInterestEl) {
                    retainedInterestEl.textContent = retainedInterestVal.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }
            } else {
                retainedInterestRow.style.display = 'none';
            }
        }

        if (interestRefundRow) {
            if (isServiceAndCapital) {
                interestRefundRow.style.display = 'none';
            } else if (interestRefundVal > 0) {
                interestRefundRow.style.display = 'table-row';
                if (interestRefundEl) {
                    interestRefundEl.textContent = interestRefundVal.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }
            } else {
                interestRefundRow.style.display = 'none';
            }
        }

        // Show interest-only total and savings if available (for flexible payment options)
        const interestOnlyTotalRow = document.getElementById('interestOnlyTotalRow');
        const interestOnlyTotalEl = document.getElementById('interestOnlyTotalResult');
        const interestSavingsRow = document.getElementById('interestSavingsRow');
        const interestSavingsEl = document.getElementById('interestSavingsResult');
        const savingsPercentageEl = document.getElementById('savingsPercentageResult');
        
        // Check if we should show interest savings comparison
        // Support both camelCase and snake_case fields returned from backend
        const interestOnlyTotalVal = parseFloat(results.interestOnlyTotal ?? results.interest_only_total ?? 0);
        const interestSavingsVal = parseFloat(results.interestSavings ?? results.interest_savings ?? 0);

        const shouldShowInterestComparison = (
            (interestSavingsVal > 0) ||
            (interestOnlyTotalVal > 0) ||
            (repaymentOption === 'service_and_capital' || repaymentOption === 'capital_payment_only' || repaymentOption === 'flexible_payment')
        );

        if (isBridgeRetainedOnly || isBridgeServicedOnly) {
            if (interestOnlyTotalRow) interestOnlyTotalRow.style.display = 'none';
            if (interestSavingsRow) interestSavingsRow.style.display = 'none';
        } else if (shouldShowInterestComparison) {
            // Show interest-only total row
            if (interestOnlyTotalRow) interestOnlyTotalRow.style.display = 'table-row';
            if (interestOnlyTotalEl) {
                interestOnlyTotalEl.textContent = interestOnlyTotalVal.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }

            // Show interest savings row only if there are actual savings
            const interestSavings = interestSavingsVal;
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
        
        // Show/hide periodic interest payment for applicable repayment types
        const periodicInterestRow = document.getElementById('periodicInterestRow');
        const periodicInterestEl = document.getElementById('periodicInterestResult');
        const periodicInterestLabel = document.getElementById('periodicInterestLabel');

        const interestRepaymentTypes = ['service_only', 'service_and_capital', 'capital_payment_only', 'flexible_payment'];
        if ((loanType === 'term' || loanType === 'bridge') && interestRepaymentTypes.includes(repaymentOption)) {
            let periodicInterest = results.periodicInterest || results.periodic_interest;
            if (!periodicInterest) {
                const gross = parseFloat(results.grossAmount ?? 0);
                const rate = parseFloat(results.interestRate ?? results.annualRate ?? 0);
                if (gross && rate) {
                    periodicInterest = gross * (rate / 100) / (paymentFrequency === 'quarterly' ? 4 : 12);
                } else {
                    periodicInterest = 0;
                }
            }

            if (periodicInterestRow) periodicInterestRow.style.display = 'table-row';
            if (periodicInterestEl) {
                periodicInterestEl.textContent = periodicInterest.toLocaleString('en-GB', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }

            if (periodicInterestLabel) {
                const label = paymentFrequency === 'quarterly' ? 'Quarterly Interest Payment' : 'Monthly Interest Payment';
                periodicInterestLabel.textContent = label;
            }
        } else {
            if (periodicInterestRow) periodicInterestRow.style.display = 'none';
        }

        const interestPaymentRow = document.getElementById('interestPaymentTimingRow');
        const interestPaymentEl = document.getElementById('interestPaymentTimingResult');
        if (isBridgeServicedOnly) {
            if (interestPaymentRow && interestPaymentEl) {
                const freqLabel = paymentFrequency === 'quarterly' ? 'Quarterly' : 'Monthly';
                const timingLabel = paymentTiming === 'advance' ? 'in Advance' : 'in Arrears';
                interestPaymentRow.style.display = 'table-row';
                interestPaymentEl.textContent = `${freqLabel} ${timingLabel}`;
            }
        } else if (interestPaymentRow) {
            interestPaymentRow.style.display = 'none';
        }

        // Display detailed payment schedule if available (for all loan types)
        this.displayDetailedPaymentSchedule(results);

        // Display tranche breakdown for development loans
        if (results.tranche_breakdown && results.tranche_breakdown.length > 0) {
            this.displayTrancheBreakdown(results.tranche_breakdown, currency);
        }

        // Display tranche schedule report in modal if available
        this.displayTrancheSchedule(results);

        // Update percentage displays with actual user input values
        this.updatePercentageDisplays();
    }

    displayDetailedPaymentSchedule(results) {
        // Hide payment schedule when Interest Retained is selected for Term or Bridge loans
        try {
            const loanTypeEl = document.getElementById('loanType');
            const repaymentEl = document.getElementById('repaymentOption');
            const loanType = loanTypeEl ? loanTypeEl.value : (results.loan_type || '');
            const repayment = repaymentEl ? repaymentEl.value : (results.repayment_option || '');
            const scheduleContainerEl = document.getElementById('detailedPaymentScheduleCard');
            if (loanType === 'development' || ((loanType === 'term' || loanType === 'bridge') && repayment === 'none')) {
                if (scheduleContainerEl) scheduleContainerEl.style.display = 'none';
                return; // don't render
            }
        } catch (e) { console.warn('Schedule visibility check failed:', e); }

        const scheduleContainer = document.getElementById('detailedPaymentScheduleCard');
        const scheduleBody = document.getElementById('detailedPaymentScheduleBody');
        const headerRow = scheduleContainer?.querySelector('thead tr');
        if (!this.defaultScheduleHeader && headerRow) {
            this.defaultScheduleHeader = headerRow.innerHTML;
        }
        
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
        
        const repaymentOption = results.repayment_option || results.repaymentOption || '';
        const isServicedOnly = repaymentOption === 'service_only';
        const isServicedCapital = repaymentOption === 'service_and_capital';
        const isFlexiblePayment = repaymentOption === 'flexible_payment';
        const isCapitalPaymentOnly = repaymentOption === 'capital_payment_only';

        if (headerRow) {
            if (isServicedOnly) {
                headerRow.innerHTML = `
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Start of Period</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">End of Period</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Days Held</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Opening Balance</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Interest Calculation</th>
                    <th class="px-2 text-center" style="color: #000; font-weight: bold; font-size: 0.875rem;">Interest Serviced</th>
                `;
            } else if (isServicedCapital || isFlexiblePayment || isCapitalPaymentOnly) {
                headerRow.innerHTML = `
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Period</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Start of Period</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">End of Period</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Days Held</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Capital Outstanding</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Annual Interest %</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Interest P.A.</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Scheduled Repayment</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Interest Accrued</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Interest Retained</th>
                    <th class="px-2 text-center" style="border-right: 1px solid #000; color: #000; font-weight: bold; font-size: 0.875rem;">Interest Refund</th>
                    <th class="px-2 text-center" style="color: #000; font-weight: bold; font-size: 0.875rem;">Running LTV</th>
                `;
            } else if (this.defaultScheduleHeader) {
                headerRow.innerHTML = this.defaultScheduleHeader;
            }
        }

        if (isServicedOnly) {
            let totalInterest = 0;
            let totalDays = 0;
            results.detailed_payment_schedule.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.style.border = '1px solid #000';
                tr.style.background = index % 2 === 0 ? '#f8f9fa' : 'white';

                const fixedRow = {
                    start_period: row.start_period,
                    end_period: row.end_period,
                    days_held: row.days_held,
                    opening_balance: String(row.opening_balance || '').replace(/[£€]/g, currentSymbol),
                    interest_calculation: String(row.interest_calculation || '').replace(/[£€]/g, currentSymbol).replace(/\s*\+?\s*fees/gi, '').trim(),
                    interest_amount: String(row.interest_amount || '').replace(/[£€]/g, currentSymbol)
                };

                const interestNumeric = parseFloat(fixedRow.interest_amount.replace(/[^0-9.-]/g, '')) || 0;
                totalInterest += interestNumeric;
                totalDays += parseFloat(fixedRow.days_held) || 0;

                tr.innerHTML = `
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.start_period}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.end_period}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.days_held}</td>
                    <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.opening_balance}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_calculation}</td>
                    <td class="py-1 px-2 text-end" style="color: #000; font-size: 0.875rem;">${fixedRow.interest_amount}</td>
                `;

                scheduleBody.appendChild(tr);
            });

            const totalRow = document.createElement('tr');
            totalRow.style.border = '1px solid #000';
            totalRow.style.background = '#f8f9fa';
            totalRow.innerHTML = `
                <td colspan="2" class="py-1 px-2 text-end fw-bold" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">Total</td>
                <td class="py-1 px-2 text-center fw-bold" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${totalDays}</td>
                <td class="py-1 px-2" style="border-right: 1px solid #000;"></td>
                <td class="py-1 px-2" style="border-right: 1px solid #000;"></td>
                <td class="py-1 px-2 text-end fw-bold" style="color: #000; font-size: 0.875rem;">${currentSymbol}${totalInterest.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
            `;
            scheduleBody.appendChild(totalRow);

            console.log('Detailed payment schedule displayed with', results.detailed_payment_schedule.length, 'rows');
            return;
        }

        if (isServicedCapital || isFlexiblePayment || isCapitalPaymentOnly) {
            let totalScheduled = 0;
            let totalAccrued = 0;
            let totalRetained = 0;
            let totalRefund = 0;
            let totalDays = 0;

            results.detailed_payment_schedule.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.style.border = '1px solid #000';
                tr.style.background = index % 2 === 0 ? '#f8f9fa' : 'white';

                const fixedRow = {
                    start_period: row.start_period,
                    end_period: row.end_period,
                    days_held: row.days_held,
                    // Use the per-period capital balance from the schedule without
                    // falling back to any summary total values. This ensures the
                    // first period reflects the "capital_outstanding" calculated
                    // by _generate_detailed_bridge_schedule.
                    capital_outstanding: row.capital_outstanding !== undefined
                        ? String(row.capital_outstanding).replace(/[£€]/g, currentSymbol)
                        : '',
                    annual_interest_rate: row.annual_interest_rate,
                    interest_pa: row.interest_pa,
                    scheduled_repayment: String(row.scheduled_repayment || '').replace(/[£€]/g, currentSymbol),
                    interest_accrued: String(row.interest_accrued || '').replace(/[£€]/g, currentSymbol),
                    interest_retained: String(row.interest_retained || '').replace(/[£€]/g, currentSymbol),
                    interest_refund: String(row.interest_refund || '').replace(/[£€]/g, currentSymbol),
                    running_ltv: row.running_ltv
                };

                const scheduledNumeric = parseFloat(fixedRow.scheduled_repayment.replace(/[^0-9.-]/g, '')) || 0;
                const accruedNumeric = parseFloat(fixedRow.interest_accrued.replace(/[^0-9.-]/g, '')) || 0;
                const retainedNumeric = parseFloat(fixedRow.interest_retained.replace(/[^0-9.-]/g, '')) || 0;
                const refundNumeric = parseFloat(fixedRow.interest_refund.replace(/[^0-9.-]/g, '')) || 0;

                totalScheduled += scheduledNumeric;
                totalAccrued += accruedNumeric;
                totalRetained += retainedNumeric;
                totalRefund += refundNumeric;
                totalDays += parseFloat(fixedRow.days_held) || 0;

                tr.innerHTML = `
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${index + 1}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.start_period}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.end_period}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.days_held}</td>
                    <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.capital_outstanding}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.annual_interest_rate}</td>
                    <td class="py-1 px-2 text-center" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_pa}</td>
                    <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.scheduled_repayment}</td>
                    <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_accrued}</td>
                    <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_retained}</td>
                    <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_refund}</td>
                    <td class="py-1 px-2 text-center" style="color: #000; font-size: 0.875rem;">${fixedRow.running_ltv}</td>
                `;

                scheduleBody.appendChild(tr);
            });

            const totalRow = document.createElement('tr');
            totalRow.style.border = '1px solid #000';
            totalRow.style.background = '#f8f9fa';
            totalRow.innerHTML = `
                <td colspan="3" class="py-1 px-2 text-end fw-bold" style="border-right: 1px solid #000; color: #000; font-size:0.875rem;">Total</td>
                <td class="py-1 px-2 text-center fw-bold" style="border-right: 1px solid #000; color: #000; font-size:0.875rem;">${totalDays}</td>
                <td colspan="3" class="py-1 px-2" style="border-right: 1px solid #000;"></td>
                <td class="py-1 px-2 text-end fw-bold" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${currentSymbol}${totalScheduled.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
                <td class="py-1 px-2 text-end fw-bold" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${currentSymbol}${totalAccrued.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
                <td class="py-1 px-2 text-end fw-bold" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${currentSymbol}${totalRetained.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
                <td class="py-1 px-2 text-end fw-bold" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${currentSymbol}${totalRefund.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}</td>
                <td class="py-1 px-2"></td>
            `;
            scheduleBody.appendChild(totalRow);

            console.log('Detailed payment schedule displayed with', results.detailed_payment_schedule.length, 'rows');
            return;
        }

        // Populate rows from detailed payment schedule (default behavior)
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
                interest_saving: String(row.interest_saving || '').replace(/[£€]/g, currentSymbol),
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
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.interest_saving}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.principal_payment}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.total_payment}</td>
                <td class="py-1 px-2 text-end" style="border-right: 1px solid #000; color: #000; font-size: 0.875rem;">${fixedRow.closing_balance}</td>
                <td class="py-1 px-2 text-center" style="color: #000; font-size: 0.875rem;">${fixedRow.balance_change}</td>
            `;

            scheduleBody.appendChild(tr);
        });

        console.log('Detailed payment schedule displayed with', results.detailed_payment_schedule.length, 'rows');
    }

    updateVisualizationButtonsVisibility(results) {
        const loanType = results.loan_type || document.getElementById('loanType')?.value || '';
        const repaymentOption = results.repayment_option || results.repaymentOption || document.getElementById('repaymentOption')?.value || '';
        const hideAll = loanType === 'bridge' && repaymentOption === 'none';
        const isServicedOnly = repaymentOption === 'service_only';

        const paymentScheduleBtn = document.querySelector('[data-bs-target="#paymentScheduleModal"]');
        const balanceBtn = document.querySelector('[data-bs-target="#balanceModal"]');

        if (paymentScheduleBtn) {
            paymentScheduleBtn.style.display = (hideAll || loanType === 'development' || loanType === 'development2') ? 'none' : '';
        }
        if (balanceBtn) {
            balanceBtn.style.display = hideAll ? 'none' : '';
        }

        if (loanType === 'development' || loanType === 'development2') {
            const modal = document.getElementById('paymentScheduleModal');
            if (modal) modal.style.display = 'none';
        } else {
            const modal = document.getElementById('paymentScheduleModal');
            if (modal) modal.style.display = '';
        }

        if (isServicedOnly) {
            const hideSelectors = [
                '[data-bs-target="#balanceModal"]'
            ];
            hideSelectors.forEach(sel => {
                const btn = document.querySelector(sel);
                if (btn) btn.style.display = 'none';
            });
            ['balanceModal'].forEach(id => {
                const modal = document.getElementById(id);
                if (modal) modal.style.display = 'none';
            });
        } else {
            ['balanceModal'].forEach(id => {
                const modal = document.getElementById(id);
                if (modal) modal.style.display = '';
            });
        }
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
        if (window.notifications) {
            window.notifications.error('Error: ' + message);
        } else {
            alert('Error: ' + message);
        }
    }

    // All other UI helper methods remain the same...
    updateRepaymentOptions() {
        try {
            const loanTypeElement = document.getElementById('loanType');
            if (!loanTypeElement) {
                console.warn('Loan type element not found');
                return;
            }

            const loanType = loanTypeElement.value;
            const optionsMap = {
                bridge: ['none', 'service_only', 'service_and_capital', 'capital_payment_only', 'flexible_payment'],
                term: ['service_only', 'service_and_capital'],
                development: ['none'],
                development2: ['none']
            };
            const allowed = optionsMap[loanType] || [];

            document.querySelectorAll('input[name="repaymentOptionToggle"]').forEach(radio => {
                const label = document.querySelector(`label[for="${radio.id}"]`);
                const show = allowed.includes(radio.value);
                radio.style.display = show ? '' : 'none';
                if (label) label.style.display = show ? '' : 'none';
                if (!show && radio.checked) {
                    radio.checked = false;
                }
            });

            let checked = document.querySelector('input[name="repaymentOptionToggle"]:checked');
            if (!checked && allowed.length) {
                const first = document.querySelector(`input[name="repaymentOptionToggle"][value="${allowed[0]}"]`);
                if (first) {
                    first.checked = true;
                    checked = first;
                }
            }

            const hidden = document.getElementById('repaymentOption');
            if (hidden && checked) {
                hidden.value = checked.value;
            }

            console.log('Repayment options updated successfully');
            this.update360DayVisibility();
        } catch (error) {
            console.error('Error in updateRepaymentOptions:', error);
        }
    }
    
    update360DayVisibility() {
        try {
            const loanTypeElement = document.getElementById('loanType');
            const loanTermElement = document.getElementById('loanTerm');
            const use360DaysSection = document.getElementById('use360DaysSection');
            
            if (!loanTypeElement || !loanTermElement || !use360DaysSection) {
                return;
            }
            
            const loanType = loanTypeElement.value;
            const loanTerm = parseInt(loanTermElement.value) || 0;
            
            // Show 360-day option only for Bridge loans with 12 months or less
            if (loanType === 'bridge' && loanTerm <= 12) {
                use360DaysSection.style.display = 'block';
            } else {
                use360DaysSection.style.display = 'none';
                // Uncheck the checkbox when hiding
                const use360DaysCheckbox = document.getElementById('use360Days');
                if (use360DaysCheckbox) {
                    use360DaysCheckbox.checked = false;
                }
            }
        } catch (error) {
            console.error('Error in update360DayVisibility:', error);
        }
    }

    setupImprovedInputFormatting() {
        // List of monetary input field IDs that need comma formatting
        const monetaryFields = [
            'propertyValue',
            'grossAmountFixed', 
            'grossAmountPercentage',
            'netAmountInput',
            'day1Advance',
            'legalFees',
            'siteVisitFee',
            'capitalRepayment',
            'flexiblePayment',
            'autoTotalAmount'
        ];

        monetaryFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                // Format on blur only - never on focus to avoid clearing
                field.addEventListener('blur', (e) => {
                    this.safeFormatInputValue(e.target);
                });
            }
        });
    }

    safeFormatInputValue(input) {
        const originalValue = input.value;
        
        // Only proceed if there's actually a value
        if (!originalValue || originalValue.trim() === '') {
            return;
        }
        
        // Remove existing commas and parse
        const cleanValue = originalValue.replace(/,/g, '');
        const numericValue = parseFloat(cleanValue);
        
        // Only format if it's a valid positive number
        if (!isNaN(numericValue) && numericValue > 0) {
            try {
                const formattedValue = numericValue.toLocaleString('en-GB', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 4
                });
                input.value = formattedValue;
            } catch (error) {
                // If formatting fails, keep original value
                console.warn('Number formatting failed:', error);
                input.value = originalValue;
            }
        }
        // For zero, negative, or invalid numbers, leave as typed
    }

    updateAutoTotalAmount() {
        try {
            const netInput = document.getElementById('netAmountInput');
            const day1Input = document.getElementById('day1Advance');
            const autoInput = document.getElementById('autoTotalAmount');
            if (!autoInput || !netInput) return;
            const net = parseFloat((netInput.value || '').replace(/,/g, '')) || 0;
            const day1 = parseFloat((day1Input?.value || '').replace(/,/g, '')) || 0;
            const remaining = Math.max(net - day1, 0);
            autoInput.value = remaining.toString();
        } catch (error) {
            console.error('Error updating Total Development Tranche:', error);
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

            // Show LTV simulation section for bridge/term with applicable repayment options
            const ltvSection = document.getElementById('ltvSimulationSection');
            if (ltvSection) {
                if ((loanType === 'bridge' || loanType === 'term') &&
                    (repaymentOption === 'service_and_capital' || repaymentOption === 'capital_payment_only' || repaymentOption === 'flexible_payment')) {
                    ltvSection.style.display = 'block';
                    showAdditionalParams = true;
                } else {
                    ltvSection.style.display = 'none';
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
            
            const interestTypeRadios = document.querySelectorAll('input[name="interestTypeToggle"]');
            if (loanType === 'development' || loanType === 'development2') {
                // Development loans default to net amount input
                document.getElementById('netAmount').checked = true;
                document.getElementById('grossAmount').checked = false;
                if (netAmountSection) netAmountSection.style.display = 'block';
                if (grossAmountSection) grossAmountSection.style.display = 'none';

                // Set interest calculation type to compound daily for development loans
                const compoundDaily = document.getElementById('interestCompoundDaily');
                if (compoundDaily) {
                    compoundDaily.checked = true;
                }
                const interestTypeHidden = document.getElementById('interestType');
                if (interestTypeHidden) {
                    interestTypeHidden.value = 'compound_daily';
                    interestTypeHidden.dispatchEvent(new Event('change'));
                }
                interestTypeRadios.forEach(r => r.disabled = true);
            } else {
                // Bridge and term loans default to gross amount input
                document.getElementById('grossAmount').checked = true;
                document.getElementById('netAmount').checked = false;
                if (grossAmountSection) grossAmountSection.style.display = 'block';
                if (netAmountSection) netAmountSection.style.display = 'none';

                // Enable interest calculation type selection for non-development loans
                interestTypeRadios.forEach(r => r.disabled = false);
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
            this.updateAutoTotalAmount();
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
            const loanPeriodInput = document.getElementById('autoLoanPeriod');
            let loanPeriod = parseInt(loanPeriodInput?.value);
            if (isNaN(loanPeriod)) {
                loanPeriod = 0;
                if (loanPeriodInput) loanPeriodInput.value = '0';
            }
            const interestRateInput = document.getElementById('autoInterestRate');
            let interestRate = parseFloat(interestRateInput?.value);
            if (isNaN(interestRate)) {
                interestRate = 0;
                if (interestRateInput) interestRateInput.value = '0';
            }
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
            
            if (loanPeriod === 0) {
                const loanTermInput = document.getElementById('loanTerm');
                loanPeriod = parseInt(loanTermInput?.value);
                if (isNaN(loanPeriod)) loanPeriod = 0;
                console.log('Using loan term from main form:', loanPeriod);
            }

            if (interestRate === 0) {
                const annualRateInput = document.getElementById('annualRateValue');
                interestRate = parseFloat(annualRateInput?.value);
                if (isNaN(interestRate)) interestRate = 0;
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
                if (window.notifications) {
                    window.notifications.warning('Please enter a valid total loan amount');
                } else {
                    alert('Please enter a valid total loan amount');
                }
                return;
            }

            if (!startDate) {
                if (window.notifications) {
                    window.notifications.warning('Please select a start date');
                } else {
                    alert('Please select a start date');
                }
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
                // Start auto-generated tranches one month after loan start
                releaseDate.setMonth(releaseDate.getMonth() + (i * monthInterval) + 1);
                
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
            if (window.notifications) {
                window.notifications.error('Error generating tranches: ' + error.message);
            } else {
                alert('Error generating tranches: ' + error.message);
            }
        }
    }

    increaseTranches() {
        const countElement = document.getElementById('trancheCount');
        const currentCount = parseInt(countElement.textContent);
        const newCount = currentCount + 1;
        
        countElement.textContent = newCount;
        this.createTrancheItem(newCount, 0, '', 12, `Tranche ${newCount}`);
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
                this.renumberTranches();
            }
        }
    }

    clearTranches() {
        const container = document.getElementById('tranchesContainer');
        if (container) {
            container.innerHTML = '';
        }
    }

    updateTranche(number) {
        this.openEditTrancheModal(number - 1, 'manual');
    }

    deleteTranche(number) {
        this.openDeleteTrancheModal(number - 1, 'manual');
    }

    renumberTranches() {
        const container = document.getElementById('tranchesContainer');
        const items = container ? container.querySelectorAll('.tranche-item') : [];
        items.forEach((item, index) => {
            const num = index + 1;
            item.setAttribute('data-tranche', num);
            const numberCell = item.querySelector('.tranche-number');
            if (numberCell) numberCell.textContent = num;
            item.querySelector('.edit-tranche-btn')?.setAttribute('onclick', `window.loanCalculator.openEditTrancheModal(${index}, 'manual')`);
            item.querySelector('.delete-tranche-btn')?.setAttribute('onclick', `window.loanCalculator.openDeleteTrancheModal(${index}, 'manual')`);
        });
        const countElement = document.getElementById('trancheCount');
        if (countElement) countElement.textContent = items.length;
    }

    createTrancheItem(number, amount = 0, date = '', rate = 12, description = '') {
        const container = document.getElementById('tranchesContainer');
        if (!container) {
            console.error('Could not find tranchesContainer element');
            return;
        }

        console.log(`Creating tranche item ${number} in container`, container);

        const trancheHtml = `
            <tr class="tranche-item" data-tranche="${number}">
                <td class="tranche-number">${number}</td>
                <td class="text-end">
                    <span class="currency-symbol">£</span><span class="tranche-amount-display">${(amount || 0).toFixed(2)}</span>
                    <input type="hidden" name="tranche_amounts[]" class="tranche-amount" value="${amount}">
                </td>
                <td>
                    <span class="tranche-date-display">${date}</span>
                    <input type="hidden" name="tranche_dates[]" class="tranche-date" value="${date}">
                </td>
                <td class="text-end">
                    <span class="tranche-rate-display">${(rate || 0).toFixed(2)}</span>
                    <input type="hidden" name="tranche_rates[]" class="tranche-rate" value="${rate}">
                </td>
                <td>
                    <span class="tranche-description-display">${description}</span>
                    <input type="hidden" name="tranche_descriptions[]" class="tranche-description" value="${description}">
                </td>
                <td>
                    <button type="button" class="btn btn-sm btn-outline-primary me-1 edit-tranche-btn" onclick="window.loanCalculator.openEditTrancheModal(${number - 1}, 'manual')"><i class="fas fa-edit"></i></button>
                    <button type="button" class="btn btn-sm btn-outline-danger delete-tranche-btn" onclick="window.loanCalculator.openDeleteTrancheModal(${number - 1}, 'manual')"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;

        container.insertAdjacentHTML('beforeend', trancheHtml);
        console.log(`Tranche item ${number} created successfully`);
        this.renumberTranches();
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
        this.updateRateEquivalenceNote();
    }

    updateRateEquivalenceNote() {
        const noteEl = document.getElementById('rateEquivalenceNote');
        if (!noteEl) return;

        const rateType = document.querySelector('input[name="rate_input_type"]:checked')?.value || 'annual';
        const annualInput = document.getElementById('annualRateValue');
        const monthlyInput = document.getElementById('monthlyRateValue');

        if (rateType === 'monthly') {
            const monthly = parseFloat(monthlyInput?.value);
            if (!isNaN(monthly)) {
                const annual = monthly * 12;
                noteEl.textContent = `Equivalent annual rate: ${annual.toFixed(2)}% p.a.`;
            } else {
                noteEl.textContent = '';
            }
        } else {
            const annual = parseFloat(annualInput?.value);
            if (!isNaN(annual)) {
                const monthly = annual / 12;
                noteEl.textContent = `Equivalent monthly rate: ${monthly.toFixed(2)}% pcm`;
            } else {
                noteEl.textContent = '';
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
        const propertyValueInput = document.getElementById('propertyValue');
        const percentageInput = document.getElementById('grossAmountPercentage');
        const grossFixedInput = document.getElementById('grossAmountFixed');

        const propertyValue = parseFloat((propertyValueInput?.value || '').replace(/,/g, '')) || 0;
        const percentage = parseFloat((percentageInput?.value || '').replace(/,/g, '')) || 0;

        if (propertyValue > 0 && percentage > 0 && grossFixedInput) {
            const grossAmount = (propertyValue * percentage / 100).toFixed(2);
            grossFixedInput.value = grossAmount;
        } else if (grossFixedInput) {
            grossFixedInput.value = '';
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

    displayTrancheSchedule(results) {
        const btn = document.getElementById('trancheScheduleBtn');
        const body = document.getElementById('trancheScheduleBody');
        if (!btn || !body) return;

        const schedule = results.detailed_tranche_schedule;
        if (!Array.isArray(schedule) || schedule.length === 0) {
            btn.style.display = 'none';
            body.innerHTML = '';
            return;
        }

        btn.style.display = 'inline-block';
        body.innerHTML = '';

        const currency = document.getElementById('currency').value;
        const symbol = this.getCurrencySymbol(currency);

        const propertyValue = parseFloat(results.propertyValue || 0);

        const formatMoney = (val) => {
            const num = typeof val === 'string' ? parseFloat(val) : val;
            if (isNaN(num)) return val ?? '';
            return symbol + num.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        };

        let totalDays = 0;
        let totalTranche = 0;
        let totalInterest = 0;

        schedule.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.style.border = '1px solid #000';
            tr.style.background = index % 2 === 0 ? '#f8f9fa' : 'white';

            const closingVal = typeof row.closing_balance === 'string' ? parseFloat(row.closing_balance.replace(/[^0-9.-]/g, '')) : row.closing_balance;
            const runningLTV = propertyValue > 0 && !isNaN(closingVal) ? `${((closingVal / propertyValue) * 100).toFixed(2)}%` : '';

            totalDays += parseFloat(row.days_held) || 0;
            totalTranche += parseFloat(String(row.tranche_release).replace(/[^0-9.-]/g, '')) || 0;
            totalInterest += parseFloat(String(row.interest).replace(/[^0-9.-]/g, '')) || 0;

            tr.innerHTML = `
                <td class="py-1 px-2 text-center" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${row.period}</td>
                <td class="py-1 px-2 text-center" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${row.start_period || ''}</td>
                <td class="py-1 px-2 text-center" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${row.end_period || ''}</td>
                <td class="py-1 px-2 text-center" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${row.days_held ?? ''}</td>
                <td class="py-1 px-2 text-end" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(row.opening_balance)}</td>
                <td class="py-1 px-2 text-center" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${row.interest_calculation || ''}</td>
                <td class="py-1 px-2 text-end" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(row.tranche_release)}</td>
                <td class="py-1 px-2 text-end" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(row.interest)}</td>
                <td class="py-1 px-2 text-end" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(row.principal)}</td>
                <td class="py-1 px-2 text-end" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(row.total_payment)}</td>
                <td class="py-1 px-2 text-end" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(row.closing_balance)}</td>
                <td class="py-1 px-2 text-center" style="color:#000; font-size:0.875rem;">${runningLTV}</td>
            `;
            body.appendChild(tr);
        });

        const totalRow = document.createElement('tr');
        totalRow.style.border = '1px solid #000';
        totalRow.style.background = '#f8f9fa';
        totalRow.innerHTML = `
            <td colspan="3" class="py-1 px-2 text-end fw-bold" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">Total</td>
            <td class="py-1 px-2 text-center fw-bold" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${totalDays}</td>
            <td class="py-1 px-2" style="border-right:1px solid #000;"></td>
            <td class="py-1 px-2" style="border-right:1px solid #000;"></td>
            <td class="py-1 px-2 text-end fw-bold" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(totalTranche)}</td>
            <td class="py-1 px-2 text-end fw-bold" style="border-right:1px solid #000; color:#000; font-size:0.875rem;">${formatMoney(totalInterest)}</td>
            <td colspan="3" class="py-1 px-2"></td>
        `;
        body.appendChild(totalRow);
    }

    displayTrancheBreakdown(trancheData, currency) {
        console.log('Displaying tranche breakdown:', trancheData);
        this.trancheBreakdownData = trancheData.map(t => ({...t}));
        this.trancheCurrency = currency;

        // Find or create tranche breakdown table container
        let trancheContainer = document.getElementById('trancheBreakdownContainer');
        if (!trancheContainer) {
            // Create container if it doesn't exist
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) {
                trancheContainer = document.createElement('div');
                trancheContainer.id = 'trancheBreakdownContainer';
                trancheContainer.className = 'card mt-2';
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
                    <table class="table table-striped table-hover table-sm">
                        <thead class="table-dark">
                            <tr>
                                <th>Tranche</th>
                                <th>Release Date</th>
                                <th>Amount</th>
                                <th>Description</th>
                                <th>Cumulative</th>
                                <th>Rate</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.trancheBreakdownData.map((tranche, index) => `
                                <tr>
                                    <td>${tranche.tranche_number}</td>
                                    <td>${this.formatDate(tranche.release_date)}</td>
                                    <td>${currency}${tranche.amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td>${tranche.description}</td>
                                    <td>${currency}${tranche.cumulative_amount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                                    <td>${tranche.interest_rate.toFixed(2)}%</td>
                                    <td>
                                        <button type="button" class="btn btn-sm btn-outline-primary me-1" onclick="window.loanCalculator.openEditTrancheModal(${index})"><i class="fas fa-edit"></i></button>
                                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="window.loanCalculator.openDeleteTrancheModal(${index})"><i class="fas fa-trash"></i></button>
                                    </td>
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

    openEditTrancheModal(index, context = 'breakdown') {
        this.currentTrancheIndex = index;
        this.editContext = context;
        if (context === 'manual') {
            const rows = document.querySelectorAll('#tranchesContainer .tranche-item');
            const row = rows[index];
            if (!row) return;
            document.getElementById('editTrancheNumber').textContent = row.querySelector('.tranche-number')?.textContent || index + 1;
            document.getElementById('editTrancheAmount').value = row.querySelector('input.tranche-amount')?.value || 0;
            document.getElementById('editTrancheDate').value = row.querySelector('input.tranche-date')?.value || '';
            document.getElementById('editTrancheRate').value = row.querySelector('input.tranche-rate')?.value || 0;
            document.getElementById('editTrancheDescription').value = row.querySelector('input.tranche-description')?.value || '';
        } else {
            const data = this.trancheBreakdownData[index];
            if (!data) return;
            document.getElementById('editTrancheNumber').textContent = data.tranche_number;
            document.getElementById('editTrancheAmount').value = data.amount;
            document.getElementById('editTrancheDate').value = data.release_date;
            document.getElementById('editTrancheRate').value = data.interest_rate;
            document.getElementById('editTrancheDescription').value = data.description;
        }
        const modal = new bootstrap.Modal(document.getElementById('trancheEditModal'));
        modal.show();
    }

    saveTrancheEdits() {
        const idx = this.currentTrancheIndex;
        if (idx === null) return;
        if (this.editContext === 'manual') {
            const rows = document.querySelectorAll('#tranchesContainer .tranche-item');
            const row = rows[idx];
            if (!row) return;
            const amount = parseFloat(document.getElementById('editTrancheAmount').value) || 0;
            const date = document.getElementById('editTrancheDate').value;
            const rate = parseFloat(document.getElementById('editTrancheRate').value) || 0;
            const description = document.getElementById('editTrancheDescription').value;
            row.querySelector('input.tranche-amount').value = amount;
            row.querySelector('.tranche-amount-display').textContent = amount.toFixed(2);
            row.querySelector('input.tranche-date').value = date;
            row.querySelector('.tranche-date-display').textContent = date;
            row.querySelector('input.tranche-rate').value = rate;
            row.querySelector('.tranche-rate-display').textContent = rate.toFixed(2);
            row.querySelector('input.tranche-description').value = description;
            row.querySelector('.tranche-description-display').textContent = description;
        } else {
            const data = this.trancheBreakdownData[idx];
            data.amount = parseFloat(document.getElementById('editTrancheAmount').value) || 0;
            data.release_date = document.getElementById('editTrancheDate').value;
            data.interest_rate = parseFloat(document.getElementById('editTrancheRate').value) || 0;
            data.description = document.getElementById('editTrancheDescription').value;
            this.displayTrancheBreakdown(this.trancheBreakdownData, this.trancheCurrency);
        }
        const modalEl = document.getElementById('trancheEditModal');
        bootstrap.Modal.getInstance(modalEl).hide();
    }

    openDeleteTrancheModal(index, context = 'breakdown') {
        this.currentTrancheIndex = index;
        this.editContext = context;
        const modal = new bootstrap.Modal(document.getElementById('trancheDeleteModal'));
        modal.show();
    }

    confirmDeleteTranche() {
        const idx = this.currentTrancheIndex;
        if (idx === null) return;
        if (this.editContext === 'manual') {
            const rows = document.querySelectorAll('#tranchesContainer .tranche-item');
            const row = rows[idx];
            if (row) {
                row.remove();
                this.renumberTranches();
            }
        } else {
            this.trancheBreakdownData.splice(idx, 1);
            this.displayTrancheBreakdown(this.trancheBreakdownData, this.trancheCurrency);
        }
        const modalEl = document.getElementById('trancheDeleteModal');
        bootstrap.Modal.getInstance(modalEl).hide();
    }

    populateBreakdownModal() {
        const modalBody = document.getElementById('calculationBreakdownContent');
        if (!modalBody) return;

        if (!this.currentResults) {
            modalBody.innerHTML = '<p>No calculation results available. Please run a calculation first.</p>';
            return;
        }

        const r = this.currentResults;
        const currency = this.getCurrencySymbol(r.currency);
        const formatMoney = (val) => {
            const num = typeof val === 'number' ? val : parseFloat(String(val).replace(/[,£€]/g, '')) || 0;
            return currency + num.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        };

        const gross = formatMoney(r.grossAmount || r.gross_amount || 0);
        const arrangementNum = parseFloat(r.arrangementFee || 0);
        const legalNum = parseFloat(r.legalCosts || r.legalFees || 0);
        const siteNum = parseFloat(r.siteVisitFee || 0);
        const titleNum = parseFloat(r.titleInsurance || 0);
        const interestNum = parseFloat(r.totalInterest || 0);
        const paymentFrequency = r.payment_frequency || document.querySelector('input[name="payment_frequency"]:checked')?.value || 'monthly';
        const arrangement = formatMoney(arrangementNum);
        const legal = formatMoney(legalNum);
        const site = formatMoney(siteNum);
        const title = formatMoney(titleNum);
        const interest = formatMoney(interestNum);
        const day1 = formatMoney(r.day1NetAdvance || r.day1Advance || r.netDay1Advance || 0);
        const totalNet = formatMoney(r.totalNetAdvance || 0);
        const propertyValue = parseFloat(r.propertyValue || 0);
        const grossNum = parseFloat(r.grossAmount || r.gross_amount || 0);
        const startLTV = propertyValue > 0 ? ((grossNum / propertyValue) * 100).toFixed(2) : '0.00';
        let endLTV = startLTV;
        if (r.detailed_payment_schedule && r.detailed_payment_schedule.length > 0 && propertyValue > 0) {
            const last = r.detailed_payment_schedule[r.detailed_payment_schedule.length - 1];
            const closing = parseFloat(String(last.closing_balance || '').replace(/[,£€]/g, '')) || 0;
            endLTV = ((closing / propertyValue) * 100).toFixed(2);
        }

        const rateEl = document.getElementById('interestRatePercentageDisplay');
        const rateText = rateEl ? rateEl.textContent.trim() : '';
        const loanTerm = r.loanTerm || r.loan_term || 0;
        const totalFeesNum = arrangementNum + legalNum + siteNum + titleNum;
        const totalFees = formatMoney(totalFeesNum);

        const arrangementPctEl = document.getElementById('arrangementFeePercentageDisplay');
        const arrangementPctText = arrangementPctEl ? arrangementPctEl.textContent.trim() : '';
        const titlePctEl = document.getElementById('titleInsurancePercentageDisplay');
        const titlePctText = titlePctEl ? titlePctEl.textContent.trim() : '';

        let trancheHtml = '';
        if (r.tranche_breakdown && r.tranche_breakdown.length > 0) {
            trancheHtml = '<h6>Tranche Drawdowns</h6>' +
                '<table class="table table-sm"><thead><tr><th>#</th><th>Date</th><th>Amount</th><th>Description</th></tr></thead><tbody>' +
                r.tranche_breakdown.map(t => `
                    <tr>
                        <td>${t.tranche_number}</td>
                        <td>${this.formatDate(t.release_date)}</td>
                        <td>${formatMoney(t.amount)}</td>
                        <td>${t.description || ''}</td>
                    </tr>
                `).join('') +
                '</tbody></table>';
        }

        let scheduleHtml = '';
        if (r.detailed_payment_schedule && r.detailed_payment_schedule.length > 0) {
            scheduleHtml = '<h6>Payment Schedule</h6>' +
                '<table class="table table-sm"><thead><tr><th>Period</th><th>Interest</th><th>Principal</th><th>Balance</th></tr></thead><tbody>' +
                r.detailed_payment_schedule.map((p, idx) => {
                    const interestAmt = formatMoney(p.interest_amount || p.interest || 0);
                    const principalAmt = formatMoney(p.principal_payment || p.principal || p.tranche_release || 0);
                    const balanceAmt = formatMoney(p.closing_balance || 0);
                    return `<tr><td>${idx + 1}</td><td>${interestAmt}</td><td>${principalAmt}</td><td>${balanceAmt}</td></tr>`;
                }).join('') +
                '</tbody></table>';
        }

        const interestSavingsValue = parseFloat(r.interestSavings ?? r.interest_savings ?? 0);
        let interestSavingsHtml = '';
        if (interestSavingsValue > 0) {
            interestSavingsHtml = `<p><strong>Interest Savings:</strong> ${formatMoney(interestSavingsValue)} compared to an interest-only loan.</p>`;
        }

        // Determine interest calculation description
        const interestType = r.interest_type || 'simple';
        const use360 = r.use_360_days || (document.getElementById('use360Days') ? document.getElementById('use360Days').checked : false);
        const daysPerYear = use360 ? 360 : 365;
        let calcDescription = '';
        switch (interestType) {
            case 'compound_daily':
                calcDescription = `Compound daily interest where <code>Interest = Principal × (1 + Rate / ${daysPerYear})<sup>${daysPerYear} × Time</sup> - Principal</code>`;
                break;
            case 'compound_monthly':
                calcDescription = 'Compound monthly interest where <code>Interest = Principal × (1 + Rate / 12)<sup>12 × Time</sup> - Principal</code>';
                break;
            case 'compound_quarterly':
                calcDescription = 'Compound quarterly interest where <code>Interest = Principal × (1 + Rate / 4)<sup>4 × Time</sup> - Principal</code>';
                break;
            default:
                calcDescription = 'Simple interest where <code>Interest = Principal × Rate × Time</code>';
        }

        // Determine repayment method description
        const loanType = r.loan_type || document.getElementById('loanType')?.value || '';
        const repaymentOption = r.repaymentOption || r.repayment_option || document.getElementById('repaymentOption')?.value || 'none';
        let repaymentDescription = '';
        switch (repaymentOption) {
            case 'none':
            case 'retained':
                repaymentDescription = 'Interest retained  total interest is deducted at the start and repaid with the principal at the end.';
                break;
            case 'service_only':
                repaymentDescription = 'Serviced interest  interest is paid periodically while principal is repaid at maturity.';
                break;
            case 'service_and_capital':
                repaymentDescription = 'Capital & interest  regular payments amortise the loan using <code>Payment = P × r / (1 - (1 + r)<sup>-n</sup>)</code>.';
                break;
            case 'capital_payment_only':
                repaymentDescription = 'Capital payments only  interest is retained upfront and scheduled capital payments reduce the balance.';
                break;
            case 'flexible_payment':
                repaymentDescription = 'Flexible payment  custom payments reduce the balance while any shortfall accrues interest.';
                break;
            default:
                repaymentDescription = 'Standard repayment schedule.';
        }

        // Net-to-gross formula description when user inputs net amount
        const amountInputType = r.amount_input_type || document.querySelector('input[name="amount_input_type"]:checked')?.value || 'gross';
        let netToGrossDescription = '';
        if (amountInputType === 'net') {
            switch (repaymentOption) {
                case 'service_only':
                    netToGrossDescription = 'Gross = (Net + Legal + Site) / (1 - Arrangement - (Rate / 12) - Title)';
                    break;
                case 'service_and_capital':
                case 'flexible_payment':
                    netToGrossDescription = 'Gross = (Net + Legal + Site) / (1 - Arrangement - Title)';
                    break;
                default:
                    // none and capital_payment_only
                    netToGrossDescription = 'Gross = (Net + Legal + Site) / (1 - Arrangement - Rate × Time - Title)';
            }
        }

        // Fee impact on net and gross amounts
        let feeImpactDescription = `Fees total ${totalFees} (arrangement ${arrangement}, legal ${legal}, site visit ${site}, title insurance ${title}).`;
        if (['service_only', 'service_and_capital', 'flexible_payment'].includes(repaymentOption)) {
            feeImpactDescription += ' Net = Gross - Fees. Interest is calculated on the gross amount.';
        } else {
            feeImpactDescription += ' Net = Gross - Fees - Interest. Interest is calculated on the gross amount.';
        }

        // Development loan goal seek description
        let goalSeekDescription = '';
        if (loanType === 'development') {
            goalSeekDescription = 'Uses Excel-style Goal Seek to find the gross amount where Net = Gross - Fees - Interest.';
        }

        // Calculate daily, periodic and yearly interest based on gross amount and annual rate
        const annualRateNum = parseFloat(r.interestRate || r.interest_rate || 0) / 100;
        const dailyInterestNum = grossNum * annualRateNum / daysPerYear;
        const periodicInterestNum = grossNum * annualRateNum / (paymentFrequency === 'quarterly' ? 4 : 12);
        const yearlyInterestNum = grossNum * annualRateNum;
        const dailyInterest = formatMoney(dailyInterestNum);
        const periodicInterest = formatMoney(periodicInterestNum);
        const yearlyInterest = formatMoney(yearlyInterestNum);
        const periodicLabel = paymentFrequency === 'quarterly' ? 'Quarterly' : 'Monthly';

        const interestDeducted = ['none', 'retained', 'capital_payment_only'].includes(repaymentOption);
        const netNum = grossNum - arrangementNum - legalNum - siteNum - titleNum - (interestDeducted ? interestNum : 0);
        const net = formatMoney(netNum);
        const netFormula = `Net = Gross – Arrangement Fee – Legal Fees – Site Visit Fee – Title Insurance${interestDeducted ? ' – Retained Interest' : ''}`;
        const retainedInterestFormula = interestDeducted ? `(Interest Rate × Loan Term) × Gross` : '';

        // Special breakdown for bridge retained interest when user inputs gross amount
        if (loanType === 'bridge' && interestDeducted && amountInputType === 'gross') {
            modalBody.innerHTML = `
                <h6>Gross to Net Calculation</h6>
                <p>The formula for a Gross to Net bridge loan with retained interest is as follows:</p>
                <ul>
                    <li><strong>Gross</strong> = Defined by User</li>
                    <li><strong>Net</strong> = Gross – Arrangement Fee – Legal Fees – Site Visit Fee – Title Insurance – Total Interest</li>
                    <li><strong>Total Interest</strong> = Interest Rate × Loan Term × Gross</li>
                </ul>
                <h6>Net Loan Calculation Step by Step</h6>
                <table class="table table-sm table-bordered mb-3">
                    <tbody>
                        <tr><th scope="row">Gross</th><td>${gross}</td></tr>
                        <tr><th scope="row">Arrangement Fee = ${arrangementPctText} × Gross</th><td>${arrangement}</td></tr>
                        <tr><th scope="row">Legal Fees</th><td>${legal}</td></tr>
                        <tr><th scope="row">Site Visit Fee</th><td>${site}</td></tr>
                        <tr><th scope="row">Title Insurance = ${titlePctText} × Gross</th><td>${title}</td></tr>
                        <tr><th scope="row">Total Interest = ${rateText} × ${loanTerm} months ÷ 12 × Gross</th><td>${interest}</td></tr>
                        <tr class="table-active fw-bold"><th scope="row">Net</th><td>${net}</td></tr>
                    </tbody>
                </table>
                <p><strong>Term:</strong> ${loanTerm} Months</p>
                <p><strong>Days in Year:</strong> ${daysPerYear}</p>
                <p>Retained interest means total interest is deducted at the start and repaid when the loan redeems.</p>
            `;
            return;
        }

        modalBody.innerHTML = `
            <p><strong>Calculation Engine:</strong> The calculator uses ${calcDescription}.</p>
            <p><strong>Repayment Method:</strong> ${repaymentDescription}</p>
            ${amountInputType === 'net' ? `<p><strong>Net to Gross:</strong> ${netToGrossDescription}</p>` : ''}
            <p><strong>Fee Impact:</strong> ${feeImpactDescription}</p>
            ${loanType === 'development' ? `<p><strong>Goal Seek Logic:</strong> ${goalSeekDescription}</p>` : ''}
            <p><strong>Interest Rate:</strong> ${rateText} for ${loanTerm} months.</p>
            <p><strong>Interest Breakdown:</strong> Daily ${dailyInterest}, ${periodicLabel} ${periodicInterest}, Yearly ${yearlyInterest}.</p>
            
            <h6>Gross to Net Calculation</h6>
            <p class="mb-2"><strong>Formula:</strong> ${netFormula}</p>
            <table class="table table-sm table-bordered mb-3">
                <tbody>
                    <tr><th scope="row">Gross</th><td>${gross}</td></tr>
                    <tr><th scope="row">Arrangement Fee (${arrangementPctText})</th><td>${arrangement}</td></tr>
                    <tr><th scope="row">Legal Fees</th><td>${legal}</td></tr>
                    <tr><th scope="row">Site Visit Fee</th><td>${site}</td></tr>
                    <tr><th scope="row">Title Insurance (${titlePctText})</th><td>${title}</td></tr>
                    ${interestDeducted ? `<tr><th scope="row">Retained Interest (${rateText} for ${loanTerm} months)</th><td>${interest}</td></tr>` : ''}
                    <tr class="table-active fw-bold"><th scope="row">Net</th><td>${net}</td></tr>
                </tbody>
            </table>
            ${interestDeducted ? `<p><strong>Retained Interest:</strong> ${retainedInterestFormula} = ${interest}</p>` : ''}
            <p><strong>Loan to Value:</strong> start ${startLTV}% &rarr; end ${endLTV}%.</p>
            ${interestSavingsHtml}
            ${trancheHtml}
            ${scheduleHtml}
        `;

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
        if (this.chartGenerationInProgress) {
            console.log('Chart generation already in progress, skipping...');
            return;
        }

        try {
            this.chartGenerationInProgress = true;
            this.clearExistingCharts();

            setTimeout(() => {
                try {
                    if (!document.getElementById('loanBreakdownChart')) {
                        console.error('Loan breakdown chart canvas not found');
                        return;
                    }

                    const loanType = results.loan_type || '';
                    const repaymentOption = results.repayment_option || results.repaymentOption || '';
                    const isBridgeRetained = loanType === 'bridge' && repaymentOption === 'none';
                    const isServicedOnly = repaymentOption === 'service_only';

                    this.createLoanBreakdownChart(results);

                    if (!isServicedOnly && !isBridgeRetained && results.detailed_payment_schedule && results.detailed_payment_schedule.length > 0) {
                        this.createBalanceOverTimeChart(results);
                    }

                    console.log('All charts generated successfully');
                } catch (delayedError) {
                    console.error('Error in delayed chart generation:', delayedError);
                } finally {
                    this.chartGenerationInProgress = false;
                }
            }, 50);
        } catch (error) {
            console.error('Error generating charts:', error);
            this.chartGenerationInProgress = false;
        }
    }

    setupModalResizeHandlers() {
        const mappings = [
            {modal: 'loanBreakdownModal', key: 'loanBreakdown'},
            {modal: 'balanceModal', key: 'balanceOverTime'}
        ];
        mappings.forEach(({modal, key}) => {
            const modalEl = document.getElementById(modal);
            if (modalEl) {
                modalEl.addEventListener('shown.bs.modal', () => {
                    const chart = this.charts[key];
                    if (chart) {
                        chart.resize();
                    }
                });
            }
        });
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

        // Dark palette colors for loan breakdown chart
        const darkPalette = ['#0b0b16', '#b49b5c', '#ffffff', '#3a3a3a', '#6b6b6b', '#9e9e9e'];

        const data = {
            labels: ['Total Net Advance', 'Arrangement Fee', 'Legal Costs', 'Site Visit Fee', 'Title Insurance', 'Total Interest'],
            datasets: [{
                data: [totalNetAdvance, arrangementFee, legalFees, siteVisitFee, titleInsurance, totalInterest],
                backgroundColor: darkPalette,
                borderWidth: 2,
                borderColor: '#0b0b16',
                hoverOffset: 20
            }]
        };

        let chartConfig = {
            type: 'doughnut', data: data, options: { maintainAspectRatio: false, layout: { padding: { right: 20, bottom: 20 } },   cutout: '60%', maintainAspectRatio: false, layout: { padding: { bottom: 36 } }, 
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right', labels: { boxWidth: 10, padding: 8 },
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

        if (ctx && ctx.parentNode) { ctx.parentNode.style.height = '460px'; }
        if (ctx && ctx.canvas) { ctx.canvas.style.height = '420px'; ctx.canvas.style.display = 'block'; }
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

        // Convert interest values to a running cumulative sum
        let cumulativeInterest = 0;
        const interestData = schedule.map(entry => {
            const interestRaw = entry.interest_amount || entry.interest || 0;
            let interestValue = 0;
            if (typeof interestRaw === 'number') {
                interestValue = interestRaw;
            } else if (typeof interestRaw === 'string') {
                interestValue = parseFloat(interestRaw.replace(/[£€,]/g, '')) || 0;
            }
            cumulativeInterest += interestValue;
            return cumulativeInterest;
        });

        const data = {
            labels: labels,
            datasets: [
                {
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
                },
                {
                    label: 'Interest Payment',
                    data: interestData,
                    borderColor: 'rgba(70, 130, 180, 1)',
                    backgroundColor: 'rgba(70, 130, 180, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.1,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: 'rgba(70, 130, 180, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    yAxisID: 'y1'
                }
            ]
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
                            },
                            y1: {
                                title: {
                                    display: true,
                                    text: `Interest (${results.currencySymbol || results.currency_symbol || '£'})`
                                },
                                position: 'right',
                                beginAtZero: true,
                                grid: {
                                    drawOnChartArea: false
                                }
                            }
                        },
                        plugins: {
                            title: {
                                display: true,
                                text: 'Loan Balance & Interest Over Time',
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


    // Update percentage displays with actual user input values
    updatePercentageDisplays() {
        console.log('Updating percentage displays...');
        
        // Update arrangement fee percentage
        const arrangementFeePercentageEl = document.getElementById('arrangementFeePercentageDisplay');
        const arrangementFeeInput = document.getElementById('arrangementFeeRate');
        console.log('Arrangement fee elements found:', !!arrangementFeePercentageEl, !!arrangementFeeInput);
        if (arrangementFeePercentageEl && arrangementFeeInput) {
            const parsedArrangement = parseFloat(arrangementFeeInput.value);
            const arrangementFeeRate = isNaN(parsedArrangement) ? 0 : parsedArrangement;
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
            const parsedTitle = parseFloat(titleInsuranceInput.value);
            const titleInsuranceRate = isNaN(parsedTitle) ? 0 : parsedTitle;
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
                interestRate = (parseFloat(monthlyRateInput?.value) || 1.0) * 12; // Convert monthly to annual for display
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
    const watchedSelects = ['loanType', 'repaymentOption', 'paymentTiming', 'paymentFrequency', 'loanTerm', 'interestType'];
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
    const watchedSelects = ['loanType', 'repaymentOption', 'paymentTiming', 'paymentFrequency', 'loanTerm', 'interestType'];
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

// Calculator initialization is handled by the calculator.html template
// Auto-update listeners are added after calculator initialization

// === Prevent blur formatting for autoTotalAmount ===
document.getElementById('autoTotalAmount')?.addEventListener('blur', function(e) {
    e.stopImmediatePropagation(); // Block other blur handlers
}, true); // capture phase to intercept early

// === LTV Targeting Simulation Helpers ===
LoanCalculator.prototype.initializeLTVTargetControls = function() {
    const checkbox = document.getElementById('ltvTargetCheckbox');
    const inputsSection = document.getElementById('ltvTargetInputs');
    if (!checkbox) return;

    checkbox.addEventListener('change', () => {
        if (inputsSection) inputsSection.style.display = checkbox.checked ? 'block' : 'none';
        if (checkbox.checked) {
            this.calculateLTVSimulation(this.currentResults || {});
        }
    });

    document.getElementById('targetLTVExit')?.addEventListener('input', () => {
        this.calculateLTVSimulation(this.currentResults || {});
    });

    const list = document.getElementById('progressiveLTVList');
    document.getElementById('addLTVTarget')?.addEventListener('click', () => {
        if (!list) return;
        const row = document.createElement('div');
        row.className = 'row g-2 align-items-center ltv-progressive-row mb-2';
        row.innerHTML = `
            <div class="col-5"><input type="number" class="form-control ltv-month" min="1" placeholder="Month"></div>
            <div class="col-5">
                <div class="input-group">
                    <input type="number" class="form-control ltv-percent" min="0" max="100" step="0.01" placeholder="LTV %">
                    <span class="input-group-text">%</span>
                </div>
            </div>
            <div class="col-2"><button type="button" class="btn btn-outline-danger btn-sm remove-ltv-target">&times;</button></div>`;
        list.appendChild(row);
    });

    list?.addEventListener('input', () => {
        this.calculateLTVSimulation(this.currentResults || {});
    });

    list?.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-ltv-target')) {
            e.target.closest('.ltv-progressive-row')?.remove();
            this.calculateLTVSimulation(this.currentResults || {});
        }
    });
};

LoanCalculator.prototype.calculateLTVSimulation = function(results) {
    const checkbox = document.getElementById('ltvTargetCheckbox');
    if (!checkbox || !checkbox.checked) return;

    const propertyValue = parseFloat(results.propertyValue || document.getElementById('propertyValue')?.value || 0);
    const grossAmount = parseFloat(results.grossAmount || document.getElementById('grossAmountFixed')?.value || 0);
    const loanTerm = parseInt(results.loanTerm || document.getElementById('loanTerm')?.value || 0);
    if (!propertyValue || !grossAmount || !loanTerm) return;

    let targets = [];
    const exitVal = parseFloat(document.getElementById('targetLTVExit')?.value);
    if (!isNaN(exitVal)) {
        targets.push({month: loanTerm, ltv: exitVal});
    }

    document.querySelectorAll('.ltv-progressive-row').forEach(row => {
        const month = parseInt(row.querySelector('.ltv-month').value);
        const ltv = parseFloat(row.querySelector('.ltv-percent').value);
        if (!isNaN(month) && !isNaN(ltv) && month > 0 && month <= loanTerm) {
            targets.push({month, ltv});
        }
    });

    if (targets.length === 0) return;

    targets.sort((a,b) => a.month - b.month);
    if (!targets.some(t => t.month === loanTerm) && !isNaN(exitVal)) {
        targets.push({month: loanTerm, ltv: exitVal});
    }

    let prevMonth = 0;
    let balance = grossAmount;
    let totalCapital = 0;
    const schedule = [];

    const repaymentOption = document.getElementById('repaymentOption')?.value;

    targets.forEach(t => {
        const targetBalance = propertyValue * (t.ltv / 100);
        let months = t.month - prevMonth;

        // Capital payment only loans retain full interest on day 1 and
        // settle the remaining principal in the final period.  This means
        // regular capital repayments occur in the months between those two
        // events.  Reduce the month count accordingly so the calculated
        // monthly capital brings the balance to the desired target.
        if (repaymentOption === 'capital_payment_only') {
            if (prevMonth === 0) months -= 1;       // skip day‑1 retained interest
            if (t.month === loanTerm) months -= 1;  // exclude final balloon repayment
        }

        const capitalNeeded = Math.max(0, balance - targetBalance);
        const monthlyCapital = months > 0 ? capitalNeeded / months : 0;
        schedule.push({start: prevMonth + 1, end: t.month, monthly: monthlyCapital});
        totalCapital += capitalNeeded;
        balance = targetBalance;
        prevMonth = t.month;
    });

    const currencyCode = results.currency || document.getElementById('currency')?.value || 'GBP';
    const totalEl = document.getElementById('ltvTotalCapital');
    if (totalEl) {
        totalEl.textContent = Novellus.utils.formatCurrency(totalCapital, currencyCode);
    }

    const scheduleContainer = document.getElementById('ltvCapitalSchedule');
    if (scheduleContainer) {
        scheduleContainer.innerHTML = '';
        schedule.forEach(seg => {
            const p = document.createElement('p');
            p.textContent = `Months ${seg.start}-${seg.end}: ${Novellus.utils.formatCurrency(seg.monthly, currencyCode)} per month`;
            scheduleContainer.appendChild(p);
        });
    }

    // Auto-populate repayment field when a single LTV target is provided
    const amount = schedule[0]?.monthly || 0;
    if (schedule.length === 1) {
        if (repaymentOption === 'flexible_payment') {
            const flexInput = document.getElementById('flexiblePayment');
            if (flexInput) {
                flexInput.value = amount.toFixed(4);
                // Trigger input event so calculation updates immediately
                flexInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        } else {
            const capitalInput = document.getElementById('capitalRepayment');
            if (capitalInput) {
                capitalInput.value = amount.toFixed(4);
                // Trigger input event so calculation updates immediately
                capitalInput.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    }
};
