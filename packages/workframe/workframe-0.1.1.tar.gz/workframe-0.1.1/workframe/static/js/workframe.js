/*
 * WorkFrame JavaScript
 * Enhanced UX for business applications
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Enhanced confirmation dialogs for destructive actions
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            const details = this.getAttribute('data-confirm-details') || '';
            const confirmText = this.getAttribute('data-confirm-text') || 'Confirm';
            const confirmClass = this.getAttribute('data-confirm-class') || 'btn-danger';
            
            WorkFrame.showConfirmation(message, details, confirmText, confirmClass, () => {
                // If it's a form submission, submit the form
                if (this.closest('form')) {
                    this.closest('form').submit();
                } 
                // If it's a link, navigate to it
                else if (this.href) {
                    window.location.href = this.href;
                }
                // If it has a click handler, trigger it
                else if (this.onclick) {
                    this.onclick();
                }
            });
        });
    });
    
    // Auto-dismiss flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form enhancement: loading states
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable after 10 seconds as fallback
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
    
    // Enhanced table sorting (if needed)
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const sortField = this.getAttribute('data-sort');
            const currentUrl = new URL(window.location);
            const currentSort = currentUrl.searchParams.get('sort');
            const currentOrder = currentUrl.searchParams.get('order');
            
            let newOrder = 'asc';
            if (currentSort === sortField && currentOrder === 'asc') {
                newOrder = 'desc';
            }
            
            currentUrl.searchParams.set('sort', sortField);
            currentUrl.searchParams.set('order', newOrder);
            window.location.href = currentUrl.toString();
        });
    });
    
    // Search form enhancement
    const searchForms = document.querySelectorAll('form[data-search]');
    searchForms.forEach(function(form) {
        const searchInput = form.querySelector('input[type="search"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(function() {
                    if (searchInput.value.length >= 2 || searchInput.value.length === 0) {
                        form.submit();
                    }
                }, 500);
            });
        }
    });
    
    // Dashboard module cards click enhancement
    const moduleCards = document.querySelectorAll('.dashboard-module-card');
    moduleCards.forEach(function(card) {
        card.addEventListener('click', function() {
            const link = this.querySelector('a');
            if (link) {
                window.location.href = link.href;
            }
        });
    });
    
    // Field validation enhancement
    const requiredFields = document.querySelectorAll('input[required], select[required], textarea[required]');
    requiredFields.forEach(function(field) {
        field.addEventListener('invalid', function() {
            this.classList.add('is-invalid');
        });
        
        field.addEventListener('input', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            }
        });
    });
    
});

// Utility functions
window.WorkFrame = {
    
    // Show loading state on element
    showLoading: function(element) {
        element.classList.add('loading');
    },
    
    // Hide loading state on element  
    hideLoading: function(element) {
        element.classList.remove('loading');
    },
    
    // Show toast notification
    showToast: function(message, type = 'info') {
        // Create toast element if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        const toastElement = document.createElement('div');
        toastElement.className = `toast border-0 bg-${type}`;
        toastElement.innerHTML = `
            <div class="toast-body text-white">
                ${message}
                <button type="button" class="btn-close btn-close-white float-end" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toastElement);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove from DOM after hiding
        toastElement.addEventListener('hidden.bs.toast', function() {
            toastElement.remove();
        });
    },
    
    // Confirm action with custom message (legacy)
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Enhanced confirmation modal
    showConfirmation: function(message, details = '', confirmText = 'Confirm', confirmClass = 'btn-danger', callback = null) {
        const modal = document.getElementById('confirmationModal');
        const messageEl = document.getElementById('confirmationMessage');
        const detailsEl = document.getElementById('confirmationDetails');
        const confirmBtn = document.getElementById('confirmActionBtn');
        
        if (!modal || !messageEl || !detailsEl || !confirmBtn) {
            // Fallback to browser confirm if modal elements not found
            if (confirm(message)) {
                if (callback) callback();
            }
            return;
        }
        
        // Set message and details
        messageEl.textContent = message;
        if (details) {
            detailsEl.textContent = details;
            detailsEl.style.display = 'block';
        } else {
            detailsEl.style.display = 'none';
        }
        
        // Update confirm button
        confirmBtn.textContent = confirmText;
        confirmBtn.className = `btn ${confirmClass}`;
        
        // Remove existing event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        
        // Add new event listener
        if (callback) {
            newConfirmBtn.addEventListener('click', function() {
                callback();
                bootstrap.Modal.getInstance(modal).hide();
            });
        }
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }
    
};