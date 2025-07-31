/**
 * Simplified Currency Theme Manager - Optimized for Performance
 * Minimal, fast currency switching for button colors and logos
 */

class SimpleCurrencyTheme {
    constructor() {
        this.currentCurrency = 'GBP';
        this.init();
    }

    init() {
        // Set up currency dropdown listener only
        const currencySelect = document.getElementById('currency');
        if (currencySelect) {
            currencySelect.addEventListener('change', (e) => {
                this.switchCurrency(e.target.value);
            });
        }
        
        // Initial setup
        this.switchCurrency('GBP');
        console.log('Simple Currency Theme initialized');
    }

    switchCurrency(currency) {
        this.currentCurrency = currency;
        console.log(`Switching to ${currency} theme`);
        
        // Update data attributes for CSS targeting
        document.documentElement.setAttribute('data-currency', currency);
        document.body.setAttribute('data-currency', currency);
        
        // Update buttons immediately
        this.updateButtons(currency);
        
        // Update logo
        this.updateLogo(currency);
        
        // Update currency symbols
        this.updateSymbols(currency);
        
        // Update table headers and other elements
        this.updateThemeElements(currency);
    }

    updateButtons(currency) {
        const colors = {
            'GBP': { primary: '#B8860B', dark: '#8B6914' },
            'EUR': { primary: '#509664', dark: '#3d7450' }
        };
        
        const color = colors[currency];
        
        // Update Calculate button
        const calculateBtns = document.querySelectorAll('.calculate-button, .btn-primary');
        calculateBtns.forEach(btn => {
            btn.style.setProperty('background-color', color.primary, 'important');
            btn.style.setProperty('border-color', color.primary, 'important');
            btn.style.setProperty('background-image', 'none', 'important');
        });
        
        // Update Save button
        const saveBtns = document.querySelectorAll('#saveLoanBtn, .btn-success');
        saveBtns.forEach(btn => {
            btn.style.setProperty('background-color', color.dark, 'important');
            btn.style.setProperty('border-color', color.dark, 'important');
            btn.style.setProperty('background-image', 'none', 'important');
        });
    }

    updateLogo(currency) {
        const logo = document.getElementById('navbarLogo');
        if (logo) {
            // For now, use the same logo for both currencies
            // TODO: Create teal version of logo for EUR currency
            logo.src = '/static/novellus_logo.png';
            logo.style.height = '32px';
            logo.style.width = 'auto';
            logo.style.objectFit = 'contain';
            
            if (currency === 'EUR') {
                // Apply green filter to logo for EUR currency (#509664)
                logo.style.filter = 'hue-rotate(90deg) saturate(0.8) brightness(0.7)';
            } else {
                // Remove filter for GBP (original golden color)
                logo.style.filter = 'none';
            }
        }
    }

    updateSymbols(currency) {
        const symbol = currency === 'GBP' ? '£' : '€';
        const symbols = document.querySelectorAll('.currency-symbol');
        symbols.forEach(el => el.textContent = symbol);
    }

    updateThemeElements(currency) {
        const colors = {
            'GBP': { primary: '#B8860B', dark: '#8B6914' },
            'EUR': { primary: '#509664', dark: '#3d7450' }
        };
        
        const color = colors[currency];
        
        // Update table headers
        const tableHeaders = document.querySelectorAll('.table thead th, .card-header, .bg-primary');
        tableHeaders.forEach(header => {
            header.style.setProperty('background-color', color.primary, 'important');
            header.style.setProperty('border', '2px solid #000000', 'important');
            header.style.setProperty('color', 'white', 'important');
        });
        
        // Force repaint to ensure changes are visible
        document.body.style.display = 'none';
        document.body.offsetHeight; // trigger reflow
        document.body.style.display = 'block';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.currencyTheme = new SimpleCurrencyTheme();
});