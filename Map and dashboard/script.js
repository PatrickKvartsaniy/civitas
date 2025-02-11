const { Client } = require('pg');

// Database connection configuration
const client = new Client({
    user: 'your_username',
    host: 'your_host',
    database: 'your_database',
    password: 'your_password',
    port: 5432, // Default PostgreSQL port
});

async function fetchCentroids() {
    try {
        await client.connect(); // Connect to the database

        // SQL query to retrieve centroid data as GeoJSON
        const query = `
            SELECT id, name, height, ST_AsGeoJSON(centroid_geom) AS centroid
            FROM buildings_hala_centroids;
        `;

        const res = await client.query(query);

        // Format and print the results
        const centroids = res.rows.map(row => ({
            id: row.id,
            name: row.name,
            height: row.height,
            centroid: JSON.parse(row.centroid) // Convert GeoJSON string to object
        }));

        console.log(centroids);

        return centroids;
    } catch (err) {
        console.error('Error executing query:', err);
    } finally {
        await client.end(); // Close the database connection
    }
}

// Execute the function
fetchCentroids();
