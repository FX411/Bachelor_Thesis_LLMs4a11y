async function loadCart() {
    const response = await fetch('/cart');
    const cart = await response.json();
    document.getElementById('cart-items').innerHTML = cart.map(item => `<li>Produkt ${item.productId}: ${item.quantity} <button onclick="removeFromCart(${item.productId})">X</button></li>`).join('');
}

function getQuantity() {
    return document.getElementById("numberInput").value;
}

async function addToCart(productId, quantity) {
    await fetch('/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId, quantity: quantity })
    });
    alert('Produkt zum Warenkorb hinzugefügt!');
}

async function removeFromCart(productId) {
    await fetch(`/cart/${productId}`, { method: 'DELETE' });
    loadCart();
}

document.addEventListener('DOMContentLoaded', loadCart);
