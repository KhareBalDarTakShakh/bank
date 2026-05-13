DELIMITER $$

-- 1. Register a new customer (checks duplicate national_code)
DROP PROCEDURE IF EXISTS `sp_register_customer` $$
CREATE PROCEDURE `sp_register_customer`(
    IN p_full_name VARCHAR(255),
    IN p_national_code VARCHAR(15),
    IN p_phone_number VARCHAR(15),
    IN p_address TEXT,
    IN p_registered_by INT
)
BEGIN
    DECLARE existing_id INT DEFAULT NULL;
    DECLARE new_id INT;

    SELECT id INTO existing_id FROM customer WHERE national_code = p_national_code LIMIT 1;
    IF existing_id IS NOT NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A customer with this national code already exists.';
    END IF;

    INSERT INTO customer (full_name, national_code, phone_number, address, registered_by)
    VALUES (p_full_name, p_national_code, p_phone_number, p_address, p_registered_by);

    SET new_id = LAST_INSERT_ID();
    SELECT new_id AS new_customer_id;
END $$

-- 2. Search customers (by national code or partial name)
DROP PROCEDURE IF EXISTS `sp_search_customers` $$
CREATE PROCEDURE `sp_search_customers`(IN p_query VARCHAR(255))
BEGIN
    IF p_query IS NULL OR p_query = '' THEN
        SELECT id, full_name, national_code, phone_number, is_active
        FROM customer
        ORDER BY id DESC
        LIMIT 100;
    ELSE
        SELECT id, full_name, national_code, phone_number, is_active
        FROM customer
        WHERE national_code = p_query
           OR full_name LIKE CONCAT('%', p_query, '%')
        ORDER BY id DESC
        LIMIT 100;
    END IF;
END $$

-- 3. Get a single customer's details
DROP PROCEDURE IF EXISTS `sp_get_customer_by_id` $$
CREATE PROCEDURE `sp_get_customer_by_id`(IN p_customer_id INT)
BEGIN
    SELECT id, full_name, national_code, phone_number, address, is_active
    FROM customer
    WHERE id = p_customer_id;
END $$

-- 4. Update customer information (including soft delete/restore)
DROP PROCEDURE IF EXISTS `sp_update_customer` $$
CREATE PROCEDURE `sp_update_customer`(
    IN p_customer_id INT,
    IN p_full_name VARCHAR(255),
    IN p_phone_number VARCHAR(15),
    IN p_address TEXT,
    IN p_is_active TINYINT(1)
)
BEGIN
    UPDATE customer
    SET full_name = p_full_name,
        phone_number = p_phone_number,
        address = p_address,
        is_active = p_is_active
    WHERE id = p_customer_id;
END $$

-- 5. Get accounts belonging to a customer (with account type name)
DROP PROCEDURE IF EXISTS `sp_get_accounts_by_customer` $$
CREATE PROCEDURE `sp_get_accounts_by_customer`(IN p_customer_id INT)
BEGIN
    SELECT a.id, a.account_number, at.name AS account_type_name,
           a.balance, a.status, a.opening_date
    FROM account a
    JOIN account_type at ON a.account_type_id = at.id
    WHERE a.customer_id = p_customer_id
    ORDER BY a.id;
END $$

-- 6. Get cards belonging to a specific account
DROP PROCEDURE IF EXISTS `sp_get_cards_by_account` $$
CREATE PROCEDURE `sp_get_cards_by_account`(IN p_account_id INT)
BEGIN
    SELECT id, card_number, cvv2, expiry_date, status, issued_at
    FROM card
    WHERE account_id = p_account_id
    ORDER BY id;
END $$

-- 7. Open a new account for a customer
-- sp_open_account (returns new account id via SELECT)
DROP PROCEDURE IF EXISTS `sp_open_account` $$
CREATE PROCEDURE `sp_open_account`(
    IN p_customer_id INT,
    IN p_account_type_id INT,
    IN p_initial_balance DECIMAL(15,2),
    IN p_opened_by INT
)
BEGIN
    DECLARE v_account_count INT DEFAULT 0;
    DECLARE v_customer_active TINYINT(1);
    DECLARE v_account_number VARCHAR(16);
    DECLARE v_exists INT DEFAULT 1;
    DECLARE new_id INT;

    SELECT is_active INTO v_customer_active FROM customer WHERE id = p_customer_id;
    IF v_customer_active IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer not found.';
    END IF;
    IF v_customer_active = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot open account for inactive customer.';
    END IF;

    SELECT COUNT(*) INTO v_account_count FROM account WHERE customer_id = p_customer_id;
    IF v_account_count >= 5 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Maximum number of accounts (5) reached for this customer.';
    END IF;

    WHILE v_exists > 0 DO
        SET v_account_number = LPAD(FLOOR(RAND() * 10000000000000000), 16, '0');
        SELECT COUNT(*) INTO v_exists FROM account WHERE account_number = v_account_number;
    END WHILE;

    INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status)
    VALUES (v_account_number, p_customer_id, p_account_type_id, p_initial_balance, p_opened_by, CURDATE(), 'active');

    SET new_id = LAST_INSERT_ID();
    SELECT new_id AS new_account_id;
END $$

-- sp_issue_card (returns new card id via SELECT)
DROP PROCEDURE IF EXISTS `sp_issue_card` $$
CREATE PROCEDURE `sp_issue_card`(IN p_account_id INT)
BEGIN
    DECLARE v_card_number VARCHAR(16);
    DECLARE v_cvv2 VARCHAR(3);
    DECLARE v_exists INT DEFAULT 1;
    DECLARE new_id INT;

    WHILE v_exists > 0 DO
        SET v_card_number = LPAD(FLOOR(RAND() * 10000000000000000), 16, '0');
        SELECT COUNT(*) INTO v_exists FROM card WHERE card_number = v_card_number;
    END WHILE;

    SET v_cvv2 = LPAD(FLOOR(RAND() * 1000), 3, '0');

    INSERT INTO card (account_id, card_number, cvv2, expiry_date, status, issued_at)
    VALUES (p_account_id, v_card_number, v_cvv2, DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW());

    SET new_id = LAST_INSERT_ID();
    SELECT new_id AS new_card_id, v_card_number AS card_number, v_cvv2 AS cvv2;
END $$

DELIMITER ;