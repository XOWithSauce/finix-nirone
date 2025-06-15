const createApp = require('../src/app');
const expect = require("chai").expect;
const request = require("supertest");
const fs = require("fs");
const path = require("path");


describe("Routes", () => {
  const port = 3000;
  const host = "127.0.0.1";
  const base_url = `http://${host}:${port}/data`;
  /** @type {import('http').Server || undefined} */
  let server;
  let app;

  before((done) => {
    app = createApp();
    server = app.listen(port, host, () => { done(); })
  });

  it("Can get base_url", async () => {
    const response = await fetch(base_url);
    expect(response.status).to.equal(200);
  });

  it("Not found works", async () => {
    // Not found (text/plain)
    const r1 = await fetch(`${base_url}/hello`);
    expect(r1.status).to.equal(404);
    expect(await r1.text()).to.equal("not found");
    // Not found (application/json)
    const r2 = await fetch(`${base_url}/hello`, {
      headers: { Accept: "application/json" },
    });
    expect(r2.status).to.equal(404);
    expect(JSON.stringify(await r2.json())).to.equal('{"msg":"not found"}');
    // Not found (text/html)
    /** @type {RequestInit} */
    const r3 = await fetch(`${base_url}/hello`, {
      headers: { Accept: "text/html" },
    });
    expect(r3.status).to.equal(404);
    const notfound_file = fs.readFileSync(
      path.join(__dirname, "..", "public/not-found.html"),
      { encoding: "utf8", flag: "r" }
    );
    expect(await r3.text()).to.equal(notfound_file);
  });

  it("Content-Type headers validation works for POST http://localhost:3000/data endpoint", async () => {
    const r1 = await request(app)
      .post("/data")
      .set("content-type", "")
      .expect(400);
    expect(r1.body.msg).to.equal("Invalid Content-Type header");
    const r2 = await request(app)
      .post("/data")
      .set("content-type", "xml")
      .expect(400);
    expect(r2.body.msg).to.equal("Invalid Content-Type header");
  });

  it("Content-Type headers validation works for POST http://localhost:3000/data/notify endpoint", async () => {
    const r1 = await request(app)
      .post("/data/notify")
      .set("content-type", "")
      .expect(400);
    expect(r1.body.msg).to.equal("Invalid Content-Type header");
    const r2 = await request(app)
      .post("/data/notify")
      .set("content-type", "xml")
      .expect(400);
    expect(r2.body.msg).to.equal("Invalid Content-Type header");
    const r3 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .expect(400);
    expect(r3.body.msg).to.equal("Missing HMAC header");
    const r4 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .expect(400);
    expect(r4.body.msg).to.equal("Invalid X-Hmac-Sig header");
    const r5 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33y116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .expect(400);
    expect(r5.body.msg).to.equal("Invalid X-Hmac-Sig header");
  });

  it("Request body validation works for POST http://localhost:3000/data endpoint", async () => {
    const r1 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: "123.123" })
      .expect(400);
    expect(r1.body.msg).to.equal("Missing request body content");
    const r2 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: "123.123", time: "1", id: "1", type: "wrong" })
      .expect(400);
    expect(r2.body.msg).to.equal("Invalid request data content");
    const data_arr = Array(512).fill("a"); 
    const r3 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: data_arr, time: "1", id: "1", type: "wrong" })
      .expect(400);
    expect(r3.body.msg).to.equal("Invalid data elements");
    const valid_data_arr = Array(512).fill(1);
    const r4 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: valid_data_arr, time: "123", id: "1", type: "wrong" })
      .expect(400);
    expect(r4.body.msg).to.equal("Invalid timestamp");
    const r5 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: valid_data_arr, time: 1714231851231231, id: "1", type: "wrong" })
      .expect(400);
    expect(r5.body.msg).to.equal("Invalid timestamp");
    const r6 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: valid_data_arr, time: 1714212345, id: "1", type: "wrong" })
      .expect(400);
    expect(r6.body.msg).to.equal("Invalid ID type");
    const r7 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: valid_data_arr, time: 1714212345, id: 123, type: "wrong" })
      .expect(400);
    expect(r7.body.msg).to.equal("Invalid ID length");
    const r8 = await request(app)
      .post("/data")
      .set("content-type", "application/json")
      .send({ data: valid_data_arr, time: 1714212345, id: 1, type: "wrong" })
      .expect(400);
    expect(r8.body.msg).to.equal("Invalid request type field");
  });

  it("Request body validation works for POST http://localhost:3000/data/notify endpoint", async () => {
    const r1 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33d116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .send({ id: "1" })
      .expect(400);
    expect(r1.body.msg).to.equal("Missing request body content");
    const r2 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33d116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .send({ id: "1", time: "123" })
      .expect(400);
    expect(r2.body.msg).to.equal("Invalid timestamp");
    const r3 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33d116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .send({ id: "1", time: 1244324342344})
      .expect(400);
    expect(r3.body.msg).to.equal("Invalid timestamp");
    const r4 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33d116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .send({ id: "1", time: 1714212345})
      .expect(400);
    expect(r4.body.msg).to.equal("Invalid ID type");
    const r5 = await request(app)
      .post("/data/notify")
      .set("content-type", "application/json")
      .set("X-Hmac-Sig", "2919235b26d3233a33d116050303d0431d8960cd56ca1aec22e30f5a198aa2f3")
      .send({ id: 123, time: 1714212345})
      .expect(400);
    expect(r5.body.msg).to.equal("Invalid ID length");
  });

  it("Frontend input validation works for GET http://localhost:3000/data/get-by-did endpoint", async () => {
    const r1 = await request(app)
      .get("/data/get-by-did")
      .set("content-type", "")
      .expect(400);
    expect(r1.body.msg).to.equal("Invalid Content-Type header");
    const r2 = await request(app)
      .get("/data/get-by-did")
      .set("content-type", "xml")
      .expect(400);
    expect(r2.body.msg).to.equal("Invalid Content-Type header");
    const r3 = await request(app)
      .get("/data/get-by-did")
      .set("content-type", "application/json")
      .query({ did: 1, extra: "malicious" })
      .expect(400);
    expect(r3.body.msg).to.equal("Invalid request body");
    const r4 = await request(app)
      .get("/data/get-by-did")
      .set("content-type", "application/json")
      .query({ did: 1.5002 })
      .expect(400);
    expect(r4.body.msg).to.equal("Invalid request DID");
  });



  after(() => {
    server.closeAllConnections();
    server.closeIdleConnections();
    server.close();
  });
});
