DELIMITER $$

DROP FUNCTION IF EXISTS `fn_calculate_pmt` $$
CREATE FUNCTION `fn_calculate_pmt`(
    p_principal DECIMAL(15,2),
    p_annual_rate DECIMAL(5,2),
    p_months INT
)
RETURNS DECIMAL(15,2)
DETERMINISTIC
BEGIN
    DECLARE r DECIMAL(10,6);
    DECLARE pmt DECIMAL(15,2);

    -- Convert annual percentage to monthly decimal
    SET r = (p_annual_rate / 100.0) / 12.0;

    -- PMT = P * (r * (1+r)^n) / ((1+r)^n - 1)
    IF r = 0 THEN
        SET pmt = p_principal / p_months;
    ELSE
        SET pmt = p_principal * (r * POW(1 + r, p_months)) / (POW(1 + r, p_months) - 1);
    END IF;

    RETURN ROUND(pmt, 2);
END $$

-- ------------------------------------------------------------
-- 2. Submit a new loan request (status = 'pending')
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_submit_loan_request` $$
CREATE PROCEDURE `sp_submit_loan_request`(
    IN p_customer_id INT,
    IN p_loan_type_id INT,
    IN p_amount DECIMAL(15,2),
    IN p_installments INT,
    IN p_employee_id INT
)
BEGIN
    DECLARE v_max_amount DECIMAL(15,2);
    DECLARE v_max_installments INT;
    DECLARE v_customer_active TINYINT(1);
    DECLARE v_message VARCHAR(255);

    -- Validate customer is active
    SELECT is_active INTO v_customer_active FROM customer WHERE id = p_customer_id;
    IF v_customer_active IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Customer not found.';
    END IF;
    IF v_customer_active = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot request loan for inactive customer.';
    END IF;

    -- Check loan type limits
    SELECT max_amount, max_installments INTO v_max_amount, v_max_installments
    FROM loan_type WHERE id = p_loan_type_id;

    IF v_max_amount IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan type not found.';
    END IF;

    IF p_amount > v_max_amount THEN
        SET v_message = CONCAT('Amount exceeds maximum (', v_max_amount, ') for this loan type.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_message;
    END IF;

    IF p_installments > v_max_installments THEN
        SET v_message = CONCAT('Installments exceed maximum (', v_max_installments, ') for this loan type.');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_message;
    END IF;

    -- Insert the loan request
    INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status)
    VALUES (p_customer_id, p_loan_type_id, p_amount, p_installments, NOW(), 'pending');

    SELECT LAST_INSERT_ID() AS loan_request_id;
END $$

-- ------------------------------------------------------------
-- 3. Get pending loan requests (for manager approval queue)
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_get_pending_loans` $$
CREATE PROCEDURE `sp_get_pending_loans`()
BEGIN
    SELECT lr.id,
           lr.customer_id,
           c.full_name AS customer_name,
           lr.loan_type_id,
           lt.name AS loan_type_name,
           lr.amount,
           lr.installments,
           lt.annual_interest_rate,
           lr.requested_at,
           lr.status
    FROM loan_request lr
    JOIN customer c ON lr.customer_id = c.id
    JOIN loan_type lt ON lr.loan_type_id = lt.id
    WHERE lr.status = 'pending'
    ORDER BY lr.requested_at DESC;
END $$

-- ------------------------------------------------------------
-- 4. Approve a loan request (generate installments)
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_approve_loan` $$
CREATE PROCEDURE `sp_approve_loan`(
    IN p_loan_request_id INT,
    IN p_employee_id INT
)
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE v_amount DECIMAL(15,2);
    DECLARE v_installments INT;
    DECLARE v_annual_rate DECIMAL(5,2);
    DECLARE v_monthly_pmt DECIMAL(15,2);
    DECLARE v_current_date DATE;
    DECLARE i INT DEFAULT 1;

    -- Check current status
    SELECT lr.status, lr.amount, lr.installments, lt.annual_interest_rate
        INTO v_status, v_amount, v_installments, v_annual_rate
    FROM loan_request lr
    JOIN loan_type lt ON lr.loan_type_id = lt.id
    WHERE lr.id = p_loan_request_id;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan request not found.';
    END IF;

    IF v_status != 'pending' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only pending loans can be approved.';
    END IF;

    -- Calculate monthly payment
    SET v_monthly_pmt = fn_calculate_pmt(v_amount, v_annual_rate, v_installments);

    -- Update loan request status
    UPDATE loan_request
    SET status = 'approved', approved_by = p_employee_id, approved_at = NOW()
    WHERE id = p_loan_request_id;

    -- Generate installment rows
    SET v_current_date = CURDATE();
    WHILE i <= v_installments DO
        INSERT INTO installment (loan_request_id, due_date, amount, paid_amount, status)
        VALUES (p_loan_request_id,
                DATE_ADD(v_current_date, INTERVAL i MONTH),
                v_monthly_pmt,
                0.00,
                'unpaid');
        SET i = i + 1;
    END WHILE;

    SELECT v_monthly_pmt AS monthly_payment, v_installments AS total_installments;
END $$

-- ------------------------------------------------------------
-- 5. Reject a loan request
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_reject_loan` $$
CREATE PROCEDURE `sp_reject_loan`(
    IN p_loan_request_id INT,
    IN p_employee_id INT
)
BEGIN
    DECLARE v_status VARCHAR(20);

    SELECT status INTO v_status FROM loan_request WHERE id = p_loan_request_id;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan request not found.';
    END IF;

    IF v_status != 'pending' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only pending loans can be rejected.';
    END IF;

    UPDATE loan_request
    SET status = 'rejected', approved_by = p_employee_id, approved_at = NOW()
    WHERE id = p_loan_request_id;
END $$

-- ------------------------------------------------------------
-- 6. Get loans and installments for a customer
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_get_customer_loans` $$
CREATE PROCEDURE `sp_get_customer_loans`(IN p_customer_id INT)
BEGIN
    SELECT lr.id,
           lr.amount,
           lr.installments AS total_installments,
           lt.name AS loan_type_name,
           lt.annual_interest_rate,
           lr.status,
           lr.requested_at,
           lr.approved_at
    FROM loan_request lr
    JOIN loan_type lt ON lr.loan_type_id = lt.id
    WHERE lr.customer_id = p_customer_id
    ORDER BY lr.requested_at DESC;
END $$

-- ------------------------------------------------------------
-- 7. Get installments for a specific loan
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_get_loan_installments` $$
CREATE PROCEDURE `sp_get_loan_installments`(IN p_loan_request_id INT)
BEGIN
    SELECT id,
           due_date,
           amount,
           paid_amount,
           status,
           paid_at
    FROM installment
    WHERE loan_request_id = p_loan_request_id
    ORDER BY due_date ASC;
END $$

-- ------------------------------------------------------------
-- 8. Pay an installment
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS `sp_pay_installment` $$
CREATE PROCEDURE `sp_pay_installment`(
    IN p_installment_id INT,
    IN p_amount DECIMAL(15,2)
)
BEGIN
    DECLARE v_status VARCHAR(10);
    DECLARE v_due_amount DECIMAL(15,2);

    SELECT status, amount INTO v_status, v_due_amount
    FROM installment
    WHERE id = p_installment_id;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Installment not found.';
    END IF;

    IF v_status = 'paid' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This installment is already paid.';
    END IF;

    UPDATE installment
    SET status = 'paid',
        paid_amount = p_amount,
        paid_at = NOW()
    WHERE id = p_installment_id;
END $$

DELIMITER ;