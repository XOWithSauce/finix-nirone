/**
 * Request headers validation
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 */
const validate_headers = (req, res, next) => {
  let route = req.url;
  if (route === "/") { 
    try {
      if (
        !req.headers["content-type"] ||
        req.headers["content-type"] !== "application/json"
      ) {
        // Checks that headers contain content-type: application-json
        console.log('Missing content-type header "application-json" ');
        return res.status(400).json({ msg: "Invalid Content-Type header" });
      } else {
        // Validation passed
        next();
      }
    } catch (error) {
      console.log("Headers validation failed with: ", error);
      return res.status(500).json({ msg: "Internal server error" });
    }
  } else if (route === "/notify") {
    let hexRegExp = /^[0-9a-f]{64}$/
    try {
      if (
        !req.headers["content-type"] ||
        req.headers["content-type"] !== "application/json"
      ) {
        // Checks that headers contain content-type: application-json
        console.log('Missing content-type header "application-json" ');
        return res.status(400).json({ msg: "Invalid Content-Type header" });
      } else if ( !req.headers["x-hmac-sig"] ) {
        // Checks that headers contain X-Hmac-Sig field
        console.log('Missing Hmac signature header field');
        return res.status(400).json({ msg: "Missing HMAC header" });
      } else if ( req.headers["x-hmac-sig"].length !== 64 ) {
        // Checks that X-Hmac-Sig value has a value length of 64
        console.log('Invalid X-Hmac-Sig format (length mismatch)');
        return res.status(400).json({ msg: "Invalid X-Hmac-Sig header" });
      } else if (!req.headers["x-hmac-sig"].match(hexRegExp)) {
        // Checks that X-Hmac-Sig has a value that matches hexadecimal RegExp
        console.log('Invalid X-Hmac-Sig format (No RegExp match)');
        return res.status(400).json({ msg: "Invalid X-Hmac-Sig header" });
      } else {
        // Validation passed
        next();
      }


    } catch (error) {
      console.log("Headers validation failed with: ", error);
      return res.status(500).json({ msg: "Internal server error" });
    }
  }
};


/**
 * Request body validation
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 */
const validate_body = (req, res, next) => {
  let route = req.url;
  if (route === "/") { 
    try {
      if (!("data" in req.body) || !("time" in req.body) || !("id" in req.body) || !("type" in req.body)) {
        // Validate request body content to include data, time and id
        console.log("Missing data, time, id, or type in request body.");
        return res.status(400).json({ msg: "Missing request body content" });
      } else if (!Array.isArray(req.body.data) || req.body.data.length !== 512) {
        // Validate request body data to be an array with 512 elements
        console.log("Request data field is not an array or missing elements.");
        return res.status(400).json({ msg: "Invalid request data content" });
      } else if (req.body.data.every(element => typeof element !== 'number')) {
        // Validate each element in data array to be a number and not an NaN number.
        console.log("Invalid data elements. Not all elements are numbers.");
        return res.status(400).json({ msg: "Invalid data elements" });
      } else if (typeof req.body.time !== "number" || req.body.time.toString().length != 10) {
        // Validate timestamp to be a number (UNIX)
        console.log("Invalid timestamp, not a number or not valid UNIX.");
        return res.status(400).json({ msg: "Invalid timestamp" });
      } else if (typeof req.body.id !== "number") {
        // Validate Device ID to be a number and length of 1 (MORE THAN 9 DEVICES NOT SUPPORTED)
        console.log("Device ID type not a number.");
        return res.status(400).json({ msg: "Invalid ID type" });
      } else if (req.body.id.toString().length !== 1) {
        // Validate Device ID to be a number and length of 1 (MORE THAN 9 DEVICES NOT SUPPORTED)
        console.log("Device ID not within valid range.");
        return res.status(400).json({ msg: "Invalid ID length" });
      } else if (typeof req.body.type !== "string" || req.body.type.length !== 1) {
        // Validate request body type to be a single character
        console.log("Request body.type is incorrectly formatted, not string or too long.");
        return res.status(400).json({ msg: "Invalid request type field" });
      } else {
        // Validation passed
        next();
      }
    } catch (error) {
      console.log("Request body validation failed with error: ", error);
      // Handle unexpected errors
      return res.status(500).json({ msg: "Internal server error" });
    }
  } else if (route === "/notify") {
    try {
      if (!("time" in req.body) || !("id" in req.body)) {
        // Validate request body content to include time and id
        console.log("Missing time or id in request body.");
        return res.status(400).json({ msg: "Missing request body content" });
      } else if (typeof req.body.time !== "number" || req.body.time.toString().length != 10) {
        // Validate timestamp to be a number (UNIX)
        console.log("Invalid timestamp, not a number or not valid UNIX.");
        return res.status(400).json({ msg: "Invalid timestamp" });
      } else if (typeof req.body.id !== "number") {
        // Validate Device ID to be a number and length of 1 (MORE THAN 9 DEVICES NOT SUPPORTED)
        console.log("Device ID type not a number.");
        return res.status(400).json({ msg: "Invalid ID type" });
      } else if (req.body.id.toString().length !== 1) {
        // Validate Device ID to be a number and length of 1 (MORE THAN 9 DEVICES NOT SUPPORTED)
        console.log("Device ID not within valid range.");
        return res.status(400).json({ msg: "Invalid ID length" });
      } else {
        // Validation passed
        next();
      }
    } catch (error) {
      console.log("Request body validation failed with error: ", error);
      // Handle unexpected errors
      return res.status(500).json({ msg: "Internal server error" });
    }
  } else { // No route specified within req.url param
    console.error("No route specified for body validation");
    return res.status(500).json({ msg: "Internal server error" });
  }

};

module.exports = { validate_headers, validate_body };
