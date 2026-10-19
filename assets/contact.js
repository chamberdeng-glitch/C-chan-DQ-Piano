(() => {
  const form = document.querySelector("[data-contact-form]");
  if (!form) return;

  const status = form.querySelector("[data-contact-status]");
  const submit = form.querySelector('button[type="submit"]');
  const lang = form.dataset.lang === "en" ? "en" : "ja";
  const messages = {
    ja: {
      success: "送信しました。内容を確認のうえ、必要な場合にご連絡します。",
      error: "送信できませんでした。しばらくしてからもう一度お試しください。",
      turnstile: "送信前に認証を完了してください。",
    },
    en: {
      success: "Sent. I'll review your message and get back to you if needed.",
      error: "Could not send. Please try again later.",
      turnstile: "Please complete the verification before sending.",
    },
  }[lang];
  let widgetId = null;
  let token = "";
  let sending = false;

  function show(message, kind = "") {
    status.textContent = message;
    status.dataset.kind = kind;
  }

  function resetTurnstile() {
    token = "";
    if (widgetId !== null && window.turnstile) window.turnstile.reset(widgetId);
  }

  async function initializeTurnstile() {
    try {
      const response = await fetch("/api/contact/config", {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error("config");
      const { siteKey } = await response.json();
      if (!siteKey || !window.turnstile) throw new Error("turnstile");
      widgetId = window.turnstile.render("[data-turnstile]", {
        sitekey: siteKey,
        action: "contact",
        theme: "dark",
        size: "flexible",
        callback(value) {
          token = value;
          show("");
        },
        "expired-callback"() {
          resetTurnstile();
        },
        "error-callback"() {
          token = "";
          show(messages.error, "error");
        },
      });
    } catch {
      submit.disabled = true;
      show(messages.error, "error");
    }
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (sending) return;
    if (!form.checkValidity()) {
      form.reportValidity();
      form.querySelector(":invalid")?.focus();
      return;
    }
    if (!token) {
      show(messages.turnstile, "error");
      form.querySelector("[data-turnstile]")?.scrollIntoView({ block: "center", behavior: "smooth" });
      return;
    }

    sending = true;
    submit.disabled = true;
    show("");
    const data = new FormData(form);
    const payload = {
      name: String(data.get("name") || ""),
      email: String(data.get("email") || ""),
      message: String(data.get("message") || ""),
      consent: data.get("consent") === "on",
      website: String(data.get("website") || ""),
      turnstileToken: token,
      lang,
    };

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("send");
      form.reset();
      resetTurnstile();
      show(messages.success, "success");
    } catch {
      resetTurnstile();
      show(messages.error, "error");
    } finally {
      sending = false;
      submit.disabled = false;
    }
  });

  if (window.turnstile) {
    initializeTurnstile();
  } else {
    window.addEventListener("load", initializeTurnstile, { once: true });
  }
})();
