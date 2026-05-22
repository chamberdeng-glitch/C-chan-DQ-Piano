const OLD_HOST = "c-chan-dq-piano.chamberdeng.workers.dev";
const NEW_ORIGIN = "https://dqpiano.com";
const NEW_HOST = "dqpiano.com";

function canonicalPath(pathname) {
  const path = pathname.replace(/\/{2,}/g, "/");
  const mappings = new Map([
    ["/en", "/en/"],
    ["/en.html", "/en/"],
    ["/series-index", "/series-index/"],
    ["/series-index.html", "/series-index/"],
    ["/category-index", "/category-index/"],
    ["/category-index.html", "/category-index/"],
    ["/en/series-index", "/en/series-index/"],
    ["/en/series-index.html", "/en/series-index/"],
    ["/en/category-index", "/en/category-index/"],
    ["/en/category-index.html", "/en/category-index/"],
    ["/category/battle", "/category/normal-battle/"],
    ["/category/battle/", "/category/normal-battle/"],
    ["/category/battle.html", "/category/normal-battle/"],
    ["/en/category/battle", "/en/category/normal-battle/"],
    ["/en/category/battle/", "/en/category/normal-battle/"],
    ["/en/category/battle.html", "/en/category/normal-battle/"],
  ]);

  if (mappings.has(path)) {
    return mappings.get(path);
  }

  if (path !== "/" && !path.endsWith("/") && !path.split("/").pop().includes(".")) {
    return `${path}/`;
  }

  return path;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const normalizedPath = canonicalPath(url.pathname);

    if (url.hostname === OLD_HOST) {
      return Response.redirect(`${NEW_ORIGIN}${normalizedPath}${url.search}`, 301);
    }

    if (url.hostname === NEW_HOST && (url.protocol === "http:" || url.pathname !== normalizedPath)) {
      url.hostname = NEW_HOST;
      url.protocol = "https:";
      url.pathname = normalizedPath;
      return Response.redirect(url.toString(), 301);
    }

    if (normalizedPath !== "/" && normalizedPath.endsWith("/")) {
      const assetUrl = new URL(request.url);
      assetUrl.pathname = `${normalizedPath}index.html`;
      return env.ASSETS.fetch(new Request(assetUrl, request));
    }

    return env.ASSETS.fetch(request);
  },
};
