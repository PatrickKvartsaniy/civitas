const map = initMap('map');

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
                ['==', ['get', 'requires_maintenance'], true], window.maintenanceColors.true.color, // Color based on requires_maintenance
                window.maintenanceColors.false.color // Default color (no maintenance needed)
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
        const buildingId = properties.id;

        // Highlight selected building (improved)
        map.setPaintProperty('buildings-layer', 'fill-color', [
            'case',
            ['==', ['get', 'id'], properties.id],
            '#ff6600', // Highlight color
            [ // Restore original color
                'case',
                ['==', ['get', 'requires_maintenance'], true], window.maintenanceColors.true.color,
                window.maintenanceColors.false.color
            ]
        ]);

    const form = document.createElement('form');
    form.id = 'maintenance-form';
    form.classList.add('row', 'g-3');

    const requiresMaintenanceValue = properties.requires_maintenance;

    const img = document.createElement('img');
    img.src = `${API_URL}/buildings/${buildingId}/image`;
    img.alt = "Building Image";
    img.style.maxWidth = "100%";
    img.style.height = "auto";
    img.classList.add('mb-3');

    const spinner = document.createElement('div');
    spinner.classList.add('spinner-border', 'text-primary', 'd-flex', 'justify-content-center'); // Center the spinner
    spinner.setAttribute('role', 'status');
    spinner.innerHTML = '<span class="visually-hidden">Loading...</span>';

form.innerHTML = `
    <h4>Update Maintenance Status</h4>
    <div class="col-12">
        <label for="requires_maintenance" class="form-label">Requires Maintenance:</label>
        <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" role="switch" id="requires_maintenance" name="requires_maintenance" ${requiresMaintenanceValue ? 'checked' : ''}>
        </div>
    </div>
    <div class="col-12">
        <label for="information" class="form-label">Additional Information:</label>
        <textarea class="form-control" id="information" name="information">${properties.information || ''}</textarea>
    </div>
    <div class="col-12">
        <button type="submit" class="btn btn-primary">Update</button>
    </div>
`;
form.prepend(spinner);
form.prepend(img);

    img.onload = () => {
        spinner.remove(); // Hide spinner when image is loaded
    };

    img.onerror = () => {
        console.error("Failed to load building image.");
        img.alt = "Building image not available.";
        spinner.remove();// Hide spinner on error too
    };

        form.addEventListener('submit', (event) => {
            event.preventDefault();

            const newStatus = document.getElementById('requires_maintenance').checked;
            const additionalInfo = document.getElementById('information').value;
            updateMaintenanceStatus(buildingId, newStatus, additionalInfo);

            form.remove();
        });

        const buildingInfoDiv = document.getElementById('building-info');
        buildingInfoDiv.innerHTML = "";
        buildingInfoDiv.appendChild(form);

    });

    map.on('mouseenter', 'buildings-layer', () => {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'buildings-layer', () => {
        map.getCanvas().style.cursor = '';
    });
}

// Click event to toggle maintenance status
map.on('click', 'buildings', (e) => {
    const feature = e.features[0];
    const buildingId = feature.properties.id;
    const currentStatus = feature.properties.requires_maintenance;

    const newStatus = !currentStatus; // Toggle maintenance status

    // Open a prompt to allow updating `information`, `updated_by`, `amenity_id`
    const additionalInfo = prompt("Enter additional information:");
    const updatedBy = prompt("Your name:");

    updateMaintenanceStatus(buildingId, newStatus, additionalInfo, updatedBy);
});

// Update maintenance status in backend
function updateMaintenanceStatus(buildingId, newStatus, information) {
    fetch(`${API_URL}/buildings/${buildingId}`, {
        method: 'PATCH',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            requires_maintenance: newStatus,
            information: information,
        })
    })
        .then(response => response.json())
        .then(updatedBuilding => {
            fetchAndCacheData(addBuildingsLayer);
        })
        .catch(error => console.error("Error updating maintenance:", error));
}

map.on('load', () => {
    getCachedData().then(cachedData => {
        if (cachedData) {
            console.log("Using cached data.");
            addBuildingsLayer(cachedData);
        } else {
            console.log("Fetching fresh data.");
            fetchAndCacheData(addBuildingsLayer);
        }
    });
    const legend = createLegend("Buildings status", window.maintenanceColors); // Create the legend
    document.getElementById('map').parentNode.appendChild(legend); // Append legend
});
