--------- why I made separate layers of buidings ----------
-- for better performance in pgadmin (to have a layer with less count of feature)
-- will be be easier in visualization 
-- I gave it the name followed by _hala so you can know who to ask in case you wanna inquire about something.
-- I didn't change the original layers to not interrupt your work.

--------- why I did not use the information field as a ditionary ----------
-- to reduce the time of making sql quries every time I want to get a spesific value
-- to will be complex to make some kinds of statitics on data we get by a query, also hard to verify the results
-- separating the values out of information field will make it easier to calculate statistics in dashboard

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