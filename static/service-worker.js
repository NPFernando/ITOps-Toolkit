const SHELL_CACHE = "itops-shell-v1";
const SHELL_FALLBACK = "/";
const PRECACHE_URLS = [SHELL_FALLBACK, "/app/static/manifest.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== SHELL_CACHE).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).catch(
        () =>
          caches.match(SHELL_FALLBACK).then((cached) => cached || new Response("Offline", { status: 503 })),
      ),
    );
    return;
  }

  if (url.pathname.startsWith("/app/static/")) {
    event.respondWith(caches.match(request).then((cached) => cached || fetch(request)));
  }
});
