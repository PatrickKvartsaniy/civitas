const DB_NAME = "CivitasCache";
const STORE_NAME = "buildings";
const CACHE_EXPIRATION = 60 * 60 * 1000; // 1 hour in milliseconds

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, 1);
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME, { keyPath: "id" });
            }
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject("Failed to open IndexedDB");
    });
}

function getCachedData() {
    return openDB().then(db => {
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORE_NAME, "readonly");
            const store = tx.objectStore(STORE_NAME);
            const request = store.get("geojson");

            request.onsuccess = () => {
                const result = request.result;
                if (result && Date.now() - result.timestamp < CACHE_EXPIRATION) {
                    resolve(result.data);
                } else {
                    resolve(null);
                }
            };
            request.onerror = () => reject("Failed to retrieve cached data");
        });
    });
}

function cacheData(geojson) {
    return openDB().then(db => {
        const tx = db.transaction(STORE_NAME, "readwrite");
        const store = tx.objectStore(STORE_NAME);
        store.put({ id: "geojson", data: geojson, timestamp: Date.now() });
    });
}

function fetchAndCacheData(callback) {
    fetch(API_URL)
        .then(response => response.json())
        .then(geojson => {
            cacheData(geojson);
            callback(geojson);
        })
        .catch(error => console.error('Error fetching buildings:', error));
}
