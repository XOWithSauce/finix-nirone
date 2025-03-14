// device_factory.js
const Device = require('./device_config');

class DeviceFactory {
    constructor() {
        // console.log("Device Factory constructor invoked.");
    }
    async createDevice(did) {
        if (!isNaN(Number(did))) { // is number
            if (did >= 1 || did <= 10) { // did is between 1-10
                return new Device(did)
            } else { console.log("Failed to factory a device, DID out of bounds."); }
        } else { console.log("Failed to factory a device, isNan Number."); }
    }
}

module.exports = DeviceFactory;