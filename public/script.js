async function loadCart() {
    const response = await fetch('/cart');
    if (!response.ok) {
        console.error("Fehler beim Laden des Warenkorbs:", response.status);
        return;
    }
    const cart = await response.json();
    const cartItemsList = document.getElementById('cart-items');
    cartItemsList.innerHTML = ''; // Leere die Liste zuerst

    if (cart.length === 0) {
        cartItemsList.innerHTML = '<li>Ihr Warenkorb ist leer.</li>';
    } else {
        cart.forEach(item => {
            const listItem = document.createElement('li');
            listItem.textContent = `Produkt ${item.productId}: ${item.quantity} `;

            const removeButton = document.createElement('button');
            removeButton.textContent = 'Entfernen';
            removeButton.addEventListener('click', () => removeFromCart(item.productId));
            // Accessibility improvements for remove button
            removeButton.setAttribute('aria-label', `Produkt ${item.productId} entfernen`);


            listItem.appendChild(removeButton);
            cartItemsList.appendChild(listItem);
        });
    }
}


function getQuantity() {
    return parseInt(document.getElementById("numberInput").value) || 1; // Standardwert 1, falls keine gültige Zahl
}


async function addToCart(productId, quantity) {
    if (quantity <=0) {
        alert("Bitte geben Sie eine gültige Menge ein."); // Hinweis bei ungültiger Menge
        return;
    }

    const response = await fetch('/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId, quantity })
    });

    if (!response.ok) {
        console.error("Fehler beim Hinzufügen zum Warenkorb:", response.status);
        // Fehlermeldung für den Benutzer anzeigen:
        let messageContainer = document.getElementById("success-message-container");
        messageContainer.textContent = "Fehler beim Hinzufügen zum Warenkorb.";
        return;
    }

    updateCartMessage("Produkt wurde erfolgreich hinzugefügt!");
    loadCart();
}


async function removeFromCart(productId) {
    const response = await fetch(`/cart/${productId}`, { method: 'DELETE' });

    if (!response.ok) {
        console.error("Fehler beim Entfernen aus dem Warenkorb:", response.status);
        return;
    }

    updateCartMessage("Produkt wurde erfolgreich entfernt!");
    loadCart();
}


function updateCartMessage(message) {
    let messageContainer = document.getElementById("success-message-container");
    messageContainer.textContent = message;

    setTimeout(() => {
        messageContainer.textContent = ""; // Meldung ausblenden
    }, 5000);
}



document.addEventListener('DOMContentLoaded', loadCart);


document.addEventListener("DOMContentLoaded", function () {
    let galleries = document.querySelectorAll(".gallery");

    galleries.forEach((gallery) => {
        let mainImage = gallery.querySelector(".main-image");
        let thumbnails = gallery.querySelectorAll(".thumbnails img");
        let images = gallery.dataset.images.split(",");
        let currentIndex = 0;
        let interval;
        let isAutoRotating = true;


        mainImage.addEventListener("click", () => {
            isAutoRotating = !isAutoRotating;
            if (isAutoRotating) {
                startAutoRotate();
            }
            else {
                clearInterval(interval);
            }
        });


        function changeImage(src) {
            mainImage.src = src;
            mainImage.alt = thumbnails[images.indexOf(src)].alt;
            currentIndex = images.indexOf(src);
        }

        function autoRotate() {
            currentIndex = (currentIndex + 1) % images.length;
            changeImage(images[currentIndex]);
        }



        thumbnails.forEach((thumb) => {
            thumb.addEventListener("click", function () {
                changeImage(this.src);
                if (isAutoRotating) resetAutoRotate();
            });


            thumb.addEventListener("keydown", function(event) {
                if (event.key === "Enter") {
                    changeImage(this.src);
                    if (isAutoRotating) resetAutoRotate();
                }
            });

        });

        function startAutoRotate() {
            if (interval) {
                clearInterval(interval);
            }
            interval = setInterval(autoRotate, 5000); // Intervall auf 5 Sekunden erhöht
        }


        function resetAutoRotate() {
            clearInterval(interval);
            startAutoRotate();
        }



        // Starte die automatische Rotation nach 5 Sekunden
        setTimeout(startAutoRotate, 5000);



    });
});