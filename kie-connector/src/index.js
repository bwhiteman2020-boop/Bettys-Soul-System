// Betty's private Kie.ai connector for Claude.
// A tiny MCP server (Streamable HTTP, stateless JSON responses) that runs on
// Cloudflare Workers. It never stores anything. The Kie.ai key lives only in
// the Cloudflare secret KIE_API_KEY, and the connector only answers at
// /mcp/<CONNECTOR_PASSWORD>, so nobody else can spend Betty's credits.

const KIE_API = "https://api.kie.ai/api/v1";
const KIE_UPLOAD = "https://kieai.redpandaai.co/api";
const SUPPORTED_PROTOCOLS = ["2025-06-18", "2025-03-26", "2024-11-05"];
const SERVER_INFO = { name: "betty-kie-ai", version: "1.0.0" };

const IMAGE_MODELS = ["nano-banana-pro", "nano-banana-2", "bytedance/seedream-v4-edit"];
const MAX_CLIP_SECONDS = 17;
const VIDEO_MODELS = ["kling-2.6/image-to-video", "kling/v2-1-standard", "veo-3-1"];

const TOOLS = [
  {
    name: "create_image",
    description:
      "Start a Kie.ai image generation. Pass reference_image_urls (public links, e.g. from upload_reference_image) to keep a person's face, clothing or a place consistent across shots. Returns a task_id; call check_task until it finishes. Uses Kie.ai credits.",
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "What the image should show: subject, setting, lighting, camera framing, mood." },
        model: {
          type: "string",
          enum: IMAGE_MODELS,
          default: "nano-banana-2",
          description: "nano-banana-2: the default, good character consistency for fewer credits. nano-banana-pro: higher quality but costs more; use only if Betty asks. bytedance/seedream-v4-edit: edits that need reference images.",
        },
        reference_image_urls: { type: "array", items: { type: "string" }, description: "Optional public image links to use as references." },
        aspect_ratio: { type: "string", description: "Default 9:16 (Betty's micro drama standard). Only change if Betty asks." },
        resolution: { type: "string", description: "Nano Banana only: 1K, 2K or 4K. Default 1K, the cheapest, which covers a 720p vertical frame." },
      },
      required: ["prompt"],
    },
  },
  {
    name: "create_video",
    description:
      "Start a Kie.ai video generation, usually by animating a still image (image to video). Returns a task_id; call check_task until it finishes (videos often take 1 to 5 minutes). Uses Kie.ai credits, more than images.",
    inputSchema: {
      type: "object",
      properties: {
        prompt: { type: "string", description: "The motion and action: what moves, how the camera moves, the emotion." },
        image_url: { type: "string", description: "Public link to the starting frame. Required for Kling models." },
        model: {
          type: "string",
          enum: VIDEO_MODELS,
          default: "kling/v2-1-standard",
          description: "kling/v2-1-standard: the default, 720p, the fewest credits for a good result. kling-2.6/image-to-video: stronger motion, costs more; use only if Betty asks. veo-3-1: Google Veo, can work from text alone, costs the most.",
        },
        duration: { type: "string", enum: ["5", "10"], description: "Seconds, Kling only. Default 5. Clips are never longer than 17 seconds." },
        aspect_ratio: { type: "string", description: "Veo only. Default 9:16 (Betty's micro drama standard)." },
        sound: { type: "boolean", description: "Kling 2.6 only: generate audio. Doubles the price. Default false." },
      },
      required: ["prompt"],
    },
  },
  {
    name: "check_task",
    description: "Check a Kie.ai task. Returns its state (waiting, queuing, generating, success, fail) and, once finished, the result links. Kie.ai deletes results after 14 days, so save them somewhere permanent.",
    inputSchema: {
      type: "object",
      properties: { task_id: { type: "string" } },
      required: ["task_id"],
    },
  },
  {
    name: "upload_reference_image",
    description: "Put a reference photo on Kie.ai's temporary storage so models can use it. Give either a public file link (file_url) or base64 data (base64_data, under 10 MB). Returns a link that works for 24 hours. Free.",
    inputSchema: {
      type: "object",
      properties: {
        file_url: { type: "string", description: "A public link to the image." },
        base64_data: { type: "string", description: "Base64 image data, or a data: URL." },
        file_name: { type: "string", description: "Optional name, e.g. betty-1986.jpg" },
      },
    },
  },
  {
    name: "get_credits",
    description: "Show how many Kie.ai credits are left on the account.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "create_task_advanced",
    description:
      "For any other Kie.ai Market model not covered above: send the exact model name and input fields from the Kie.ai docs (docs.kie.ai). Follow Betty's rule: 9:16, 720p (or the lowest resolution at or above 720p), duration 17 seconds or less, cheapest mode and no audio unless asked. Returns a task_id for check_task. Uses Kie.ai credits.",
    inputSchema: {
      type: "object",
      properties: {
        model: { type: "string", description: "Exact model string from docs.kie.ai, e.g. bytedance/seedance-v1-pro-image-to-video" },
        input: { type: "object", description: "The model's input object exactly as the docs show it." },
      },
      required: ["model", "input"],
    },
  },
];

// ---------- Kie.ai calls ----------

async function kie(env, url, init = {}) {
  const res = await fetch(url, {
    ...init,
    headers: {
      Authorization: `Bearer ${env.KIE_API_KEY}`,
      "Content-Type": "application/json",
      ...(init.headers || {}),
    },
  });
  let body;
  try {
    body = await res.json();
  } catch {
    throw new Error(`Kie.ai answered with HTTP ${res.status} and no readable data.`);
  }
  // Kie.ai reports errors as HTTP 200 with an error code in the body.
  if (!res.ok || body.code !== 200) {
    const hint = {
      401: "The Kie.ai key was refused. Check the KIE_API_KEY secret in Cloudflare.",
      402: "Not enough Kie.ai credits. Top up at kie.ai.",
      429: "Too many requests at once. Wait a few seconds and try again.",
      455: "Kie.ai is under maintenance. Try again later.",
    }[body.code];
    throw new Error(`Kie.ai error ${body.code ?? res.status}: ${body.msg || "unknown"}${hint ? ` (${hint})` : ""}`);
  }
  return body.data;
}

function createTask(env, model, input) {
  return kie(env, `${KIE_API}/jobs/createTask`, {
    method: "POST",
    body: JSON.stringify({ model, input }),
  });
}

function startedMessage(data, model) {
  return {
    task_id: data.taskId,
    model,
    next_step: "Call check_task with this task_id in about 20 seconds (images) or 1 to 2 minutes (videos).",
  };
}

const handlers = {
  async create_image(env, a) {
    const model = a.model || "nano-banana-2";
    if (!IMAGE_MODELS.includes(model)) throw new Error(`model must be one of: ${IMAGE_MODELS.join(", ")}`);
    const refs = a.reference_image_urls || [];
    let input;
    if (model === "bytedance/seedream-v4-edit") {
      if (!refs.length) throw new Error("seedream-v4-edit needs at least one reference_image_urls entry.");
      input = { prompt: a.prompt, image_urls: refs, max_images: 1 };
    } else {
      input = {
        prompt: a.prompt,
        image_input: refs,
        aspect_ratio: a.aspect_ratio || "9:16",
        resolution: a.resolution || "1K",
        output_format: "png",
      };
    }
    return startedMessage(await createTask(env, model, input), model);
  },

  async create_video(env, a) {
    const model = a.model || "kling/v2-1-standard";
    if (!VIDEO_MODELS.includes(model)) throw new Error(`model must be one of: ${VIDEO_MODELS.join(", ")}`);
    let input;
    if (model === "veo-3-1") {
      input = {
        prompt: a.prompt,
        aspect_ratio: a.aspect_ratio || "9:16",
        generation_type: a.image_url ? "FIRST_AND_LAST_FRAMES_2_VIDEO" : "TEXT_2_VIDEO",
        ...(a.image_url ? { image_urls: [a.image_url] } : {}),
      };
    } else {
      if (!a.image_url) throw new Error("Kling models need image_url (the starting frame).");
      const duration = a.duration || "5";
      input =
        model === "kling-2.6/image-to-video"
          ? { prompt: a.prompt, image_urls: [a.image_url], duration, sound: !!a.sound }
          : { prompt: a.prompt, image_url: a.image_url, duration };
    }
    return startedMessage(await createTask(env, model, input), model);
  },

  async check_task(env, a) {
    if (!a.task_id) throw new Error("task_id is required.");
    const d = await kie(env, `${KIE_API}/jobs/recordInfo?taskId=${encodeURIComponent(a.task_id)}`);
    let resultUrls = [];
    if (d.resultJson) {
      try {
        resultUrls = JSON.parse(d.resultJson).resultUrls || [];
      } catch {
        /* leave empty */
      }
    }
    const out = { task_id: d.taskId, model: d.model, state: d.state };
    if (d.progress != null) out.progress = d.progress;
    if (d.creditsConsumed != null) out.credits_used = d.creditsConsumed;
    if (d.state === "success") {
      out.result_urls = resultUrls;
      out.note = "Kie.ai deletes these files after 14 days. Save them to Drive.";
    } else if (d.state === "fail") {
      out.error = d.failMsg || d.failCode || "Generation failed.";
    } else {
      out.next_step = "Still working. Check again in 20 to 60 seconds.";
    }
    return out;
  },

  async upload_reference_image(env, a) {
    const uploadPath = "betty-references";
    let data;
    if (a.file_url) {
      data = await kie(env, `${KIE_UPLOAD}/file-url-upload`, {
        method: "POST",
        body: JSON.stringify({ fileUrl: a.file_url, uploadPath, ...(a.file_name ? { fileName: a.file_name } : {}) }),
      });
    } else if (a.base64_data) {
      data = await kie(env, `${KIE_UPLOAD}/file-base64-upload`, {
        method: "POST",
        body: JSON.stringify({ base64Data: a.base64_data, uploadPath, ...(a.file_name ? { fileName: a.file_name } : {}) }),
      });
    } else {
      throw new Error("Give either file_url or base64_data.");
    }
    return { url: data.downloadUrl, expires: "24 hours after upload" };
  },

  async get_credits(env) {
    return { credits_remaining: await kie(env, `${KIE_API}/chat/credit`) };
  },

  async create_task_advanced(env, a) {
    if (!a.model || typeof a.input !== "object") throw new Error("model and input are required.");
    const secs = Number(a.input.duration);
    if (Number.isFinite(secs) && secs > MAX_CLIP_SECONDS) {
      throw new Error(`Clips must be ${MAX_CLIP_SECONDS} seconds or shorter (Betty's micro drama rule).`);
    }
    return startedMessage(await createTask(env, a.model, a.input), a.model);
  },
};

// ---------- MCP plumbing ----------

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}
function rpcError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

async function handleRpc(msg, env) {
  const { id, method, params = {} } = msg;
  const isNotification = id === undefined || id === null;
  switch (method) {
    case "initialize": {
      const requested = params.protocolVersion;
      return rpcResult(id, {
        protocolVersion: SUPPORTED_PROTOCOLS.includes(requested) ? requested : SUPPORTED_PROTOCOLS[0],
        capabilities: { tools: {} },
        serverInfo: SERVER_INFO,
        instructions:
          "Kie.ai image and video generation for Betty's micro dramas. Betty's standing rule: every clip is 9:16, 720p, 17 seconds or shorter, and made with the setting that gives the best result for the fewest credits. The defaults already follow this; only pick a pricier model, higher resolution or sound when Betty asks. Every create_* call spends credits, so confirm the shot list before generating many. Generation is asynchronous: start with create_image or create_video, then poll check_task. Results expire after 14 days.",
      });
    }
    case "ping":
      return rpcResult(id, {});
    case "tools/list":
      return rpcResult(id, { tools: TOOLS });
    case "tools/call": {
      const fn = handlers[params.name];
      if (!fn) return rpcError(id, -32602, `Unknown tool: ${params.name}`);
      try {
        const out = await fn(env, params.arguments || {});
        return rpcResult(id, { content: [{ type: "text", text: JSON.stringify(out, null, 2) }] });
      } catch (e) {
        return rpcResult(id, { content: [{ type: "text", text: String(e.message || e) }], isError: true });
      }
    }
    default:
      if (isNotification) return null;
      return rpcError(id, -32601, `Method not found: ${method}`);
  }
}

function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/" && request.method === "GET") {
      return new Response("Betty's Kie.ai connector is running.", { status: 200 });
    }

    const match = url.pathname.match(/^\/mcp\/([^/]+)\/?$/);
    if (!match) return new Response("Not found", { status: 404 });

    if (!env.CONNECTOR_PASSWORD || env.CONNECTOR_PASSWORD.length < 16) {
      return new Response("Setup needed: add a CONNECTOR_PASSWORD secret (16+ characters) in Cloudflare.", { status: 500 });
    }
    if (!safeEqual(decodeURIComponent(match[1]), env.CONNECTOR_PASSWORD)) {
      return new Response("Not found", { status: 404 });
    }
    if (!env.KIE_API_KEY) {
      return new Response("Setup needed: add a KIE_API_KEY secret in Cloudflare.", { status: 500 });
    }

    if (request.method === "GET" || request.method === "DELETE") {
      // Stateless server: no server-to-client stream and no sessions.
      return new Response("Method not allowed", { status: 405, headers: { Allow: "POST" } });
    }
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });

    let payload;
    try {
      payload = await request.json();
    } catch {
      return json(rpcError(null, -32700, "Parse error"), 400);
    }

    if (Array.isArray(payload)) {
      const results = (await Promise.all(payload.map((m) => handleRpc(m, env)))).filter(Boolean);
      return results.length ? json(results) : new Response(null, { status: 202 });
    }
    const result = await handleRpc(payload, env);
    return result ? json(result) : new Response(null, { status: 202 });
  },
};
