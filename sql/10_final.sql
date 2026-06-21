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

-- Replace province summary view
CREATE OR REPLACE VIEW `vw_province_summary` AS
SELECT
    p.id AS province_id,
    p.name AS province_name,
    COUNT(DISTINCT b.id) AS branch_count,
    COUNT(DISTINCT a.id) AS active_accounts,
    COALESCE(SUM(a.balance), 0) AS total_deposits,
    COALESCE(SUM(CASE WHEN lr.status = 'approved' THEN lr.amount ELSE 0 END), 0) AS total_loans,
    COALESCE(SUM(CASE WHEN t.transaction_type = 'withdrawal' THEN t.amount ELSE 0 END), 0) AS total_withdrawals,
    COUNT(DISTINCT t.id) AS total_transactions
FROM province p
JOIN city c ON c.province_id = p.id
JOIN branch b ON b.city_id = c.id
LEFT JOIN employee e ON e.branch_id = b.id
LEFT JOIN account a ON a.openend_by = e.id AND a.status = 'active'
LEFT JOIN loan_request lr ON lr.customer_id IN (
    SELECT a2.customer_id FROM account a2 WHERE a2.openend_by = e.id
) AND lr.status = 'approved'
LEFT JOIN `transaction` t ON t.created_by = e.id
GROUP BY p.id, p.name
ORDER BY p.name;

-- Replace per‑branch performance procedure
DROP PROCEDURE IF EXISTS `sp_get_branch_performance_by_province` $$
CREATE PROCEDURE `sp_get_branch_performance_by_province`(IN p_province_id INT)
BEGIN
    SELECT
        b.id AS branch_id,
        b.name AS branch_name,
        COUNT(DISTINCT a.id) AS active_accounts,
        COALESCE(SUM(a.balance), 0) AS total_deposits,
        COALESCE(SUM(CASE WHEN lr.status = 'approved' THEN lr.amount ELSE 0 END), 0) AS total_loans,
        COALESCE(SUM(CASE WHEN t.transaction_type = 'withdrawal' THEN t.amount ELSE 0 END), 0) AS total_withdrawals,
        COUNT(DISTINCT t.id) AS transaction_count
    FROM branch b
    JOIN city c ON b.city_id = c.id
    LEFT JOIN employee e ON e.branch_id = b.id
    LEFT JOIN account a ON a.openend_by = e.id AND a.status = 'active'
    LEFT JOIN loan_request lr ON lr.customer_id IN (
        SELECT a2.customer_id FROM account a2 WHERE a2.openend_by = e.id
    ) AND lr.status = 'approved'
    LEFT JOIN `transaction` t ON t.created_by = e.id
    WHERE c.province_id = p_province_id
    GROUP BY b.id, b.name
    ORDER BY b.name;
END $$
DELIMITER ;