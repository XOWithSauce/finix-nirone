const { expect } = require('chai');
const crypto = require("crypto");
const dotenv = require('dotenv');
const KeyValidator = require('../src/functions/key_validator');
const keyValidator = new KeyValidator();

describe("Auth validation tests", () => {

    it("Validates signatures correctly", () => {
        // clientSignature that would be extracted from headers
        // with headers["X-Hmac-Sig"]
        // clientMessage is the unix utc timestamp for client
        // that was used in generating the signature
        let clientMessage = '1714258662';
        // Because we compare shared key signatures we can use our key
        // to assume that it matches
        utf8Encode = new TextEncoder();
        dotenv.config();
        const shared_key = utf8Encode.encode(process.env.SHARED_KEY)
        let clientSig = crypto.createHmac('sha256', shared_key)
                                        .update(clientMessage)
                                        .digest('hex');

        // Correct HMAC validation
        const result1 = keyValidator.isValidClientKey(clientSig, clientMessage);
        expect(result1).to.be.true;

        // Client message is incorrect for signature
        clientMessage = '1714258666'
        const result2 = keyValidator.isValidClientKey(clientSig, clientMessage);
        expect(result2).to.be.false;

        // Client signature is incorrect for message
        clientMessage = '1714258662';
        clientSig = '1010205020d0283030d016070303d0301d0060cd00c01bec20e00f0a0d00a203';
        const result3 = keyValidator.isValidClientKey(clientSig, clientMessage);
        expect(result3).to.be.false;
    });
});
