// Set your Mapbox token
mapboxgl.accessToken = 'pk.eyJ1IjoicGV0cm8ta3ZhcnRzaWFueWkiLCJhIjoiY202ejdiMmlkMDI1ODJwc2s4NTIxeWc4dSJ9.-k0IrJNRzERdc-Qgsl_ovA'; // Replace with your token

// Initialize the map
const map = new mapboxgl.Map({
  container: 'map', // Container ID
  style: 'mapbox://styles/mapbox/streets-v12', // Map style
  center: [14.5146, 35.8989], // Malta's coordinates [lng, lat]
  zoom: 15, // Starting zoom level
  pitch: 45, // Tilt the map for 3D effect
  bearing: -17.6, // Rotate the map
});

// Add 3D buildings layer
map.on('load', () => {
  map.addLayer({
    id: '3d-buildings',
    source: 'composite',
    'source-layer': 'building',
    filter: ['==', 'extrude', 'true'],
    type: 'fill-extrusion',
    minzoom: 15,
    paint: {
      'fill-extrusion-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], // Check if the building is selected
        '#00ff00', // Selected color (green)
        '#aaa', // Default color
      ],
      'fill-extrusion-height': [
        'interpolate',
        ['linear'],
        ['zoom'],
        15,
        0,
        15.05,
        ['get', 'height'],
      ],
      'fill-extrusion-base': [
        'interpolate',
        ['linear'],
        ['zoom'],
        15,
        0,
        15.05,
        ['get', 'min_height'],
      ],
      'fill-extrusion-opacity': 0.6,
    },
  });

  let selectedBuildingId = null;

  // Add interactivity
  map.on('click', '3d-buildings', (e) => {
    // Reset previously selected building
    if (selectedBuildingId !== null) {
      map.setFeatureState(
        { source: 'composite', sourceLayer: 'building', id: selectedBuildingId },
        { selected: false }
      );
    }

    // Get clicked building's ID
    const clickedBuildingId = e.features[0].id;

    // Highlight the clicked building
    map.setFeatureState(
      { source: 'composite', sourceLayer: 'building', id: clickedBuildingId },
      { selected: true }
    );

    // Update the selected building ID
    selectedBuildingId = clickedBuildingId;

    // Get clicked building's properties
    const properties = e.features[0].properties;

    // Get coordinates
    const lng = e.lngLat.lng.toFixed(5);
    const lat = e.lngLat.lat.toFixed(5);

    // Update the coordinates panel in the HTML
    document.getElementById("coordinates").innerHTML = `Longitude: ${lng}, Latitude: ${lat}`;

    // Create a popup
    new mapboxgl.Popup()
      .setLngLat(e.lngLat) // Set popup position to the clicked location
      .setHTML(`
        <h3>Building Info</h3>
        <p>Height: ${properties.height || 'N/A'} meters</p>
        <p>Min Height: ${properties.min_height || 'N/A'} meters</p>
        <p>Coordinates: ${lng}, ${lat}</p>
      `)
      .addTo(map);
  });

  // Change cursor to pointer when hovering over buildings
  map.on('mouseenter', '3d-buildings', () => {
    map.getCanvas().style.cursor = 'pointer';
  });

  // Change cursor back to default when not hovering over buildings
  map.on('mouseleave', '3d-buildings', () => {
    map.getCanvas().style.cursor = '';
  });
});
