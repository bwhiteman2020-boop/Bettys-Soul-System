import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";

const PW = "test-password-1234567890";
const env = { KIE_API_KEY: "fake-key", CONNECTOR_PASSWORD: PW };
let calls;

beforeEach(() => {
  calls = [];
  globalThis.fetch = async (url, init = {}) => {
    calls.push({ url, init, body: init.body ? JSON.parse(init.body) : undefined });
    const u = String(url);
    let data;
    if (u.endsWith("/jobs/createTask")) data = { taskId: "task_123" };
    else if (u.includes("/jobs/recordInfo"))
      data = { taskId: "task_123", model: "nano-banana-pro", state: "success", resultJson: '{"resultUrls":["https://x/img.png"]}', creditsConsumed: 4 };
    else if (u.endsWith("/chat/credit")) data = 250.5;
    else if (u.endsWith("/file-url-upload")) data = { downloadUrl: "https://tempfile/ref.jpg" };
    return new Response(JSON.stringify({ code: 200, msg: "success", data }), { status: 200 });
  };
});

function rpc(body, path = `/mcp/${PW}`) {
  return worker.fetch(
    new Request(`https://w.example${path}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
    env,
  );
}
async function call(name, args) {
  const res = await rpc({ jsonrpc: "2.0", id: 1, method: "tools/call", params: { name, arguments: args } });
  const j = await res.json();
  return { raw: j.result, out: j.result.isError ? j.result.content[0].text : JSON.parse(j.result.content[0].text) };
}

test("wrong password is hidden as 404", async () => {
  const res = await rpc({ jsonrpc: "2.0", id: 1, method: "tools/list" }, "/mcp/wrong");
  assert.equal(res.status, 404);
  assert.equal(calls.length, 0);
});

test("initialize and tools/list", async () => {
  const init = await (await rpc({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18" } })).json();
  assert.equal(init.result.protocolVersion, "2025-06-18");
  const list = await (await rpc({ jsonrpc: "2.0", id: 2, method: "tools/list" })).json();
  assert.deepEqual(list.result.tools.map((t) => t.name), ["create_image", "create_video", "check_task", "upload_reference_image", "get_credits", "create_task_advanced"]);
});

test("notification gets 202", async () => {
  const res = await rpc({ jsonrpc: "2.0", method: "notifications/initialized" });
  assert.equal(res.status, 202);
});

test("create_image defaults to nano banana 2, 9:16, 1K with references and bearer key", async () => {
  const { out } = await call("create_image", { prompt: "a detective at her desk", reference_image_urls: ["https://r/1.jpg"] });
  assert.equal(out.task_id, "task_123");
  assert.equal(calls[0].init.headers.Authorization, "Bearer fake-key");
  assert.deepEqual(calls[0].body, {
    model: "nano-banana-2",
    input: { prompt: "a detective at her desk", image_input: ["https://r/1.jpg"], aspect_ratio: "9:16", resolution: "1K", output_format: "png" },
  });
});

test("create_video defaults to kling 2.1 standard, 5 seconds", async () => {
  await call("create_video", { prompt: "she looks up slowly", image_url: "https://r/frame.png" });
  assert.deepEqual(calls[0].body, {
    model: "kling/v2-1-standard",
    input: { prompt: "she looks up slowly", image_url: "https://r/frame.png", duration: "5" },
  });
});

test("create_task_advanced refuses clips over 17 seconds", async () => {
  const { raw, out } = await call("create_task_advanced", { model: "x/video", input: { prompt: "p", duration: "20" } });
  assert.equal(raw.isError, true);
  assert.match(out, /17 seconds/);
  assert.equal(calls.length, 0);
});

test("create_video kling 2.6 uses image_urls array", async () => {
  await call("create_video", { prompt: "she looks up slowly", image_url: "https://r/frame.png", model: "kling-2.6/image-to-video" });
  assert.deepEqual(calls[0].body, {
    model: "kling-2.6/image-to-video",
    input: { prompt: "she looks up slowly", image_urls: ["https://r/frame.png"], duration: "5", sound: false },
  });
});

test("create_video kling needs an image", async () => {
  const { raw } = await call("create_video", { prompt: "x" });
  assert.equal(raw.isError, true);
  assert.equal(calls.length, 0);
});

test("check_task parses result urls", async () => {
  const { out } = await call("check_task", { task_id: "task_123" });
  assert.equal(out.state, "success");
  assert.deepEqual(out.result_urls, ["https://x/img.png"]);
});

test("credits and upload", async () => {
  assert.equal((await call("get_credits", {})).out.credits_remaining, 250.5);
  assert.equal((await call("upload_reference_image", { file_url: "https://r/a.jpg" })).out.url, "https://tempfile/ref.jpg");
});

test("kie error code in a 200 body becomes a tool error with a hint", async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ code: 402, msg: "Insufficient credits" }), { status: 200 });
  const { raw, out } = await call("get_credits", {});
  assert.equal(raw.isError, true);
  assert.match(out, /Top up/);
});
