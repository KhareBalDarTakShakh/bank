DELIMITER $$

-- ============================================================
-- COUNTRY MANAGEMENT
-- ============================================================
CREATE PROCEDURE `sp_get_all_countries`()
BEGIN
    SELECT id, name, iso_code FROM country ORDER BY name;
END$$

CREATE PROCEDURE `sp_get_country_by_id`(IN p_id INT)
BEGIN
    SELECT id, name, iso_code FROM country WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_insert_country`(
    IN p_name VARCHAR(255),
    IN p_iso_code CHAR(2)
)
BEGIN
    INSERT INTO country (name, iso_code) VALUES (p_name, p_iso_code);
END$$

CREATE PROCEDURE `sp_update_country`(
    IN p_id INT,
    IN p_name VARCHAR(255),
    IN p_iso_code CHAR(2)
)
BEGIN
    UPDATE country SET name = p_name, iso_code = p_iso_code WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_delete_country`(IN p_id INT)
BEGIN
    DELETE FROM country WHERE id = p_id;
END$$

-- ============================================================
-- PROVINCE MANAGEMENT
-- ============================================================
CREATE PROCEDURE `sp_get_all_provinces`()
BEGIN
    SELECT p.id, p.name, p.country_id, c.name AS country_name
    FROM province p
    JOIN country c ON p.country_id = c.id
    ORDER BY c.name, p.name;
END$$

CREATE PROCEDURE `sp_get_province_by_id`(IN p_id INT)
BEGIN
    SELECT id, name, country_id FROM province WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_insert_province`(
    IN p_name VARCHAR(255),
    IN p_country_id INT
)
BEGIN
    INSERT INTO province (name, country_id) VALUES (p_name, p_country_id);
END$$

CREATE PROCEDURE `sp_update_province`(
    IN p_id INT,
    IN p_name VARCHAR(255),
    IN p_country_id INT
)
BEGIN
    UPDATE province SET name = p_name, country_id = p_country_id WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_delete_province`(IN p_id INT)
BEGIN
    DELETE FROM province WHERE id = p_id;
END$$

-- ============================================================
-- CITY MANAGEMENT
-- ============================================================
CREATE PROCEDURE `sp_get_all_cities`()
BEGIN
    SELECT c.id, c.name, c.province_id, p.name AS province_name,
           p.country_id, co.name AS country_name
    FROM city c
    JOIN province p ON c.province_id = p.id
    JOIN country co ON p.country_id = co.id
    ORDER BY co.name, p.name, c.name;
END$$

CREATE PROCEDURE `sp_get_city_by_id`(IN p_id INT)
BEGIN
    SELECT id, name, province_id FROM city WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_insert_city`(
    IN p_name VARCHAR(255),
    IN p_province_id INT
)
BEGIN
    INSERT INTO city (name, province_id) VALUES (p_name, p_province_id);
END$$

CREATE PROCEDURE `sp_update_city`(
    IN p_id INT,
    IN p_name VARCHAR(255),
    IN p_province_id INT
)
BEGIN
    UPDATE city SET name = p_name, province_id = p_province_id WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_delete_city`(IN p_id INT)
BEGIN
    DELETE FROM city WHERE id = p_id;
END$$

DELIMITER ;