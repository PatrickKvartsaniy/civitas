const map = initMap('map');

function addMaintenanceBuildingsLayer(geojson) {
    if (map.getSource('buildings-source')) {
        map.getSource('buildings-source').setData(geojson);
        return;
    }
    map.addSource('buildings-source', { type: 'geojson', data: geojson });

    map.easeTo({ pitch: 60, bearing: -20 });

    // 3D Extrusion Layer for Buildings
    map.addLayer({
        id: 'buildings-layer',
        type: 'fill-extrusion',
        source: 'buildings-source',
        paint: {
            'fill-extrusion-color': [
                'case',
                ['==', ['get', 'requires_maintenance'], true], window.maintenanceColors.true.color,
                window.maintenanceColors.false.color
            ],
            'fill-extrusion-opacity': 0.7,
            'fill-extrusion-height': ['get', 'height'], // Ensure height is available in GeoJSON properties
            'fill-extrusion-base': 0
        }
    });

    // Outline for better visibility
    map.addLayer({
        id: 'buildings-outline',
        type: 'line',
        source: 'buildings-source',
        paint: { 'line-color': '#000', 'line-width': 1 }
    });

    // Click event to highlight a building
    map.on('click', 'buildings-layer', (e) => {
        const properties = e.features[0].properties;
        const buildingId = properties.id;

        map.setPaintProperty('buildings-layer', 'fill-extrusion-color', [
            'case',
            ['==', ['get', 'id'], properties.id],
            '#ff6600',
            [
                'case',
                ['==', ['get', 'requires_maintenance'], true], window.maintenanceColors.true.color,
                window.maintenanceColors.false.color
            ]
        ]);

        const maintenance = window.maintenanceColors[properties.requires_maintenance];
        const content = `
            <p><strong><i class="bi ${maintenance.icon}"></i> Maintenance:</strong>
            <span class="badge text-white" style="background-color: ${maintenance.color};">
                ${maintenance.label}
            </span></p>
        `;

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
        spinner.classList.add('spinner-border', 'text-primary', 'd-flex', 'justify-content-center');
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

        img.onload = () => { spinner.remove(); };
        img.onerror = () => {
            console.error("Failed to load building image.");
            img.alt = "Building image not available.";
            spinner.remove();
        };

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            const newStatus = document.getElementById('requires_maintenance').checked;
            const additionalInfo = document.getElementById('information').value;
            updateMaintenanceStatus(buildingId, newStatus, additionalInfo);
            form.remove();
        });

        const buildingInfoDiv = document.getElementById('building-info');
        buildingInfoDiv.innerHTML = content;
        buildingInfoDiv.appendChild(form);
    });

    map.on('mouseenter', 'buildings-layer', () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'buildings-layer', () => { map.getCanvas().style.cursor = ''; });
}

// Add Mapbox Terrain for better 3D effect
map.on('load', () => {
    map.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
        tileSize: 512,
        maxzoom: 14
    });
    map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });

    getCachedData().then(cachedData => {
        if (cachedData) {
            addMaintenanceBuildingsLayer(cachedData);
        } else {
            console.log("Fetching fresh data.");
            fetchAndCacheData(addMaintenanceBuildingsLayer);
        }
    });

    const legend = createLegend("Buildings status", window.maintenanceColors);
    document.getElementById('map').parentNode.appendChild(legend);
});
