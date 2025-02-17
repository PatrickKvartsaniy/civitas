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
            '#ff6600', // Highlight selected building
            [
                'case',
                ['has', 'amenity_category'], // Check if 'amenity_category' exists
                [
                    'case',
                    ['has', ['get', 'amenity_category'], ['literal', categoryColors]], // Check if in categoryColors
                    ['get', ['get', 'amenity_category'], ['literal', categoryColors]], // Get category color
                    '#888888' // Default if category not in categoryColors
                ],
                '#888888' // Default if no 'amenity_category'
            ]
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

    const category = properties.amenity_category || "Unknown";

    if (category === "Residential") {
        sidebar.innerHTML = "<h3>Residential Building</h3>";

        Object.keys(categoryColors).forEach(cat => {
            if (cat !== "Residential") {
                const button = document.createElement("button");
                button.textContent = `Find Closest ${cat}`;
                button.onclick = () => findClosestAmenity(properties, cat);
                sidebar.appendChild(button);
            }
        });

    } else {
        // Fetch amenity details if not a residential building
        fetch(`/buildings/${properties.id}/amenity`)
            .then(response => response.json())
            .then(data => {
                sidebar.innerHTML = `<h3>${category}</h3>`; // Show category name

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
            })
            .catch(error => {
                console.error("Error fetching building amenities:", error);
                sidebar.innerHTML = `<p>Error loading building info.</p>`;
            });
    }
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
