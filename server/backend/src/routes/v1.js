const routes = require("express").Router();
const http = require('http');
const KeyValidator = require("../functions/key_validator");
const { validate_headers, validate_body } = require("../middlewares/req_validation");
const { validate_frontend_input } = require("../middlewares/input_validator");
const proxyConfig = require("../proxy/proxy_config");
const DeviceManager = require("../device/device_manager");

const keyValidator = new KeyValidator();
const deviceManager = new DeviceManager();
proxyConfig.getInstance();

// GET http://localhost:3000/data
routes.get("/", (req, res) => res.sendStatus(200));

// GET http://localhost:3000/data/get-by-did endpoint for Frontend client
routes.get("/get-by-did", validate_frontend_input, async (req, res) => {
  let res_msg = {};
  const default_msg = {
    "label": "0",
    "time": "0"
  };
  try {
    let did = Number(req.query?.did);
    if (did !== undefined && did !== null && !isNaN(did)) {
      if (await deviceManager.doesExist(did)) {
        let device = await deviceManager.getDevice(did);
        let instanceDid = device.getDid();
        if (instanceDid === did) {
          let msg = {
            "label": device.getPredictedLabel().toString(),
            "time": device.getLastUpdate().toString()
          };
          res_msg = msg;
        } else {
          throw new Error("Requested DID does not match any instance DID.")
        }
      } else {
        throw new Error("There are no mapped devices with requested DID.")
      }
    } else {
      res_msg = default_msg;
    }
  } catch (err) {
    console.error("Error from frontend request: ", err);
    res_msg = default_msg;
  }
  res.status(200).json({ msg: res_msg });
});

// GET http://localhost:3000/data/get-devices endpoint for Frontend client
routes.get("/get-devices", async (req, res) => {
  let res_msg = {}
  const default_msg = {
    "count": 0,
    "ids": [0],
  };
  try {
    res_msg = await deviceManager.getNumDevices();
  } catch (err) {
    console.error("Error from frontend request: ", err);
    res_msg = default_msg;
  }
  res.status(200).json({ msg: res_msg });
});

// POST http://localhost:3000/data endpoint for Embedded client
routes.post("/", validate_headers, validate_body, async (clientReq, clientRes) => {
  try {
    let did = Number(clientReq.body.id);
    if (did !== undefined && did !== null && !isNaN(did)) {
      if (await deviceManager.doesExist(did)) {
        let device = await deviceManager.getDevice(did);
        switch (clientReq.body.type) {
          case 'w':
            device.setWhiteReference(clientReq.body.data);
            clientRes.status(200).json({ msg: 'White reference updated.' });
            break;
          case 'b':
            device.setDarkReference(clientReq.body.data);
            clientRes.status(200).json({ msg: 'Dark reference updated.' });
            break;
          case 'm':
            scaled_data = device.applyScalingTo(clientReq.body.data);
            await proxyConfig.forwardToProxy(
              scaled_data,
              clientReq,
              clientRes,
              (proxyRes) => {
                device.setPredictedLabel(proxyRes);
                device.setLastUpdate(clientReq.body.time);
              }
            );
            break;
          default:
            throw new Error("Client failed to provide measure type.");
        }
      } else { // deviceManager.doesExist(did) == false
        throw new Error("Device ID does not exist in mapped devices.");
      }
    } else { // did == undefined or null or isNan
      throw new Error("Failed to parse device ID from client request.");
    }
  } catch (error) {
    console.error(error);
    clientRes.status(500).json({ msg: 'Internal Server Error' });
  }
});

// POST http://localhost:3000/data/notify endpoint for Embedded client to create the device object
routes.post("/notify", validate_headers, validate_body, async (req, res) => {
  try {
    if (keyValidator.isValidClientKey(req.headers["x-hmac-sig"], req.body.time.toString())) {
      let did = Number(req.body.id);
      if (did !== undefined && did !== null && !isNaN(did)) {
        device = await deviceManager.createDevice(did);
        if (device !== undefined && device !== null) {
          // Device object succesfully initiated and added to mapping
          res.status(200).json({ msg: 'Device succesfully initated' });
        } else {
          // Initiated device is undefined or null
          res.status(500).json({ msg: 'Internal Server Error' });
        }
      } else {
        // client request did invalid
        console.log("Provided client device id was incorrect.")
        res.status(400).json({ msg: 'Invalid device id' });
      }
    } else {
      console.log("Provided client key was incorrect.")
      res.status(400).json({ msg: 'Invalid client key' });
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({ msg: 'Internal Server Error' });
  }
});

module.exports = routes;
