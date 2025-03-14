/**
 * Validate IPv4 address.
 * @param {string} ip only IPv4 works
 * @returns {boolean}
 */
const checkIPv4 = (ip) => {
    /** @type {boolean} */
    let valid = false;
    if (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip)) {  
        valid = true;
    }
    return valid;
}

// const checkIPv6...

module.exports = {
    check_ipv4: checkIPv4,
    // check_ipv6: checkIPv6
};
