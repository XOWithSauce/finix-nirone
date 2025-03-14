const app = require("../src/app");
const { data_packet } = require("./helpers/helperv1")
const expect = require("chai").expect;
const request = require("supertest");
const nock = require("nock");

describe("Proxy routing", () => {
  /**
   * Proxy logic tests with nock
   */
  const port = 3000;
  const host = "127.0.0.1";
  /**
   * Define a preset package in the same format as nirso-client sends it
   */
  /** @type {import('http').Server || undefined} */
  let server;
  before((done) => (server = app.listen(port, host, () => done())));
  afterEach(() => {
    nock.cleanAll();
  });
  it("Loads the test environment", async () => {
    const proxy_port = "8001";
    const proxy_ip = "10.0.0.12";
    const proxy_href = "v1/models/resnet:predict";
    const proxy_protocol = "http";
    expect(process.env.TF_PROXY_PORT).to.equal(proxy_port);
    expect(process.env.TF_PROXY_IP).to.equal(proxy_ip);
    expect(process.env.TF_PROXY_HREF).to.equal(proxy_href);
    expect(process.env.TF_PROXY_PROTOCOl).to.equal(proxy_protocol);
  });
  it("Route handles proxy requests succesfully", async () => {
    /**
     * Predefined response of Nock server
     */
    const expectedData = [[0.0, 0.0, 0.0]];
    /**
     * Setup a Nock server that simulates a response
     * of Tensorflow Serving served model from the HTTP REST API
     */
    nock('http://10.0.0.12:8001')
      .post('/v1/models/resnet:predict')
      .times(1)
      .reply(200, {'outputs': expectedData});
    /**
     * Making the POST request to /data endpoint decrypts the data array from request body
     * and forwards the data to Tensorflow Serving HTTP REST API in a subnet (nocked)
     */
    const time_now = new Date().toISOString();
    const r1 = await request(app)
      .post("/data")
      .set("Content-Type", "application/json")
      .send({ data: data_packet, time: time_now, id: 1 })
      .expect(200);
    const parsedResponse = JSON.parse(r1.text);
    expect(parsedResponse.outputs).to.deep.equal(expectedData);
  });
  after(() => {
    server.closeAllConnections();
    server.closeIdleConnections();
    server.close();
  });
});
