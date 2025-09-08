/**
 * Novellus Loan Management System - Main JavaScript
 * Global utilities, event handlers, and common functionality
 */

// Global application object
window.Novellus = {
    utils: {},
    components: {},
    config: {
        currency: {
            GBP: { symbol: '£', locale: 'en-GB' },
            EUR: { symbol: '€', locale: 'en-GB' },
            USD: { symbol: '$', locale: 'en-US' }
        }
    }
};

/**
 * Utility Functions
 */
Novellus.utils = {
    // Format currency with proper symbol and locale
    formatCurrency: function(amount, currency = 'GBP') {
        const config = Novellus.config.currency[currency];
        if (!config) return `£${amount.toLocaleString()}`;
        
        return new Intl.NumberFormat(config.locale, {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    },

    // Format percentage
    formatPercentage: function(value, decimals = 1) {
        return `${value.toFixed(decimals)}%`;
    },

    // Format date
    formatDate: function(date, format = 'short') {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        
        const options = {
            short: { day: '2-digit', month: '2-digit', year: 'numeric' },
            long: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
            medium: { year: 'numeric', month: 'short', day: 'numeric' }
        };
        
        return date.toLocaleDateString('en-GB', options[format] || options.short);
    },

    // Parse currency string to number
    parseCurrency: function(currencyString) {
        if (typeof currencyString === 'number') return currencyString;
        return parseFloat(currencyString.replace(/[£€$,]/g, '')) || 0;
    },

    // Debounce function
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction() {
            const context = this;
            const args = arguments;
            const later = function() {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    },

    // Show loading spinner
    showLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            element.classList.add('loading');
            const spinner = element.querySelector('.spinner-border');
            if (spinner) {
                spinner.style.display = 'inline-block';
            }
        }
    },

    // Hide loading spinner
    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            element.classList.remove('loading');
            const spinner = element.querySelector('.spinner-border');
            if (spinner) {
                spinner.style.display = 'none';
            }
        }
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        // Initialize and show toast
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        bsToast.show();
        
        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Validate email format
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Validate phone number (basic)
    validatePhone: function(phone) {
        const re = /^[\d\s\-\(\)\+]+$/;
        return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
    },

    // Copy text to clipboard
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                Novellus.utils.showToast('Copied to clipboard', 'success');
            }).catch(() => {
                Novellus.utils.showToast('Failed to copy to clipboard', 'danger');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                Novellus.utils.showToast('Copied to clipboard', 'success');
            } catch (err) {
                Novellus.utils.showToast('Failed to copy to clipboard', 'danger');
            }
            document.body.removeChild(textArea);
        }
    }
};

/**
 * Form Utilities
 */
Novellus.forms = {
    // Serialize form data to object
    serialize: function(form) {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        return data;
    },

    // Validate form
    validate: function(form) {
        let isValid = true;
        const invalidFields = [];
        const requiredFields = form.querySelectorAll('[required]');

        // Helper to remove tooltip
        const removeTooltip = (field) => {
            const tooltip = bootstrap.Tooltip.getInstance(field);
            if (tooltip) tooltip.dispose();
            field.removeAttribute('data-bs-toggle');
            field.removeAttribute('title');
        };

        requiredFields.forEach(field => {
            const label = form.querySelector(`label[for="${field.id}"]`);
            const labelText = label ? label.textContent.trim() : field.name || field.id;
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                field.dataset.bsToggle = 'tooltip';
                field.title = `${labelText} is required`;
                if (!bootstrap.Tooltip.getInstance(field)) {
                    new bootstrap.Tooltip(field);
                }
                isValid = false;
                invalidFields.push(labelText);
            } else {
                field.classList.remove('is-invalid');
                removeTooltip(field);
            }
        });

        // Email validation
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(field => {
            if (field.value && !Novellus.utils.validateEmail(field.value)) {
                field.classList.add('is-invalid');
                field.dataset.bsToggle = 'tooltip';
                field.title = 'Invalid email address';
                if (!bootstrap.Tooltip.getInstance(field)) {
                    new bootstrap.Tooltip(field);
                }
                isValid = false;
                const label = form.querySelector(`label[for="${field.id}"]`);
                invalidFields.push(label ? label.textContent.trim() : field.name || field.id);
            } else {
                field.classList.remove('is-invalid');
                removeTooltip(field);
            }
        });

        // Phone validation
        const phoneFields = form.querySelectorAll('input[type="tel"]');
        phoneFields.forEach(field => {
            if (field.value && !Novellus.utils.validatePhone(field.value)) {
                field.classList.add('is-invalid');
                field.dataset.bsToggle = 'tooltip';
                field.title = 'Invalid phone number';
                if (!bootstrap.Tooltip.getInstance(field)) {
                    new bootstrap.Tooltip(field);
                }
                isValid = false;
                const label = form.querySelector(`label[for="${field.id}"]`);
                invalidFields.push(label ? label.textContent.trim() : field.name || field.id);
            } else {
                field.classList.remove('is-invalid');
                removeTooltip(field);
            }
        });

        if (!isValid) {
            const message = 'Please correct: ' + invalidFields.join(', ');
            if (window.notifications) {
                window.notifications.error(message);
            } else {
                Novellus.utils.showToast(message, 'danger');
            }
        }

        return isValid;
    },

    // Reset form validation
    resetValidation: function(form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => {
            field.classList.remove('is-invalid');
            const tooltip = bootstrap.Tooltip.getInstance(field);
            if (tooltip) tooltip.dispose();
            field.removeAttribute('data-bs-toggle');
            field.removeAttribute('title');
        });
    }
};

/**
 * API Helper Functions
 */
Novellus.api = {
    // Make API request with error handling
    request: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // GET request
    get: function(url) {
        return this.request(url, { method: 'GET' });
    },

    // POST request
    post: function(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // PUT request
    put: function(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // DELETE request
    delete: function(url) {
        return this.request(url, { method: 'DELETE' });
    }
};

/**
 * Component Initializers
 */
Novellus.components = {
    // Initialize tooltips
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    // Initialize popovers
    initPopovers: function() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function(popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    },

    // Initialize data tables (if needed)
    initDataTables: function() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            // Add sorting functionality
            const headers = table.querySelectorAll('th[data-sort]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(table, header.cellIndex, header.dataset.sort);
                });
            });
        });
    },

    // Sort table
    sortTable: function(table, columnIndex, dataType) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAscending = table.dataset.sortDirection !== 'asc';
        
        rows.sort((a, b) => {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            let comparison = 0;
            
            switch (dataType) {
                case 'number':
                    comparison = Novellus.utils.parseCurrency(aValue) - Novellus.utils.parseCurrency(bValue);
                    break;
                case 'date':
                    comparison = new Date(aValue) - new Date(bValue);
                    break;
                default:
                    comparison = aValue.localeCompare(bValue);
            }
            
            return isAscending ? comparison : -comparison;
        });
        
        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
        
        // Update sort direction
        table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
        
        // Update header indicators
        table.querySelectorAll('th[data-sort]').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        
        const currentHeader = table.querySelectorAll('th[data-sort]')[columnIndex];
        currentHeader.classList.add(isAscending ? 'sorted-asc' : 'sorted-desc');
    }
};

/**
 * Event Handlers
 */
document.addEventListener('DOMContentLoaded', function() {
    // Add tooltips to toggle buttons
    document.querySelectorAll('.btn-group label.btn').forEach(btn => {
        btn.setAttribute('title', btn.textContent.trim());
        btn.setAttribute('data-bs-toggle', 'tooltip');
    });

    // Initialize Bootstrap components
    Novellus.components.initTooltips();
    Novellus.components.initPopovers();
    Novellus.components.initDataTables();
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 300);
            }, 5000);
        }
    });
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                Novellus.utils.showLoading(submitButton);
            }
        });
    });
    
    // Add click-to-copy functionality
    const copyElements = document.querySelectorAll('[data-copy]');
    copyElements.forEach(element => {
        element.style.cursor = 'pointer';
        element.addEventListener('click', function() {
            const textToCopy = this.dataset.copy || this.textContent;
            Novellus.utils.copyToClipboard(textToCopy);
        });
    });
    
    // Add confirmation dialogs
    const confirmElements = document.querySelectorAll('[data-confirm]');
    confirmElements.forEach(element => {
        element.addEventListener('click', function(e) {
            const confirmMessage = this.dataset.confirm;
            if (!confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // Auto-format currency inputs
    const currencyInputs = document.querySelectorAll('.currency-input');
    currencyInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = Novellus.utils.parseCurrency(this.value);
            if (!isNaN(value)) {
                this.value = value.toLocaleString();
            }
        });
        
        input.addEventListener('focus', function() {
            const value = Novellus.utils.parseCurrency(this.value);
            if (!isNaN(value)) {
                this.value = value.toString();
            }
        });
    });
    
    // Auto-format percentage inputs
    const percentageInputs = document.querySelectorAll('.percentage-input');
    percentageInputs.forEach(input => {
        input.addEventListener('blur', function() {
            const value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(3);
            }
        });
    });
    
    // Add search functionality to tables
    const searchInputs = document.querySelectorAll('[data-search-table]');
    searchInputs.forEach(input => {
        const tableSelector = input.dataset.searchTable;
        const table = document.querySelector(tableSelector);
        
        if (table) {
            const searchFunction = Novellus.utils.debounce(function() {
                const searchTerm = input.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }, 300);
            
            input.addEventListener('input', searchFunction);
        }
    });
});

// Handle browser back/forward navigation
window.addEventListener('popstate', function(event) {
    if (event.state) {
        // Handle state restoration if needed
        console.log('Navigation state:', event.state);
    }
});

// Handle online/offline status
window.addEventListener('online', function() {
    Novellus.utils.showToast('Connection restored', 'success');
});

window.addEventListener('offline', function() {
    Novellus.utils.showToast('Connection lost - some features may not work', 'warning');
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    
    // Don't show error toast for script loading errors in development
    if (event.filename && event.filename.includes('localhost')) {
        return;
    }
    
    Novellus.utils.showToast('An unexpected error occurred', 'danger');
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Prevent the default behavior (logging to console)
    event.preventDefault();
    
    Novellus.utils.showToast('A network or processing error occurred', 'danger');
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + S to save forms
    if ((event.ctrlKey || event.metaKey) && event.key === 's') {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            event.preventDefault();
            const submitButton = activeForm.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                submitButton.click();
            }
        }
    }
    
    // Escape key to close modals
    if (event.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modal = bootstrap.Modal.getInstance(openModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Export for use in other scripts
window.Novellus = Novellus;
