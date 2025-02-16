mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;

const categoryColors = {  // Define colors for each category
    "Emergency and Public Services": "#007bff", // Blue
    "Food and Drink": "#ffc107", // Yellow
    "Community and Culture": "#28a745", // Green
    "Commercial and Financial": "#dc3545", // Red
    "Other Amenities": "#6c757d",  // Gray
};

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
    map.addSource('buildings-source', {type: 'geojson', data: geojson});

    map.addLayer({
    id: 'buildings-layer',
    type: 'fill',
    source: 'buildings-source',
    paint: {
        'fill-color': [
            'case',
            ['has', 'amenity_category'], // Check if 'amenity_category' exists
            [
                'case',
                ['has', ['get', 'amenity_category'], ['literal', categoryColors]], //Check if the amenity_category is in categoryColors
                [
                    'get', ['get', 'amenity_category'], ['literal', categoryColors] // Directly get the color
                ],
                '#888888' // Default color if no 'amenity_category' is in categoryColors
            ],
            '#888888' // Default color if no 'amenity_category'
        ],
        'fill-opacity': 0.5
    }
});

    map.addLayer({
        id: 'buildings-outline',
        type: 'line',
        source: 'buildings-source',
        paint: {'line-color': '#000', 'line-width': 1}
    });

    map.on('click', 'buildings-layer', (e) => {
        const properties = e.features[0].properties;
        displayBuildingInfo(properties);

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

function displayBuildingInfo(properties) {
    const sidebar = document.getElementById("building-info");
    sidebar.innerHTML = `<p>Loading...</p>`;

    fetch(`/buildings/${properties.id}/amenity`)
        .then(response => response.json())
        .then(data => {
            sidebar.innerHTML = ""; // Clear loading message

            Object.keys(data).forEach(key => {
                const value = data[key] || "N/A";
                const div = document.createElement("div");
                div.classList.add("property-item");

                const label = document.createElement("label");
                label.textContent = key.replace(/_/g, " ").toUpperCase();

                if (key === "information") {
                    const input = document.createElement("input");
                    input.type = "text";
                    input.value = JSON.stringify(value, null, 2);
                    input.dataset.key = key;
                    input.disabled = true;
                    input.id = "info-input";

                    const editButton = document.createElement("button");
                    editButton.textContent = "Edit";
                    editButton.onclick = () => toggleEdit(input, editButton);

                    const saveButton = document.createElement("button");
                    saveButton.textContent = "Save";
                    saveButton.onclick = () => saveBuildingInfo(properties.id, input);
                    saveButton.style.display = "none";

                    div.appendChild(label);
                    div.appendChild(input);
                    div.appendChild(editButton);
                    div.appendChild(saveButton);
                } else {
                    const span = document.createElement("span");
                    span.textContent = value;
                    div.appendChild(label);
                    div.appendChild(span);
                }
                sidebar.appendChild(div);
            });

            // Find closest restaurant button
            const restaurantButton = document.createElement("button");
            restaurantButton.textContent = "Find Closest Restaurant";
            restaurantButton.onclick = () => findClosestRestaurant(properties);
            sidebar.appendChild(restaurantButton);
        })
        .catch(error => {
            console.error("Error fetching building amenities:", error);
            sidebar.innerHTML = `<p>Error loading building info.</p>`;
        });
}

function saveBuildingInfo(buildingId, input) {
    try {
        const updatedInfo = JSON.parse(input.value);

        fetch(`/buildings/${buildingId}/amenity`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({information: updatedInfo})
        })
            .then(response => {
                if (!response.ok) throw new Error("Failed to save");
                alert("Changes saved successfully!");
            })
            .catch(error => {
                console.error("Save error:", error);
                alert("Error saving changes.");
            });
    } catch (error) {
        alert("Invalid JSON format");
    }
}

function toggleEdit(input, button) {
    input.disabled = !input.disabled;
    button.nextElementSibling.style.display = input.disabled ? "none" : "block";
    button.textContent = input.disabled ? "Edit" : "Cancel";
}

function findClosestRestaurant(properties) {
    const lat = properties.latitude || 35.9052445; // Use actual property or fallback
    const lon = properties.longitude || 14.4551924;

    fetch(`https://your-api.com/closest-restaurant?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            alert(`Closest restaurant: ${data.name}, Distance: ${data.distance}m, Time: ${data.time}min`);
            showRoute([lon, lat], [data.lon, data.lat]);
        })
        .catch(error => console.error("Error fetching restaurant:", error));
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
