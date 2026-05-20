DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_get_branch_vault_account` $$
CREATE PROCEDURE `sp_get_branch_vault_account`(
    IN p_branch_id INT,
    OUT p_vault_account_id INT
)
BEGIN
    DECLARE v_customer_id INT;
    DECLARE v_national_code VARCHAR(15);
    DECLARE v_account_number VARCHAR(16);
    DECLARE v_exists INT DEFAULT 1;

    -- National code used to identify the vault customer
    SET v_national_code = CONCAT('VAULT', LPAD(p_branch_id, 10, '0'));

    -- Check if the vault customer already exists
    SELECT id INTO v_customer_id
    FROM customer
    WHERE national_code = v_national_code;

    IF v_customer_id IS NULL THEN
        -- Create the vault customer (active, no real phone/address)
        INSERT INTO customer (full_name, national_code, phone_number, address, registered_by)
        VALUES (CONCAT('Branch Vault ', p_branch_id), v_national_code, '0000000000', 'System Vault', 1);
        SET v_customer_id = LAST_INSERT_ID();
    END IF;

    -- Check if the customer already has an account (any account)
    SELECT id INTO p_vault_account_id
    FROM account
    WHERE customer_id = v_customer_id
    LIMIT 1;

    IF p_vault_account_id IS NULL THEN
        -- Generate a unique account number
        WHILE v_exists > 0 DO
            SET v_account_number = LPAD(CAST(FLOOR(RAND() * 10000000000000000) AS UNSIGNED), 16, '0');
            SELECT COUNT(*) INTO v_exists FROM account WHERE account_number = v_account_number;
        END WHILE;

        -- Create a Savings account (account_type_id = 1) with a large initial balance
        INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status)
        VALUES (v_account_number, v_customer_id, 1, 100000000000.00, 1, CURDATE(), 'active');
        SET p_vault_account_id = LAST_INSERT_ID();
    END IF;
END $$

-- ------------------------------------------------------------
-- 2. Core Transfer Procedure
--    Moves money from one account to another.
--    The trigger will check balances and update them automatically.
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_transfer` $$
CREATE PROCEDURE `sp_transfer`(
    IN p_from_account_id INT,
    IN p_to_account_id INT,
    IN p_amount DECIMAL(15,2),
    IN p_description VARCHAR(255),
    IN p_created_by INT,
    IN p_transaction_type VARCHAR(20)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Insert the transaction row – the trigger does the rest
    INSERT INTO `transaction` (
        from_account_id,
        to_account_id,
        amount,
        transaction_type,
        description,
        created_by,
        created_at,
        status
    ) VALUES (
        p_from_account_id,
        p_to_account_id,
        p_amount,
        p_transaction_type,
        p_description,
        p_created_by,
        NOW(),
        'completed'
    );

    COMMIT;

    -- Return the transaction summary
    SELECT
        t.id AS transaction_id,
        t.amount,
        t.transaction_type,
        t.status,
        t.created_at
    FROM `transaction` t
    WHERE t.id = LAST_INSERT_ID();
END $$

-- ------------------------------------------------------------
-- 3. Deposit (Branch Vault → Customer Account)
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_deposit` $$
CREATE PROCEDURE `sp_deposit`(
    IN p_to_account_id INT,
    IN p_amount DECIMAL(15,2),
    IN p_branch_id INT,
    IN p_employee_id INT,
    IN p_description VARCHAR(255)
)
BEGIN
    DECLARE v_vault_account_id INT;

    -- Get or create the branch vault account
    CALL sp_get_branch_vault_account(p_branch_id, v_vault_account_id);

    -- Use transfer: from vault to customer
    CALL sp_transfer(v_vault_account_id, p_to_account_id, p_amount, p_description, p_employee_id, 'deposit');
END $$

-- ------------------------------------------------------------
-- 4. Withdrawal (Customer Account → Branch Vault)
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_withdrawal` $$
CREATE PROCEDURE `sp_withdrawal`(
    IN p_from_account_id INT,
    IN p_amount DECIMAL(15,2),
    IN p_branch_id INT,
    IN p_employee_id INT,
    IN p_description VARCHAR(255)
)
BEGIN
    DECLARE v_vault_account_id INT;

    -- Get or create the branch vault account
    CALL sp_get_branch_vault_account(p_branch_id, v_vault_account_id);

    -- Use transfer: from customer to vault
    CALL sp_transfer(p_from_account_id, v_vault_account_id, p_amount, p_description, p_employee_id, 'withdrawal');
END $$

-- ------------------------------------------------------------
-- 5. Get transaction history for an account
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_get_transactions` $$
CREATE PROCEDURE `sp_get_transactions`(
    IN p_account_id INT,
    IN p_limit INT,
    IN p_offset INT
)
BEGIN
    SELECT
        t.id,
        t.from_account_id,
        t.to_account_id,
        t.amount,
        t.transaction_type,
        t.description,
        t.created_at,
        t.status
    FROM `transaction` t
    WHERE t.from_account_id = p_account_id OR t.to_account_id = p_account_id
    ORDER BY t.created_at DESC
    LIMIT p_limit OFFSET p_offset;
END $$

-- ------------------------------------------------------------
-- 6. Branch report (totals, vault balance, account count)
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_get_branch_report` $$
CREATE PROCEDURE `sp_get_branch_report`(IN p_branch_id INT)
BEGIN
    DECLARE v_vault_account_id INT;

    -- Obtain the vault account id for this branch
    CALL sp_get_branch_vault_account(p_branch_id, v_vault_account_id);

    -- Total deposits / withdrawals for the branch (all time)
    SELECT
        (SELECT IFNULL(SUM(amount), 0) FROM `transaction` WHERE to_account_id = v_vault_account_id) AS total_deposits,
        (SELECT IFNULL(SUM(amount), 0) FROM `transaction` WHERE from_account_id = v_vault_account_id) AS total_withdrawals,
        (SELECT balance FROM account WHERE id = v_vault_account_id) AS vault_balance,
        (SELECT COUNT(*) FROM account WHERE openend_by IN (SELECT id FROM employee WHERE branch_id = p_branch_id)) AS branch_accounts,
        (SELECT COUNT(*) FROM `transaction` WHERE created_by IN (SELECT id FROM employee WHERE branch_id = p_branch_id)) AS branch_transactions;
END $$

-- ------------------------------------------------------------
-- TRIGGERS
-- ------------------------------------------------------------

-- 7. BEFORE INSERT – prevent negative balances and inactive accounts
DROP TRIGGER IF EXISTS `trg_transaction_validate` $$
CREATE TRIGGER `trg_transaction_validate`
BEFORE INSERT ON `transaction`
FOR EACH ROW
BEGIN
    DECLARE v_balance DECIMAL(15,2);
    DECLARE v_from_status VARCHAR(10);
    DECLARE v_to_status VARCHAR(10);

    -- Validate sender
    IF NEW.from_account_id IS NOT NULL THEN
        SELECT balance, status INTO v_balance, v_from_status
        FROM account
        WHERE id = NEW.from_account_id;

        IF v_from_status != 'active' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Sender account is not active.';
        END IF;

        IF v_balance < NEW.amount THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient balance.';
        END IF;
    END IF;

    -- Validate receiver
    IF NEW.to_account_id IS NOT NULL THEN
        SELECT status INTO v_to_status
        FROM account
        WHERE id = NEW.to_account_id;

        IF v_to_status != 'active' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Receiver account is not active.';
        END IF;
    END IF;
END $$

-- 8. AFTER INSERT – update balances
DROP TRIGGER IF EXISTS `trg_transaction_update_balances` $$
CREATE TRIGGER `trg_transaction_update_balances`
AFTER INSERT ON `transaction`
FOR EACH ROW
BEGIN
    -- Deduct from sender
    IF NEW.from_account_id IS NOT NULL THEN
        UPDATE account
        SET balance = balance - NEW.amount
        WHERE id = NEW.from_account_id;
    END IF;

    -- Add to receiver
    IF NEW.to_account_id IS NOT NULL THEN
        UPDATE account
        SET balance = balance + NEW.amount
        WHERE id = NEW.to_account_id;
    END IF;
END $$

-- 9. AFTER INSERT – audit log
DROP TRIGGER IF EXISTS `trg_transaction_audit` $$
CREATE TRIGGER `trg_transaction_audit`
AFTER INSERT ON `transaction`
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (employee_id, action_type, table_affected, record_id, new_value, created_at)
    VALUES (
        NEW.created_by,
        'TRANSACTION',
        'transaction',
        NEW.id,
        CONCAT('Type: ', NEW.transaction_type, ' Amount: ', NEW.amount, ' From: ', IFNULL(NEW.from_account_id, 'N/A'), ' To: ', IFNULL(NEW.to_account_id, 'N/A')),
        NOW()
    );
END $$

DELIMITER ;