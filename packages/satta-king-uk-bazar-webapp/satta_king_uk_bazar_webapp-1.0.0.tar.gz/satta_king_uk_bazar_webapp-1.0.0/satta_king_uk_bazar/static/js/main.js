// Satta King UK Bazar - Main JavaScript

// Global variables
let searchTimeout;
let lastUpdateTime = Date.now();

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize the application
function initializeApp() {
    setupEventListeners();
    updateTimestamp();
    setupAutoRefresh();
    initializeSearchHighlight();
    setupTableEnhancements();
    checkConnectionStatus();
}

// Setup event listeners
function setupEventListeners() {
    // Search input with debounce
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }

    // Table row click handlers
    setupTableClickHandlers();
    
    // Mobile touch handlers
    setupMobileHandlers();
}

// Search functionality
function searchGames() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        performSearch();
    }
}

function performSearch() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    const gameRows = document.querySelectorAll('tbody tr');
    let visibleCount = 0;

    gameRows.forEach(function(row) {
        const gameName = row.querySelector('td strong');
        const gameTime = row.querySelector('td small');
        
        if (gameName) {
            const nameText = gameName.textContent.toLowerCase();
            const timeText = gameTime ? gameTime.textContent.toLowerCase() : '';
            
            if (searchTerm === '' || nameText.includes(searchTerm) || timeText.includes(searchTerm)) {
                row.style.display = '';
                highlightSearchTerm(row, searchTerm);
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        }
    });

    // Show search results count
    updateSearchResultsCount(visibleCount, gameRows.length);
    
    // Show/hide section headers based on visible games
    updateSectionVisibility();
}

// Highlight search terms
function highlightSearchTerm(row, searchTerm) {
    if (!searchTerm) {
        // Remove existing highlights
        row.querySelectorAll('.search-highlight').forEach(function(element) {
            element.outerHTML = element.innerHTML;
        });
        return;
    }

    const textNodes = getTextNodes(row);
    textNodes.forEach(function(node) {
        const parent = node.parentNode;
        const text = node.textContent;
        const regex = new RegExp(`(${escapeRegex(searchTerm)})`, 'gi');
        
        if (regex.test(text)) {
            const highlightedHTML = text.replace(regex, '<span class="search-highlight bg-warning">$1</span>');
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = highlightedHTML;
            
            while (tempDiv.firstChild) {
                parent.insertBefore(tempDiv.firstChild, node);
            }
            parent.removeChild(node);
        }
    });
}

// Initialize search highlighting
function initializeSearchHighlight() {
    const style = document.createElement('style');
    style.textContent = `
        .search-highlight {
            background-color: #fff3cd !important;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }
    `;
    document.head.appendChild(style);
}

// Setup table click handlers
function setupTableClickHandlers() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(function(row) {
        row.addEventListener('click', function() {
            const chartLink = row.querySelector('a[href*="game"]');
            if (chartLink) {
                // Add visual feedback
                row.style.background = '#e3f2fd';
                setTimeout(function() {
                    window.location.href = chartLink.href;
                }, 150);
            }
        });
        
        // Add hover effect
        row.style.cursor = 'pointer';
    });
}

// Setup mobile-specific handlers
function setupMobileHandlers() {
    // Touch feedback for mobile devices
    if (isMobileDevice()) {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(function(btn) {
            btn.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.95)';
            });
            
            btn.addEventListener('touchend', function() {
                this.style.transform = '';
            });
        });
    }
}

// Auto-refresh functionality
function setupAutoRefresh() {
    // Refresh every 5 minutes for live games
    if (document.querySelector('.live-game')) {
        setInterval(function() {
            if (document.visibilityState === 'visible') {
                refreshLiveGames();
            }
        }, 300000); // 5 minutes
    }
    
    // Check for updates every minute
    setInterval(function() {
        checkForUpdates();
    }, 60000);
}

// Refresh live games data
function refreshLiveGames() {
    if (navigator.onLine) {
        showLoadingIndicator();
        
        fetch('/api/games')
            .then(response => response.json())
            .then(data => {
                updateLiveGameResults(data);
                lastUpdateTime = Date.now();
                updateTimestamp();
            })
            .catch(error => {
                console.error('Error refreshing live games:', error);
                showErrorMessage('Failed to refresh live results');
            })
            .finally(() => {
                hideLoadingIndicator();
            });
    }
}

// Update live game results
function updateLiveGameResults(data) {
    data.live_games.forEach(function(game) {
        const gameRow = document.querySelector(`[data-game-id="${game.id}"]`);
        if (gameRow) {
            const todayResult = gameRow.querySelector('.today-result');
            if (todayResult && game.today_result !== '--') {
                todayResult.textContent = game.today_result;
                todayResult.className = 'badge bg-success';
                
                // Add update animation
                todayResult.style.animation = 'pulse 0.5s';
                setTimeout(() => {
                    todayResult.style.animation = '';
                }, 500);
            }
        }
    });
}

// Check for updates
function checkForUpdates() {
    const timeSinceUpdate = Date.now() - lastUpdateTime;
    if (timeSinceUpdate > 600000) { // 10 minutes
        showUpdateNotification();
    }
}

// Update timestamp display
function updateTimestamp() {
    const timestampElements = document.querySelectorAll('[data-timestamp]');
    timestampElements.forEach(function(element) {
        element.textContent = formatTimestamp(new Date());
    });
}

// Setup table enhancements
function setupTableEnhancements() {
    // Add sorting capability
    const tableHeaders = document.querySelectorAll('th[data-sortable]');
    tableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(this);
        });
    });
    
    // Add sticky headers for mobile
    if (isMobileDevice()) {
        const headers = document.querySelectorAll('thead');
        headers.forEach(function(header) {
            header.style.position = 'sticky';
            header.style.top = '0';
            header.style.zIndex = '10';
        });
    }
}

// Table sorting functionality
function sortTable(header) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(header.parentNode.children).indexOf(header);
    const isAscending = header.getAttribute('data-sort-direction') !== 'asc';
    
    rows.sort(function(a, b) {
        const aValue = a.children[columnIndex].textContent.trim();
        const bValue = b.children[columnIndex].textContent.trim();
        
        if (isNumeric(aValue) && isNumeric(bValue)) {
            return isAscending ? 
                parseInt(aValue) - parseInt(bValue) : 
                parseInt(bValue) - parseInt(aValue);
        } else {
            return isAscending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        }
    });
    
    // Update DOM
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    // Update sort direction
    header.setAttribute('data-sort-direction', isAscending ? 'asc' : 'desc');
    
    // Update visual indicators
    updateSortIndicators(header, isAscending);
}

// Update sort indicators
function updateSortIndicators(activeHeader, isAscending) {
    // Remove existing indicators
    document.querySelectorAll('.sort-indicator').forEach(function(indicator) {
        indicator.remove();
    });
    
    // Add new indicator
    const indicator = document.createElement('i');
    indicator.className = `fas fa-sort-${isAscending ? 'up' : 'down'} sort-indicator ms-1`;
    activeHeader.appendChild(indicator);
}

// Connection status check
function checkConnectionStatus() {
    window.addEventListener('online', function() {
        hideErrorMessage();
        showSuccessMessage('Connection restored');
        refreshLiveGames();
    });
    
    window.addEventListener('offline', function() {
        showErrorMessage('No internet connection. Results may be outdated.');
    });
}

// Show/hide notification functions
function showLoadingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'loading-indicator';
    indicator.className = 'position-fixed top-0 end-0 m-3 p-3 bg-primary text-white rounded';
    indicator.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating results...';
    document.body.appendChild(indicator);
}

function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function showSuccessMessage(message) {
    showToast(message, 'success');
}

function showErrorMessage(message) {
    showToast(message, 'danger');
}

function showUpdateNotification() {
    showToast('Results may be outdated. Refresh for latest updates.', 'warning');
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// Utility functions
function debounce(func, wait) {
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(searchTimeout);
            func(...args);
        };
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(later, wait);
    };
}

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

function isNumeric(str) {
    return !isNaN(str) && !isNaN(parseFloat(str));
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function getTextNodes(element) {
    const textNodes = [];
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        null,
        false
    );
    
    let node;
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    return textNodes;
}

function formatTimestamp(date) {
    return date.toLocaleString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Asia/Kolkata'
    }) + ' IST';
}

function updateSearchResultsCount(visible, total) {
    let countElement = document.getElementById('search-results-count');
    if (!countElement) {
        countElement = document.createElement('div');
        countElement.id = 'search-results-count';
        countElement.className = 'alert alert-info mt-2';
        document.querySelector('.container').insertBefore(countElement, document.querySelector('.container').firstChild);
    }
    
    if (visible < total) {
        countElement.innerHTML = `<i class="fas fa-search"></i> Showing ${visible} of ${total} games`;
        countElement.style.display = 'block';
    } else {
        countElement.style.display = 'none';
    }
}

function updateSectionVisibility() {
    const sections = document.querySelectorAll('section');
    sections.forEach(function(section) {
        const visibleRows = section.querySelectorAll('tbody tr:not([style*="display: none"])');
        const sectionCard = section.querySelector('.card');
        
        if (visibleRows.length === 0) {
            sectionCard.style.display = 'none';
        } else {
            sectionCard.style.display = 'block';
        }
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        const searchInput = document.getElementById('searchInput');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            performSearch();
        }
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(function() {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log(`Page load time: ${perfData.loadEventEnd - perfData.loadEventStart}ms`);
        }, 0);
    });
}

// Service Worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Only register if service worker file exists
        fetch('/sw.js', { method: 'HEAD' })
            .then(() => {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered: ', registration);
                    })
                    .catch(registrationError => {
                        console.log('SW registration failed: ', registrationError);
                    });
            })
            .catch(() => {
                // Service worker file doesn't exist, skip registration
            });
    });
}
