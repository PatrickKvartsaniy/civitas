

select * from buildings_hala
limit 50
-- I use limit to get better/faster performance with the very huge count of features

--amenities table
CREATE TABLE amenities_hala AS
select * from buildings WHERE information::jsonb ? 'amenity'; 

ALTER TABLE amenities_hala
ADD COLUMN categories VARCHAR(255),
ADD COLUMN sub_categories VARCHAR(255),
ADD COLUMN name VARCHAR(255),
ADD COLUMN historical BOOLEAN,
ADD COLUMN wikipedia TEXT,
ADD COLUMN image_url TEXT;

UPDATE amenities_hala
SET categories = information::jsonb->>'amenity';

UPDATE amenities_hala
SET sub_categories = information::jsonb->>'building';

UPDATE amenities_hala
SET name = information::jsonb->>'name';

UPDATE amenities_hala
SET Website = information::jsonb->>'url';

UPDATE amenities_hala 
SET Website = COALESCE(information::jsonb->>'website', information::jsonb->>'url');

UPDATE amenities_hala
SET historical = 
    CASE 
        WHEN information::TEXT ILIKE '%historic%' THEN TRUE 
        ELSE FALSE 
    END;

UPDATE amenities_hala 
SET image_url = COALESCE(information::jsonb->>'image', information::jsonb->>'image_url');


--------------------------------------------
-- buildings_hala table
--------------------------------------------
select * from all_buildings_hala 
limit 50

-- I did some filter to get only the buildings
CREATE TABLE buildings_hala AS

SELECT *
FROM all_buildings_hala 

WHERE NOT (
information::jsonb ? 'amenity' 
OR information::jsonb ? 'historic' 
OR information::jsonb ? 'military' 
OR information::jsonb ? 'name'
OR information::jsonb ? 'content'
OR information::jsonb ? 'power'
OR information::jsonb ? 'man_made'
)
AND (information::jsonb->>'building' = 'yes' )
--------------------------------------------
-- buildings_centroids_hala table
--------------------------------------------

CREATE TABLE buildings_centroids_hala AS 
SELECT 
    id,
    osm_id, 
    information, 
    -- Add a new column with the centroid point geometry
    ST_Centroid(geometry) AS centroid_geom 
FROM buildings_hala;

