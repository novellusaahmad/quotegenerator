/**
 * Novellus Notification System - Golden Theme
 * Creates beautiful golden notifications with white text throughout the application
 */
class NotificationSystem {
    constructor() {
        this.createNotificationContainer();
    }

    createNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10001;
                max-width: 450px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        this.container = container;
    }

    show(message, type = 'info', duration = 8000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        // Golden theme styling
        notification.style.cssText = `
            background: linear-gradient(135deg, #B8860B 0%, #DAA520 100%);
            border: 2px solid #FFD700;
            border-left: 6px solid #FFF;
            color: #FFFFFF;
            font-weight: 500;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
            box-shadow: 0 6px 20px rgba(184, 134, 11, 0.4);
            border-radius: 8px;
            margin-bottom: 12px;
            pointer-events: all;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease-in-out;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            position: relative;
        `;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle', 
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        notification.innerHTML = `
            <div style="display: flex; align-items: center; padding: 16px 20px;">
                <i class="${icons[type] || icons.info}" style="
                    color: #FFF;
                    font-size: 18px;
                    margin-right: 12px;
                    flex-shrink: 0;
                "></i>
                <div style="
                    flex-grow: 1;
                    color: #FFF;
                    font-weight: 500;
                    line-height: 1.4;
                ">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: #FFF;
                    font-size: 16px;
                    cursor: pointer;
                    margin-left: 12px;
                    padding: 4px;
                    border-radius: 50%;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background-color 0.2s;
                " onmouseover="this.style.backgroundColor='rgba(255,255,255,0.2)'" 
                   onmouseout="this.style.backgroundColor='transparent'">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        this.container.appendChild(notification);

        // Show with animation
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 100);

        // Auto-remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.style.transform = 'translateX(100%)';
                    notification.style.opacity = '0';
                    setTimeout(() => {
                        if (notification.parentElement) {
                            notification.remove();
                        }
                    }, 300);
                }
            }, duration);
        }

        return notification;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Global notification instance
const notifications = new NotificationSystem();
window.notifications = notifications;

// Global functions for easy access
function showNotification(message, type = 'info', duration = 8000) {
    return notifications.show(message, type, duration);
}

function showSuccess(message, duration) {
    return notifications.success(message, duration);
}

function showError(message, duration) {
    return notifications.error(message, duration);
}

function showWarning(message, duration) {
    return notifications.warning(message, duration);
}

function showInfo(message, duration) {
    return notifications.info(message, duration);
}

// Test notification function
function testNotification() {
    showSuccess('Golden notification system is working!', 5000);
}