(() => {
  const section = document.querySelector("[data-medley-browser]");
  if (!section) return;

  const grid = section.querySelector("[data-medley-grid]");
  const count = section.querySelector("[data-medley-count]");
  const empty = section.querySelector("[data-medley-empty]");
  const cards = [...section.querySelectorAll("[data-medley-card]")];
  const state = { filter: "all", sort: "popular" };

  function preferredYouTubeUrl(rawUrl) {
    try {
      const url = new URL(rawUrl, window.location.href);
      const host = url.hostname.replace(/^www\./, "");
      let videoId = "";

      if (host === "youtu.be") {
        videoId = url.pathname.split("/").filter(Boolean)[0] || "";
      } else if (host === "youtube.com" || host === "m.youtube.com") {
        videoId = url.searchParams.get("v") || "";
        if (!videoId) {
          const parts = url.pathname.split("/").filter(Boolean);
          if (["shorts", "embed", "live"].includes(parts[0])) videoId = parts[1] || "";
        }
      }

      return videoId ? `https://youtu.be/${videoId}` : rawUrl;
    } catch {
      return rawUrl;
    }
  }

  cards.forEach((card) => {
    card.href = preferredYouTubeUrl(card.href);
    card.removeAttribute("target");
  });

  const number = (card, key) => Number(card.dataset[key] || 0);

  function sortedVisibleCards() {
    const visible = cards.filter((card) => state.filter === "all" || card.dataset.category === state.filter);
    return visible.sort((a, b) => {
      if (state.sort === "duration") {
        return number(b, "duration") - number(a, "duration") || number(b, "views") - number(a, "views");
      }
      return number(b, "views") - number(a, "views") || number(b, "duration") - number(a, "duration");
    });
  }

  function updateButtons() {
    section.querySelectorAll("[data-medley-filter]").forEach((button) => {
      const active = button.dataset.medleyFilter === state.filter;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    section.querySelectorAll("[data-medley-sort]").forEach((button) => {
      const active = button.dataset.medleySort === state.sort;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function render() {
    const visible = sortedVisibleCards();
    cards.forEach((card) => {
      card.hidden = true;
      card.classList.remove("is-top-ranked");
    });
    visible.forEach((card, index) => {
      card.hidden = false;
      const rank = card.querySelector("[data-medley-rank]");
      if (rank) {
        rank.textContent = String(index + 1);
        rank.hidden = state.sort !== "popular";
      }
      card.classList.toggle("is-top-ranked", state.sort === "popular" && index < 3);
      grid.append(card);
    });
    count.textContent = String(visible.length);
    empty.hidden = visible.length !== 0;
    updateButtons();
  }

  section.addEventListener("click", (event) => {
    const filter = event.target.closest("[data-medley-filter]");
    if (filter) {
      state.filter = filter.dataset.medleyFilter;
      render();
      return;
    }
    const sort = event.target.closest("[data-medley-sort]");
    if (sort) {
      state.sort = sort.dataset.medleySort;
      render();
    }
  });

  render();
})();
