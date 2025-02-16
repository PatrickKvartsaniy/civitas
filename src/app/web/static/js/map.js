mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v12',
    center: [14.4551924, 35.9052445],
    zoom: 10
});

function addBuildingsLayer(geojson) {
    if (map.getSource('buildings-source')) {
        map.getSource('buildings-source').setData(geojson);
        return;
    }

    map.addSource('buildings-source', { type: 'geojson', data: geojson });

    map.addLayer({
        id: 'buildings-layer',
        type: 'fill',
        source: 'buildings-source',
        paint: { 'fill-color': '#888888', 'fill-opacity': 0.5 }
    });

    map.addLayer({
        id: 'buildings-outline',
        type: 'line',
        source: 'buildings-source',
        paint: { 'line-color': '#000', 'line-width': 1 }
    });

    map.on('click', 'buildings-layer', (e) => {
        const properties = e.features[0].properties;
        document.getElementById("building-info").innerHTML = `
            <strong>Building ID:</strong> ${properties.id || 'N/A'}<br>
            <strong>Name:</strong> ${properties.name || 'Unknown'}
        `;

        map.setPaintProperty('buildings-layer', 'fill-color', [
            'case',
            ['==', ['get', 'id'], properties.id],
            '#ff6600',
            '#888888'
        ]);
    });

    map.on('mouseenter', 'buildings-layer', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'buildings-layer', () => {
        map.getCanvas().style.cursor = '';
    });
}

getCachedData().then(cachedData => {
    if (cachedData) {
        console.log("Using cached data.");
        console.log(cachedData);
        addBuildingsLayer(cachedData);
    } else {
        console.log("Fetching fresh data.");
        fetchAndCacheData(addBuildingsLayer);
    }
});
