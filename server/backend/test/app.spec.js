const app = require('../src/app');
const expect = require('chai').expect;

describe("Express application", () => {
    const port = 3000;
    const host = "127.0.0.1";
    const base_url = `http://${host}:${port}/`;
    /** @type {import('http').Server || undefined} */
    let server;
    
    before((done) => server = app.listen(port, host, () => done()));

    it("responds", async () => {
        const response = await fetch(base_url);
        expect(response.status).to.equal(200);
    });
    

    after(() => {
        server.closeAllConnections();
        server.closeIdleConnections();
        server.close();
    });
});
