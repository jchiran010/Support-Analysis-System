document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('globalSearchInput');
    const dropdown = document.getElementById('globalSearchResults');
    if (!input || !dropdown) return;

    let timeout = null;

    input.addEventListener('input', (e) => {
        clearTimeout(timeout);
        const query = e.target.value.trim();
        if (query.length < 2) {
            dropdown.classList.remove('show');
            dropdown.innerHTML = '';
            return;
        }

        timeout = setTimeout(() => {
            fetch(`/api/search?q=${encodeURIComponent(query)}`)
                .then(res => res.json())
                .then(data => {
                    dropdown.innerHTML = '';
                    if (data.length === 0) {
                        dropdown.innerHTML = `<div class="p-3 text-muted small text-center">No tickets matching "${query}"</div>`;
                    } else {
                        data.forEach(item => {
                            const a = document.createElement('a');
                            a.className = 'dropdown-item p-2 border-bottom d-flex align-items-center justify-content-between';
                            a.href = item.url;
                            a.innerHTML = `
                                <div>
                                    <div class="fw-bold text-dark font-size-sm">#TKT-${item.id}: ${item.title}</div>
                                    <small class="text-muted">${item.category}</small>
                                </div>
                                <span class="badge bg-secondary" style="font-size:0.7rem;">${item.status}</span>
                            `;
                            dropdown.appendChild(a);
                        });
                    }
                    dropdown.classList.add('show');
                })
                .catch(() => {
                    dropdown.classList.remove('show');
                });
        }, 250);
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('show');
        }
    });
});
