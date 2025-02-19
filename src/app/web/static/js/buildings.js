const defaultColor = '#888888';
const selectedBuildingColor = '#ff0000'; // Highlight color for selected buildings
const categoryColors = window.categoryColors || {}; // Ensure categoryColors is defined

let selectedBuildingId = null; // Store the selected building ID

function addBuildingsLayer(geojson) {
    if (map.getSource('buildings-source')) {
        map.getSource('buildings-source').setData(geojson);
        return;
    }

    map.addSource('buildings-source', { type: 'geojson', data: geojson });

    // Set map pitch for 3D effect
    map.easeTo({ pitch: 60, bearing: -20 });

    // Add 3D buildings layer
    map.addLayer({
        id: 'buildings-layer',
        type: 'fill-extrusion',
        source: 'buildings-source',
        paint: {
            'fill-extrusion-color': [
                'case',
                ['==', ['get', 'id'], ['literal', selectedBuildingId]], selectedBuildingColor, // Highlight selected
                ['match',
                    ['get', 'amenity_category'],
                    ...Object.entries(categoryColors).flatMap(([key, value]) => [key, value.color]),
                    defaultColor
                ]
            ],
            'fill-extrusion-height': ['get', 'height'], // Use building height from GeoJSON
            'fill-extrusion-base': 0,
            'fill-extrusion-opacity': 0.8
        }
    });

    map.on('click', 'buildings-layer', (e) => {
        const properties = e.features[0].properties;
        selectBuilding(properties.id);
        displayBuildingInfo(properties);
    });

    map.on('mouseenter', 'buildings-layer', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'buildings-layer', () => {
        map.getCanvas().style.cursor = '';
    });
}


function selectBuilding(buildingId) {
    selectedBuildingId = buildingId;
    map.setPaintProperty('buildings-layer', 'fill-color', [
        'case',
        ['==', ['get', 'id'], ['literal', selectedBuildingId]], selectedBuildingColor, // Highlight selected
        ['match',
            ['get', 'amenity_category'],
            ...Object.entries(categoryColors).flatMap(([key, value]) => [key, value.color]),
            defaultColor
        ]
    ]);
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
                button.textContent = `Find Closest ${categoryColors[cat].label}`;
                button.onclick = () => findClosestAmenity(properties, cat);
                sidebar.appendChild(button);
            }
        });

    } else {
        fetch(`/buildings/${properties.id}/amenity`)
            .then(response => response.json())
            .then(data => {
                sidebar.innerHTML = `<h3>${category}</h3>`;

                Object.keys(data).forEach(key => {
                    const value = data[key] || "N/A";
                    const div = document.createElement("div");
                    div.classList.add("property-item");

                    const label = document.createElement("label");
                    label.textContent = key.replace(/_/g, " ").toUpperCase();

                    if (key === "information") {
                        const input = document.createElement("textarea");
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
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ information: updatedInfo })
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
