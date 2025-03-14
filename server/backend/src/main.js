const dotenv = require('dotenv');
const app = require('./app');
const { check_ipv4 } = require('./functions/ip_validation');
const { check_fqdn } = require('./functions/fqdn_validation');

class Main {
    /** @type {string} ip or fqdn */
    host;
    /** @type {number} integer 0-65535 */
    port;
    /** @type {import('http').Server} */
    server;
    constructor() {
        // initialize
        this.setupEnvironment();
        // operate
        this.startServer();
        // cleanup
        // this.server.close();
    }
    setupEnvironment() {
        // load config
        dotenv.config();
        try {
            const host = process.env.HOST;
            if (check_ipv4(host) || check_fqdn(host)) {
                this.host = host;
            } else {
                console.log(check_ipv4(host));
                console.log(check_fqdn(host));
                throw new Error(`Invalid hostname`);
            }
            this.port = parseInt(process.env.PORT, 10);
            if (0 > this.port >= 65536) {
                throw new Error(`Port not within valid range.`);
            }
        } catch (err) {
            console.error(err);
            throw new Error(`Failed to parse environment variables.`);
        }
    }
    startServer() {
        this.server = app.listen(this.port, this.host, () => {
            console.log(`Server listening http://${this.host}:${this.port}`);
        });
    }
}

new Main();