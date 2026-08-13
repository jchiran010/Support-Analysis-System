document.addEventListener('DOMContentLoaded', () => {
    const values = document.querySelectorAll('.stat-value');
    
    values.forEach(el => {
        const target = parseInt(el.textContent.trim()) || 0;
        if (isNaN(target)) return;
        
        let start = 0;
        const duration = 1200;
        const startTime = performance.now();
        
        function update(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out quad
            const current = Math.floor(progress * (2 - progress) * target);
            el.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                el.textContent = target;
            }
        }
        
        requestAnimationFrame(update);
    });
});
