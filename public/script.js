async function loadCart() {
    const response = await fetch('/cart');
    const cart = await response.json();
    document.getElementById('cart-items').innerHTML = cart.map(item =>
        `<li>Produkt ${item.productId}: ${item.quantity} 
            <button onclick="removeFromCart(${item.productId})">X</button>
        </li>`
    ).join('');
}

function getQuantity() {
    return document.getElementById("numberInput").value;
}

async function addToCart(productId, quantity) {
    await fetch('/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId, quantity })
    });

    let existingMessage = document.getElementById("success-message");
    if (existingMessage) existingMessage.remove();

    let message = document.createElement("p");
    message.innerText = "Produkt wurde erfolgreich hinzugefügt!";
    message.id = "success-message";
    document.body.appendChild(message);

    loadCart();
}

async function removeFromCart(productId) {
    await fetch(`/cart/${productId}`, { method: 'DELETE' });
    loadCart();
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

        function changeImage(src) {
            mainImage.src = src;
            currentIndex = images.indexOf(src);
        }

        function autoRotate() {
            currentIndex = (currentIndex + 1) % images.length;
            mainImage.src = images[currentIndex];
        }

        thumbnails.forEach((thumb) => {
            thumb.addEventListener("click", function () {
                changeImage(this.src);
                resetAutoRotate();
            });
        });

        function startAutoRotate() {
            interval = setInterval(autoRotate, 3000);
        }
        startAutoRotate();

        function resetAutoRotate() {
            clearInterval(interval);
            startAutoRotate();
        }
    });
});
