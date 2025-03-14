const ip_validation = require('../src/functions/ip_validation');
const fqdn_validation = require('../src/functions/fqdn_validation');
const { expect } = require('chai');

describe("Validation tests", () => {
    it("validates IPv4s correctly", () => {
        const check_ipv4 = ip_validation.check_ipv4;
        // valid IPv4s
        expect(check_ipv4("127.0.0.1")).to.be.true;
        expect(check_ipv4("0.0.0.0")).to.be.true;
        expect(check_ipv4("192.168.1.1")).to.be.true;
        expect(check_ipv4("12.34.56.78")).to.be.true;
        // invalid IPv4s
        expect(check_ipv4("a.b.c.d")).to.be.false;
        expect(check_ipv4("hello")).to.be.false;
        expect(check_ipv4(undefined)).to.be.false;
        expect(check_ipv4(127001)).to.be.false;
    });
    it("validates FQDNs correctly", () => {
        const check_fqdn = fqdn_validation.check_fqdn;
        const valid_FQDNs = [
            "a.bc",
            "1.2.3.4.com",
            "xn--kxae4bafwg.xn--pxaix.gr",
            "a23456789-123456789.b23.com",
            "a23456789-a234567890.a23456789.com"
        ];
        for (const valid_FQDN of valid_FQDNs) {
            expect(check_fqdn(valid_FQDN)).to.be.true;
        }
        // invalid FQDNs
        const invalid_FQDNs = [
            "a..bc",
            "a.b",
            "ab--cd.ef--com",
            "ab.cd-.example.com",
            "-ab_cd$1%2-3.sub-.example.com",
            "ab-10-100-100-100.web-.example.com.",
            "label.name.321",
            "so-me.na-me.567",
            "a23456789-123456789-123456789-123456789-123456789-123456789-1234.b23.com",
            "a23456789-a23456789-a234567890.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.com",
            "mx.example.com.",
            "a23456789-a23456789-a234567890.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a2345678.com."
        ]
        for (const invalid_FQDN of invalid_FQDNs) {
            expect(check_fqdn(invalid_FQDN)).to.be.false;
        }
    });
});
