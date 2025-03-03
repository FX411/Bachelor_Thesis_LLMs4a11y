const express = require('express');
const app = express();
const port = 3000;

app.use(express.static('public'));
app.use(express.json());

let cart = [];

app.get('/cart', (req, res) => {
    res.json(cart);
});

app.post('/cart', (req, res) => {
    const { productId, quantity } = req.body;
    const existingItem = cart.find(item => item.productId === productId);
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({ productId, quantity });
    }
    res.json(cart);
});

app.delete('/cart/:productId', (req, res) => {
    const { productId } = req.params;
    cart = cart.filter(item => item.productId !== productId);
    res.json(cart);
});

app.post('/checkout', (req, res) => {
    res.json({ message: "Checkout erfolgreich!", cart });
    cart = [];
});

app.listen(port, () => {
    console.log(`Server läuft auf http://localhost:${port}`);
});