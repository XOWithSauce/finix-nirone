const express = require('express');
const app = express();
const request_logger = require('./middlewares/request_logger');
const routes = require('./routes/v1');
const not_found = require('./middlewares/not-found');

// Logging requests middleware
app.use(request_logger);

// GET http://localhost:3000/
app.get('/', (req, res) => res.sendStatus(200));

// Parsing JSON payloads
//app.use(express.json());

app.use((req, res, next) => {
    // invalid json parsing
    const parse_handler = (err) => {
        if (err instanceof SyntaxError) {
            console.error("invalid json");
            res.status(400).json({msg: "invalid json"});
        } else if (err !== undefined) {
            console.error("unknown json");
            res.sendStatus(500);
        } else {
            next();
        }
    }
    express.json()(req, res, parse_handler);
});

// Routes
app.use("/data", routes);

// not found responses
app.use(not_found);

module.exports = app;
