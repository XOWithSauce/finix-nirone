const crypto = require("crypto");
const dotenv = require('dotenv');

class KeyValidator {
    /** @type {Uint8Array} Shared key */
    #shared_key;
    /** @type {TextEncoder} UTF8 Encoder */
    #utf8Encode;
    constructor() {
        this.#shared_key;
        this.#utf8Encode = new TextEncoder();
        this.#setupEnvironment();
    }
    #setupEnvironment() {
        dotenv.config();
        try {
            this.#shared_key = this.#utf8Encode.encode(process.env.SHARED_KEY);
        } catch (error) {
            console.error("Key Validator failed to initialize environment. Client Key Failed.");
            console.log(error);
        }
    }
    #compareSig(clientSig, calculatedSig) {
        let result = false;
        try {
            if (!(clientSig instanceof Uint8Array) || !(calculatedSig instanceof Uint8Array)) {
                console.log("Client signature maybe not Uint8Array: ", clientSig.constructor.name);
                console.log("Server signature maybe not Uint8Array: ", calculatedSig.constructor.name);
                throw new Error('Parameters must be of type ArrayBufferView');
            }
            if (clientSig.byteLength !== calculatedSig.byteLength) {
                console.log("Client signature: ", clientSig.byteLength, " ", clientSig);
                console.log("Server signature: ", calculatedSig.byteLength, " " , calculatedSig);
                throw new Error('Byte lengths of parameters must be equal');
            }
            result = crypto.timingSafeEqual(clientSig, calculatedSig);
        } catch (error) {
            console.log("Error while comparing signatures: \n", error);
            result = false;
        }
        return result;
    }
    #createSignatureFrom(message) {
        const signature = crypto.createHmac('sha256', this.#shared_key)
                                .update(message)
                                .digest('hex');
        //console.log("Created signature: ", signature);
        return signature;
    }
    isValidClientKey(clientSignature, message) {
        let result = false;
        try {
            let bserverSignature = this.#utf8Encode.encode(this.#createSignatureFrom(message));
            let bclientSignature = this.#utf8Encode.encode(clientSignature);
            result = this.#compareSig(bclientSignature, bserverSignature);
            //console.log("COMPARE RESULT: ", result);
        } catch (error) {
            console.log("Error while running isValidClientKey method: \n", error);
            result = false;
        }
        return result;
    }
}

module.exports = KeyValidator;