function toggleAmountInputSections() {
    const amountInputType = document.querySelector('input[name="amount_input_type"]:checked')?.value;
    const netAmountSection = document.getElementById('netAmountSection');
    const grossAmountSection = document.getElementById('grossAmountSection');
    if (!amountInputType || !netAmountSection || !grossAmountSection) return;

    if (amountInputType === 'net') {
        netAmountSection.style.display = 'block';
        grossAmountSection.style.display = 'none';
    } else {
        netAmountSection.style.display = 'none';
        grossAmountSection.style.display = 'block';
        toggleGrossAmountInputs();
    }
}

function toggleGrossAmountInputs() {
    const grossAmountTypeRadio = document.querySelector('input[name="gross_amount_type"]:checked');
    if (!grossAmountTypeRadio) return;

    const grossAmountType = grossAmountTypeRadio.value;
    const grossFixedInput = document.getElementById('grossFixedInput');
    const grossPercentageInput = document.getElementById('grossPercentageInput');
    if (!grossFixedInput || !grossPercentageInput) return;

    if (grossAmountType === 'fixed') {
        grossFixedInput.style.setProperty('display', 'flex', 'important');
        grossPercentageInput.style.setProperty('display', 'none', 'important');
    } else {
        grossFixedInput.style.setProperty('display', 'none', 'important');
        grossPercentageInput.style.setProperty('display', 'flex', 'important');
        updateGrossAmountFromPercentage();
    }
}

function toggleRateInputs() {
    const rateInputTypeRadio = document.querySelector('input[name="rate_input_type"]:checked');
    if (!rateInputTypeRadio) return;

    const rateInputType = rateInputTypeRadio.value;
    const monthlyRateInput = document.getElementById('monthlyRateInput');
    const annualRateInput = document.getElementById('annualRateInput');
    const monthlyRateValue = document.getElementById('monthlyRateValue');
    const annualRateValue = document.getElementById('annualRateValue');
    if (!monthlyRateInput || !annualRateInput) return;

    if (rateInputType === 'monthly') {
        if (monthlyRateValue && annualRateValue) {
            const annual = parseFloat(annualRateValue.value);
            if (!isNaN(annual)) {
                monthlyRateValue.value = (annual / 12).toFixed(4);
            }
        }
        monthlyRateInput.style.setProperty('display', 'flex', 'important');
        annualRateInput.style.setProperty('display', 'none', 'important');
    } else {
        if (monthlyRateValue && annualRateValue) {
            const monthly = parseFloat(monthlyRateValue.value);
            if (!isNaN(monthly)) {
                annualRateValue.value = (monthly * 12).toFixed(4);
            }
        }
        monthlyRateInput.style.setProperty('display', 'none', 'important');
        annualRateInput.style.setProperty('display', 'flex', 'important');
    }
    updateRateEquivalenceNote();
}

function updateRateEquivalenceNote() {
    const rateInputType = document.querySelector('input[name="rate_input_type"]:checked')?.value;
    const note = document.getElementById('rateEquivalenceNote');
    if (!note) return;

    let text = '';
    if (rateInputType === 'monthly') {
        const monthly = parseFloat(document.getElementById('monthlyRateValue')?.value);
        if (!isNaN(monthly)) {
            text = `Equivalent to ${(monthly * 12).toFixed(2)}% per annum`;
        }
    } else {
        const annual = parseFloat(document.getElementById('annualRateValue')?.value);
        if (!isNaN(annual)) {
            text = `Equivalent to ${(annual / 12).toFixed(4)}% per month`;
        }
    }
    note.textContent = text;
}

function updateGrossAmountFromPercentage() {
    const propertyValueInput = document.getElementById('propertyValue');
    const grossPercentageInput = document.getElementById('grossAmountPercentage');
    const grossAmountInput = document.getElementById('grossAmountFixed');
    if (!propertyValueInput || !grossPercentageInput || !grossAmountInput) return;

    const propertyValue = parseFloat((propertyValueInput.value || '').replace(/,/g, ''));
    const percentage = parseFloat(grossPercentageInput.value);
    if (!isNaN(propertyValue) && !isNaN(percentage)) {
        const grossAmount = propertyValue * (percentage / 100);
        grossAmountInput.value = grossAmount.toFixed(2);
    }
}

function updateRepaymentOptions() {
    const loanTypeElement = document.getElementById('loanType');
    const repaymentSelect = document.getElementById('repaymentOption');
    if (!loanTypeElement || !repaymentSelect) return;

    const loanType = loanTypeElement.value;
    const optionsMap = {
        bridge: ['none', 'service_only', 'service_and_capital', 'capital_payment_only', 'flexible_payment'],
        term: ['service_only', 'service_and_capital'],
        development: ['none'],
        development2: ['none']
    };
    const allowed = optionsMap[loanType] || [];

    Array.from(repaymentSelect.options).forEach(opt => {
        opt.hidden = !allowed.includes(opt.value);
    });

    if (!allowed.includes(repaymentSelect.value)) {
        repaymentSelect.value = allowed[0] || '';
    }
    updateAdditionalParams();
}

function updateAdditionalParams() {
    const loanTypeElement = document.getElementById('loanType');
    const repaymentOptionElement = document.getElementById('repaymentOption');
    if (!loanTypeElement || !repaymentOptionElement) return;

    const loanType = loanTypeElement.value;
    const repaymentOption = repaymentOptionElement.value;

    const trancheSection = document.getElementById('developmentTrancheSection');
    const day1AdvanceSection = document.getElementById('day1AdvanceSection');
    const capitalRepaymentSection = document.getElementById('capitalRepaymentSection');
    const flexiblePaymentSection = document.getElementById('flexiblePaymentSection');
    const additionalParamsContainer = document.getElementById('additionalParams');

    let showAdditionalParams = false;

    if (trancheSection) {
        if (loanType === 'development' || loanType === 'development2') {
            trancheSection.style.display = 'block';
            showAdditionalParams = true;
        } else {
            trancheSection.style.display = 'none';
        }
    }

    if (day1AdvanceSection) {
        if (loanType === 'development' || loanType === 'development2') {
            day1AdvanceSection.style.display = 'block';
            showAdditionalParams = true;
        } else {
            day1AdvanceSection.style.display = 'none';
        }
    }

    if (capitalRepaymentSection) {
        if (repaymentOption === 'service_and_capital' || repaymentOption === 'capital_payment_only') {
            capitalRepaymentSection.style.display = 'block';
            showAdditionalParams = true;
        } else {
            capitalRepaymentSection.style.display = 'none';
        }
    }

    if (flexiblePaymentSection) {
        if (repaymentOption === 'flexible_payment') {
            flexiblePaymentSection.style.display = 'block';
            showAdditionalParams = true;
        } else {
            flexiblePaymentSection.style.display = 'none';
        }
    }

    if (additionalParamsContainer) {
        additionalParamsContainer.style.display = showAdditionalParams ? 'block' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof loadParametersFromURL === 'function') {
        loadParametersFromURL();
    }
    toggleAmountInputSections();
    toggleGrossAmountInputs();
    toggleRateInputs();
    updateRepaymentOptions();
    updateAdditionalParams();

    document.getElementById('loanType')?.addEventListener('change', () => {
        updateRepaymentOptions();
        updateAdditionalParams();
    });
    document.getElementById('repaymentOption')?.addEventListener('change', updateAdditionalParams);
    document.querySelectorAll('input[name="amount_input_type"]').forEach(el => {
        el.addEventListener('change', toggleAmountInputSections);
    });
    document.querySelectorAll('input[name="gross_amount_type"]').forEach(el => {
        el.addEventListener('change', toggleGrossAmountInputs);
    });
    document.querySelectorAll('input[name="rate_input_type"]').forEach(el => {
        el.addEventListener('change', toggleRateInputs);
    });
    document.getElementById('currency')?.addEventListener('change', updateAdditionalParams);
});

