const { expect } = require('chai');
const KeyValidator = require('../src/functions/key_validator');
const keyValidator = new KeyValidator();

describe("Auth validation tests", () => {
    it("Validates signatures correctly", () => {
        // clientSignature that would be extracted from headers
        // with headers["X-Hmac-Sig"]
        let clientSig = '2919235b26d3233a33d116050303d0431d8960cd56ca1aec22e30f5a198aa2f3';
        // clientMessage is the unix utc timestamp for client
        // that was used in generating the signature
        let clientMessage = '1714258662';

        // Correct HMAC validation
        const result1 = keyValidator.isValidClientKey(clientSig, clientMessage);
        expect(result1).to.be.true;

        // Client message is incorrect for signature
        clientMessage = '1714258666'
        const result2 = keyValidator.isValidClientKey(clientSig, clientMessage);
        expect(result2).to.be.false;

        // Client signature is incorrect for message
        clientMessage = '1714258662';
        clientSig = '2919235b23d3233a33d116070303d0431da960cd56ca1aec22e30f5a1d8aa2f3';
        const result3 = keyValidator.isValidClientKey(clientSig, clientMessage);
        expect(result3).to.be.false;
    });
});
