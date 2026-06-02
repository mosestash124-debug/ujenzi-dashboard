const CACHE_NAME = "ujenzi-v1";
const urlsToCache = [
  "/ujenzi-dashboard/",
  "/ujenzi-dashboard/index.html",
  "/ujenzi-dashboard/dashboard.html",
  "/ujenzi-dashboard/bailout.html",
  "/ujenzi-dashboard/report.html",
  "/ujenzi-dashboard/reports_view.html",
  "/ujenzi-dashboard/sludge_report.json",
  "/ujenzi-dashboard/bailout.json",
  "/ujenzi-dashboard/manifest.json"
];

self.addEventListener("install", function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});
