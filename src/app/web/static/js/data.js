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
    fetch(API_URL + "/buildings/geojson")
      .then(response => {
            if (!response.ok) { // Check for HTTP errors (status outside 200-299)
                throw new Error(`HTTP error! status: ${response.status}`); // Throw an error to be caught
            }
            return response.json(); // If response is OK, parse JSON
        })
      .then(geojson => {
            if (!geojson ||!geojson.features ||!Array.isArray(geojson.features)) {
                console.error("Invalid GeoJSON format:", geojson);
                throw new Error("Invalid GeoJSON data"); // Throw error for invalid data
            }
            cacheData(geojson)
              .then(r => console.log("Data cached"))
              .catch(error => console.error("Error caching data:", error)); // Catch caching errors
            callback(geojson); // Call the callback after successful fetch and cache
        })
      .catch(error => {
            console.error('Error fetching or processing buildings:', error); // Catch all errors
        });
}
