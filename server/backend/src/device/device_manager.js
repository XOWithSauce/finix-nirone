// device_manager.js
const DeviceFactory = require('./device_factory');

class DeviceManager {
    /** @type {Map} Mapped device instances */
    #devices;
    /** @type {DeviceFactory} Device Factory instance */
    #deviceFactory;
    constructor() {
        this.#deviceFactory = new DeviceFactory;
        this.#devices = new Map();
    }
    /**
     * Validates if the provided id is an integer.
     * @param {any} id The id to validate.
     * @returns {boolean} True if the id is an integer, false otherwise.
     */
    static isValidId(id) {
        return Number.isInteger(id) && id > 0 && id <= 10;
    }
    async createDevice(did) {
        if (!DeviceManager.isValidId(did)) {
            throw new Error("Invalid device ID. Please provide an integer.");
        }
        let id = Number(did);
        let doesDeviceExist = await this.doesExist(id)
        if (doesDeviceExist) {
            return this.#devices.get(id);
        } else {
            // console.log("Device Manager invoking a new device: ", id);
            let newDevice = await this.#deviceFactory.createDevice(id);
            this.#devices.set(id, newDevice);
            return newDevice;
        }
    }
    async doesExist(did) {
        if (!DeviceManager.isValidId(did)) {
            throw new Error("Invalid device ID. Please provide an integer.");
        }
        return this.#devices.has(did);
    }
    async getDevice(did) {
        if (!DeviceManager.isValidId(did)) {
            throw new Error("Invalid device ID. Please provide an integer.");
        }
        return this.#devices.get(did);
    }
    async getNumDevices() {
        let deviceIds = Array.from(this.#devices.keys());
        return {
          count: this.#devices.size,
          ids: deviceIds,
        };
    }
}

module.exports = DeviceManager;