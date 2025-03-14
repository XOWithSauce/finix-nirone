/**
 * Frontend request validation
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 */

const validate_frontend_input = (req, res, next) => {
  try {
    if (
      !req.headers["content-type"] ||
      req.headers["content-type"] !== "application/json"
    ) {
      console.log('Missing content-type header "application-json" ');
      return res.status(400).json({ msg: "Invalid Content-Type header" });
    } else if (!req.query?.did || Object.keys(req.query).length !== 1) {
        console.log('Missing or unknown elements in request body.');
        return res.status(400).json({ msg: "Invalid request body" });
    } else if (!Number.isInteger(Number(req.query?.did))) {
        console.log('Request DID is not a valid integer.');
        return res.status(400).json({ msg: "Invalid request DID" });
    } else {
      // Validation passed
      next();
    }
  } catch (error) {
    console.error(error);
    return res.status(500).json({ msg: "Internal server error" });
  }
};

module.exports = { validate_frontend_input };
