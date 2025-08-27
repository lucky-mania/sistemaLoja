// Main JavaScript file for the inventory management system

document.addEventListener('DOMContentLoaded', function() {
    // Initialize currency formatting
    initCurrencyInputs();
    
    // Initialize tooltips
    initTooltips();
    
    // Initialize auto-dismiss alerts
    initAlerts();
    
    // Initialize form validations
    initFormValidations();
});

// Currency input formatting
function initCurrencyInputs() {
    const currencyInputs = document.querySelectorAll('.currency-input');
    
    currencyInputs.forEach(input => {
        // Format on input
        input.addEventListener('input', function(e) {
            formatCurrency(e.target);
        });
        
        // Format on blur
        input.addEventListener('blur', function(e) {
            formatCurrency(e.target);
        });
        
        // Initial formatting if value exists
        if (input.value) {
            formatCurrency(input);
        }
    });
}

function formatCurrency(input) {
    let value = input.value;
    
    // Remove all non-digit characters except comma and dot
    value = value.replace(/[^\d,.-]/g, '');
    
    // Replace comma with dot for parsing
    value = value.replace(',', '.');
    
    // Parse as float
    const numericValue = parseFloat(value) || 0;
    
    // Format back to Brazilian currency format
    const formatted = numericValue.toFixed(2).replace('.', ',');
    
    input.value = formatted;
}

// Parse currency value to float
function parseCurrency(value) {
    if (!value) return 0;
    return parseFloat(value.replace(/[^\d,]/g, '').replace(',', '.')) || 0;
}

// Format number to Brazilian currency
function formatBrazilianCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-dismiss alerts after 5 seconds
function initAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Form validation initialization
function initFormValidations() {
    // Custom validation styles
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Utility function to show loading state
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

// Utility function to hide loading state
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Confirmation dialog for delete actions
function confirmDelete(message = 'Tem certeza que deseja excluir este item?') {
    return confirm(message);
}

// Format date to Brazilian format
function formatBrazilianDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString + 'T00:00:00');
    return date.toLocaleDateString('pt-BR');
}

// Debounce function for search inputs
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

// Search functionality with debounce
function initSearchDebounce() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    
    searchInputs.forEach(input => {
        const form = input.closest('form');
        if (form) {
            const debouncedSubmit = debounce(() => {
                form.submit();
            }, 500);
            
            input.addEventListener('input', debouncedSubmit);
        }
    });
}

// Initialize search debounce if search inputs exist
if (document.querySelector('input[name="search"]')) {
    initSearchDebounce();
}

// Product selection handler for sales form
function initProductSelection() {
    const productSelect = document.getElementById('produto_id');
    if (!productSelect) return;
    
    productSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        const saleDetails = document.getElementById('sale-details');
        const quantityInput = document.getElementById('quantidade');
        const priceInput = document.getElementById('valor_venda');
        const availableStock = document.getElementById('available-stock');
        
        if (selectedOption.value) {
            const stock = parseInt(selectedOption.dataset.stock);
            const price = parseFloat(selectedOption.dataset.price);
            
            // Show sale details
            if (saleDetails) {
                saleDetails.style.display = 'block';
            }
            
            // Set available stock
            if (availableStock) {
                availableStock.textContent = stock;
            }
            
            if (quantityInput) {
                quantityInput.max = stock;
                quantityInput.value = 1;
            }
            
            // Set price
            if (priceInput) {
                priceInput.value = price.toFixed(2).replace('.', ',');
            }
            
            // Calculate total
            updateSaleTotal();
        } else {
            if (saleDetails) {
                saleDetails.style.display = 'none';
            }
        }
    });
}

// Update sale total calculation
function updateSaleTotal() {
    const quantityInput = document.getElementById('quantidade');
    const priceInput = document.getElementById('valor_venda');
    const totalInput = document.getElementById('total');
    
    if (!quantityInput || !priceInput || !totalInput) return;
    
    const quantity = parseInt(quantityInput.value) || 0;
    const price = parseCurrency(priceInput.value);
    const total = quantity * price;
    
    totalInput.value = total.toFixed(2).replace('.', ',');
}

// Initialize sale form if it exists
if (document.getElementById('produto_id')) {
    initProductSelection();
    
    // Add event listeners for total calculation
    const quantityInput = document.getElementById('quantidade');
    const priceInput = document.getElementById('valor_venda');
    
    if (quantityInput) {
        quantityInput.addEventListener('input', updateSaleTotal);
    }
    
    if (priceInput) {
        priceInput.addEventListener('input', updateSaleTotal);
    }
}

// Table row hover effects
function initTableEffects() {
    const tables = document.querySelectorAll('.table-hover');
    
    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = 'rgba(0, 123, 255, 0.05)';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    });
}

// Initialize table effects
initTableEffects();

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            const target = document.querySelector(href);
            
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize smooth scrolling
initSmoothScrolling();

// Export functionality
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    const csvContent = [];
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        
        cols.forEach(col => {
            csvRow.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
        });
        
        csvContent.push(csvRow.join(','));
    });
    
    const csvData = csvContent.join('\n');
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Initialize print buttons
function initPrintButtons() {
    const printButtons = document.querySelectorAll('[data-action="print"]');
    
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            printPage();
        });
    });
}

// Initialize print functionality
initPrintButtons();

// Theme toggle functionality (future enhancement)
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    themeToggle.addEventListener('click', function() {
        const theme = document.documentElement.getAttribute('data-theme');
        const newTheme = theme === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
}

// Initialize theme toggle
initThemeToggle();

// Keyboard shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save (prevent default save)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveButton = document.querySelector('button[type="submit"]');
            if (saveButton) {
                saveButton.click();
            }
        }
        
        // Escape key to cancel/go back
        if (e.key === 'Escape') {
            const cancelButton = document.querySelector('a[href*="back"], .btn-secondary');
            if (cancelButton) {
                cancelButton.click();
            }
        }
    });
}

// Initialize keyboard shortcuts
initKeyboardShortcuts();

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    
    // Show user-friendly error message (optional)
    // You can implement a toast notification here
});

// Utility function to show toast notifications
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Make utility functions globally available
window.inventorySystem = {
    formatCurrency,
    parseCurrency,
    formatBrazilianCurrency,
    showLoading,
    hideLoading,
    confirmDelete,
    exportTableToCSV,
    showToast,
    updateSaleTotal
};
