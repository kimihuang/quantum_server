/**
 * Toast — 轻量级消息提示。
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');

    const icons = { success: '✓', error: '✗', info: 'ℹ', warning: '⚠' };
    const toast = createElement('div', {
        className: `toast toast-${type}`,
        html: `<span class="toast-icon">${icons[type] || ''}</span> ${escapeHtml(message)}`,
    });

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
