DELIMITER $$

-- Prevent inserting a headquarters if one already exists in the province
CREATE TRIGGER `trg_prevent_multiple_hq_per_province`
BEFORE INSERT ON `branch`
FOR EACH ROW
BEGIN
    DECLARE hq_count INT DEFAULT 0;
    IF NEW.is_headquarter = 1 THEN
        SELECT COUNT(*) INTO hq_count
        FROM branch b
        JOIN city c ON b.city_id = c.id
        WHERE c.province_id = (SELECT province_id FROM city WHERE id = NEW.city_id)
          AND b.is_headquarter = 1;
        IF hq_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A headquarter already exists in this province.';
        END IF;
    END IF;
END$$

-- Prevent updating a branch to headquarters if another already exists in the province
CREATE TRIGGER `trg_prevent_multiple_hq_per_province_update`
BEFORE UPDATE ON `branch`
FOR EACH ROW
BEGIN
    DECLARE hq_count INT DEFAULT 0;
    IF NEW.is_headquarter = 1 AND (OLD.is_headquarter = 0 OR NEW.city_id != OLD.city_id) THEN
        SELECT COUNT(*) INTO hq_count
        FROM branch b
        JOIN city c ON b.city_id = c.id
        WHERE c.province_id = (SELECT province_id FROM city WHERE id = NEW.city_id)
          AND b.is_headquarter = 1
          AND b.id != NEW.id;
        IF hq_count > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'A headquarter already exists in this province.';
        END IF;
    END IF;
END$$

DELIMITER ;