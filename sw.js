const CACHE_NAME = "ujenzi-v2";  // Increment version to force update
const urlsToCache = [
  "/ujenzi-dashboard/",
  "/ujenzi-dashboard/index.html",
  "/ujenzi-dashboard/dashboard.html",
  "/ujenzi-dashboard/bailout.html",
  "/ujenzi-dashboard/report.html",
  "/ujenzi-dashboard/reports_view.html",
  "/ujenzi-dashboard/install.html",
  "/ujenzi-dashboard/sludge_report.json",
  "/ujenzi-dashboard/bailout.json",
  "/ujenzi-dashboard/manifest.json",
  "/ujenzi-dashboard/icon-192.png",
  "/ujenzi-dashboard/icon-512.png"
];

// Install event: cache all files
self.addEventListener("install", function(event) {
  console.log("[Service Worker] Installing new version...");
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(urlsToCache);
    })
  );
  // Force the waiting service worker to become active
  self.skipWaiting();
});

// Activate event: clean up old caches
self.addEventListener("activate", function(event) {
  console.log("[Service Worker] Activating new version...");
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cache) {
          if (cache !== CACHE_NAME) {
            console.log("[Service Worker] Deleting old cache:", cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  // Take control of all clients immediately
  self.clients.claim();
});

// Fetch event: serve from cache, fallback to network
self.addEventListener("fetch", function(event) {
  event.respondWith(
    caches.match(event.request).then(function(response) {
      return response || fetch(event.request);
    })
  );
});
