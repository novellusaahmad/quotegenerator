/**
 * Unified notification wrappers using Bootstrap toasts
 */
(function() {
    function mapType(type) {
        switch(type) {
            case 'error':
            case 'danger':
            case 'fail':
            case 'failure':
                return 'danger';
            case 'warning':
                return 'warning';
            case 'success':
                return 'success';
            default:
                return 'info';
        }
    }

    function showNotification(message, type = 'info', duration = 5000) {
        if (Novellus?.utils?.showToast) {
            Novellus.utils.showToast(message, mapType(type), { delay: duration });
        }
    }

    const notifications = {
        show: showNotification,
        success: (msg, duration) => showNotification(msg, 'success', duration),
        error: (msg, duration) => showNotification(msg, 'danger', duration),
        warning: (msg, duration) => showNotification(msg, 'warning', duration),
        info: (msg, duration) => showNotification(msg, 'info', duration)
    };

    window.notifications = notifications;
    window.showNotification = showNotification;
    window.showSuccess = notifications.success;
    window.showError = notifications.error;
    window.showWarning = notifications.warning;
    window.showInfo = notifications.info;
})();
