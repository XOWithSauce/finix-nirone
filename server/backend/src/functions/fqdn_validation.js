/**
 * Validate FQDN.
 * @param {string} fqdn Fully Qualified Domain Name
 * @returns {boolean}
 */
const validateFQDN = (fqdn) => {
    /** @type {boolean} */
    let valid = false;
    if (/(?=^.{4,253}$)(^((?!-)[a-zA-Z0-9-]{0,62}[a-zA-Z0-9]\.)+[a-zA-Z]{2,63}$)/gm.test(fqdn)) {  
        valid = true;
    }
    return valid;
}

module.exports = {
    check_fqdn: validateFQDN
};
