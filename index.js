const express = require('express');
const app = express();
const pair = require('./pair');

app.use('/', pair);

// হোস্টিং সার্ভারের পোর্ট অটোমেটিক ডিটেক্ট করবে
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`✅ Server is running on port ${PORT}`);
});
