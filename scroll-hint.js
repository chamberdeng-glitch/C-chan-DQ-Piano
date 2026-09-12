(() => {
  const locale = document.documentElement.lang === "en" ? "en" : "ja";
  const label = locale === "en" ? "Scroll horizontally" : "横にスクロールできます";
  const storageKey = `dqPianoScrollHintSeen:${locale}`;

  const markUsed = (node) => {
    node.classList.add("has-used-scroll");
    try {
      sessionStorage.setItem(storageKey, "1");
    } catch (_) {
      /* sessionStorage can be unavailable in some embedded browsers. */
    }
  };

  const hasSeenHint = () => {
    try {
      return sessionStorage.getItem(storageKey) === "1";
    } catch (_) {
      return false;
    }
  };

  const setupHint = (node) => {
    if (node.dataset.scrollHintReady === "true") return;
    node.dataset.scrollHintReady = "true";

    const hint = document.createElement("span");
    hint.className = "scroll-hint";
    hint.setAttribute("aria-hidden", "true");
    hint.innerHTML = `<span class="scroll-hint-icon" aria-hidden="true">⇆</span><span>${label}</span>`;
    node.appendChild(hint);

    const update = () => {
      const canScroll = node.scrollWidth > node.clientWidth + 8;
      node.classList.toggle("is-scrollable", canScroll);
      if (!canScroll) {
        node.classList.add("has-used-scroll");
        return;
      }
      if (!hasSeenHint()) {
        node.classList.remove("has-used-scroll");
      }
    };

    node.addEventListener("scroll", () => markUsed(node), { passive: true, once: true });
    node.addEventListener("pointerdown", () => markUsed(node), { passive: true, once: true });
    node.addEventListener("wheel", () => markUsed(node), { passive: true, once: true });
    node.addEventListener("keydown", (event) => {
      if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
        markUsed(node);
      }
    }, { once: true });

    update();
    window.addEventListener("resize", update, { passive: true });
  };

  const init = () => {
    document.querySelectorAll(".bookcase-scroll").forEach(setupHint);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
