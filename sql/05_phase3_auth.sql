DELIMITER $$

CREATE PROCEDURE `sp_authenticate_employee`(
    IN p_username VARCHAR(150),
    IN p_password_plain VARCHAR(255)
)
BEGIN
    DECLARE v_id INT;
    DECLARE v_full_name VARCHAR(255);
    DECLARE v_branch_id INT;
    DECLARE v_role_id INT;
    DECLARE v_role_name VARCHAR(100);
    DECLARE v_acount_status TINYINT(1);
    DECLARE v_password_hash VARCHAR(255);

    -- Try to find the employee by username (along with role name)
    SELECT e.id, e.full_name, e.branch_id, e.role_id, r.name, e.acount_status, e.password_hash
        INTO v_id, v_full_name, v_branch_id, v_role_id, v_role_name, v_acount_status, v_password_hash
        FROM employee e
        JOIN role r ON e.role_id = r.id
        WHERE e.username = p_username;

    -- If no row was returned, v_id stays NULL
    IF v_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username or password.';
    END IF;

    -- Check if the account is active
    IF v_acount_status != 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Account is inactive. Contact support.';
    END IF;

    -- Validate the password hash
    IF v_password_hash != SHA2(p_password_plain, 256) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid username or password.';
    END IF;

    -- Return the authenticated employee details (without the hash)
    SELECT v_id AS id,
           v_full_name AS full_name,
           v_branch_id AS branch_id,
           v_role_id AS role_id,
           v_role_name AS role_name,
           p_username AS username;
END$$

DELIMITER ;
