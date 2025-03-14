const path = require('path');

/**
 * Not found middleware
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 */
const not_found = (req, res) => {
    if (req.get("Accept") == 'text/html') {
        res.status(404).sendFile(path.join(__dirname, '..', '..', 'public/not-found.html'));
    } else if (req.get("Accept") == 'application/json') {
        res.status(404).json({ msg: "not found" });
    } else {
        res.status(404).send('not found');
    }
};

module.exports = not_found;
