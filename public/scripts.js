// Hilfsfunktionen für Accessibility
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
    }
};

// Warenkorb-Funktionen
async function loadCart() {
    try {
        const response = await fetch('/cart');
        const cart = await response.json();
        const cartList = document.getElementById('cart-items');
        const emptyMessage = document.getElementById('cart-empty');
        
        if (!cart || cart.length === 0) {
            if (emptyMessage) emptyMessage.classList.remove('hidden');
            if (cartList) cartList.innerHTML = '';
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
        }
    } catch (error) {
        console.error('Fehler beim Laden des Warenkorbs:', error);
        a11y.announceMessage('Fehler beim Laden des Warenkorbs');
    }
}

function getQuantity() {
    const input = document.getElementById("numberInput");
    if (!input) return 1;
    return parseInt(input.value) || 1;
}

async function addToCart(productId, quantity) {
    try {
        const response = await fetch('/cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ productId, quantity })
        });

        if (!response.ok) throw new Error('Netzwerkfehler');

        let existingMessage = document.getElementById("success-message");
        if (existingMessage) existingMessage.remove();

        let message = document.createElement("p");
        message.innerText = "Produkt wurde erfolgreich zum Warenkorb hinzugefügt!";
        message.id = "success-message";
        message.setAttribute('role', 'alert');
        document.body.appendChild(message);

        a11y.announceMessage("Produkt wurde zum Warenkorb hinzugefügt");
        loadCart();

    } catch (error) {
        console.error('Fehler beim Hinzufügen zum Warenkorb:', error);
        a11y.announceMessage('Fehler beim Hinzufügen zum Warenkorb');
    }
}

async function removeFromCart(productId) {
    try {
        const response = await fetch(`/cart/${productId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Netzwerkfehler');
        
        a11y.announceMessage("Produkt wurde aus dem Warenkorb entfernt");
        loadCart();
    } catch (error) {
        console.error('Fehler beim Entfernen aus dem Warenkorb:', error);
        a11y.announceMessage('Fehler beim Entfernen aus dem Warenkorb');
    }
}

// Formularvalidierung
function initFormValidation() {
    const form = document.getElementById('checkout-form');
    if (!form) return;

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let isValid = validateForm(this);
        
        if (isValid) {
            submitForm(this);
        }
    });

    // Live-Validierung für einzelne Felder
    form.querySelectorAll('input').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

function validateField(field) {
    const errorDiv = document.getElementById(`${field.id}-error`);
    let isValid = true;
    let errorMessage = '';

    // Pflichtfeld-Validierung
    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        errorMessage = 'Dieses Feld ist erforderlich.';
    }

    // Pattern-Validierung
    if (field.pattern && field.value) {
        const regex = new RegExp(field.pattern);
        if (!regex.test(field.value)) {
            isValid = false;
            errorMessage = getPatternErrorMessage(field);
        }
    }

    // Visuelles Feedback
    field.setAttribute('aria-invalid', !isValid);
    if (errorDiv) {
        errorDiv.textContent = errorMessage;
    }

    return isValid;
}

function getPatternErrorMessage(field) {
    switch(field.id) {
        case 'zip':
            return 'Bitte geben Sie eine gültige 5-stellige PLZ ein.';
        case 'card-number':
            return 'Bitte geben Sie eine gültige 16-stellige Kartennummer ein.';
        case 'expiry':
            return 'Bitte geben Sie ein gültiges Ablaufdatum im Format MM/YY ein.';
        case 'cvv':
            return 'Bitte geben Sie einen gültigen CVV-Code ein (3-4 Ziffern).';
        default:
            return 'Bitte überprüfen Sie Ihre Eingabe.';
    }
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

async function submitForm(form) {
    const formData = new FormData(form);
    try {
        // Hier würde normalerweise der API-Call erfolgen
        
        const feedback = document.getElementById('form-feedback');
        feedback.innerHTML = `
            <div class="success-message" role="alert">
                <h2>Bestellung erfolgreich!</h2>
                <p>Ihre Bestellung wurde erfolgreich aufgegeben.</p>
            </div>
        `;
        
        // Fokus auf die Erfolgsmeldung setzen
        feedback.focus();
        
    } catch (error) {
        console.error('Fehler beim Absenden des Formulars:', error);
        const feedback = document.getElementById('form-feedback');
        feedback.innerHTML = `
            <div class="error-message" role="alert">
                <h2>Fehler</h2>
                <p>Bei der Verarbeitung Ihrer Bestellung ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.</p>
            </div>
        `;
    }
}

// Galerie-Funktionen
function initGallery() {
    const galleries = document.querySelectorAll('.gallery');
    
    galleries.forEach(gallery => {
        const mainImage = gallery.querySelector('.main-image');
        const thumbnails = gallery.querySelectorAll('.thumb-button');
        
        // Keyboard-Navigation für Thumbnails
        thumbnails.forEach((thumb, index) => {
            thumb.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowLeft' && index > 0) {
                    thumbnails[index - 1].focus();
                }
                if (e.key === 'ArrowRight' && index < thumbnails.length - 1) {
                    thumbnails[index + 1].focus();
                }
            });
        });
    });
}

function changeImage(src, alt) {
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = src;
        if (alt) mainImage.alt = alt;
        a11y.announceMessage('Bild wurde gewechselt');
    }
}

// Initialisierung
document.addEventListener('DOMContentLoaded', () => {
    loadCart();
    initFormValidation();
    initGallery();
});
