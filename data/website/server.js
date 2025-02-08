// server.js - Der Node.js-Server mit Express
const express = require('express');
const app = express();
const port = 3000;

// Statische Dateien aus dem "public"-Ordner bereitstellen
app.use(express.static('public'));

app.listen(port, () => {
    console.log(`Server läuft auf http://localhost:${port}`);
});
