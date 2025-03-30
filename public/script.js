// Accessibility Helper Functions
const a11y = {
    announceMessage: function(message) {
        let announce = document.getElementById('a11y-announce');
        if (!announce) {
            announce = document.createElement('div');
            announce.id = 'a11y-announce';
            announce.setAttribute('role', 'alert');
            announce.setAttribute('aria-live', 'polite');
            announce.className = 'sr-only';
            document.body.appendChild(announce);
        }
        announce.textContent = message;
    },

    focusableElements: 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',

    trapFocus: function(element) {
        const focusableEls = element.querySelectorAll(this.focusableElements);
        const firstFocusableEl = focusableEls[0];
        const lastFocusableEl = focusableEls[focusableEls.length - 1];

        element.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                if (e.shiftKey && document.activeElement === firstFocusableEl) {
                    e.preventDefault();
                    lastFocusableEl.focus();
                } else if (!e.shiftKey && document.activeElement === lastFocusableEl) {
                    e.preventDefault();
                    firstFocusableEl.focus();
                }
            }
        });
    }
};

// Warenkorb Funktionen
async function loadCart() {
    try {
        const response = await fetch('/cart');
        const cart = await response.json();
        const cartList = document.getElementById('cart-items');
        const emptyMessage = document.getElementById('cart-empty');
        
        if (!cart || cart.length === 0) {
            if (emptyMessage) emptyMessage.classList.remove('hidden');
            if (cartList) cartList.innerHTML = '';
            updateCartCounter(0);
            return;
        }

        if (emptyMessage) emptyMessage.classList.add('hidden');
        
        if (cartList) {
            cartList.innerHTML = cart.map(item => `
                <li class="cart-item">
                    <span class="item-name">Produkt ${item.productId}</span>
                    <span class="item-quantity">Anzahl: ${item.quantity}</span>
                    <button 
                        onclick="removeFromCart(${item.productId})"
                        class="remove-button"
                        aria-label="Entferne ${item.productId} aus dem Warenkorb">
                        Entfernen
                    </button>
                </li>
            `).join('');
            
            updateCartCounter(cart.length);
        }
    } catch (error) {
        console.error('Fehler beim Laden des Warenkorbs:', error);
        a11y.announceMessage('Fehler beim Laden des Warenkorbs. Bitte versuchen Sie es später erneut.');
    }
}

function updateCartCounter(count) {
    const cartLink = document.querySelector('.cart-link');
    if (cartLink) {
        cartLink.setAttribute('aria-label', `Zum Warenkorb, ${count} Artikel`);
    }
}

function getQuantity() {
    const input = document.getElementById("numberInput");
    if (!input) return 1;
    return Math.max(1, Math.min(100, parseInt(input.value) || 1));
}

async function addToCart(productId, quantity) {
    try {
        const response = await fetch('/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ productId, quantity })
        });

        if (!response.ok) throw new Error('Netzwerkfehler');

        showNotification('Produkt wurde erfolgreich zum Warenkorb hinzugefügt', 'success');
        a11y.announceMessage(`${quantity} Produkt(e) wurden zum Warenkorb hinzugefügt`);
        
        loadCart();

    } catch (error) {
        console.error('Fehler beim Hinzufügen zum Warenkorb:', error);
        showNotification('Fehler beim Hinzufügen zum Warenkorb', 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.setAttribute('role', 'alert');
    notification.textContent = message;
    
    const container = document.getElementById('notifications');
    if (container) {
        container.innerHTML = '';
        container.appendChild(notification);
        container.classList.add('show');
        
        setTimeout(() => {
            container.classList.remove('show');
        }, 5000);
    }
}

async function removeFromCart(productId) {
    try {
        const response = await fetch(`/cart/${productId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Netzwerkfehler');
        
        showNotification('Produkt wurde aus dem Warenkorb entfernt', 'info');
        a11y.announceMessage('Produkt wurde aus dem Warenkorb entfernt');
        
        loadCart();
    } catch (error) {
        console.error('Fehler beim Entfernen aus dem Warenkorb:', error);
        showNotification('Fehler beim Entfernen aus dem Warenkorb', 'error');
    }
}

// Galerie Funktionen
function initGallery() {
    const galleries = document.querySelectorAll('.gallery');
    
    galleries.forEach(gallery => {
        const mainImage = gallery.querySelector('.main-image');
        const thumbnails = gallery.querySelectorAll('.thumb-button');
        
        // Keyboard Navigation für Thumbnails
        thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('keydown', (e) => {
                switch(e.key) {
                    case 'ArrowLeft':
                        if (index > 0) {
                            thumbnails[index - 1].focus();
                        }
                        break;
                    case 'ArrowRight':
                        if (index < thumbnails.length - 1) {
                            thumbnails[index + 1].focus();
                        }
                        break;
                }
            });
        });

        // Touch-Support
        if ('ontouchstart' in window) {
            let touchStartX = 0;
            let touchEndX = 0;

            mainImage.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
            });

            mainImage.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            });

            function handleSwipe() {
                const swipeThreshold = 50;
                const diff = touchEndX - touchStartX;
                
                if (Math.abs(diff) > swipeThreshold) {
                    const currentIndex = Array.from(thumbnails).findIndex(
                        thumb => thumb.querySelector('img').src === mainImage.src
                    );
                    
                    if (diff > 0 && currentIndex > 0) {
                        // Swipe rechts
                        thumbnails[currentIndex - 1].click();
                    } else if (diff < 0 && currentIndex < thumbnails.length - 1) {
                        // Swipe links
                        thumbnails[currentIndex + 1].click();
                    }
                }
            }
        }
    });
}

function changeImage(src, alt) {
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = src;
        if (alt) {
            mainImage.alt = alt;
            a11y.announceMessage(`Bild gewechselt: ${alt}`);
        }
    }
}

// Formularvalidierung
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
            }
        });

        // Live-Validierung
        form.querySelectorAll('input').forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });
}

function validateField(field) {
    const errorDiv = document.getElementById(`${field.id}-error`);
    let isValid = true;
    let errorMessage = '';

    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        errorMessage = `${field.labels[0].textContent} ist erforderlich.`;
    } else if (field.pattern && !new RegExp(field.pattern).test(field.value)) {
        isValid = false;
        errorMessage = getPatternErrorMessage(field);
    }

    field.setAttribute('aria-invalid', !isValid);
    if (errorDiv) {
        errorDiv.textContent = errorMessage;
    }

    return isValid;
}

function validateForm(form) {
    let isValid = true;
    form.querySelectorAll('input').forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    return isValid;
}

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initGallery();
    initFormValidation();
    loadCart();
});