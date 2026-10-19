import classificationConfig from "../config/contact-classification.json" with { type: "json" };

const MAX_BODY_BYTES = 16 * 1024;
const DEFAULT_LIMITS = Object.freeze({
  ipHour: 5,
  ipDay: 20,
  emailDay: 3,
  globalDay: 200,
});
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/u;
const HEADER_BREAK_RE = /[\r\n]/u;
const CONTROL_RE = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/gu;
let rateLimitQueue = Promise.resolve();

function jsonResponse(status, ok = false) {
  return new Response(JSON.stringify({ ok }), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

function splitConfig(value) {
  return String(value || "")
    .split(/[\n,]/u)
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
}

function characterLength(value) {
  return Array.from(value).length;
}

function normalizeText(value) {
  return String(value || "").normalize("NFKC").toLowerCase();
}

function stripControls(value) {
  return String(value || "").replace(CONTROL_RE, "");
}

export function classifyMessage(message, config = classificationConfig) {
  const normalized = normalizeText(message);
  const rights = config.rightsKeywords.some((keyword) => normalized.includes(normalizeText(keyword)));
  if (rights) return ["RIGHTS"];

  const tags = [];
  const urls = normalized.match(/(?:https?:\/\/|www\.)[^\s<>()]+/giu) || [];
  if (urls.length >= 3) tags.push("LINKS");
  if (config.ngKeywords.some((keyword) => normalized.includes(normalizeText(keyword)))) tags.push("NG");

  const lines = normalized
    .split(/\r?\n/u)
    .map((line) => line.trim())
    .filter((line) => line.length >= 4);
  const counts = new Map();
  for (const line of lines) counts.set(line, (counts.get(line) || 0) + 1);
  if ([...counts.values()].some((count) => count >= 3)) tags.push("REPEAT");
  return tags;
}

export function validatePayload(payload) {
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) return null;
  const requiredStrings = ["name", "email", "message", "turnstileToken", "lang"];
  if (requiredStrings.some((key) => typeof payload[key] !== "string")) return null;
  if (typeof payload.consent !== "boolean" || typeof payload.website !== "string") return null;

  if (HEADER_BREAK_RE.test(payload.name) || HEADER_BREAK_RE.test(payload.email)) return null;
  const name = stripControls(payload.name).trim();
  const email = stripControls(payload.email).trim().toLowerCase();
  const message = stripControls(payload.message).trim();
  const website = stripControls(payload.website).trim();
  const turnstileToken = stripControls(payload.turnstileToken).trim();
  const lang = payload.lang === "en" ? "en" : payload.lang === "ja" ? "ja" : "";

  if (characterLength(name) < 1 || characterLength(name) > 100) return null;
  if (characterLength(email) > 254 || !EMAIL_RE.test(email)) return null;
  if (characterLength(message) < 10 || characterLength(message) > 3000) return null;
  if (!payload.consent || !lang || characterLength(turnstileToken) > 2048) return null;

  return { name, email, message, website, turnstileToken, lang };
}

function allowedRequestSource(request, env) {
  const allowed = new Set(splitConfig(env.CONTACT_ALLOWED_ORIGINS || "https://dqpiano.com"));
  const origin = request.headers.get("Origin");
  const referer = request.headers.get("Referer");
  if (!origin && !referer) return false;

  const candidates = [];
  if (origin) candidates.push(origin);
  if (referer) {
    try {
      candidates.push(new URL(referer).origin);
    } catch {
      return false;
    }
  }
  return candidates.every((candidate) => allowed.has(candidate.toLowerCase()));
}

async function verifyTurnstile(payload, request, env, fetchImpl) {
  if (!env.TURNSTILE_SECRET_KEY || !payload.turnstileToken) return false;
  const form = new FormData();
  form.set("secret", env.TURNSTILE_SECRET_KEY);
  form.set("response", payload.turnstileToken);
  const ip = request.headers.get("CF-Connecting-IP");
  if (ip) form.set("remoteip", ip);
  form.set("idempotency_key", crypto.randomUUID());

  let response;
  try {
    response = await fetchImpl("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body: form,
    });
  } catch {
    return false;
  }
  if (!response.ok) return false;

  const result = await response.json();
  const allowedHostnames = new Set(splitConfig(env.CONTACT_ALLOWED_HOSTNAMES || "dqpiano.com"));
  const expectedAction = env.CONTACT_TURNSTILE_ACTION || "contact";
  return Boolean(
    result.success &&
    allowedHostnames.has(String(result.hostname || "").toLowerCase()) &&
    result.action === expectedAction
  );
}

async function hmacHash(value, salt) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(salt),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return [...new Uint8Array(signature)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function configuredLimits(env) {
  let override = {};
  if (env.CONTACT_RATE_LIMITS_JSON) {
    try {
      override = JSON.parse(env.CONTACT_RATE_LIMITS_JSON);
    } catch {
      override = {};
    }
  }
  const values = { ...DEFAULT_LIMITS, ...override };
  for (const [key, fallback] of Object.entries(DEFAULT_LIMITS)) {
    const parsed = Number.parseInt(values[key], 10);
    values[key] = Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
  }
  return values;
}

function windowIds(now) {
  return {
    hour: Math.floor(now / 3_600_000),
    day: Math.floor(now / 86_400_000),
  };
}

async function withRateLimitLock(operation) {
  const previous = rateLimitQueue;
  let release;
  rateLimitQueue = new Promise((resolve) => { release = resolve; });
  await previous;
  try {
    return await operation();
  } finally {
    release();
  }
}

async function checkAndRecordRateLimits(payload, request, env, now) {
  if (!env.CONTACT_RATE_LIMITS || !env.CONTACT_HASH_SALT) return { configured: false, allowed: false };
  const ip = request.headers.get("CF-Connecting-IP");
  if (!ip) return { configured: false, allowed: false };

  const [ipHash, emailHash] = await Promise.all([
    hmacHash(`ip:${ip}`, env.CONTACT_HASH_SALT),
    hmacHash(`email:${payload.email}`, env.CONTACT_HASH_SALT),
  ]);
  const limits = configuredLimits(env);
  const windows = windowIds(now);
  const checks = [
    { prefix: `ip-hour:${windows.hour}:${ipHash}:`, limit: limits.ipHour, ttl: 3600 },
    { prefix: `ip-day:${windows.day}:${ipHash}:`, limit: limits.ipDay, ttl: 86400 },
    { prefix: `email-day:${windows.day}:${emailHash}:`, limit: limits.emailDay, ttl: 86400 },
    { prefix: `global-day:${windows.day}:`, limit: limits.globalDay, ttl: 86400 },
  ];

  return withRateLimitLock(async () => {
    for (const check of checks) {
      const result = await env.CONTACT_RATE_LIMITS.list({ prefix: check.prefix, limit: check.limit });
      if (result.keys.length >= check.limit) return { configured: true, allowed: false };
    }
    const eventId = crypto.randomUUID();
    await Promise.all(checks.map((check) => (
      env.CONTACT_RATE_LIMITS.put(`${check.prefix}${eventId}`, "1", { expirationTtl: check.ttl })
    )));
    return { configured: true, allowed: true };
  });
}

function isBlocked(email, env) {
  const blockedEmails = new Set(splitConfig(env.CONTACT_BLOCKED_EMAILS));
  const blockedDomains = new Set(splitConfig(env.CONTACT_BLOCKED_DOMAINS));
  const domain = email.split("@").pop();
  return blockedEmails.has(email) || blockedDomains.has(domain);
}

export function buildEmail(payload, request, env, now = Date.now()) {
  const tags = classifyMessage(payload.message);
  const tagPrefix = tags.map((tag) => `[${tag}]`).join("");
  const subject = `${tagPrefix}[dqpiano.com] お問い合わせ`;
  const country = request.headers.get("CF-IPCountry") || "unknown";
  const tagLabel = tags.length ? tags.join(", ") : "none";
  const text = [
    `名前 / Name: ${payload.name}`,
    `メール / Email: ${payload.email}`,
    `言語 / Language: ${payload.lang}`,
    `国コード / Country: ${country}`,
    `分類タグ / Tags: ${tagLabel}`,
    `送信時刻 / Sent at: ${new Date(now).toISOString()}`,
    "",
    "本文 / Message:",
    payload.message,
  ].join("\n");
  return {
    to: env.CONTACT_TO_EMAIL,
    from: env.CONTACT_FROM_EMAIL,
    replyTo: payload.email,
    subject,
    text,
  };
}

export async function handleContactRequest(request, env, options = {}) {
  const fetchImpl = options.fetchImpl || fetch;
  const now = options.now || Date.now();
  if (request.method !== "POST") return jsonResponse(405);
  if (!allowedRequestSource(request, env)) return jsonResponse(403);
  if (!(request.headers.get("Content-Type") || "").toLowerCase().startsWith("application/json")) {
    return jsonResponse(415);
  }

  const declaredLength = Number.parseInt(request.headers.get("Content-Length") || "0", 10);
  if (declaredLength > MAX_BODY_BYTES) return jsonResponse(413);
  const raw = await request.arrayBuffer();
  if (raw.byteLength > MAX_BODY_BYTES) return jsonResponse(413);

  let parsed;
  try {
    parsed = JSON.parse(new TextDecoder().decode(raw));
  } catch {
    return jsonResponse(400);
  }
  const payload = validatePayload(parsed);
  if (!payload) return jsonResponse(400);
  if (payload.website) return jsonResponse(200, true);
  if (isBlocked(payload.email, env)) return jsonResponse(200, true);

  const turnstileValid = await verifyTurnstile(payload, request, env, fetchImpl);
  if (!turnstileValid) return jsonResponse(400);

  const rate = await checkAndRecordRateLimits(payload, request, env, now);
  if (!rate.configured) return jsonResponse(503);
  if (!rate.allowed) return jsonResponse(429);
  if (!env.CONTACT_EMAIL || !env.CONTACT_TO_EMAIL || !env.CONTACT_FROM_EMAIL) return jsonResponse(503);

  try {
    await env.CONTACT_EMAIL.send(buildEmail(payload, request, env, now));
  } catch {
    return jsonResponse(502);
  }
  return jsonResponse(200, true);
}

export function handleContactConfig(env) {
  if (!env.TURNSTILE_SITE_KEY) return jsonResponse(503);
  return new Response(JSON.stringify({ siteKey: env.TURNSTILE_SITE_KEY }), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
