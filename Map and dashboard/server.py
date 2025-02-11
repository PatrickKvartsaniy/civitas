from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# Database connection parameters
DB_CONFIG = {
    "host": "ep-black-sky-a2vsl2a2-pooler.eu-central-1.aws.neon.tech",
    "database": "neondb",
    "user": "neondb_owner",
    "password": "npg_jrUpozuT7g0y",
}


def fetch_geojson(table_name, geom_column="geom"):
    """Fetch data from a given table and return it as GeoJSON"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    query = f"""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON({geom_column})::json,
                    'properties', to_jsonb(t) - '{geom_column}'
                )
            )
        )
        FROM {table_name} t;
    """

    cur.execute(query)
    data = cur.fetchone()[0]

    cur.close()
    conn.close()

    return data


# --- API Endpoints for different tables ---
@app.route("/buildings_centroids")
def get_buildings():
    return jsonify(fetch_geojson("buildings_centroids_hala"))


@app.route("/buildings")
def get_roads():
    return jsonify(fetch_geojson("buildings_hala"))


@app.route("/amenities")
def get_land_parcels():
    return jsonify(fetch_geojson("amenities_hala"))


@app.route("/all_data/<table_name>")
def get_any_table(table_name):
    """Dynamic endpoint to fetch data from any table"""
    return jsonify(fetch_geojson(table_name))


if __name__ == "__main__":
    app.run(debug=True)
