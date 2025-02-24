// Initialize Map
function initMap(container) {
    return new mapboxgl.Map({
        container: container,
        style: 'mapbox://styles/mapbox/light-v11',
        center: [14.4943068,35.8711361],
        zoom: 12
    });
}


// Function to show route
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

function createLegend(titleText, categoryColors) {
    const legend = document.createElement('div');
    legend.className = 'legend';

    const title = document.createElement('h3');
    title.textContent = titleText
    legend.appendChild(title);
    for (const [_, category] of Object.entries(categoryColors)) {
        const item = document.createElement('div');
        const key = document.createElement('span');
        key.className = 'legend-key';
        key.style.backgroundColor = category.color;

        const value = document.createElement('span');
        value.textContent = category.label;
        item.appendChild(key);
        item.appendChild(value);
        legend.appendChild(item);
    }
    return legend; // Return the legend element
}
