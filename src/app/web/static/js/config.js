mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;

window.categoryColors = {
    "Emergency and Public Services": {
        color: "#007bff",
        label: "Public Services",
        icon: "bi-shield-exclamation"
    },
    "Food and Drink": {
        color: "#ffc107",
        label: "Food and Drink",
        icon: "bi-cup-straw"
    },
    "Community and Culture": {
        color: "#28a745",
        label: "Community and Culture",
        icon: "bi-people"
    },
    "Commercial and Financial": {
        color: "#dc3545",
        label: "Commercial and Financial",
        icon: "bi-bank"
    },
    "Residential": {
        color: "#17a2b8",
        label: "Residential",
        icon: "bi-house"
    },
    "Other Amenities": {
        color: "#6f42c1",
        label: "Other Amenities",
        icon: "bi-map"
    }
};

window.maintenanceColors = {
    true: {
        color: '#FF0000',
        label: "Needs Maintenance",
        icon: "bi-tools"
    },
    false: {
        color: '#00FF00',
        label: "Good Condition",
        icon: "bi-check-circle"
    }
};
