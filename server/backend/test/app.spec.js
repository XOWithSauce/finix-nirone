const expect = require('chai').expect;
const createApp = require('../src/app');
const request = require('supertest');

describe("Express application", () => {
    const port = 3000;
    const host = "127.0.0.1";
    const base_url = `http://${host}:${port}/`;
    let server;
    let app;

    beforeEach((done) => {
        app = createApp();
        server = app.listen(port, host, () => { done(); });
    });

    afterEach((done) => {
        server.closeAllConnections();
        server.closeIdleConnections();
        server.close();
        done();
    });

    it("responds", async () => {
        const response = await fetch(base_url);
        expect(response.status).to.equal(200);
    });
    
    it("rate limits", async () => {
        const limit = 30;
        for (let i = 1; i <= limit; i++) {
            const response = await fetch(base_url);
            expect(response.status).to.equal(200);
        }

        const requestsAfterLimit = 1;
        for (let i = 1; i <= requestsAfterLimit; i++) {
            const response = await fetch(base_url);
            expect(response.status).to.equal(429);
        }
    });
});
