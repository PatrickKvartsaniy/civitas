import psycopg2, geopandas as gpd, folium, mapclassify
from matplotlib import pyplot as plt
conn = psycopg2.connect(
    host="ep-black-sky-a2vsl2a2-pooler.eu-central-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_jrUpozuT7g0y"
)
"""
cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone())

cursor.close()
conn.close()
"""
print(conn)


