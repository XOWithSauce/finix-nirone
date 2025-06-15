const dotenv = require('dotenv');
const http = require('http');
const { check_ipv4 } = require('../functions/ip_validation');
const { check_fqdn } = require('../functions/fqdn_validation');
let instance;

class ProxyConfig {
    /** @type {string} ip or fqdn */
    ip;
    /** @type {number} integer 8000-8001 */
    port;
    /** @type {string} empty or base/href */
    href;
    /** @type {string} http or https */
    protocol;
    /** @type {string} fully constructed proxy url */
    url;
    constructor() {
        // Singleton pattern
        if (instance) {
            throw new Error("Multiple instances not allowed.");
        }
        instance = this;
        // initialize
        this.setupEnvironment();
        // cleanup
    }
    setupEnvironment() {
        // load config
        dotenv.config();
        try {
            const ip = process.env.TF_PROXY_IP;
            if (check_ipv4(ip) || check_fqdn(ip)) {
                this.ip = ip;
            } else {
                throw new Error(`Invalid proxy hostname`);
            }
            this.port = parseInt(process.env.PORT, 10);
            if (0 > this.port >= 65536) {
                throw new Error(`Proxy Port not within valid range.`);
            }
            const href = process.env.TF_PROXY_HREF;
            this.href = href;

            const protocol = process.env.TF_PROXY_PROTOCOL;
            this.protocol = protocol;
        } catch (error) {
            console.error(error);
            throw new Error(`Failed to parse environment variables.`);
        }
    }
    getInstance() {
        return this
    }
    /**
     * Performs a POST request to the configured proxy server and updates device data
     * @param {number[]} decrypted data to send to the proxy server
     * @param {http.IncomingMessage} clientReq The incoming client request
     * @param {http.ServerResponse} clientRes The outgoing client response
     * @param {function(string)} onProxyResponse Callback function to update predictedLabel of deviceConfig
     */
    async forwardToProxy(postData, clientReq, clientRes, onProxyResponse) {
        try {
            const options = {
                hostname: this.ip,
                port: this.port,
                path: `/${this.href}`,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Forwarded-For': clientReq.ip
                }
            };

            const proxyReq = http.request(options, (proxyRes) => {
                console.log(`Status: ${proxyRes.statusCode}`);
                console.log(`Headers: ${JSON.stringify(proxyRes.headers)}`);

                proxyRes.on('data', (chunk) => {
                    onProxyResponse(chunk.toString());
                    clientRes.write(chunk);
                    console.log(`Body: ${chunk.toString()}`);
                });

                proxyRes.on('end', () => {
                    clientRes.end();
                });
            });

            proxyReq.on('error', (error) => {
                console.error('Error on proxy server: ', error);
                clientRes.status(500).json({ msg: 'Internal Server Error' });
                proxyReq.destroy();
            });

            const timeout = setTimeout(() => {
                console.warn("Client response timed out, closing stream.");
                clientRes.end();
            }, 5000);

            clientRes.on('finish', () => {
                clearTimeout(timeout);
            });

            // FORMAT PACKET FOR TFS
            var requestData = {
                "inputs": [postData, ]
            }
            proxyReq.write(JSON.stringify(requestData));
            
            proxyReq.end();
        } catch (error) {
            console.error("Failed to handle proxy request on /data POST route.");
            clientRes.status(500).json({ msg: 'Internal Server Error' });
        }
    }
}

module.exports = Object.freeze(new ProxyConfig())
