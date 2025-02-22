const map = initMap('map');

let popup; // Global variable to store popup reference
let selectedBuildingId = null; // Store the selected building ID

const defaultColor = '#888888';
const selectedBuildingColor = '#ff0000'; // Highlight color for selected buildings
const categoryColors = window.categoryColors || {}; // Ensure categoryColors is defined

function findClosestAmenity(buildingId, category) {
    fetch(`${API_URL}/buildings/${buildingId}/closest/${encodeURIComponent(category)}`)
        .then(response => response.json())
        .then(data => {
            if (!data || !data.amenity || !data.route) {
                throw new Error('Invalid data format received');
            }
            let amenity = JSON.parse(data.amenity);
            if (popup) popup.remove();
            console.log(amenity.geometry)
            popup = new mapboxgl.Popup()
                .setLngLat(amenity.geometry.coordinates)
                .setHTML(`
                    <strong>Closest ${category}:</strong> ${amenity.properties.name || 'Unknown'}<br>
                    <strong>Distance:</strong> ${data.route.distance}m<br>
                    <strong>Time:</strong> ${Math.floor(data.route.duration / 60)} min walking
                `)
                .addTo(map);

            showRoute(data.route.geometry);
            highlightDestination(amenity);
        })
        .catch(error => console.error(`Error fetching closest ${category}:`, error));
}

function highlightDestination(amenity) {
    if (map.getSource('destination-point')) {
        map.getSource('destination-point').setData(amenity);
    } else {
        map.addSource('destination-point', {
            type: 'geojson',
            data: amenity
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


function selectBuilding(buildingId) {
    if (!map.getLayer('buildings-layer')) return;

    selectedBuildingId = buildingId;
    map.setPaintProperty('buildings-layer', 'fill-extrusion-color', [
        'case',
        ['==', ['get', 'id'], ['literal', selectedBuildingId]], selectedBuildingColor,
        ['match',
            ['get', 'amenity_category'],
            ...Object.entries(categoryColors).flatMap(([key, value]) => [key, value.color]),
            defaultColor
        ]
    ]);
}


function displayBuildingInfo(properties) {
    const sidebar = document.getElementById("building-info");
    sidebar.innerHTML = `<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div>`;

    const category = properties.amenity_category || "Unknown";
    const isResidential = category === "Residential";

    let content = `
        <div class="card shadow">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0"><i class="bi bi-building"></i> ${category}</h5>
                <button type="button" class="btn-close" aria-label="Close" onclick="closeBuildingInfo()"></button>
            </div>
            <div class="card-body">
                <p><strong><i class="bi bi-key"></i> Building ID:</strong> ${properties.id}</p>
    `;

    if (isResidential) {
        content += `<h6 class="mt-3"><i class="bi bi-geo-alt"></i> Find Closest Amenities</h6>
                    <div class="d-grid gap-2">`;

        Object.keys(categoryColors).forEach(cat => {
            if (cat !== "Residential") {
                content += `<button class="btn btn-outline-primary find-closest-btn" data-category="${cat}">
                    <i class="bi bi-search"></i> Find Closest ${categoryColors[cat].label}
                </button>`;
            }
        });

        content += `</div></div>`;
        sidebar.innerHTML = content;

        const buttons = sidebar.querySelectorAll('.find-closest-btn');  // Select all the buttons
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                const category = button.dataset.category;
                findClosestAmenity(properties.id, category);
            });
        });
    } else {
        fetch(`${API_URL}/buildings/${properties.id}/amenity`)
            .then(response => response.json())
            .then(data => {
                content += `<div class="accordion" id="amenityAccordion">`;
                Object.keys(data).forEach((key, index) => {
                    content += `
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="heading-${index}">
                                <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${index}">
                                    <i class="bi bi-info-circle"></i> ${key.replace(/_/g, " ").toUpperCase()}
                                </button>
                            </h2>
                            <div id="collapse-${index}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}">
                                <div class="accordion-body">
                                    <p>${data[key] || "N/A"}</p>
                                </div>
                            </div>
                        </div>`;
                });
                content += `</div></div>`;
                sidebar.innerHTML = content;
            })
            .catch(error => {
                console.error("Error fetching building amenities:", error);
                sidebar.innerHTML = `<div class="alert alert-danger"><i class="bi bi-exclamation-triangle"></i> Error loading building info.</div>`;
            });
    }
}

// Close building info
function closeBuildingInfo() {
    document.getElementById("building-info").innerHTML = "";
}

function addBuildingsLayer(geojson) {
    map.on('load', () => {  // Ensure map is fully loaded
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
            'fill-extrusion-height': ['get', 'height'],
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
    })
}


getCachedData().then(cachedData => {
    if (cachedData) {
        addBuildingsLayer(cachedData);
    }
    else {
        console.log("Fetching fresh data.");
        fetchAndCacheData(addBuildingsLayer);
    }
});

map.on('load', () => {
    const legend = createLegend("Buildings function", window.categoryColors); // Create the legend
    document.getElementById('map').parentNode.appendChild(legend); // Append legend
});
