const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000;

// Serve static files from current directory
app.use(express.static(__dirname));

// Serve index.html as the main page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log('');
    console.log('===========================================');
    console.log('  Resource Planning Dashboard is running!');
    console.log('===========================================');
    console.log('');
    console.log(`  Open your browser and go to:`);
    console.log(`  --> http://localhost:${PORT}`);
    console.log('');
    console.log('  Press Ctrl+C to stop the server');
    console.log('');
});
