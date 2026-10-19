import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import {
  buildEmail,
  classifyMessage,
  handleContactRequest,
  validatePayload,
} from "../src/contact.js";

const TURNSTILE_TEST_SECRETS = {
  pass: "1x0000000000000000000000000000000AA",
  fail: "2x0000000000000000000000000000000AA",
  duplicate: "3x0000000000000000000000000000000AA",
};

class MemoryKV {
  constructor() {
    this.values = new Map();
  }

  async list({ prefix, limit }) {
    const keys = [...this.values.keys()]
      .filter((name) => name.startsWith(prefix))
      .slice(0, limit)
      .map((name) => ({ name }));
    return { keys, list_complete: true };
  }

  async put(key, value) {
    this.values.set(key, value);
  }
}

function validPayload(overrides = {}) {
  return {
    name: "山田 花子",
    email: "person@example.com",
    message: "お問い合わせの本文です。確認をお願いします。",
    consent: true,
    website: "",
    turnstileToken: "valid-token",
    lang: "ja",
    ...overrides,
  };
}

function requestFor(payload = validPayload(), overrides = {}) {
  const body = JSON.stringify(payload);
  const headers = {
    "Content-Type": "application/json",
    Origin: "https://dqpiano.com",
    "CF-Connecting-IP": overrides.ip || "203.0.113.10",
    "CF-IPCountry": "JP",
    ...(overrides.headers || {}),
  };
  return new Request("https://dqpiano.com/api/contact", {
    method: overrides.method || "POST",
    headers,
    body: (overrides.method || "POST") === "GET" ? undefined : body,
  });
}

function turnstileFetch(result = {}) {
  return async (_url, init) => {
    const token = init.body.get("response");
    if (token === "fail-token") {
      return Response.json({ success: false, "error-codes": ["invalid-input-response"] });
    }
    if (token === "expired-token" || token === "duplicate-token") {
      return Response.json({ success: false, "error-codes": ["timeout-or-duplicate"] });
    }
    return Response.json({ success: true, hostname: "dqpiano.com", action: "contact", ...result });
  };
}

function makeEnv(overrides = {}) {
  const sent = [];
  return {
    TURNSTILE_SECRET_KEY: "test-secret",
    CONTACT_ALLOWED_ORIGINS: "https://dqpiano.com",
    CONTACT_ALLOWED_HOSTNAMES: "dqpiano.com",
    CONTACT_TURNSTILE_ACTION: "contact",
    CONTACT_HASH_SALT: "test-only-long-random-salt",
    CONTACT_TO_EMAIL: "owner@example.test",
    CONTACT_FROM_EMAIL: "contact@example.test",
    CONTACT_RATE_LIMITS: new MemoryKV(),
    CONTACT_EMAIL: { async send(message) { sent.push(message); } },
    sent,
    ...overrides,
  };
}

async function submit(payload = validPayload(), env = makeEnv(), overrides = {}) {
  return handleContactRequest(requestFor(payload, overrides), env, {
    fetchImpl: overrides.fetchImpl || turnstileFetch(),
    now: overrides.now || Date.UTC(2026, 9, 19, 0, 0, 0),
  });
}

test("classification gives RIGHTS exclusive priority", () => {
  const message = "著作権 SEO https://a.example https://b.example https://c.example\nrepeat\nrepeat\nrepeat";
  assert.deepEqual(classifyMessage(message), ["RIGHTS"]);
  assert.deepEqual(classifyMessage("Rights-Related Contact DMCA SEO"), ["RIGHTS"]);
});

test("classification applies normal tags without discarding messages", () => {
  assert.deepEqual(classifyMessage("SEOについて相談したいです"), ["NG"]);
  assert.deepEqual(classifyMessage("https://a.example https://b.example"), []);
  assert.deepEqual(classifyMessage("https://a.example https://b.example https://c.example"), ["LINKS"]);
  assert.deepEqual(classifyMessage("広告掲載 https://a.example https://b.example https://c.example\n同じ文です\n同じ文です\n同じ文です"), ["LINKS", "NG", "REPEAT"]);
});

test("generic words do not become rights tags", () => {
  for (const word of ["削除", "権利", "permission", "license"]) {
    assert.equal(classifyMessage(`一般的な質問 ${word}`).includes("RIGHTS"), false);
  }
});

test("normal submission sends a plain-text structured email with UTF-8 and Reply-To", async () => {
  const env = makeEnv();
  const response = await submit(validPayload({ name: "山田 花子", message: "日本語の本文を正しく送信します。" }), env);
  assert.equal(response.status, 200);
  assert.equal(env.sent.length, 1);
  assert.equal(env.sent[0].replyTo, "person@example.com");
  assert.equal(env.sent[0].subject, "[dqpiano.com] お問い合わせ");
  assert.match(env.sent[0].text, /山田 花子/u);
  assert.match(env.sent[0].text, /日本語の本文を正しく送信します。/u);
  assert.equal("html" in env.sent[0], false);
});

test("rights and NG messages are both sent with the expected subject tag", async () => {
  const rightsEnv = makeEnv();
  await submit(validPayload({ message: "著作権 SEO https://a.example https://b.example https://c.example" }), rightsEnv);
  assert.equal(rightsEnv.sent[0].subject, "[RIGHTS][dqpiano.com] お問い合わせ");

  const ngEnv = makeEnv();
  await submit(validPayload({ message: "広告掲載についての営業連絡です。" }), ngEnv);
  assert.equal(ngEnv.sent[0].subject, "[NG][dqpiano.com] お問い合わせ");
});

test("honeypot and blocklist return success without Turnstile or email", async () => {
  const honeypotEnv = makeEnv();
  const honeypot = await submit(validPayload({ website: "bot.example" }), honeypotEnv, {
    fetchImpl: async () => { throw new Error("must not call"); },
  });
  assert.equal(honeypot.status, 200);
  assert.equal(honeypotEnv.sent.length, 0);

  const blockedEnv = makeEnv({ CONTACT_BLOCKED_DOMAINS: "example.com" });
  const blocked = await submit(validPayload(), blockedEnv, {
    fetchImpl: async () => { throw new Error("must not call"); },
  });
  assert.equal(blocked.status, 200);
  assert.equal(blockedEnv.sent.length, 0);
});

test("Turnstile failure, expiry, and replay responses do not send email", async () => {
  for (const token of ["fail-token", "expired-token", "duplicate-token"]) {
    const env = makeEnv();
    const response = await submit(validPayload({ turnstileToken: token }), env);
    assert.equal(response.status, 400);
    assert.equal(env.sent.length, 0);
  }
});

test("Cloudflare official Turnstile test-secret scenarios are wired", async () => {
  const officialKeyFetch = async (_url, init) => {
    const secret = init.body.get("secret");
    if (secret === TURNSTILE_TEST_SECRETS.pass) {
      return Response.json({ success: true, hostname: "dqpiano.com", action: "contact" });
    }
    return Response.json({
      success: false,
      "error-codes": [secret === TURNSTILE_TEST_SECRETS.duplicate ? "timeout-or-duplicate" : "invalid-input-response"],
    });
  };
  for (const [kind, secret] of Object.entries(TURNSTILE_TEST_SECRETS)) {
    const env = makeEnv({ TURNSTILE_SECRET_KEY: secret });
    const response = await submit(validPayload(), env, { fetchImpl: officialKeyFetch });
    assert.equal(response.status, kind === "pass" ? 200 : 400);
  }
});

test("server validation rejects all boundary violations", async () => {
  const cases = [
    validPayload({ name: "a".repeat(101) }),
    validPayload({ email: `${"a".repeat(250)}@x.test` }),
    validPayload({ message: "a".repeat(3001) }),
    validPayload({ message: "short" }),
    validPayload({ name: "safe\r\nBcc: victim@example.com" }),
    validPayload({ email: "safe@example.com\r\nBcc:victim@example.com" }),
    validPayload({ consent: false }),
  ];
  for (const payload of cases) {
    const response = await submit(payload, makeEnv());
    assert.equal(response.status, 400);
  }
  assert.equal(validatePayload(validPayload({ name: "a".repeat(100), message: "a".repeat(3000) })) !== null, true);
});

test("request guards enforce size, source, content type, and method", async () => {
  const tooLarge = await submit(validPayload({ message: "a".repeat(17000) }), makeEnv());
  assert.equal(tooLarge.status, 413);

  const wrongOrigin = await submit(validPayload(), makeEnv(), { headers: { Origin: "https://evil.example" } });
  assert.equal(wrongOrigin.status, 403);

  const missingHeaders = new Headers({ "Content-Type": "application/json", "CF-Connecting-IP": "203.0.113.10" });
  const missingSource = await handleContactRequest(new Request("https://dqpiano.com/api/contact", {
    method: "POST", headers: missingHeaders, body: JSON.stringify(validPayload()),
  }), makeEnv(), { fetchImpl: turnstileFetch() });
  assert.equal(missingSource.status, 403);

  const wrongType = await submit(validPayload(), makeEnv(), { headers: { "Content-Type": "text/plain" } });
  assert.equal(wrongType.status, 415);

  const get = await handleContactRequest(new Request("https://dqpiano.com/api/contact"), makeEnv());
  assert.equal(get.status, 405);
});

test("email binding failure is not reported as success", async () => {
  const env = makeEnv({ CONTACT_EMAIL: { async send() { throw new Error("delivery failed"); } } });
  const response = await submit(validPayload(), env);
  assert.equal(response.status, 502);
});

test("missing secrets or bindings fail closed", async () => {
  const missingRate = makeEnv({ CONTACT_RATE_LIMITS: undefined });
  assert.equal((await submit(validPayload(), missingRate)).status, 503);
  const missingEmail = makeEnv({ CONTACT_TO_EMAIL: "" });
  assert.equal((await submit(validPayload(), missingEmail)).status, 503);
});

test("IP hourly sixth submission is rejected", async () => {
  const env = makeEnv({ CONTACT_RATE_LIMITS_JSON: JSON.stringify({ emailDay: 99 }) });
  for (let index = 0; index < 5; index += 1) {
    const response = await submit(validPayload({ email: `person${index}@example.com`, turnstileToken: `token-${index}` }), env);
    assert.equal(response.status, 200);
  }
  const sixth = await submit(validPayload({ email: "person6@example.com", turnstileToken: "token-6" }), env);
  assert.equal(sixth.status, 429);
});

test("IP daily twenty-first submission is rejected", async () => {
  const env = makeEnv({ CONTACT_RATE_LIMITS_JSON: JSON.stringify({ ipHour: 99, emailDay: 99 }) });
  for (let index = 0; index < 20; index += 1) {
    assert.equal((await submit(validPayload({ email: `daily${index}@example.com`, turnstileToken: `daily-${index}` }), env)).status, 200);
  }
  assert.equal((await submit(validPayload({ email: "daily21@example.com", turnstileToken: "daily-21" }), env)).status, 429);
});

test("email daily fourth submission is rejected", async () => {
  const env = makeEnv({ CONTACT_RATE_LIMITS_JSON: JSON.stringify({ ipHour: 99, ipDay: 99 }) });
  for (let index = 0; index < 3; index += 1) {
    assert.equal((await submit(validPayload({ turnstileToken: `email-${index}` }), env, { ip: `203.0.113.${index + 1}` })).status, 200);
  }
  assert.equal((await submit(validPayload({ turnstileToken: "email-4" }), env, { ip: "203.0.113.9" })).status, 429);
});

test("global daily two-hundred-first submission is rejected", async () => {
  const env = makeEnv({ CONTACT_RATE_LIMITS_JSON: JSON.stringify({ ipHour: 999, ipDay: 999, emailDay: 999 }) });
  for (let index = 0; index < 200; index += 1) {
    const response = await submit(validPayload({ email: `global${index}@example.com`, turnstileToken: `global-${index}` }), env, { ip: `198.51.${Math.floor(index / 250)}.${(index % 250) + 1}` });
    assert.equal(response.status, 200);
  }
  assert.equal((await submit(validPayload({ email: "global201@example.com", turnstileToken: "global-201" }), env, { ip: "198.51.100.250" })).status, 429);
});

test("same-isolate concurrent submissions are serialized", async () => {
  const env = makeEnv({ CONTACT_RATE_LIMITS_JSON: JSON.stringify({ emailDay: 99 }) });
  const responses = await Promise.all(Array.from({ length: 6 }, (_, index) => (
    submit(validPayload({ email: `parallel${index}@example.com`, turnstileToken: `parallel-${index}` }), env)
  )));
  assert.deepEqual(responses.map((response) => response.status).sort(), [200, 200, 200, 200, 200, 429]);
});

test("client script contains double-submit and expired-token handling", async () => {
  const script = await readFile(new URL("../assets/contact.js", import.meta.url), "utf8");
  assert.match(script, /if \(sending\) return;/u);
  assert.match(script, /"expired-callback"/u);
  assert.match(script, /turnstile\.reset/u);
});

test("buildEmail never includes IP address or user-agent", () => {
  const request = requestFor();
  const email = buildEmail(validPayload(), request, makeEnv(), Date.UTC(2026, 9, 19));
  assert.doesNotMatch(email.text, /203\.0\.113\.10/u);
  assert.doesNotMatch(email.text, /user-agent/iu);
});
