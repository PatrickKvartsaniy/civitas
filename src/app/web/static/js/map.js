const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [14.4551924, 35.9052445],
    zoom: 10
});

function findClosestAmenity(properties, category) {
    const lat = properties.latitude || 35.9052445;
    const lon = properties.longitude || 14.4551924;

    fetch(API_URL + "/buildings/&category=${encodeURIComponent(category)}")
        .then(response => response.json())
        .then(data => {
            alert(`Closest ${category}: ${data.name}, Distance: ${data.distance}m, Time: ${data.time}min`);
            showRoute([lon, lat], [data.lon, data.lat]);
        })
        .catch(error => console.error(`Error fetching closest ${category}:`, error));
}

function showRoute(start, end) {
    fetch(`https://your-api.com/route?start=${start}&end=${end}`)
        .then(response => response.json())
        .then(data => {
            map.addLayer({
                id: 'route',
                type: 'line',
                source: {
                    type: 'geojson',
                    data: {
                        type: 'Feature',
                        geometry: {
                            type: 'LineString',
                            coordinates: data.route
                        }
                    }
                },
                paint: {'line-color': '#ff0000', 'line-width': 3}
            });
        })
        .catch(error => console.error("Error fetching route:", error));
}

getCachedData().then(cachedData => {
    if (cachedData) {
        console.log("Using cached data.");
        addBuildingsLayer(cachedData);
    } else {
        console.log("Fetching fresh data.");
        fetchAndCacheData(addBuildingsLayer);
    }
});

const legend = document.createElement('div');
legend.className = 'legend';

const title = document.createElement('h3');
title.textContent = 'Building Categories';
legend.appendChild(title);

for (const [category, color] of Object.entries(categoryColors)) {
    const item = document.createElement('div');
    const key = document.createElement('span');
    key.className = 'legend-key';
    key.style.backgroundColor = color;

    const value = document.createElement('span');
    value.textContent = category;
    item.appendChild(key);
    item.appendChild(value);
    legend.appendChild(item);
}


map.on('load', () => {
    document.getElementById('map').parentNode.appendChild(legend); // Append legend to the map's parent
});
