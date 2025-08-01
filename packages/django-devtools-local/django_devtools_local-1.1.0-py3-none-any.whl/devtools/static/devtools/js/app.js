/**
 * Django DevTools - Main JavaScript
 * Version: 1.0.0
 */

// Global configuration
const DevTools = {
    config: {
        animationDuration: 300,
        tablePageSize: 50,
        codeEditorTheme: 'default'
    },
    
    // Data cache
    cache: new Map(),
    
    // Global state
    state: {
        currentApp: null,
        currentModel: null,
        isLoading: false
    }
};

/**
 * General utilities
 */
DevTools.Utils = {
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: function(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, function(m) { 
            return map[m]; 
        });
    },
    
    /**
     * Format numbers with separators
     */
    formatNumber: function(num) {
        return new Intl.NumberFormat('en-US').format(num);
    },
    
    /**
     * Debounce for repeated events
     */
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Display toast notifications
     */
    showToast: function(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toastContainer') || 
                              this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-info-circle me-2"></i>${this.escapeHtml(message)}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            delay: duration
        });
        bsToast.show();
        
        // Auto cleanup
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration + 1000);
    },
    
    /**
     * Create toast container if it doesn't exist
     */
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },
    
    /**
     * Copy to clipboard
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Text copied to clipboard', 'success');
            }).catch(() => {
                this.showToast('Error copying text', 'danger');
            });
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                this.showToast('Text copied to clipboard', 'success');
            } catch (err) {
                this.showToast('Error copying text', 'danger');
            }
            
            document.body.removeChild(textArea);
        }
    },
    
    /**
     * Loading state for elements
     */
    setLoading: function(element, isLoading = true) {
        if (isLoading) {
            element.classList.add('loading');
            element.style.pointerEvents = 'none';
            element.style.opacity = '0.6';
        } else {
            element.classList.remove('loading');
            element.style.pointerEvents = '';
            element.style.opacity = '';
        }
    },
    
    /**
     * Smooth scroll animation
     */
    smoothScrollTo: function(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
};

/**
 * AJAX request handler
 */
DevTools.API = {
    
    /**
     * Generic GET request
     */
    get: function(url, options = {}) {
        return fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },
    
    /**
     * Generic POST request
     */
    post: function(url, data, options = {}) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            },
            body: JSON.stringify(data)
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },
    
    /**
     * Get CSRF token
     */
    getCSRFToken: function() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name=csrf-token]')?.content ||
                     document.querySelector('input[name=csrfmiddlewaretoken]')?.value;
        
        if (!token) {
            console.warn('CSRF token not found');
        }
        
        return token || '';
    }
};

/**
 * Code editor handler
 */
DevTools.CodeEditor = {
    
    /**
     * Initialize editor
     */
    init: function(editorId = 'codeEditor') {
        const editor = document.getElementById(editorId);
        if (!editor) return null;
        
        // Basic configuration
        editor.addEventListener('keydown', this.handleKeyDown.bind(this));
        editor.addEventListener('input', this.handleInput.bind(this));
        
        // Auto-resize
        this.setupAutoResize(editor);
        
        return editor;
    },
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyDown: function(event) {
        const editor = event.target;
        
        // Ctrl+Enter to execute
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            const executeBtn = document.getElementById('executeBtn');
            if (executeBtn) executeBtn.click();
        }
        
        // Tab for indentation
        if (event.key === 'Tab') {
            event.preventDefault();
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            
            // Insert 4 spaces
            editor.value = editor.value.substring(0, start) + 
                          '    ' + 
                          editor.value.substring(end);
            
            editor.selectionStart = editor.selectionEnd = start + 4;
        }
    },
    
    /**
     * Handle input
     */
    handleInput: function(event) {
        // Basic auto-completion
        this.handleAutoComplete(event);
    },
    
    /**
     * Simple auto-completion
     */
    handleAutoComplete: function(event) {
        const editor = event.target;
        const value = editor.value;
        const cursorPos = editor.selectionStart;
        
        // Auto-close parentheses and quotes
        const pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        };
        
        const lastChar = event.data;
        if (pairs[lastChar]) {
            const before = value.substring(0, cursorPos);
            const after = value.substring(cursorPos);
            
            editor.value = before + pairs[lastChar] + after;
            editor.selectionStart = editor.selectionEnd = cursorPos;
        }
    },
    
    /**
     * Textarea auto-resize
     */
    setupAutoResize: function(editor) {
        const resize = () => {
            editor.style.height = 'auto';
            editor.style.height = Math.max(200, editor.scrollHeight) + 'px';
        };
        
        editor.addEventListener('input', resize);
        resize(); // Initial resize
    },
    
    /**
     * Insert code at cursor position
     */
    insertCode: function(editorId, code) {
        const editor = document.getElementById(editorId);
        if (!editor) return;
        
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        
        editor.value = editor.value.substring(0, start) + 
                      code + 
                      editor.value.substring(end);
        
        editor.selectionStart = editor.selectionEnd = start + code.length;
        editor.focus();
    }
};

/**
 * Table handler
 */
DevTools.Tables = {
    
    /**
     * Enhance tables with search and sort
     */
    enhance: function(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        this.addSearchCapability(table);
        this.addSortCapability(table);
        this.addRowHighlight(table);
    },
    
    /**
     * Add search capability
     */
    addSearchCapability: function(table) {
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.className = 'form-control mb-3';
        searchInput.placeholder = 'Search in table...';
        
        table.parentNode.insertBefore(searchInput, table);
        
        searchInput.addEventListener('input', DevTools.Utils.debounce((e) => {
            this.filterTable(table, e.target.value);
        }, 300));
    },
    
    /**
     * Filter table rows
     */
    filterTable: function(table, searchTerm) {
        const rows = table.querySelectorAll('tbody tr');
        const term = searchTerm.toLowerCase();
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    },
    
    /**
     * Add sort capability
     */
    addSortCapability: function(table) {
        const headers = table.querySelectorAll('thead th');
        
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => {
                this.sortTable(table, index);
            });
        });
    },
    
    /**
     * Sort table
     */
    sortTable: function(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aText = a.cells[columnIndex]?.textContent.trim() || '';
            const bText = b.cells[columnIndex]?.textContent.trim() || '';
            
            // Numeric sort if possible
            const aNum = parseFloat(aText);
            const bNum = parseFloat(bText);
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return aNum - bNum;
            }
            
            return aText.localeCompare(bText);
        });
        
        // Reinsert sorted rows
        rows.forEach(row => tbody.appendChild(row));
    },
    
    /**
     * Add row highlighting
     */
    addRowHighlight: function(table) {
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            row.addEventListener('mouseenter', () => {
                row.classList.add('table-warning');
            });
            
            row.addEventListener('mouseleave', () => {
                row.classList.remove('table-warning');
            });
        });
    }
};

/**
 * Modal handler
 */
DevTools.Modal = {
    
    /**
     * Open modal with dynamic content
     */
    show: function(modalId, title, content) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        const titleElement = modal.querySelector('.modal-title');
        const bodyElement = modal.querySelector('.modal-body');
        
        if (titleElement) titleElement.textContent = title;
        if (bodyElement) bodyElement.innerHTML = content;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        return bsModal;
    },
    
    /**
     * Close modal
     */
    hide: function(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) bsModal.hide();
    }
};

/**
 * Initialization on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize code editor
    DevTools.CodeEditor.init();
    
    // Enhance existing tables
    document.querySelectorAll('.table').forEach((table, index) => {
        table.id = table.id || `devtools-table-${index}`;
        DevTools.Tables.enhance(table.id);
    });
    
    // Handle Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Entry animation for cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
    
    // Global JavaScript error handling
    window.addEventListener('error', function(e) {
        console.error('DevTools error:', e.error);
        DevTools.Utils.showToast('A JavaScript error occurred', 'danger');
    });
    
    // Confirmation before closing if code is being edited
    window.addEventListener('beforeunload', function(e) {
        const editor = document.getElementById('codeEditor');
        if (editor && editor.value.trim() && !confirm) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
    
    console.log('🔧 Django DevTools initialized successfully');
});

// Global export for use in templates
window.DevTools = DevTools; 