/**
 * JSON Parsing middleware
 * @param {import('express').Request} req
 */
const request_logger = (req, res, next) => {
    const time_now = new Date().toISOString();
    console.log("[%s] %s - %s", time_now, req.method, req.url);
    next();
};

module.exports = request_logger;
