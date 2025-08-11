document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.chart-container').forEach(el => {
        if (!el.style.minHeight) el.style.minHeight = el.offsetHeight + 'px';
    });
});
