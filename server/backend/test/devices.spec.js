const { expect } = require('chai');
const DeviceManager = require("../src/device/device_manager");
const Device = require("../src/device/device_config");

describe("Device Manager Tests", () => {
    let deviceManager;
    beforeEach(async () => {
        deviceManager = new DeviceManager();
    });
    afterEach(async () => {
        delete deviceManager;
    });
    it("Can create a new device", async () => {
        let newDevice = await deviceManager.createDevice(1);
        expect(newDevice).to.be.an.instanceof(Device);
        expect(newDevice.getDid()).to.equal(1);
    });
    it("Can map devices", async () => {
        await deviceManager.createDevice(1);
        await deviceManager.createDevice(3);
        await deviceManager.createDevice(7);
        let resultArr = await deviceManager.getNumDevices();
        expect(resultArr).to.have.property('count').that.is.a('number');
        expect(resultArr).to.have.property('ids').that.is.an('array');
        expect(resultArr.count).to.equal(3);
        expect(resultArr.ids).to.deep.equal([1, 3, 7]);
    });
    it("Does not create overlapping devices", async () => {
        let newDevice = await deviceManager.createDevice(1);
        let sameDevice = await deviceManager.createDevice(1);
        expect(newDevice).to.deep.eq(sameDevice);
    });
    it("Does not allow device creation with strings", async () => {
        try {
            await deviceManager.createDevice("test");
        } catch (error) {
            if (error instanceof Error) {
              expect(error.message).to.include("Invalid device ID. Please provide an integer.");
            }
        }
        try {
            await deviceManager.doesExist("test");
        } catch (error) {
            if (error instanceof Error) {
              expect(error.message).to.include("Invalid device ID. Please provide an integer.");
            }
        }
        try {
            await deviceManager.getDevice("test");
        } catch (error) {
            if (error instanceof Error) {
              expect(error.message).to.include("Invalid device ID. Please provide an integer.");
            }
        }
    });
    it("Does not allow device creation with integers below or eq to 0, or above 10", async () => {
        try {
            await deviceManager.createDevice(0);
        } catch (error) {
            if (error instanceof Error) {
              expect(error.message).to.include("Invalid device ID. Please provide an integer.");
            }
        }
        try {
            await deviceManager.createDevice(-1);
        } catch (error) {
            if (error instanceof Error) {
              expect(error.message).to.include("Invalid device ID. Please provide an integer.");
            }
        }
        try {
            await deviceManager.createDevice(11);
        } catch (error) {
            if (error instanceof Error) {
              expect(error.message).to.include("Invalid device ID. Please provide an integer.");
            }
        }
    });
});
