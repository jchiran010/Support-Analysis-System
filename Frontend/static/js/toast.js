document.addEventListener('DOMContentLoaded', () => {
    // Create toast container if not exists
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1090';
        document.body.appendChild(container);
    }

    window.showToast = function(message, type = 'info') {
        const bgMap = {
            'success': 'bg-success text-white',
            'danger': 'bg-danger text-white',
            'warning': 'bg-warning text-dark',
            'info': 'bg-primary text-white'
        };
        const iconMap = {
            'success': 'bi-check-circle-fill',
            'danger': 'bi-x-circle-fill',
            'warning': 'bi-exclamation-triangle-fill',
            'info': 'bi-info-circle-fill'
        };

        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center ${bgMap[type] || 'bg-dark text-white'} border-0 shadow-lg mb-2 show fade-in-up`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        toastEl.style.borderRadius = '12px';

        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2 font-weight-medium">
                    <i class="bi ${iconMap[type] || 'bi-info-circle'} fs-5"></i>
                    <span>${message}</span>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;

        container.appendChild(toastEl);
        setTimeout(() => {
            toastEl.classList.remove('show');
            setTimeout(() => toastEl.remove(), 300);
        }, 4000);
    };

    // Auto convert flash alerts to toasts
    const flashes = document.querySelectorAll('.alert-dismissible');
    flashes.forEach(el => {
        const text = el.innerText.replace(/[\n\r]/g, ' ').trim();
        let type = 'info';
        if (el.classList.contains('alert-success') || el.classList.contains('bg-success')) type = 'success';
        if (el.classList.contains('alert-danger') || el.classList.contains('bg-danger')) type = 'danger';
        if (el.classList.contains('alert-warning') || el.classList.contains('bg-warning')) type = 'warning';
        
        window.showToast(text, type);
        el.style.display = 'none';
    });
});
