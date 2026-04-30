DELIMITER $$

-- ============================================================
-- BRANCH MANAGEMENT
-- ============================================================

-- List all branches with city and province names
CREATE PROCEDURE `sp_get_all_branches`()
BEGIN
    SELECT b.id, b.name, b.is_headquarter, b.email, b.phone_number,
           b.address, b.city_id, c.name AS city_name,
           p.id AS province_id, p.name AS province_name, b.status
    FROM branch b
    JOIN city c ON b.city_id = c.id
    JOIN province p ON c.province_id = p.id
    ORDER BY p.name, c.name, b.name;
END$$

-- Insert a new branch
CREATE PROCEDURE `sp_insert_branch`(
    IN p_name VARCHAR(255),
    IN p_is_headquarter TINYINT(1),
    IN p_email VARCHAR(255),
    IN p_phone_number VARCHAR(255),
    IN p_address TEXT,
    IN p_city_id INT,
    IN p_status TINYINT(1)
)
BEGIN
    INSERT INTO branch (name, is_headquarter, email, phone_number, address, city_id, status)
    VALUES (p_name, p_is_headquarter, p_email, p_phone_number, p_address, p_city_id, p_status);
END$$

-- Update an existing branch
CREATE PROCEDURE `sp_update_branch`(
    IN p_id INT,
    IN p_name VARCHAR(255),
    IN p_is_headquarter TINYINT(1),
    IN p_email VARCHAR(255),
    IN p_phone_number VARCHAR(255),
    IN p_address TEXT,
    IN p_city_id INT,
    IN p_status TINYINT(1)
)
BEGIN
    UPDATE branch
    SET name = p_name,
        is_headquarter = p_is_headquarter,
        email = p_email,
        phone_number = p_phone_number,
        address = p_address,
        city_id = p_city_id,
        status = p_status
    WHERE id = p_id;
END$$

-- Delete a branch
CREATE PROCEDURE `sp_delete_branch`(IN p_id INT)
BEGIN
    DELETE FROM branch WHERE id = p_id;
END$$

-- Get a single branch by ID
CREATE PROCEDURE `sp_get_branch_by_id`(IN p_id INT)
BEGIN
    SELECT b.id, b.name, b.is_headquarter, b.email, b.phone_number,
           b.address, b.city_id, b.status
    FROM branch b
    WHERE b.id = p_id;
END$$

-- ============================================================
-- EMPLOYEE MANAGEMENT
-- ============================================================

-- List all employees with branch and role names
CREATE PROCEDURE `sp_get_all_employees`()
BEGIN
    SELECT e.id, e.full_name, e.national_code, e.phone_number, e.email,
           e.branch_id, b.name AS branch_name,
           e.role_id, r.name AS role_name,
           e.username, e.acount_status, e.created_at
    FROM employee e
    JOIN branch b ON e.branch_id = b.id
    JOIN role r ON e.role_id = r.id
    ORDER BY e.full_name;
END$$

-- Insert a new employee (stores SHA‑256 hashed password)
CREATE PROCEDURE `sp_insert_employee`(
    IN p_full_name VARCHAR(255),
    IN p_national_code VARCHAR(15),
    IN p_phone_number VARCHAR(255),
    IN p_email VARCHAR(255),
    IN p_branch_id INT,
    IN p_role_id INT,
    IN p_username VARCHAR(150),
    IN p_password_plain VARCHAR(255),   -- plain text, will be hashed
    IN p_acount_status TINYINT(1)
)
BEGIN
    INSERT INTO employee (
        full_name, national_code, phone_number, email,
        branch_id, role_id, username, password_hash,
        acount_status, created_at
    )
    VALUES (
        p_full_name, p_national_code, p_phone_number, p_email,
        p_branch_id, p_role_id, p_username,
        SHA2(p_password_plain, 256),
        p_acount_status, NOW()
    );
END$$

-- Update an existing employee (optional password change)
CREATE PROCEDURE `sp_update_employee`(
    IN p_id INT,
    IN p_full_name VARCHAR(255),
    IN p_national_code VARCHAR(15),
    IN p_phone_number VARCHAR(255),
    IN p_email VARCHAR(255),
    IN p_branch_id INT,
    IN p_role_id INT,
    IN p_username VARCHAR(150),
    IN p_password_plain VARCHAR(255),   -- NULL if no change
    IN p_acount_status TINYINT(1)
)
BEGIN
    UPDATE employee
    SET full_name = p_full_name,
        national_code = p_national_code,
        phone_number = p_phone_number,
        email = p_email,
        branch_id = p_branch_id,
        role_id = p_role_id,
        username = p_username,
        acount_status = p_acount_status,
        password_hash = IF(p_password_plain IS NOT NULL,
                           SHA2(p_password_plain, 256),
                           password_hash)
    WHERE id = p_id;
END$$

-- Delete an employee
CREATE PROCEDURE `sp_delete_employee`(IN p_id INT)
BEGIN
    DELETE FROM employee WHERE id = p_id;
END$$

-- Get employee by ID (useful for edit forms)
CREATE PROCEDURE `sp_get_employee_by_id`(IN p_id INT)
BEGIN
    SELECT e.id, e.full_name, e.national_code, e.phone_number, e.email,
           e.branch_id, e.role_id, e.username, e.acount_status
    FROM employee e
    WHERE e.id = p_id;
END$$

-- ============================================================
-- ROLE MANAGEMENT
-- ============================================================

CREATE PROCEDURE `sp_get_all_roles`()
BEGIN
    SELECT id, name FROM role ORDER BY name;
END$$

CREATE PROCEDURE `sp_insert_role`(IN p_name VARCHAR(100))
BEGIN
    INSERT INTO role (name) VALUES (p_name);
END$$

CREATE PROCEDURE `sp_update_role`(IN p_id INT, IN p_name VARCHAR(100))
BEGIN
    UPDATE role SET name = p_name WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_delete_role`(IN p_id INT)
BEGIN
    DELETE FROM role WHERE id = p_id;
END$$

-- ============================================================
-- ACCOUNT TYPE MANAGEMENT
-- ============================================================

CREATE PROCEDURE `sp_get_all_account_types`()
BEGIN
    SELECT id, name, interest_rate FROM account_type ORDER BY name;
END$$

CREATE PROCEDURE `sp_insert_account_type`(
    IN p_name VARCHAR(255),
    IN p_interest_rate DECIMAL(5,2)
)
BEGIN
    INSERT INTO account_type (name, interest_rate) VALUES (p_name, p_interest_rate);
END$$

CREATE PROCEDURE `sp_update_account_type`(
    IN p_id INT,
    IN p_name VARCHAR(255),
    IN p_interest_rate DECIMAL(5,2)
)
BEGIN
    UPDATE account_type SET name = p_name, interest_rate = p_interest_rate WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_delete_account_type`(IN p_id INT)
BEGIN
    DELETE FROM account_type WHERE id = p_id;
END$$

-- ============================================================
-- LOAN TYPE MANAGEMENT
-- ============================================================

CREATE PROCEDURE `sp_get_all_loan_types`()
BEGIN
    SELECT id, name, max_amount, annual_interest_rate, max_installments
    FROM loan_type ORDER BY name;
END$$

CREATE PROCEDURE `sp_insert_loan_type`(
    IN p_name VARCHAR(255),
    IN p_max_amount DECIMAL(15,2),
    IN p_annual_interest_rate DECIMAL(5,2),
    IN p_max_installments INT
)
BEGIN
    INSERT INTO loan_type (name, max_amount, annual_interest_rate, max_installments)
    VALUES (p_name, p_max_amount, p_annual_interest_rate, p_max_installments);
END$$

CREATE PROCEDURE `sp_update_loan_type`(
    IN p_id INT,
    IN p_name VARCHAR(255),
    IN p_max_amount DECIMAL(15,2),
    IN p_annual_interest_rate DECIMAL(5,2),
    IN p_max_installments INT
)
BEGIN
    UPDATE loan_type
    SET name = p_name,
        max_amount = p_max_amount,
        annual_interest_rate = p_annual_interest_rate,
        max_installments = p_max_installments
    WHERE id = p_id;
END$$

CREATE PROCEDURE `sp_delete_loan_type`(IN p_id INT)
BEGIN
    DELETE FROM loan_type WHERE id = p_id;
END$$

DELIMITER ;