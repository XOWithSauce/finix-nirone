// device_config.js

class Device {
    /** @type {number} Unique device id integer */
    #did;
    /** @type {string} UNIX UTC Timestamp */
    #lastUpdate;
    /** @type {string} string */
    #predictedLabel;
    /** @type {number[]} list of floats (512) */
    #whiteReference;
    /** @type {number[]} list of floats (512) */
    #darkReference;

    constructor(did) {
        // console.log("Constructing a device with ID: ", did);
        this.#did = did; // Unique device identifier
        this.#lastUpdate = "";
        this.#predictedLabel = "";
        this.#whiteReference = Array(512).fill(0);
        this.#darkReference = Array(512).fill(0);
    }
    // Set
    setLastUpdate(timestamp) {
        this.#lastUpdate = timestamp;
    }
    setPredictedLabel(proxyRes) {
        try {
            let decodedLabel = "";
            decodedLabel = this.__labelDecoder(proxyRes);
            // Update predicted label
            this.#predictedLabel = decodedLabel;
        } catch(err) {
            this.#predictedLabel = "";
        }
    }
    __labelDecoder(proxyRes) {
        let decodedLabels = [];
        try {
          const parsedData = JSON.parse(proxyRes);
          if (parsedData.outputs) {
            const probabilities = parsedData.outputs[0];
            for (let i = 0; i < probabilities.length; i++) {
              const material = this.getMaterialName(i);
              decodedLabels.push({ material, probability: probabilities[i] });
            }
            decodedLabels.sort((a, b) => b.probability - a.probability);
            const formattedString = decodedLabels.map(label => `${label.material}: ${label.probability.toFixed(2)}`).join('\n');
            return formattedString;
          }
        } catch (err) {
          console.error("Failed to decode label:", err);
        }
        return "Unknown";
    }
    setWhiteReference(measurement) {
        this.#whiteReference = measurement;
    }
    setDarkReference(measurement) {
        this.#darkReference = measurement;
    }
    applyScalingTo(meas) {
        let white = this.#whiteReference;
        let dark = this.#darkReference;
        meas.forEach(float => {console.log(float)});
        let result = [];
        for (let i = 0; i < meas.length; i++) {
            result.push( (meas[i] - dark[i]) / (white[i] - dark[i]) );
        }
        let minReflectance = Math.min(...result);
        let maxReflectance = Math.max(...result);
        let scaledReflectance = result.map(value => (value - minReflectance) / (maxReflectance - minReflectance));
        // TODO: Apply savgol filter after reflectance (translate to js and simplify based on https://github.com/scipy/scipy/blob/v1.15.3/scipy/signal/_savitzky_golay.py)
        // Use params from Model / ThesisBase
        return scaledReflectance;
    }


    // Get
    getDid() {
        return this.#did;
    }
    getLastUpdate() {
        let lastUpdateTime = "0";
        try {
            let timestamp = this.#lastUpdate;
            if (timestamp !== "") {
                let unixTimestampMs = timestamp * 1000;
                let dateObj = new Date(unixTimestampMs);
                let options = { timeZone: 'Europe/Helsinki', timeZoneName: 'short' };
                let date = dateObj.toLocaleDateString('fi-FI', options);
                let time = dateObj.toLocaleTimeString('fi-FI', options);
                lastUpdateTime = `${date} | ${time}`;
            }
        } catch(err) {
            console.log("Device class failed to return lastUpdateTime: ", err);
        }
        return lastUpdateTime;
    }
    getPredictedLabel() {
        let predictedLabel = "0";
        try {
            let label = this.#predictedLabel;
            if (label !== "") {
                predictedLabel = `${label}`;
            }
        } catch(err) {
            console.log("Device class failed to return predictedLabel: ", err);
        }
        return predictedLabel;
    }
    getWhiteReference() {
        return this.#whiteReference;
    }
    getDarkReference() {
        return this.#darkReference;
    }
    getMaterialName(index) {
        const materialNames = ["Polyester", "Cotton", "Wool"];
        if (index >= 0 && index < materialNames.length) {
          return materialNames[index];
        } else {
          console.warn("Invalid index for material name:", index);
          return "Unknown";
        }
    }
}

module.exports = Device;