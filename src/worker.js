const OLD_HOST = "c-chan-dq-piano.chamberdeng.workers.dev";
const NEW_ORIGIN = "https://dqpiano.com";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname === OLD_HOST) {
      return Response.redirect(`${NEW_ORIGIN}${url.pathname}${url.search}`, 301);
    }

    if (url.protocol === "http:") {
      url.protocol = "https:";
      return Response.redirect(url.toString(), 301);
    }

    return env.ASSETS.fetch(request);
  },
};
