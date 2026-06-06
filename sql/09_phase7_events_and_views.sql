-- ============================================================
-- PHASE 7 – AUTOMATIC INTEREST & HQ PROVINCE DASHBOARD
-- ============================================================

-- 1. Central Bank Treasury Account (interest source)
INSERT IGNORE INTO customer (full_name, national_code, phone_number, address, registered_by, is_active)
VALUES ('Bank Treasury', 'BANK0000000', '0000000000', 'System Treasury', 1, 1);
SET @treasury_cust_id = (SELECT id FROM customer WHERE national_code = 'BANK0000000');

INSERT IGNORE INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status)
SELECT '9999999999999999', @treasury_cust_id, (SELECT id FROM account_type WHERE name = 'Savings' LIMIT 1), 1000000000000.00, 1, CURDATE(), 'active'
WHERE NOT EXISTS (SELECT 1 FROM account WHERE account_number = '9999999999999999');

-- 2. Monthly Interest Calculation Procedure
DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_process_monthly_interest` $$
CREATE PROCEDURE `sp_process_monthly_interest`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_acc_id INT;
    DECLARE v_balance DECIMAL(15,2);
    DECLARE v_rate DECIMAL(5,2);
    DECLARE v_interest DECIMAL(15,2);
    DECLARE v_treasury_id INT;

    DECLARE cur CURSOR FOR
        SELECT a.id, a.balance, at.interest_rate
        FROM account a
        JOIN account_type at ON a.account_type_id = at.id
        WHERE a.status = 'active' AND at.interest_rate > 0 AND a.id != v_treasury_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SELECT id INTO v_treasury_id FROM account WHERE account_number = '9999999999999999';

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_acc_id, v_balance, v_rate;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET v_interest = ROUND(v_balance * (v_rate / 100.0) / 12.0, 2);
        IF v_interest > 0 THEN
            CALL sp_transfer(v_treasury_id, v_acc_id, v_interest, 'Monthly interest', 1, 'interest');
        END IF;
    END LOOP;
    CLOSE cur;
END $$
DELIMITER ;

-- 3. Enable event scheduler (run once globally)
SET GLOBAL event_scheduler = ON;

-- 4. Monthly event: runs on the 1st of every month at 02:00
DELIMITER $$
DROP EVENT IF EXISTS `evt_monthly_interest` $$
CREATE EVENT `evt_monthly_interest`
ON SCHEDULE EVERY 1 MONTH
STARTS DATE_ADD(CURDATE(), INTERVAL 1 DAY)
DO
BEGIN
    CALL sp_process_monthly_interest();
END $$
DELIMITER ;

-- 5. View for Province Summary
CREATE OR REPLACE VIEW `vw_province_summary` AS
SELECT
    p.id AS province_id,
    p.name AS province_name,
    COUNT(DISTINCT b.id) AS branch_count,
    COUNT(DISTINCT a.id) AS active_accounts,
    COALESCE(SUM(a.balance), 0) AS total_deposits,
    COALESCE(SUM(CASE WHEN lr.status = 'approved' THEN lr.amount ELSE 0 END), 0) AS total_loans
FROM province p
JOIN city c ON c.province_id = p.id
JOIN branch b ON b.city_id = c.id
LEFT JOIN employee e ON e.branch_id = b.id
LEFT JOIN account a ON a.openend_by = e.id AND a.status = 'active'
LEFT JOIN loan_request lr ON lr.customer_id IN (
    SELECT a2.customer_id FROM account a2 WHERE a2.openend_by = e.id
) AND lr.status = 'approved'
GROUP BY p.id, p.name
ORDER BY p.name;

-- 6. Stored procedure to get province report
DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_get_province_report` $$
CREATE PROCEDURE `sp_get_province_report`(IN p_province_id INT)
BEGIN
    SELECT province_id, province_name, branch_count, active_accounts, total_deposits, total_loans
    FROM vw_province_summary
    WHERE province_id = p_province_id;
END $$
DELIMITER ;

-- 7. Stored procedure for per‑branch performance in a province
DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_get_branch_performance_by_province` $$
CREATE PROCEDURE `sp_get_branch_performance_by_province`(IN p_province_id INT)
BEGIN
    SELECT
        b.id AS branch_id,
        b.name AS branch_name,
        COUNT(DISTINCT a.id) AS active_accounts,
        COALESCE(SUM(a.balance), 0) AS total_deposits,
        COALESCE(SUM(CASE WHEN lr.status = 'approved' THEN lr.amount ELSE 0 END), 0) AS total_loans
    FROM branch b
    JOIN city c ON b.city_id = c.id
    LEFT JOIN employee e ON e.branch_id = b.id
    LEFT JOIN account a ON a.openend_by = e.id AND a.status = 'active'
    LEFT JOIN loan_request lr ON lr.customer_id IN (
        SELECT a2.customer_id FROM account a2 WHERE a2.openend_by = e.id
    ) AND lr.status = 'approved'
    WHERE c.province_id = p_province_id
    GROUP BY b.id, b.name
    ORDER BY b.name;
END $$
DELIMITER ;