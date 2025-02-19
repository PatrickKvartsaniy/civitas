const map = initMap('map');

let popup; // Global variable to store popup reference

function findClosestAmenity(properties, category) {
    fetch(API_URL + `/buildings/${properties.id}/closest/${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);

            // Remove previous popup if it exists
            if (popup) popup.remove();

            // Show a new popup at the amenity location
            popup = new mapboxgl.Popup()
                .setLngLat(data.amenity.geometry.coordinates)
                .setHTML(`
                    <strong>Closest ${category}:</strong> ${data.amenity.properties.name}<br>
                    <strong>Distance:</strong> ${data.route.distance}m<br>
                    <strong>Time:</strong> ${Math.floor(data.route.duration / 60)} min walking
                `)
                .addTo(map);

            showRoute(data.route.geometry);

            highlightDestination(data.amenity.geometry.coordinates);
        })
        .catch(error => console.error(`Error fetching closest ${category}:`, error));
}

function highlightDestination(coordinates) {
    if (map.getSource('destination-point')) {
        map.getSource('destination-point').setData({
            type: 'FeatureCollection',
            features: [{ type: 'Feature', geometry: { type: 'Point', coordinates } }]
        });
    } else {
        map.addSource('destination-point', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: [{ type: 'Feature', geometry: { type: 'Point', coordinates } }]
            }
        });

        map.addLayer({
            id: 'destination-layer',
            type: 'circle',
            source: 'destination-point',
            paint: {
                'circle-radius': 8,
                'circle-color': '#ff0000',
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff'
            }
        });
    }
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

map.on('load', () => {
    const legend = createLegend("Buildings function", window.categoryColors); // Create the legend
    document.getElementById('map').parentNode.appendChild(legend); // Append legend
});
