/**
 * Novellus Loan Calculator JavaScript
 * Handles all calculator functionality, form interactions, and API calls
 */

class LoanCalculator {
    constructor() {
        this.form = document.getElementById('calculatorForm');
        this.resultsSection = document.getElementById('resultsSection');
        this.noResults = document.getElementById('noResults');
        this.currentResults = null;
        
        // Only initialize if required elements exist
        if (this.form) {
            this.initializeEventListeners();
            this.setDefaultDate();
            this.updateCurrencySymbols();
        }
    }

    initializeEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.calculateLoan();
        });

        // Loan type and repayment option changes
        document.getElementById('loanType').addEventListener('change', () => {
            this.updateRepaymentOptions();
            this.updateAdditionalParams();
        });

        document.getElementById('repaymentOption').addEventListener('change', () => {
            this.updateAdditionalParams();
        });

        // Currency changes
        document.getElementById('currency').addEventListener('change', () => {
            this.updateCurrencySymbols();
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

        // Start date changes - trigger calculation without updating other fields
        const startDateHandler = () => {
            console.log('Start date changed, triggering recalculation...');
            // Only update end date if it's empty or user hasn't manually set it
            const endDateElement = document.getElementById('endDate');
            if (!endDateElement.value || !endDateElement.hasAttribute('data-manual-set')) {
                this.updateEndDateFromStartAndTerm();
            }
            // Automatically trigger calculation if we have results already
            if (this.currentResults) {
                console.log('Triggering recalculation due to start date change...');
                this.calculateLoan();
            }
        };
        
        document.getElementById('startDate').addEventListener('change', startDateHandler);
        document.getElementById('startDate').addEventListener('input', startDateHandler);
        
        document.getElementById('loanTerm').addEventListener('input', () => {
            // Only update end date if it's empty or user hasn't manually set it
            const endDateElement = document.getElementById('endDate');
            if (!endDateElement.value || !endDateElement.hasAttribute('data-manual-set')) {
                this.updateEndDateFromStartAndTerm();
            }
            // Automatically trigger calculation if we have results already
            if (this.currentResults) {
                // Add small delay to prevent rapid-fire calculations while typing
                clearTimeout(this.loanTermTimeout);
                this.loanTermTimeout = setTimeout(() => {
                    this.calculateLoan();
                }, 500);
            }
        });

        // End date changes - trigger calculation without updating other fields
        const endDateHandler = () => {
            console.log('End date changed, triggering recalculation...');
            // Mark that user has manually set the end date
            document.getElementById('endDate').setAttribute('data-manual-set', 'true');
            
            // Calculate loan term days directly from the current start and end dates
            const startDate = new Date(document.getElementById('startDate').value);
            const endDate = new Date(document.getElementById('endDate').value);
            
            if (startDate && endDate && endDate > startDate) {
                const timeDiff = endDate.getTime() - startDate.getTime();
                const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
                console.log(`Manual end date change: ${daysDiff} days between ${startDate.toISOString().split('T')[0]} and ${endDate.toISOString().split('T')[0]}`);
            }
            
            // Automatically trigger calculation if we have results already
            if (this.currentResults) {
                console.log('Triggering recalculation due to end date change...');
                // Use a small delay to ensure DOM updates are processed
                setTimeout(() => {
                    this.calculateLoan();
                }, 100);
            }
        };
        
        document.getElementById('endDate').addEventListener('change', endDateHandler);
        document.getElementById('endDate').addEventListener('input', endDateHandler);



        // Tranche mode toggle
        document.querySelectorAll('input[name="tranche_mode"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.toggleTrancheMode();
            });
        });

        // Auto generate tranches button
        const generateBtn = document.getElementById('generateTranches');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateAutoTranches();
            });
        }

        // PDF and Excel quote generation handled by global functions
        // downloadPDFQuote() and downloadExcelQuote() called via onclick attributes

        // Development loan tranche controls
        const decreaseBtn = document.getElementById('decreaseTranches');
        const increaseBtn = document.getElementById('increaseTranches');
        
        if (decreaseBtn) {
            decreaseBtn.addEventListener('click', () => {
                this.decreaseTranches();
            });
        }

        if (increaseBtn) {
            increaseBtn.addEventListener('click', () => {
                this.increaseTranches();
            });
        }
    }

    setDefaultDate() {
        const startDateElement = document.getElementById('startDate');
        if (startDateElement && !startDateElement.value) {
            // Only set default date if field is empty
            const today = new Date();
            const dateString = today.toISOString().split('T')[0];
            startDateElement.value = dateString;
            
            // Set initial end date based on default loan term
            this.updateEndDateFromStartAndTerm();
        }
    }

    updateCurrencySymbols() {
        const currencyElement = document.getElementById('currency');
        if (currencyElement) {
            const currency = currencyElement.value;
            const symbol = currency === 'EUR' ? '€' : '£';
            
            document.querySelectorAll('.currency-symbol').forEach(element => {
                element.textContent = symbol;
            });
        }
    }

    updateEndDateFromStartAndTerm() {
        const startDateElement = document.getElementById('startDate');
        const loanTermElement = document.getElementById('loanTerm');
        const endDateElement = document.getElementById('endDate');
        
        if (startDateElement && loanTermElement && endDateElement) {
            const startDate = new Date(startDateElement.value);
            const loanTermMonths = parseInt(loanTermElement.value);
            
            if (startDate && loanTermMonths > 0) {
                // Calculate end date by adding months to start date
                const endDate = new Date(startDate);
                endDate.setMonth(endDate.getMonth() + loanTermMonths);
                
                // Format as YYYY-MM-DD for date input
                const endDateString = endDate.toISOString().split('T')[0];
                endDateElement.value = endDateString;
            }
        }
    }

    updateLoanTermFromDates() {
        const startDateElement = document.getElementById('startDate');
        const endDateElement = document.getElementById('endDate');
        const loanTermElement = document.getElementById('loanTerm');
        
        if (startDateElement && endDateElement && loanTermElement) {
            const startDate = new Date(startDateElement.value);
            const endDate = new Date(endDateElement.value);
            
            if (startDate && endDate && endDate > startDate) {
                // Calculate the difference in days first
                const timeDiff = endDate.getTime() - startDate.getTime();
                const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
                
                // Convert days to months using average days per month (30.44)
                const monthsFromDays = Math.max(1, Math.round(daysDiff / 30.44));
                
                // Update loan term based on actual days calculation
                loanTermElement.value = monthsFromDays;
                
                console.log(`Date change: ${daysDiff} days = ${monthsFromDays} months`);
                
                // Trigger a change event on the loan term field to update any dependent calculations
                loanTermElement.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    }

    updateRepaymentOptions() {
        const loanType = document.getElementById('loanType').value;
        const repaymentSelect = document.getElementById('repaymentOption');
        
        // Clear existing options
        repaymentSelect.innerHTML = '';
        
        if (loanType === 'bridge') {
            repaymentSelect.innerHTML = `
                <option value="none">Retained Interest</option>
                <option value="service_only">Interest Only</option>
                <option value="service_and_capital">Capital & Interest</option>
                <option value="flexible_payment">Flexible Payment</option>
            `;
        } else if (loanType === 'term') {
            repaymentSelect.innerHTML = `
                <option value="service_only">Interest Only</option>
                <option value="service_and_capital">Capital & Interest</option>
            `;
        } else if (loanType === 'development') {
            repaymentSelect.innerHTML = `
                <option value="none">Retained Interest</option>
                <option value="service_only">Interest Only</option>
                <option value="service_and_capital">Capital & Interest</option>
            `;
            
            // Default to net amount for development loans
            const netAmountRadio = document.getElementById('netAmount');
            const grossAmountRadio = document.getElementById('grossAmount');
            if (netAmountRadio && grossAmountRadio) {
                netAmountRadio.checked = true;
                grossAmountRadio.checked = false;
                this.toggleAmountInputSections();
            }
        } else {
            // For bridge and term loans, default to gross amount
            const netAmountRadio = document.getElementById('netAmount');
            const grossAmountRadio = document.getElementById('grossAmount');
            if (netAmountRadio && grossAmountRadio) {
                grossAmountRadio.checked = true;
                netAmountRadio.checked = false;
                this.toggleAmountInputSections();
            }
        }
        
        this.updateAdditionalParams();
    }

    updateAdditionalParams() {
        const loanType = document.getElementById('loanType').value;
        const repaymentOption = document.getElementById('repaymentOption').value;
        const additionalParams = document.getElementById('additionalParams');
        const paymentTimingSection = document.getElementById('paymentTimingSection');
        const capitalRepaymentSection = document.getElementById('capitalRepaymentSection');
        const flexiblePaymentSection = document.getElementById('flexiblePaymentSection');
        const developmentTrancheSection = document.getElementById('developmentTrancheSection');
        
        // Hide all additional parameters first (with null checks)
        if (additionalParams) additionalParams.style.display = 'none';
        if (paymentTimingSection) paymentTimingSection.style.display = 'none';
        if (capitalRepaymentSection) capitalRepaymentSection.style.display = 'none';
        if (flexiblePaymentSection) flexiblePaymentSection.style.display = 'none';
        if (developmentTrancheSection) developmentTrancheSection.style.display = 'none';
        
        // Show payment timing options for service_only and service_and_capital
        const showPaymentTiming = repaymentOption === 'service_only' || repaymentOption === 'service_and_capital';
        
        // Show payment timing for applicable repayment options
        if (showPaymentTiming) {
            if (additionalParams) additionalParams.style.display = 'block';
            if (paymentTimingSection) paymentTimingSection.style.display = 'block';
        }
        
        // Show relevant parameters based on loan type and repayment option
        if (loanType === 'bridge' && repaymentOption === 'service_and_capital') {
            if (additionalParams) additionalParams.style.display = 'block';
            if (paymentTimingSection) paymentTimingSection.style.display = 'block';
            if (capitalRepaymentSection) capitalRepaymentSection.style.display = 'block';
        } else if (loanType === 'bridge' && repaymentOption === 'flexible_payment') {
            if (additionalParams) additionalParams.style.display = 'block';
            if (flexiblePaymentSection) flexiblePaymentSection.style.display = 'block';
        } else if ((loanType === 'term' || loanType === 'development') && showPaymentTiming) {
            if (additionalParams) additionalParams.style.display = 'block';
            if (paymentTimingSection) paymentTimingSection.style.display = 'block';
            
            if (repaymentOption === 'service_and_capital') {
                if (capitalRepaymentSection) capitalRepaymentSection.style.display = 'block';
            }
        }
        
        // Always show development tranche section for development loans
        if (loanType === 'development') {
            if (developmentTrancheSection) developmentTrancheSection.style.display = 'block';
            
            // Show Day 1 Advance section for development loans with net amount input
            const day1AdvanceSection = document.getElementById('day1AdvanceSection');
            const netAmountRadio = document.getElementById('netAmount');
            if (day1AdvanceSection && netAmountRadio && netAmountRadio.checked) {
                day1AdvanceSection.style.display = 'block';
            }
        } else {
            // Hide Day 1 Advance for non-development loans
            const day1AdvanceSection = document.getElementById('day1AdvanceSection');
            if (day1AdvanceSection) day1AdvanceSection.style.display = 'none';
        }
    }

    toggleAmountInputSections() {
        const amountInputTypeRadio = document.querySelector('input[name="amount_input_type"]:checked');
        if (!amountInputTypeRadio) return;
        
        const amountInputType = amountInputTypeRadio.value;
        const grossAmountSection = document.getElementById('grossAmountSection');
        const netAmountSection = document.getElementById('netAmountSection');
        const day1AdvanceSection = document.getElementById('day1AdvanceSection');
        const loanType = document.getElementById('loanType').value;
        
        if (grossAmountSection && netAmountSection) {
            if (amountInputType === 'gross') {
                grossAmountSection.style.display = 'block';
                netAmountSection.style.display = 'none';
                if (day1AdvanceSection) day1AdvanceSection.style.display = 'none';
            } else {
                grossAmountSection.style.display = 'none';
                netAmountSection.style.display = 'block';
                
                // Show Day 1 Advance for development loans with net amount
                if (loanType === 'development' && day1AdvanceSection) {
                    day1AdvanceSection.style.display = 'block';
                }
            }
        }
    }

    toggleGrossAmountInputs() {
        const grossAmountTypeRadio = document.querySelector('input[name="gross_amount_type"]:checked');
        if (!grossAmountTypeRadio) return;
        
        const grossAmountType = grossAmountTypeRadio.value;
        const grossFixedInput = document.getElementById('grossFixedInput');
        const grossPercentageInput = document.getElementById('grossPercentageInput');
        
        if (grossFixedInput && grossPercentageInput) {
            if (grossAmountType === 'fixed') {
                grossFixedInput.style.display = 'block';
                grossPercentageInput.style.display = 'none';
            } else {
                grossFixedInput.style.display = 'none';
                grossPercentageInput.style.display = 'block';
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
        
        if (monthlyRateInput && annualRateInput) {
            if (rateInputType === 'monthly') {
                monthlyRateInput.style.display = 'block';
                annualRateInput.style.display = 'none';
            } else {
                monthlyRateInput.style.display = 'none';
                annualRateInput.style.display = 'block';
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

    async calculateLoan() {
        console.log('Calculate button clicked');
        const submitButton = this.form.querySelector('button[type="submit"]');
        
        // Show loading state
        submitButton.disabled = true;
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Calculating...';
        
        try {
            const formData = this.collectFormData();
            console.log('Form data collected:', formData);
            console.log('Date parameters:', {
                start_date: formData.start_date,
                end_date: formData.end_date,
                loan_term: formData.loan_term
            });
            console.log('Raw start_date field value:', document.getElementById('startDate').value);
            console.log('Loan type and repayment option:', {
                loan_type: formData.loan_type,
                repayment_option: formData.repayment_option
            });
            
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
            console.log('Loan term days from backend:', results.loanTermDays);
            this.currentResults = results;
            
            // Store results globally for download functions
            window.calculatorResults = results;
            
            this.displayResults(results);
            
        } catch (error) {
            console.error('Calculation error:', error);
            this.showError(error.message);
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
        
        // Handle payment timing and frequency for applicable repayment options
        const repaymentOption = data.repayment_option;
        if (repaymentOption === 'service_only' || repaymentOption === 'service_and_capital') {
            const paymentTiming = document.querySelector('input[name="payment_timing"]:checked');
            const paymentFrequency = document.querySelector('input[name="payment_frequency"]:checked');
            
            if (paymentTiming) {
                data.payment_timing = paymentTiming.value;
            }
            if (paymentFrequency) {
                data.payment_frequency = paymentFrequency.value;
            }
        }
        
        // Handle development loan tranches
        if (data.loan_type === 'development') {
            const trancheAmounts = Array.from(document.querySelectorAll('.tranche-amount')).map(input => parseFloat(input.value) || 0);
            const trancheDates = Array.from(document.querySelectorAll('.tranche-date')).map(input => input.value);
            const trancheRates = Array.from(document.querySelectorAll('.tranche-rate')).map(input => parseFloat(input.value) || 0);
            const trancheDescriptions = Array.from(document.querySelectorAll('.tranche-description')).map(input => input.value);
            
            // Include Day 1 net advance if specified
            const day1AdvanceField = document.getElementById('autoDay1Advance');
            if (day1AdvanceField) {
                data.day1_net_advance = parseFloat(day1AdvanceField.value) || 0;
            }
            
            // Only include tranches with valid amounts and dates
            data.tranches = trancheAmounts.map((amount, index) => ({
                amount: amount,
                date: trancheDates[index],
                rate: trancheRates[index] || data.annual_rate || data.monthly_rate * 12 || 12,
                description: trancheDescriptions[index] || `Tranche ${index + 1}`
            })).filter(tranche => tranche.amount > 0 && tranche.date);
        }
        
        return data;
    }

    displayResults(results) {
        // Hide no results message and show results section
        const noResults = document.getElementById('noResults');
        const resultsSection = document.getElementById('resultsSection');
        
        if (noResults) noResults.style.display = 'none';
        if (resultsSection) resultsSection.style.display = 'block';
        
        // Show download options
        const downloadOptionsCard = document.getElementById('downloadOptionsCard');
        if (downloadOptionsCard) {
            downloadOptionsCard.style.display = 'block';
        }
        
        // Update Loan Summary table
        const currency = results.currency_symbol || '£';
        
        // Log values for debugging
        console.log('Updating Loan Summary:', {
            grossAmount: results.grossAmount,
            netAdvance: results.netAdvance,
            propertyValue: results.propertyValue,
            startDate: results.startDate,
            loanTerm: results.loanTerm
        });
        
        // Debug log to see what's in the results
        console.log('Full results object:', results);
        
        // Map backend field names to display values (using exact API response fields)
        const grossAmount = results.grossAmount || 0;
        const netAdvance = results.netAdvance || 0;
        const totalInterest = results.totalInterest || 0;
        const propertyValue = results.propertyValue || 0;
        const arrangementFee = results.arrangementFee || 0;
        const legalFees = results.totalLegalFees || results.legalFees || 0;
        const siteVisitFee = results.siteVisitFee || 0;
        const titleInsurance = results.titleInsurance || 0;
        const loanTerm = results.loanTerm || 0;
        const loanTermDays = results.loanTermDays || 0;
        const interestRate = results.interestRate || 0;
        const arrangementFeeRate = results.arrangementFeeRate || 0;
        const day1Advance = results.day1Advance || 0;
        const netAmount = results.netAmount || 0;
        
        console.log('Mapped values:', {
            grossAmount, netAdvance, totalInterest, propertyValue, arrangementFee, legalFees, loanTerm, loanTermDays
        });
        
        // Get DOM elements for the new table format
        const propertyValueEl = document.getElementById('propertyValueResult');
        const grossAmountEl = document.getElementById('grossAmountResult');
        const startDateEl = document.getElementById('startDateResult');
        const endDateEl = document.getElementById('endDateResult');
        const loanTermEl = document.getElementById('loanTermResult');
        const loanTermDaysEl = document.getElementById('loanTermDaysResult');
        const arrangementFeeEl = document.getElementById('arrangementFeeResult');
        const legalCostsEl = document.getElementById('legalCostsResult');
        const totalInterestEl = document.getElementById('totalInterestResult');
        const netDay1AdvanceEl = document.getElementById('netDay1AdvanceResult');
        const ltvRatioEl = document.getElementById('ltvRatioResult');
        const totalNetAdvanceEl = document.getElementById('totalNetAdvanceResult');
        
        // Populate the loan summary table with exact format
        if (propertyValueEl) propertyValueEl.textContent = propertyValue.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        if (grossAmountEl) grossAmountEl.textContent = grossAmount.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        // Format start date
        if (startDateEl) {
            const startDate = results.start_date || results.startDate || new Date().toISOString().split('T')[0];
            try {
                const dateObj = new Date(startDate);
                const formatDate = dateObj.toLocaleDateString('en-GB', {
                    day: '2-digit',
                    month: '2-digit', 
                    year: 'numeric'
                });
                startDateEl.textContent = formatDate;
            } catch (e) {
                startDateEl.textContent = '00/01/1900';
            }
        }
        
        // Format end date
        if (endDateEl) {
            const endDate = results.end_date || results.endDate;
            if (endDate) {
                try {
                    const dateObj = new Date(endDate);
                    const formatDate = dateObj.toLocaleDateString('en-GB', {
                        day: '2-digit',
                        month: '2-digit', 
                        year: 'numeric'
                    });
                    endDateEl.textContent = formatDate;
                } catch (e) {
                    endDateEl.textContent = '00/01/1900';
                }
            } else {
                endDateEl.textContent = '00/01/1900';
            }
        }
        
        if (loanTermEl) loanTermEl.textContent = loanTerm.toFixed(2);
        if (loanTermDaysEl) {
            console.log('Updating loanTermDays field with value:', loanTermDays);
            loanTermDaysEl.textContent = loanTermDays.toLocaleString('en-GB');
        } else {
            console.log('loanTermDaysEl element not found');
        }
        if (arrangementFeeEl) arrangementFeeEl.textContent = arrangementFee.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        // Legal costs + title insurance + site visit fee
        if (legalCostsEl) {
            const totalLegalCosts = legalFees + titleInsurance + siteVisitFee;
            legalCostsEl.textContent = totalLegalCosts.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
        
        if (totalInterestEl) totalInterestEl.textContent = totalInterest.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        // For development loans, show Day 1 advance, otherwise show 0
        if (netDay1AdvanceEl) {
            const day1NetAdvance = results.day1NetAdvance || results.day1Advance || day1Advance || 0;
            netDay1AdvanceEl.textContent = day1NetAdvance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
        
        // Calculate and display LTV ratio
        if (ltvRatioEl && propertyValue > 0) {
            const ltvRatio = (grossAmount / propertyValue * 100);
            ltvRatioEl.textContent = ltvRatio.toFixed(2) + '%';
        } else if (ltvRatioEl) {
            ltvRatioEl.textContent = '0.00%';
        }
        
        // Total Net Advance
        if (totalNetAdvanceEl) {
            // Use totalNetAdvance field (user input) instead of netAdvance (calculated value)
            const totalNetAdvance = results.totalNetAdvance || results.netAmount || 0;
            totalNetAdvanceEl.textContent = totalNetAdvance.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
        
        // Only display loan summary table - all visualizations and reports removed
        
        // Scroll to results
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Removed: Payment schedule table update (not needed for loan summary only)

    updateCalculationBreakdownTable(schedule, currency, results) {
        const tableBody = document.querySelector('#calculationBreakdownTable tbody');
        if (!tableBody) return;
        tableBody.innerHTML = '';
        
        if (!schedule || schedule.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No calculation breakdown available</td></tr>';
            return;
        }
        
        const annualRate = results.interestRate || 12;
        const paymentFrequency = results.payment_frequency || 'monthly';
        const frequencyMultiplier = paymentFrequency === 'quarterly' ? 3 : 1;
        const ratePerPeriod = (annualRate / 12) * frequencyMultiplier / 100;
        
        // Get user's tranches from results - CRITICAL: Use actual user tranche data
        const userTranches = results.tranches || [];
        console.log('TRANCHE DEBUG - User tranches from results:', userTranches);
        
        schedule.forEach((payment, index) => {
            const row = document.createElement('tr');
            
            const openingBalance = payment.opening_balance || 0;
            const closingBalance = payment.closing_balance || payment.balance || 0;
            const interestAmount = payment.interest || 0;
            const principalPayment = payment.principal || 0;
            const totalPayment = payment.total_payment || payment.payment || 0;
            
            // CRITICAL FIX: Use actual user tranche values instead of calculated values
            let trancheRelease = payment.tranche_release || 0;
            let trancheNote = '';
            
            // Check if this period has a user tranche release
            if (userTranches && userTranches.length > 0) {
                const currentPeriod = payment.period || index + 1;
                const matchingTranche = userTranches.find(t => t.month === currentPeriod);
                
                if (matchingTranche) {
                    trancheRelease = matchingTranche.amount || 0;
                    trancheNote = `User Tranche ${currentPeriod}: £${matchingTranche.amount.toLocaleString()}`;
                    console.log(`TRANCHE DEBUG - Period ${currentPeriod}: Using user tranche £${matchingTranche.amount} instead of calculated £${payment.tranche_release}`);
                }
            }
            
            const balanceChange = openingBalance - closingBalance;
            
            // Create interest calculation explanation
            let interestCalculation = payment.interest_formula || `${currency}${openingBalance.toLocaleString()} × ${(ratePerPeriod * 100).toFixed(3)}%`;
            
            // Create row with proper tranche display
            row.innerHTML = `
                <td class="text-center">${payment.period || index + 1}</td>
                <td class="text-center">${payment.payment_date || '-'}</td>
                <td class="text-end">${currency}${openingBalance.toLocaleString()}</td>
                <td class="text-end ${trancheRelease > 0 ? 'text-success' : ''}">${trancheRelease > 0 ? currency + trancheRelease.toLocaleString() : '-'}</td>
                <td class="text-center text-muted" style="font-size: 0.8rem;">${interestCalculation}</td>
                <td class="text-end text-primary">${currency}${interestAmount.toLocaleString()}</td>
                <td class="text-end">${currency}${principalPayment.toLocaleString()}</td>
                <td class="text-end">${currency}${totalPayment.toLocaleString()}</td>
                <td class="text-end">${currency}${closingBalance.toLocaleString()}</td>
                <td class="text-end ${balanceChange > 0 ? 'text-success' : balanceChange < 0 ? 'text-danger' : ''}">${balanceChange > 0 ? '↓' : balanceChange < 0 ? '↑' : '='} ${currency}${Math.abs(balanceChange).toLocaleString()}</td>
            `;
            
            if (trancheNote) {
                row.title = trancheNote;
            }
            
            tableBody.appendChild(row);
        });
    }

    updateMonthlyBreakdownTable(monthlyBreakdown, currency, results) {
        const monthlyBreakdownCard = document.getElementById('monthlyBreakdownCard');
        const tableBody = document.querySelector('#monthlyBreakdownTable tbody');
        
        // Null checks
        if (!monthlyBreakdownCard || !tableBody) return;
        
        // Only show for development loans with breakdown data
        const isDevLoan = results.loanType === 'development' || results.loan_type === 'development';
        if (!monthlyBreakdown || monthlyBreakdown.length === 0 || !isDevLoan) {
            console.log('DEBUG - Monthly breakdown hidden. Loan type:', results.loanType, results.loan_type, 'Is dev loan:', isDevLoan, 'Breakdown length:', monthlyBreakdown?.length);
            monthlyBreakdownCard.style.display = 'none';
            return;
        }
        
        monthlyBreakdownCard.style.display = 'block';
        tableBody.innerHTML = '';
        
        // Update formula in alert box with actual rate
        const alertBox = monthlyBreakdownCard.querySelector('.alert');
        if (alertBox) {
            const annualRate = results.annualRate ? (results.annualRate * 100).toFixed(2) : '12.00';
            alertBox.innerHTML = `<strong>Daily Compound Interest Formula:</strong> Outstanding Balance × (1 + ${annualRate}%/365)^{days_in_period} - Outstanding Balance`;
        }
        
        // Get user's tranches from results - CRITICAL: Use actual user tranche data
        const userTranches = results.tranches || [];
        console.log('MONTHLY BREAKDOWN DEBUG - User tranches from results:', userTranches);
        
        monthlyBreakdown.forEach((month, index) => {
            const row = document.createElement('tr');
            
            // CRITICAL FIX: Use actual user tranche values instead of calculated values
            // Note: API returns different field names than expected
            let trancheRelease = month.tranche_release || 0;
            
            // Check if this month has a user tranche release
            if (userTranches && userTranches.length > 0) {
                const currentMonth = month.month || index + 1;
                const matchingTranche = userTranches.find(t => t.month === currentMonth);
                
                if (matchingTranche) {
                    trancheRelease = matchingTranche.amount || 0;
                    console.log(`MONTHLY BREAKDOWN DEBUG - Month ${currentMonth}: Using user tranche £${matchingTranche.amount} instead of calculated £${month.tranche_release}`);
                }
            }
            
            // Map API field names to frontend expectations
            const periodStart = month.period_start || month.date || '-';
            const periodEnd = month.period_end || month.date || '-';
            const daysInPeriod = month.days_in_period || month.days_in_month || 30;
            const openingBalance = month.opening_balance || 0;
            const balanceAfterTranche = month.balance_after_tranche || (openingBalance + trancheRelease);
            const compoundFactor = month.compound_factor || 1;
            const interestEarned = month.interest_earned || month.monthly_interest || 0;
            const closingBalance = month.closing_balance || 0;
            const excelFormula = month.excel_formula || month.calculation_formula || 'N/A';
            
            row.innerHTML = `
                <td><strong>${month.month}</strong></td>
                <td>${periodStart} to ${periodEnd}</td>
                <td class="text-center">${daysInPeriod}</td>
                <td class="text-end">${currency}${openingBalance.toLocaleString()}</td>
                <td class="text-end${trancheRelease > 0 ? ' text-success' : ''}">${trancheRelease > 0 ? currency + trancheRelease.toLocaleString() : '—'}</td>
                <td class="text-end">${currency}${balanceAfterTranche.toLocaleString()}</td>
                <td class="text-center">${compoundFactor.toFixed(8)}</td>
                <td class="text-end text-primary"><strong>${currency}${interestEarned.toLocaleString()}</strong></td>
                <td class="text-end"><strong>${currency}${closingBalance.toLocaleString()}</strong></td>
                <td class="text-muted" style="font-size: 0.8rem;">${excelFormula}</td>
            `;
            
            tableBody.appendChild(row);
        });
    }

    updateExcelStyleBreakdownTable(monthlyBreakdown, currency, results) {
        console.log('Excel breakdown - monthlyBreakdown:', monthlyBreakdown);
        console.log('Excel breakdown - results.loan_type:', results.loan_type);
        console.log('Excel breakdown - results.loanType:', results.loanType);
        
        const excelBreakdownCard = document.getElementById('excelBreakdownCard');
        const tableBody = document.querySelector('#excelStyleBreakdownTable tbody');
        
        if (!excelBreakdownCard || !tableBody) {
            console.error('Excel breakdown elements not found');
            return;
        }
        
        // Only show for development loans with breakdown data
        if (!monthlyBreakdown || monthlyBreakdown.length === 0 || (results.loan_type !== 'development' && results.loanType !== 'development')) {
            console.log('Hiding Excel breakdown - no data or not development loan');
            excelBreakdownCard.style.display = 'none';
            return;
        }
        
        console.log('Showing Excel breakdown table with', monthlyBreakdown.length, 'rows');
        excelBreakdownCard.style.display = 'block';
        tableBody.innerHTML = '';
        
        // Update formula in alert box with actual rate
        const alertBox = excelBreakdownCard.querySelector('.alert');
        const annualRate = results.annualRate ? (results.annualRate * 100).toFixed(2) : '12.00';
        if (alertBox) {
            alertBox.innerHTML = `<strong>Formula:</strong> Principal Balance × (1 + ${annualRate}%/365)^days = New Balance | Interest = New Balance - Principal Balance`;
        } else {
            console.warn('Alert box not found in Excel breakdown card');
        }
        
        let cumulativeInterest = 0;
        
        monthlyBreakdown.forEach((month, index) => {
            try {
                console.log(`Processing month ${index + 1}:`, month);
                
                const row = document.createElement('tr');
                
                // Calculate values for the Excel-style display
                const openingBalance = month.opening_balance || 0;
                const trancheRelease = month.tranche_release || 0;
                const principalForInterest = openingBalance + trancheRelease;
                const dailyRate = month.daily_rate_decimal || 0;
                const compoundFactor = month.compound_factor || 1;
                const newBalance = principalForInterest * compoundFactor;
                const interestEarned = month.interest_earned || 0;
                const closingBalance = month.closing_balance || 0;
                
                cumulativeInterest += interestEarned;
                
                // Color coding for different values
                let trancheColor = trancheRelease > 0 ? 'text-success' : '';
                let interestColor = interestEarned > 0 ? 'text-primary' : '';
                
                row.innerHTML = `
                    <td class="text-center"><strong>${month.month}</strong></td>
                    <td class="text-center">${month.days_in_period}</td>
                    <td class="text-end">${currency}${openingBalance.toLocaleString()}</td>
                    <td class="text-end ${trancheColor}">${trancheRelease > 0 ? currency + trancheRelease.toLocaleString() : '—'}</td>
                    <td class="text-end"><strong>${currency}${principalForInterest.toLocaleString()}</strong></td>
                    <td class="text-center" style="font-size: 0.75rem;">${(dailyRate * 100).toFixed(6)}%</td>
                    <td class="text-center">${compoundFactor.toFixed(8)}</td>
                    <td class="text-end">${currency}${newBalance.toLocaleString()}</td>
                    <td class="text-end ${interestColor}"><strong>${currency}${interestEarned.toLocaleString()}</strong></td>
                    <td class="text-end" style="background: #f8f9fa;"><strong>${currency}${closingBalance.toLocaleString()}</strong></td>
                    <td class="text-end text-warning"><strong>${currency}${cumulativeInterest.toLocaleString()}</strong></td>
                `;
                
                tableBody.appendChild(row);
                console.log(`Row ${index + 1} added successfully`);
                
            } catch (error) {
                console.error(`Error processing month ${index + 1}:`, error, month);
            }
        });
        
        // Add totals row
        if (monthlyBreakdown.length > 0) {
            try {
                console.log('Adding totals row...');
                const totalRow = document.createElement('tr');
                totalRow.style.background = '#e9ecef';
                totalRow.style.fontWeight = 'bold';
                
                const totalTranches = monthlyBreakdown.reduce((sum, month) => sum + (month.tranche_release || 0), 0);
                const finalBalance = monthlyBreakdown[monthlyBreakdown.length - 1].closing_balance || 0;
                
                totalRow.innerHTML = `
                    <td class="text-center"><strong>TOTAL</strong></td>
                    <td class="text-center">—</td>
                    <td class="text-end">—</td>
                    <td class="text-end"><strong>${currency}${totalTranches.toLocaleString()}</strong></td>
                    <td class="text-end">—</td>
                    <td class="text-center">—</td>
                    <td class="text-center">—</td>
                    <td class="text-end">—</td>
                    <td class="text-end text-primary"><strong>${currency}${cumulativeInterest.toLocaleString()}</strong></td>
                    <td class="text-end" style="background: #B8860B; color: white;"><strong>${currency}${finalBalance.toLocaleString()}</strong></td>
                    <td class="text-end text-warning"><strong>${currency}${cumulativeInterest.toLocaleString()}</strong></td>
                `;
                
                tableBody.appendChild(totalRow);
                console.log('Totals row added successfully');
            } catch (error) {
                console.error('Error adding totals row:', error);
            }
        }
        
        console.log('Excel breakdown table setup complete');
    }

    updateExcelStyleBreakdownTable(monthlyBreakdown, currency, results) {
        console.log('Excel breakdown - monthlyBreakdown:', monthlyBreakdown);
        console.log('Excel breakdown - results.loan_type:', results.loan_type);
        console.log('Excel breakdown - results.loanType:', results.loanType);
        
        // Only show Excel-style breakdown for development loans
        const excelStyleCard = document.getElementById('excelStyleBreakdownCard');
        const tableBody = document.getElementById('excelStyleBreakdownBody');
        
        if (!excelStyleCard || !tableBody) {
            console.error('Excel breakdown elements not found');
            return;
        }
        
        if (results.loan_type !== 'development') {
            excelStyleCard.style.display = 'none';
            return;
        }
        
        console.log('Showing Excel-style breakdown for development loan');
        excelStyleCard.style.display = 'block';
        
        // Use the monthly breakdown data directly instead of making a separate API call
        if (!monthlyBreakdown || monthlyBreakdown.length === 0) {
            console.log('No monthly breakdown data available');
            tableBody.innerHTML = '<tr><td colspan="10" class="text-center text-muted">No breakdown data available</td></tr>';
            return;
        }
        
        // Get user's tranches from results - CRITICAL: Use actual user tranche data
        const userTranches = results.tranches || [];
        console.log('EXCEL BREAKDOWN DEBUG - User tranches from results:', userTranches);
        
        // Clear existing table
        tableBody.innerHTML = '';
        
        let cumulativeInterest = 0;
        let totalReleases = 0;
        
        // Populate table with data using user's actual tranche values
        monthlyBreakdown.forEach((month, index) => {
            const tr = document.createElement('tr');
            
            // CRITICAL FIX: Use actual user tranche values instead of calculated values
            let monthlyRelease = month.tranche_release || 0;
            
            // Check if this month has a user tranche release
            if (userTranches && userTranches.length > 0) {
                const currentMonth = month.month || index + 1;
                const matchingTranche = userTranches.find(t => t.month === currentMonth);
                
                if (matchingTranche) {
                    monthlyRelease = matchingTranche.amount || 0;
                    console.log(`EXCEL BREAKDOWN DEBUG - Month ${currentMonth}: Using user tranche £${matchingTranche.amount} instead of calculated £${month.tranche_release}`);
                }
            }
            
            const monthlyInterest = month.monthly_interest || month.interest_earned || 0;
            cumulativeInterest += monthlyInterest;
            totalReleases += monthlyRelease;
            
            tr.innerHTML = `
                <td class="text-center"><strong>${month.month}</strong></td>
                <td class="text-center">${month.date || month.period_start || '-'}</td>
                <td class="text-end">${currency}${(month.opening_balance || 0).toLocaleString()}</td>
                <td class="text-end ${monthlyRelease > 0 ? 'text-success' : ''}">${monthlyRelease > 0 ? currency + monthlyRelease.toLocaleString() : '—'}</td>
                <td class="text-end"><strong>${currency}${(month.balance_after_release || month.balance_after_tranche || 0).toLocaleString()}</strong></td>
                <td class="text-center">${month.days_in_month || month.days_in_period || 30}</td>
                <td class="text-center" style="font-size: 0.8rem;">${month.daily_rate || '0.032877%'}</td>
                <td class="text-end text-primary"><strong>${currency}${monthlyInterest.toLocaleString()}</strong></td>
                <td class="text-end" style="background: #f8f9fa;"><strong>${currency}${(month.closing_balance || 0).toLocaleString()}</strong></td>
                <td class="text-end text-warning"><strong>${currency}${cumulativeInterest.toLocaleString()}</strong></td>
            `;
            tableBody.appendChild(tr);
        });
        
        // Add totals row
        const totalRow = document.createElement('tr');
        totalRow.style.background = '#e9ecef';
        totalRow.style.fontWeight = 'bold';
        totalRow.innerHTML = `
            <td class="text-center"><strong>TOTAL</strong></td>
            <td class="text-center">—</td>
            <td class="text-end">—</td>
            <td class="text-end"><strong>${currency}${totalReleases.toLocaleString()}</strong></td>
            <td class="text-end">—</td>
            <td class="text-center">—</td>
            <td class="text-center">—</td>
            <td class="text-end text-primary"><strong>${currency}${cumulativeInterest.toLocaleString()}</strong></td>
            <td class="text-end" style="background: #B8860B; color: white;"><strong>${currency}${(monthlyBreakdown[monthlyBreakdown.length - 1]?.closing_balance || 0).toLocaleString()}</strong></td>
            <td class="text-end text-warning"><strong>${currency}${cumulativeInterest.toLocaleString()}</strong></td>
        `;
        tableBody.appendChild(totalRow);
        
        console.log('Excel-style breakdown table populated successfully');
    }

    updatePaymentChart(schedule) {
        const ctx = document.getElementById('paymentChart').getContext('2d');
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        if (!schedule || schedule.length === 0) {
            return;
        }
        
        // Get payment frequency from calculation results to determine chart labels
        const paymentFrequency = this.currentResults?.payment_frequency || 'monthly';
        const periodLabel = paymentFrequency === 'quarterly' ? 'Quarter' : 'Month';
        
        const labels = schedule.map(payment => {
            const periodNum = payment.period || payment.month || 0;
            const paymentDate = payment.payment_date || payment.date || '';
            return paymentDate ? `${periodLabel} ${periodNum} (${paymentDate})` : `${periodLabel} ${periodNum}`;
        });
        const principalData = schedule.map(payment => payment.principal || 0);
        const interestData = schedule.map(payment => payment.interest || 0);
        const balanceData = schedule.map(payment => payment.closing_balance || payment.balance || 0);
        
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Principal Payment',
                        data: principalData,
                        backgroundColor: 'rgba(184, 134, 11, 0.8)',  // Novellus gold
                        borderColor: 'rgba(184, 134, 11, 1)',
                        borderWidth: 2,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Interest Payment',
                        data: interestData,
                        backgroundColor: 'rgba(205, 164, 76, 0.8)',  // Lighter gold
                        borderColor: 'rgba(205, 164, 76, 1)',
                        borderWidth: 2,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Remaining Balance',
                        type: 'line',
                        data: balanceData,
                        backgroundColor: 'rgba(30, 43, 58, 0.1)',    // Novellus navy
                        borderColor: 'rgba(30, 43, 58, 1)',
                        borderWidth: 3,
                        pointBackgroundColor: 'rgba(30, 43, 58, 1)',
                        pointBorderColor: 'rgba(255, 255, 255, 1)',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        fill: false,
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Payment Period'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Payment Amount (£)'
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '£' + value.toLocaleString();
                            }
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Remaining Balance (£)'
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '£' + value.toLocaleString();
                            }
                        },
                        grid: {
                            drawOnChartArea: true,
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Payment Breakdown & Remaining Balance',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#1E2B3A'
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return label + ': £' + value.toLocaleString();
                            },
                            afterBody: function(tooltipItems) {
                                const principalItem = tooltipItems.find(item => item.dataset.label === 'Principal Payment');
                                const interestItem = tooltipItems.find(item => item.dataset.label === 'Interest Payment');
                                
                                if (principalItem && interestItem) {
                                    const total = principalItem.parsed.y + interestItem.parsed.y;
                                    return ['', 'Total Payment: £' + total.toLocaleString()];
                                }
                                return [];
                            }
                        }
                    }
                }
            }
        });
    }

    showTrancheChart(tranches, paymentSchedule, currency) {
        const trancheChartContainer = document.getElementById('trancheChartContainer');
        const ctx = document.getElementById('trancheChart').getContext('2d');
        
        // Show the tranche chart container
        trancheChartContainer.style.display = 'block';
        
        // Destroy existing tranche chart if it exists
        if (this.trancheChart) {
            this.trancheChart.destroy();
        }
        
        if (!tranches || tranches.length === 0) {
            return;
        }
        
        // Create cumulative tranche release data by period
        const periodLabels = paymentSchedule.map(payment => `Month ${payment.period || payment.month || 0}`);
        const trancheReleaseData = paymentSchedule.map(payment => payment.tranche_release || 0);
        const cumulativeReleaseData = [];
        let cumulativeTotal = 0;
        
        trancheReleaseData.forEach(release => {
            cumulativeTotal += release;
            cumulativeReleaseData.push(cumulativeTotal);
        });
        
        // Create datasets for tranche visualization with Novellus brand colors
        const datasets = [];
        
        // Individual tranche releases - Novellus gold
        datasets.push({
            label: 'Tranche Releases',
            data: trancheReleaseData,
            backgroundColor: 'rgba(184, 134, 11, 0.8)',  // Novellus gold
            borderColor: 'rgba(184, 134, 11, 1)',
            borderWidth: 2,
            yAxisID: 'y'
        });
        
        // Cumulative release line - Novellus navy
        datasets.push({
            label: 'Cumulative Releases',
            type: 'line',
            data: cumulativeReleaseData,
            backgroundColor: 'rgba(30, 43, 58, 0.1)',    // Novellus navy
            borderColor: 'rgba(30, 43, 58, 1)',
            borderWidth: 3,
            pointBackgroundColor: 'rgba(30, 43, 58, 1)',
            pointBorderColor: 'rgba(255, 255, 255, 1)',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: false,
            tension: 0.1,
            yAxisID: 'y1'
        });
        
        this.trancheChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: periodLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Release Period'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: `Tranche Release (${currency})`
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return currency + value.toLocaleString();
                            }
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: `Cumulative Release (${currency})`
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return currency + value.toLocaleString();
                            }
                        },
                        grid: {
                            drawOnChartArea: true,
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Development Loan Tranche Release Schedule',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#1E2B3A'
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                return `${label}: ${currency}${value.toLocaleString()}`;
                            },
                            afterBody: function(tooltipItems) {
                                // Add tranche details for this period
                                const periodIndex = tooltipItems[0].dataIndex;
                                const payment = paymentSchedule[periodIndex];
                                if (payment && payment.tranche_details && payment.tranche_details.length > 0) {
                                    const details = payment.tranche_details.map(tranche => 
                                        `${tranche.description}: ${currency}${tranche.amount.toLocaleString()}`
                                    );
                                    return ['', 'Tranches Released:', ...details];
                                }
                                return [];
                            }
                        }
                    }
                }
            }
        });
    }

    hideTrancheChart() {
        const trancheChartContainer = document.getElementById('trancheChartContainer');
        trancheChartContainer.style.display = 'none';
        
        if (this.trancheChart) {
            this.trancheChart.destroy();
            this.trancheChart = null;
        }
    }

    showInterestAccumulationChart(tranches, paymentSchedule, currency) {
        const interestContainer = document.getElementById('interestAccumulationContainer');
        const ctx = document.getElementById('interestAccumulationChart').getContext('2d');
        
        // Show the interest accumulation chart container
        interestContainer.style.display = 'block';
        
        // Destroy existing chart if it exists
        if (this.interestAccumulationChart) {
            this.interestAccumulationChart.destroy();
        }
        
        if (!tranches || tranches.length === 0) {
            return;
        }
        
        // Create data showing interest accumulation over time
        const periodLabels = paymentSchedule.map(payment => `Month ${payment.period || payment.month || 0}`);
        
        // Calculate interest for each month based on active tranches
        const cumulativeInterestData = [];
        const monthlyInterestData = [];
        let totalAccumulatedInterest = 0;
        
        // Track which tranches are active in each month
        const activeTranches = [];
        
        paymentSchedule.forEach((payment, index) => {
            // Add any new tranches released in this period
            if (payment.tranche_details && payment.tranche_details.length > 0) {
                payment.tranche_details.forEach(tranche => {
                    activeTranches.push({
                        amount: tranche.amount,
                        rate: tranche.rate,
                        description: tranche.description,
                        monthlyInterest: (tranche.amount * (tranche.rate / 100)) / 12
                    });
                });
            }
            
            // Calculate total monthly interest from all active tranches
            let monthlyInterest = 0;
            activeTranches.forEach(tranche => {
                monthlyInterest += tranche.monthlyInterest;
            });
            
            totalAccumulatedInterest += monthlyInterest;
            monthlyInterestData.push(monthlyInterest);
            cumulativeInterestData.push(totalAccumulatedInterest);
        });
        
        // Create individual tranche interest datasets with Novellus brand colors
        const trancheColors = [
            'rgba(184, 134, 11, 0.9)',   // Primary Novellus gold
            'rgba(30, 43, 58, 0.8)',     // Primary Novellus navy
            'rgba(205, 164, 76, 0.8)',   // Lighter gold variant
            'rgba(45, 58, 73, 0.8)',     // Lighter navy variant
            'rgba(139, 110, 45, 0.8)',   // Darker gold variant
            'rgba(15, 25, 35, 0.8)'      // Darker navy variant
        ];
        
        // Create individual datasets for each tranche's interest contribution
        const datasets = [];
        
        // Add a dataset for each tranche showing monthly interest once active
        tranches.forEach((tranche, trancheIndex) => {
            const trancheMonthlyInterestData = new Array(paymentSchedule.length).fill(0);
            const monthlyInterest = (tranche.amount * (tranche.rate / 100)) / 12;
            
            // Find when this tranche was released and start showing monthly interest
            let trancheActive = false;
            paymentSchedule.forEach((payment, periodIndex) => {
                if (payment.tranche_details && payment.tranche_details.length > 0) {
                    const matchingTranche = payment.tranche_details.find(td => 
                        td.amount === tranche.amount && td.description === tranche.description
                    );
                    if (matchingTranche) {
                        trancheActive = true;
                    }
                }
                
                // Show monthly interest for this tranche if it's active
                if (trancheActive) {
                    trancheMonthlyInterestData[periodIndex] = monthlyInterest;
                }
            });
            
            datasets.push({
                label: tranche.description || `Tranche ${trancheIndex + 1}`,
                data: trancheMonthlyInterestData,
                backgroundColor: trancheColors[trancheIndex % trancheColors.length],
                borderColor: trancheColors[trancheIndex % trancheColors.length].replace('0.8', '1'),
                borderWidth: 2,
                yAxisID: 'y'
            });
        });
        
        // Add cumulative interest line - Novellus navy
        datasets.push({
            label: 'Cumulative Interest',
            type: 'line',
            data: cumulativeInterestData,
            backgroundColor: 'rgba(30, 43, 58, 0.1)',
            borderColor: 'rgba(30, 43, 58, 1)',
            borderWidth: 3,
            pointBackgroundColor: 'rgba(30, 43, 58, 1)',
            pointBorderColor: 'rgba(255, 255, 255, 1)',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 8,
            fill: false,
            tension: 0.1,
            yAxisID: 'y1'
        });
        
        this.interestAccumulationChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: periodLabels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Release Period'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: `Monthly Interest (${currency})`
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return currency + value.toLocaleString();
                            }
                        },
                        grid: {
                            drawOnChartArea: false,
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: `Cumulative Interest (${currency})`
                        },
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return currency + value.toLocaleString();
                            }
                        },
                        grid: {
                            drawOnChartArea: true,
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Monthly Interest Accumulation by Tranche',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#1E2B3A'
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            generateLabels: function(chart) {
                                const original = Chart.defaults.plugins.legend.labels.generateLabels;
                                const labels = original.call(this, chart);
                                
                                // Limit the number of visible legend items to avoid overcrowding
                                return labels.slice(0, 8); // Show max 8 items
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y;
                                if (value === 0) return null; // Don't show tooltips for zero values
                                return `${label}: ${currency}${value.toLocaleString()}`;
                            },
                            afterBody: function(tooltipItems) {
                                const periodIndex = tooltipItems[0].dataIndex;
                                const payment = paymentSchedule[periodIndex];
                                
                                // Show monthly interest breakdown
                                const details = [``, 'Monthly Interest Breakdown:'];
                                
                                // Calculate and show each active tranche's monthly contribution
                                tranches.forEach(tranche => {
                                    const monthlyInterest = (tranche.amount * (tranche.rate / 100)) / 12;
                                    
                                    // Check if this tranche is active in this period
                                    let isActive = false;
                                    for (let i = 0; i <= periodIndex; i++) {
                                        const checkPayment = paymentSchedule[i];
                                        if (checkPayment && checkPayment.tranche_details && checkPayment.tranche_details.length > 0) {
                                            const matchingTranche = checkPayment.tranche_details.find(td => 
                                                td.amount === tranche.amount && td.description === tranche.description
                                            );
                                            if (matchingTranche) {
                                                isActive = true;
                                                break;
                                            }
                                        }
                                    }
                                    
                                    if (isActive) {
                                        details.push(`${tranche.description}: ${currency}${monthlyInterest.toLocaleString()} (${tranche.rate}% annual)`);
                                    }
                                });
                                
                                return details;
                                return [];
                            }
                        }
                    }
                }
            }
        });
    }

    hideInterestAccumulationChart() {
        const interestContainer = document.getElementById('interestAccumulationContainer');
        interestContainer.style.display = 'none';
        
        if (this.interestAccumulationChart) {
            this.interestAccumulationChart.destroy();
            this.interestAccumulationChart = null;
        }
    }

    showInterestAccrualChart(results) {
        const container = document.getElementById('interestAccrualContainer');
        if (!container || !results.payment_schedule) return;
        
        container.style.display = 'block';
        
        // Destroy existing chart
        if (this.interestAccrualChart) {
            this.interestAccrualChart.destroy();
            this.interestAccrualChart = null;
        }
        
        const ctx = document.getElementById('interestAccrualChart').getContext('2d');
        const currency = results.currency_symbol || '£';
        const paymentSchedule = results.payment_schedule || [];
        
        if (paymentSchedule.length === 0) return;
        
        // Calculate monthly and cumulative interest
        const labels = paymentSchedule.map(payment => `Month ${payment.period || payment.month || 0}`);
        const monthlyInterestData = [];
        const cumulativeInterestData = [];
        let cumulativeInterest = 0;
        
        // Calculate interest based on loan type and repayment option
        paymentSchedule.forEach((payment, index) => {
            let monthlyInterest = 0;
            
            if (results.loan_type === 'bridge' && results.repaymentOption === 'none') {
                // Retained interest - show total at the end
                if (index === paymentSchedule.length - 1) {
                    monthlyInterest = results.totalInterest || 0;
                } else {
                    monthlyInterest = 0;
                }
            } else if (results.loan_type === 'bridge' && results.repaymentOption === 'service_only') {
                // Interest-only payments
                monthlyInterest = results.monthlyPayment || 0;
            } else if (results.loan_type === 'term' || results.repaymentOption === 'service_and_capital') {
                // Use actual interest from payment schedule
                monthlyInterest = payment.interest || 0;
            } else {
                // Default calculation
                const balance = payment.opening_balance || payment.balance || results.grossAmount;
                const annualRate = results.interestRate || 12;
                monthlyInterest = (balance * (annualRate / 100)) / 12;
            }
            
            cumulativeInterest += monthlyInterest;
            monthlyInterestData.push(monthlyInterest);
            cumulativeInterestData.push(cumulativeInterest);
        });
        
        // Create chart datasets
        const datasets = [
            {
                label: `Monthly Interest (${currency})`,
                data: monthlyInterestData,
                backgroundColor: 'rgba(184, 134, 11, 0.8)', // Novellus gold
                borderColor: '#B8860B',
                borderWidth: 2,
                type: 'bar',
                yAxisID: 'y'
            },
            {
                label: `Cumulative Interest (${currency})`,
                data: cumulativeInterestData,
                backgroundColor: 'transparent',
                borderColor: '#1E2B3A', // Novellus navy
                borderWidth: 3,
                type: 'line',
                fill: false,
                tension: 0.1,
                yAxisID: 'y1'
            }
        ];
        
        this.interestAccrualChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${results.loan_type === 'bridge' ? 'Bridge' : 'Term'} Loan Interest Accrual`,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        color: '#1E2B3A'
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            afterBody: function(tooltipItems) {
                                const periodIndex = tooltipItems[0].dataIndex;
                                const payment = paymentSchedule[periodIndex];
                                
                                const details = [``, 'Period Details:'];
                                details.push(`Opening Balance: ${currency}${(payment.opening_balance || payment.balance || 0).toLocaleString()}`);
                                details.push(`Interest Rate: ${results.interestRate || 12}% per annum`);
                                details.push(`Repayment Type: ${results.repaymentOption || 'service_only'}`);
                                
                                if (payment.principal && payment.principal > 0) {
                                    details.push(`Principal Payment: ${currency}${payment.principal.toLocaleString()}`);
                                }
                                
                                return details;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Loan Period'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: `Monthly Interest (${currency})`
                        },
                        beginAtZero: true
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: `Cumulative Interest (${currency})`
                        },
                        beginAtZero: true,
                        grid: {
                            drawOnChartArea: false
                        }
                    }
                }
            }
        });
    }

    hideInterestAccrualChart() {
        const container = document.getElementById('interestAccrualContainer');
        if (container) {
            container.style.display = 'none';
        }
        
        // Destroy existing chart
        if (this.interestAccrualChart) {
            this.interestAccrualChart.destroy();
            this.interestAccrualChart = null;
        }
    }



    async generatePdfQuote() {
        if (!this.currentResults) {
            this.showError('No calculation results available for PDF generation');
            return;
        }

        const button = document.getElementById('generatePdfQuote');
        const originalText = button.innerHTML;
        
        try {
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating PDF...';
            button.disabled = true;

            // Collect application data from form
            const formData = this.collectFormData();
            const applicationData = {
                loan_type: formData.loan_type,
                loan_purpose: `${formData.loan_type} loan`,
                property_address: 'Property address to be confirmed',
                property_value: parseFloat(formData.property_value) || 0,
                user: {
                    first_name: 'Valued',
                    last_name: 'Client',
                    email: '',
                    phone: '',
                    company: ''
                }
            };

            // Add property value to calculation data for PDF
            const calculationDataWithProperty = {
                ...this.currentResults,
                property_value: parseFloat(formData.property_value) || 0
            };

            // Send request to generate PDF
            const response = await fetch('/api/generate-pdf-quote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    calculation_data: calculationDataWithProperty,
                    application_data: applicationData
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'PDF generation failed');
            }

            // Download the PDF file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `novellus_quote_${new Date().toISOString().split('T')[0]}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('PDF generation error:', error);
            this.showError('Failed to generate PDF quote: ' + error.message);
        } finally {
            // Restore button state
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    async generateExcelQuote() {
        if (!this.currentResults) {
            this.showError('No calculation results available for Excel generation');
            return;
        }

        const button = document.getElementById('generateExcelQuote');
        const originalText = button.innerHTML;
        
        try {
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Excel...';
            button.disabled = true;

            // Collect application data from form
            const formData = this.collectFormData();
            const applicationData = {
                loan_type: formData.loan_type,
                loan_purpose: `${formData.loan_type} loan`,
                property_address: 'Property address to be confirmed',
                property_value: parseFloat(formData.property_value) || 0,
                user: {
                    first_name: 'Valued',
                    last_name: 'Client',
                    email: '',
                    phone: '',
                    company: ''
                }
            };

            // Add property value to calculation data for Excel
            const calculationDataWithProperty = {
                ...this.currentResults,
                property_value: parseFloat(formData.property_value) || 0
            };

            // Send request to generate Excel
            const response = await fetch('/api/generate-excel-quote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    calculation_data: calculationDataWithProperty,
                    application_data: applicationData
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Excel generation failed');
            }

            // Download the Excel file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `novellus_quote_${new Date().toISOString().split('T')[0]}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

        } catch (error) {
            console.error('Excel generation error:', error);
            this.showError('Failed to generate Excel quote: ' + error.message);
        } finally {
            // Restore button state
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }

    showError(message) {
        // Create or update error alert
        let errorAlert = document.querySelector('.calculation-error');
        if (!errorAlert) {
            errorAlert = document.createElement('div');
            errorAlert.className = 'alert alert-danger alert-dismissible fade show calculation-error';
            errorAlert.innerHTML = `
                <span class="error-message"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            this.form.insertBefore(errorAlert, this.form.firstChild);
        }
        
        errorAlert.querySelector('.error-message').textContent = message;
        errorAlert.scrollIntoView({ behavior: 'smooth' });
    }

    increaseTranches() {
        const trancheCount = document.getElementById('trancheCount');
        const container = document.getElementById('tranchesContainer');
        const currentCount = parseInt(trancheCount.textContent);
        
        if (currentCount < 10) { // Limit to 10 tranches
            const newCount = currentCount + 1;
            trancheCount.textContent = newCount;
            
            const newTranche = this.createTrancheElement(newCount);
            container.appendChild(newTranche);
        }
    }

    decreaseTranches() {
        const trancheCount = document.getElementById('trancheCount');
        const container = document.getElementById('tranchesContainer');
        const currentCount = parseInt(trancheCount.textContent);
        
        if (currentCount > 1) { // Keep at least 1 tranche
            const newCount = currentCount - 1;
            trancheCount.textContent = newCount;
            
            const lastTranche = container.querySelector(`.tranche-item[data-tranche="${currentCount}"]`);
            if (lastTranche) {
                lastTranche.remove();
            }
        }
    }

    createTrancheElement(trancheNumber) {
        const trancheDiv = document.createElement('div');
        trancheDiv.className = 'tranche-item mb-3';
        trancheDiv.setAttribute('data-tranche', trancheNumber);
        
        trancheDiv.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">Tranche ${trancheNumber}</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <label class="form-label">Tranche Amount</label>
                            <div class="input-group">
                                <span class="input-group-text currency-symbol">£</span>
                                <input type="number" class="form-control tranche-amount" 
                                       name="tranche_amounts[]" min="0" step="1" placeholder="0">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Release Date</label>
                            <input type="date" class="form-control tranche-date" 
                                   name="tranche_dates[]">
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-6">
                            <label class="form-label">Interest Rate (%)</label>
                            <input type="number" class="form-control tranche-rate" 
                                   name="tranche_rates[]" min="0" max="50" step="0.1" 
                                   placeholder="Annual rate">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label">Description</label>
                            <input type="text" class="form-control tranche-description" 
                                   name="tranche_descriptions[]" placeholder="e.g., Land Purchase">
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Update currency symbols for the new tranche
        const currency = document.getElementById('currency').value;
        const symbol = currency === 'EUR' ? '€' : '£';
        trancheDiv.querySelector('.currency-symbol').textContent = symbol;
        
        return trancheDiv;
    }

    toggleTrancheMode() {
        const autoMode = document.getElementById('auto_tranches').checked;
        const autoSettings = document.getElementById('autoTrancheSettings');
        const manualControls = document.getElementById('manualTrancheControls');
        
        if (autoMode) {
            autoSettings.style.display = 'block';
            manualControls.style.display = 'none';
            // Set today's date as default
            const today = new Date().toISOString().split('T')[0];
            document.getElementById('autoStartDate').value = today;
            
            // Clear manual tranche inputs to prevent validation issues
            this.clearManualTranches();
        } else {
            autoSettings.style.display = 'none';
            manualControls.style.display = 'flex';
            
            // Clear auto-generated tranches if any exist
            this.clearAutoGeneratedTranches();
        }
    }
    
    clearManualTranches() {
        // Clear all manual tranche inputs without removing the containers
        const trancheAmounts = document.querySelectorAll('.tranche-amount');
        const trancheDates = document.querySelectorAll('.tranche-date');
        const trancheRates = document.querySelectorAll('.tranche-rate');
        const trancheDescriptions = document.querySelectorAll('.tranche-description');
        
        trancheAmounts.forEach(input => input.value = '');
        trancheDates.forEach(input => input.value = '');
        trancheRates.forEach(input => input.value = '');
        trancheDescriptions.forEach(input => input.value = '');
    }
    
    clearAutoGeneratedTranches() {
        // Clear only if tranches were auto-generated (check for specific descriptions)
        const descriptions = document.querySelectorAll('.tranche-description');
        descriptions.forEach(input => {
            if (input.value.includes('Month ') && input.value.includes('Tranche ')) {
                // This was auto-generated, clear all fields in this tranche
                const trancheItem = input.closest('.tranche-item');
                if (trancheItem) {
                    trancheItem.querySelector('.tranche-amount').value = '';
                    trancheItem.querySelector('.tranche-date').value = '';
                    trancheItem.querySelector('.tranche-rate').value = '';
                    trancheItem.querySelector('.tranche-description').value = '';
                }
            }
        });
    }

    generateAutoTranches() {
        const totalAmount = parseFloat(document.getElementById('autoTotalAmount').value) || 0;
        const startDate = document.getElementById('autoStartDate').value;
        const loanPeriod = parseInt(document.getElementById('autoLoanPeriod').value) || 12;
        const interestRate = parseFloat(document.getElementById('autoInterestRate').value) || 12;
        const trancheCount = parseInt(document.getElementById('autoTrancheCount').value) || 6;
        
        if (!totalAmount || !startDate || !trancheCount) {
            alert('Please fill in all required fields for auto generation.');
            return;
        }
        
        // Clear existing tranches
        const container = document.getElementById('tranchesContainer');
        container.innerHTML = '';
        
        // Calculate tranche amounts ensuring they work with validation constraints
        const baseAmount = Math.floor(totalAmount / trancheCount);
        const remainder = totalAmount - (baseAmount * trancheCount);
        const intervalMonths = Math.floor(loanPeriod / trancheCount);
        
        // Generate tranches
        for (let i = 0; i < trancheCount; i++) {
            const trancheDiv = this.createTrancheElement(i + 1);
            
            // Calculate release date for this tranche
            const releaseDate = new Date(startDate);
            releaseDate.setMonth(releaseDate.getMonth() + (i * intervalMonths));
            
            // Set the values
            const amountInput = trancheDiv.querySelector('.tranche-amount');
            const dateInput = trancheDiv.querySelector('.tranche-date');
            const rateInput = trancheDiv.querySelector('.tranche-rate');
            const descriptionInput = trancheDiv.querySelector('.tranche-description');
            
            // Distribute remainder among the last tranches to ensure exact total
            const trancheAmount = baseAmount + (i >= (trancheCount - remainder) ? 1 : 0);
            
            // Use exact amounts without rounding to maintain precision
            amountInput.value = trancheAmount;
            dateInput.value = releaseDate.toISOString().split('T')[0];
            // Ensure rate is within valid range (0-50%) and proper precision
            const clampedRate = Math.max(0, Math.min(50, parseFloat(interestRate.toFixed(1))));
            rateInput.value = clampedRate;
            descriptionInput.value = `Tranche ${i + 1} - Month ${i * intervalMonths + 1}`;
            
            container.appendChild(trancheDiv);
        }
        
        // Update tranche count display
        document.getElementById('trancheCount').textContent = trancheCount;
        
        // Switch to manual mode to show the generated tranches
        document.getElementById('manual_tranches').checked = true;
        // Manually show manual controls without clearing the generated tranches
        const autoSettings = document.getElementById('autoTrancheSettings');
        const manualControls = document.getElementById('manualTrancheControls');
        autoSettings.style.display = 'none';
        manualControls.style.display = 'flex';
        
        // Show success message
        this.showSuccessMessage(`Generated ${trancheCount} tranches successfully!`);
    }

    showSuccessMessage(message) {
        // Create success alert
        const successAlert = document.createElement('div');
        successAlert.className = 'alert alert-success alert-dismissible fade show';
        successAlert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the form
        const form = document.getElementById('calculatorForm');
        form.insertBefore(successAlert, form.firstChild);
        
        // Auto dismiss after 3 seconds
        setTimeout(() => {
            if (successAlert.parentNode) {
                successAlert.remove();
            }
        }, 3000);
        
        successAlert.scrollIntoView({ behavior: 'smooth' });
    }
}

// Global calculator instance
let calculator;

// Initialize calculator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    calculator = new LoanCalculator();
});

// Utility functions for form validation
function validateNumericInput(input, min = 0, max = Infinity) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value < min || value > max) {
        input.classList.add('is-invalid');
        return false;
    } else {
        input.classList.remove('is-invalid');
        return true;
    }
}

function validateRequiredField(input) {
    if (!input.value.trim()) {
        input.classList.add('is-invalid');
        return false;
    } else {
        input.classList.remove('is-invalid');
        return true;
    }
}

// Form validation on input
document.addEventListener('DOMContentLoaded', function() {
    // Add real-time validation to numeric inputs
    const numericInputs = document.querySelectorAll('input[type="number"]');
    numericInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const min = parseFloat(input.getAttribute('min')) || 0;
            const max = parseFloat(input.getAttribute('max')) || Infinity;
            validateNumericInput(input, min, max);
        });
    });
    
    // Add validation to required fields
    const requiredInputs = document.querySelectorAll('input[required], select[required]');
    requiredInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateRequiredField(input);
        });
    });
});

/**
 * Download PDF quote with charts
 */
function downloadPDFQuote() {
    const downloadBtn = document.getElementById('downloadPDFBtn');
    const originalText = downloadBtn.innerHTML;
    
    // Check if we have calculation results
    if (!window.calculatorResults || Object.keys(window.calculatorResults).length === 0) {
        console.error('No calculation results available for PDF download');
        showAlert('Please perform a calculation first before downloading PDF', 'error');
        return;
    }
    
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating PDF...';
    
    // Use async/await for better error handling
    (async function() {
        try {
            const response = await fetch('/download-pdf-quote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(window.calculatorResults || {})
            });

            console.log('PDF response status:', response.status);
            console.log('PDF response headers:', response.headers.get('content-type'));

            if (!response.ok) {
                const errorText = await response.text();
                console.error('PDF error response:', errorText);
                throw new Error('Failed to generate PDF: ' + response.statusText);
            }

            // Check if the response is actually a PDF
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/pdf')) {
                const text = await response.text();
                console.error('Expected PDF but got:', contentType, text.substring(0, 200));
                throw new Error('Server returned invalid response type: ' + contentType);
            }

            const blob = await response.blob();
            console.log('PDF blob received, size:', blob.size);
            
            if (blob.size === 0) {
                throw new Error('Empty PDF file received');
            }

            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `novellus_quote_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.pdf`;
            document.body.appendChild(a);
            a.click();
            
            // Clean up with a slight delay to ensure download starts
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }, 100);

            // Show success message
            showAlert('PDF quote downloaded successfully!', 'success');

        } catch (error) {
            console.error('Error downloading PDF:', error);
            console.error('Error details:', error.message, error.stack);
            
            // More specific error messages
            let errorMessage = 'Failed to download PDF quote';
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Network error - please check your connection and try again';
            } else if (error.message.includes('invalid response type')) {
                errorMessage = 'Server error - invalid PDF response received';
            } else if (error.message) {
                errorMessage = 'Failed to download PDF: ' + error.message;
            }
            
            showAlert(errorMessage, 'error');
        } finally {
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = originalText;
        }
    })();
}

/**
 * Download Excel quote with charts
 */
function downloadExcelQuote() {
    const downloadBtn = document.getElementById('downloadExcelBtn');
    const originalText = downloadBtn.innerHTML;
    
    // Check if we have calculation results
    if (!window.calculatorResults || Object.keys(window.calculatorResults).length === 0) {
        console.error('No calculation results available for Excel download');
        alert('Please perform a calculation first before downloading Excel');
        return;
    }
    
    console.log('Excel download - sending data:', window.calculatorResults);
    
    downloadBtn.disabled = true;
    downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Excel...';
    
    fetch('/download-excel-quote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(window.calculatorResults)
    })
    .then(response => {
        console.log('Excel response status:', response.status);
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(errorData.error || 'Failed to generate Excel');
            });
        }
        return response.blob();
    })
    .then(blob => {
        console.log('Excel blob received, size:', blob.size);
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `novellus_quote_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        showAlert('Excel quote downloaded successfully!', 'success');
    })
    .catch(error => {
        console.error('Error downloading Excel:', error);
        showAlert('Failed to download Excel quote. Please try again.', 'error');
    })
    .finally(() => {
        downloadBtn.disabled = false;
        downloadBtn.innerHTML = originalText;
    });
}

/**
 * Show alert message with auto-dismiss
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

// Report Control Functions
function initializeReportControls() {
    // Add event listeners for report toggle switches
    const reportControls = [
        'showCalculationResults',
        'showPaymentSchedule',
        'showCalculationBreakdown', 
        'showExcelBreakdown',
        'showPaymentChart',
        'showTrancheChart',
        'showInterestAccumulation'
    ];
    
    reportControls.forEach(controlId => {
        const control = document.getElementById(controlId);
        if (control) {
            control.addEventListener('change', handleReportToggle);
        }
    });
}

function handleReportToggle(event) {
    const controlId = event.target.id;
    const isChecked = event.target.checked;
    
    // Map control IDs to their corresponding section IDs
    const sectionMap = {
        'showCalculationResults': 'calculationResultsSection',
        'showPaymentSchedule': 'paymentScheduleCard',
        'showCalculationBreakdown': 'calculationBreakdownCard',
        'showExcelBreakdown': 'excelStyleBreakdownCard',
        'showPaymentChart': 'paymentChartCard',
        'showTrancheChart': 'trancheChartContainer',
        'showInterestAccumulation': 'interestAccumulationContainer'
    };
    
    const sectionId = sectionMap[controlId];
    const section = document.getElementById(sectionId);
    
    if (section) {
        section.style.display = isChecked ? 'block' : 'none';
    }
}

function toggleAllReports(showAll) {
    const reportControls = [
        'showCalculationResults',
        'showPaymentSchedule',
        'showCalculationBreakdown', 
        'showExcelBreakdown',
        'showPaymentChart',
        'showTrancheChart',
        'showInterestAccumulation'
    ];
    
    reportControls.forEach(controlId => {
        const control = document.getElementById(controlId);
        if (control) {
            control.checked = showAll;
            // Trigger change event to update visibility
            control.dispatchEvent(new Event('change'));
        }
    });
}

// Initialize report controls when the calculator is loaded
LoanCalculator.prototype.initializeReportControls = function() {
    initializeReportControls();
};

// Apply report visibility settings based on toggle states
LoanCalculator.prototype.applyReportVisibilitySettings = function() {
    const sectionMap = {
        'showCalculationResults': 'calculationResultsSection',
        'showPaymentSchedule': 'paymentScheduleCard',
        'showCalculationBreakdown': 'calculationBreakdownCard',
        'showExcelBreakdown': 'excelStyleBreakdownCard',
        'showPaymentChart': 'paymentChartCard',
        'showTrancheChart': 'trancheChartContainer',
        'showInterestAccumulation': 'interestAccumulationContainer'
    };
    
    Object.keys(sectionMap).forEach(controlId => {
        const control = document.getElementById(controlId);
        const section = document.getElementById(sectionMap[controlId]);
        
        if (control && section) {
            section.style.display = control.checked ? 'block' : 'none';
        }
    });
};
