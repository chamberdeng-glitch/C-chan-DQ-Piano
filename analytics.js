(() => {
  const EVENT_PAGE_CONTEXT = "page_context";
  const EVENT_YOUTUBE_CLICK = "youtube_click";
  const EVENT_SITE_NAVIGATION = "site_navigation_click";
  const EVENT_FILTER_CLICK = "filter_click";

  const cleanText = (value) => String(value || "").replace(/\s+/g, " ").trim().slice(0, 120);

  const getPath = () => window.location.pathname || "/";

  const getLanguage = () => {
    const path = getPath();
    return path === "/en.html" || path.startsWith("/en/") ? "en" : "ja";
  };

  const getPageType = () => {
    const path = getPath().replace(/\/index\.html$/, "/");
    const normalized = path.endsWith("/") ? path : `${path}/`;
    const withoutLang = normalized.replace(/^\/en\//, "/");

    if (withoutLang === "/" || path === "/en.html") return "home";
    if (withoutLang === "/series-index/" || withoutLang === "/series-index.html/") return "series_index";
    if (withoutLang === "/category-index/" || withoutLang === "/category-index.html/") return "category_index";
    if (/^\/dq\d+\//.test(withoutLang)) return "series_page";
    if (withoutLang.startsWith("/category/")) return "category_page";
    return "other";
  };

  const sendEvent = (name, params = {}) => {
    if (typeof window.gtag !== "function") return;

    window.gtag("event", name, {
      page_path: getPath(),
      page_language: getLanguage(),
      page_type: getPageType(),
      ...params
    });
  };

  const toUrl = (href) => {
    try {
      return new URL(href, window.location.href);
    } catch {
      return null;
    }
  };

  const isYouTubeUrl = (url) => {
    if (!url) return false;
    const host = url.hostname.replace(/^www\./, "");
    return host === "youtube.com" || host === "youtu.be" || host === "music.youtube.com";
  };

  const getLinkContext = (link) => {
    if (link.classList.contains("song-number-link")) return "song_number";
    if (link.classList.contains("song-link")) return "song";
    if (link.classList.contains("topbar-cta") || link.dataset.nav === "youtube") return "channel_cta";
    if (link.classList.contains("page-action")) return "page_action";
    if (link.classList.contains("video-link")) return "video_card";
    if (link.closest(".topbar")) return "topbar";
    if (link.closest(".breadcrumbs")) return "breadcrumb";
    if (link.closest(".entry-card")) return "entry_card";
    return "link";
  };

  const getSongId = (link) => {
    if (link.classList.contains("song-number-link")) return cleanText(link.textContent);
    return cleanText(link.closest("tr")?.querySelector(".song-number-link")?.textContent);
  };

  const trackLink = (link) => {
    const url = toUrl(link.href);
    if (!url) return;

    const params = {
      link_url: url.href,
      link_text: cleanText(link.textContent || link.getAttribute("aria-label")),
      link_context: getLinkContext(link)
    };
    const songId = getSongId(link);
    if (songId) params.song_id = songId;

    if (isYouTubeUrl(url)) {
      sendEvent(EVENT_YOUTUBE_CLICK, params);
      return;
    }

    if (url.origin === window.location.origin) {
      sendEvent(EVENT_SITE_NAVIGATION, params);
    }
  };

  const trackFilter = (button) => {
    const filterType = button.dataset.category ? "playlist_category" : "song_category";
    const filterValue = button.dataset.category || button.dataset.songCategory || "";

    sendEvent(EVENT_FILTER_CLICK, {
      filter_type: filterType,
      filter_value: filterValue,
      link_text: cleanText(button.textContent)
    });
  };

  document.addEventListener(
    "click",
    (event) => {
      const filterButton = event.target.closest("[data-category], [data-song-category]");
      if (filterButton) {
        trackFilter(filterButton);
        return;
      }

      const link = event.target.closest("a[href]");
      if (link) trackLink(link);
    },
    true
  );

  document.addEventListener("DOMContentLoaded", () => {
    sendEvent(EVENT_PAGE_CONTEXT, {
      content_group: getPageType()
    });
  });
})();
