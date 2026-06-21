DELIMITER $$
DROP PROCEDURE IF EXISTS `sp_get_province_report` $$
CREATE PROCEDURE `sp_get_province_report`(IN p_province_id INT)
BEGIN
    SELECT province_id, province_name, branch_count, active_accounts,
           total_deposits, total_loans, total_withdrawals, total_transactions
    FROM vw_province_summary
    WHERE province_id = p_province_id;
END $$
DELIMITER ;