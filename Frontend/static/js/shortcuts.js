document.addEventListener('keydown', (e) => {
    // Ctrl + K -> Focus Search
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const search = document.getElementById('globalSearchInput');
        if (search) search.focus();
    }

    // Toggle Theme with key 'T' when not typing in input
    if (e.key.toLowerCase() === 't' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) {
        const toggleBtn = document.getElementById('darkModeToggle');
        if (toggleBtn) toggleBtn.click();
    }
});
