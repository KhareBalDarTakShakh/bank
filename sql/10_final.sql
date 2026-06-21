DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_authenticate_customer` $$
CREATE PROCEDURE `sp_authenticate_customer`(
    IN p_username VARCHAR(50),
    IN p_password_plain VARCHAR(255)
)
BEGIN
    DECLARE v_customer_id INT;
    DECLARE v_full_name VARCHAR(255);
    DECLARE v_national_code VARCHAR(15);
    DECLARE v_password_hash VARCHAR(255);
    DECLARE v_login_status VARCHAR(10);
    DECLARE v_customer_active TINYINT(1);

    -- Look up login record and join customer table
    SELECT cl.customer_id, c.full_name, c.national_code, cl.password_hash, cl.status, c.is_active
        INTO v_customer_id, v_full_name, v_national_code, v_password_hash, v_login_status, v_customer_active
    FROM customer_login cl
    JOIN customer c ON cl.customer_id = c.id
    WHERE cl.username = p_username;

    -- Check if username exists
    IF v_customer_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username or password.';
    END IF;

    -- Check login status
    IF v_login_status != 'active' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account login is disabled. Contact support.';
    END IF;

    -- Check customer active status
    IF v_customer_active != 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer account is inactive.';
    END IF;

    -- Verify password hash
    IF v_password_hash != SHA2(p_password_plain, 256) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username or password.';
    END IF;

    -- Return customer details (no password hash)
    SELECT v_customer_id AS id,
           v_full_name AS full_name,
           v_national_code AS national_code,
           p_username AS username;
END $$
DELIMITER ;