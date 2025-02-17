const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [14.4551924, 35.9052445],
    zoom: 10
});

function findClosestAmenity(properties, category) {
    fetch(API_URL + `/buildings/${properties.id}/closest/${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            alert(`Closest ${category}: ${data.amenity.name}, Distance: ${data.route.distance}m, Time: ${data.route.duration}min walking`);
            showRoute(data.route.geometry);
        })
        .catch(error => console.error(`Error fetching closest ${category}:`, error));
}

function showRoute(geometry) {
    if (typeof geometry === "string") {
        geometry = JSON.parse(geometry);
    }
    if (map.getLayer('route')) {
        map.removeLayer('route');
        map.removeSource('route');
    }

    map.addSource('route', {
        type: 'geojson',
        data: {
            type: 'Feature',
            geometry: geometry
        }
    });

    map.addLayer({
        id: 'route',
        type: 'line',
        source: 'route',
        paint: { 'line-color': '#ff0000', 'line-width': 3 }
    });
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
