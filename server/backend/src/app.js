const express = require('express');
const RateLimit = require('express-rate-limit');
const request_logger = require('./middlewares/request_logger');
const routes = require('./routes/v1');
const not_found = require('./middlewares/not-found');

module.exports = () => {
    const app = express();

    const limiter = RateLimit({
        windowMs: 2 * 60 * 1000, // 2min
        max: 30, // max 30
        handler: (req, res, next) => {
            //console.warn(`Rate limit exceeded for IP: ${req.ip}`);
            res.status(429).send('Too many requests, please try again later.');
        }
    });
    app.use(limiter);

    // Logging requests middleware
    app.use(request_logger);

    // GET http://localhost:3000/
    app.get('/', (req, res) => res.sendStatus(200));

    // Parsing JSON payloads
    app.use((req, res, next) => {
        // invalid json parsing
        const parse_handler = (err) => {
            if (err instanceof SyntaxError) {
                console.error("invalid json");
                res.status(400).json({ msg: "invalid json" });
            } else if (err !== undefined) {
                console.error("unknown json");
                res.sendStatus(500);
            } else {
                next();
            }
        }
        express.json()(req, res, parse_handler);
    });

    app.use("/data", routes);

    app.use(not_found);
    return app;
};