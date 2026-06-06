
USE mydb;

-- -----------------------------------------------------------
-- Country
-- -----------------------------------------------------------
INSERT INTO country (name, iso_code) VALUES ('Iran', 'IR');

-- -----------------------------------------------------------
-- Provinces
-- -----------------------------------------------------------
INSERT INTO province (name, country_id) VALUES
('Tehran', 1),
('Isfahan', 1);

-- -----------------------------------------------------------
-- Cities
-- -----------------------------------------------------------
INSERT INTO city (name, province_id) VALUES
('Tehran City', 1),
('Shahriar', 1),
('Isfahan City', 2),
('Kashan', 2);

-- -----------------------------------------------------------
-- Branches (one HQ per province)
-- -----------------------------------------------------------
INSERT INTO branch (name, is_headquarter, email, phone_number, address, city_id, status) VALUES
('Tehran Central Branch', 1, 'tehran.hq@bank.ir', '+982166711111', 'No. 1, Valiasr Ave.', 1, 1),
('Tehran Shahriar Branch', 0, 'shahriar@bank.ir', '+982166722222', 'Shahriar Main St.', 2, 1),
('Tehran Northern Branch', 0, 'tehran.north@bank.ir', '+982166733333', 'Niavaran Blvd.', 1, 1),
('Isfahan Central Branch', 1, 'isfahan.hq@bank.ir', '+983133344444', 'Chahar Bagh Ave.', 3, 1),
('Kashan Branch', 0, 'kashan@bank.ir', '+983155566666', 'Kashan Bazaar', 4, 1);

-- -----------------------------------------------------------
-- Roles
-- -----------------------------------------------------------
INSERT INTO role (name) VALUES
('Teller'),
('Branch Manager'),
('HelpDesk'),
('System Admin');

-- -----------------------------------------------------------
-- Employees
-- All passwords: pass123  (hashed with SHA2)
-- admin: admin123
-- -----------------------------------------------------------
INSERT INTO employee (full_name, national_code, phone_number, email, branch_id, role_id, username, password_hash, acount_status, created_at) VALUES
-- Tehran Central (branch 1): manager + teller + helpdesk + admin
('Ali Rezaei',       '0012345678', '09121111111', 'ali.rezaei@bank.ir',         1, (SELECT id FROM role WHERE name='Branch Manager'), 'ali.rezaei',      SHA2('pass123',256), 1, NOW()),
('Sara Mohammadi',   '0023456789', '09122222222', 'sara.mohammadi@bank.ir',     1, (SELECT id FROM role WHERE name='Teller'),          'sara.mohammadi',   SHA2('pass123',256), 1, NOW()),
('Neda Safari',      '0089012345', '09138888888', 'neda.safari@bank.ir',         1, (SELECT id FROM role WHERE name='HelpDesk'),        'neda.safari',      SHA2('pass123',256), 1, NOW()),
('Admin User',       '0000000000', '09120000000', 'admin@bank.ir',               1, (SELECT id FROM role WHERE name='System Admin'),    'admin',            SHA2('admin123',256), 1, NOW()),

-- Shahriar (branch 2): teller
('Reza Ansari',      '0034567890', '09123333333', 'reza.ansari@bank.ir',         2, (SELECT id FROM role WHERE name='Teller'),          'reza.ansari',      SHA2('pass123',256), 1, NOW()),

-- Tehran Northern (branch 3): manager
('Maryam Hosseini',  '0045678901', '09124444444', 'maryam.hosseini@bank.ir',     3, (SELECT id FROM role WHERE name='Branch Manager'),  'maryam.hosseini',  SHA2('pass123',256), 1, NOW()),

-- Isfahan Central (branch 4): manager + teller
('Ehsan Karimi',     '0056789012', '09135555555', 'ehsan.karimi@bank.ir',        4, (SELECT id FROM role WHERE name='Branch Manager'),  'ehsan.karimi',     SHA2('pass123',256), 1, NOW()),
('Fatemeh Ghasemi',  '0067890123', '09136666666', 'fatemeh.ghasemi@bank.ir',     4, (SELECT id FROM role WHERE name='Teller'),          'fatemeh.ghasemi',  SHA2('pass123',256), 1, NOW()),

-- Kashan (branch 5): teller
('Amir Tavakoli',    '0078901234', '09137777777', 'amir.tavakoli@bank.ir',        5, (SELECT id FROM role WHERE name='Teller'),          'amir.tavakoli',    SHA2('pass123',256), 1, NOW());

-- -----------------------------------------------------------
-- Account types
-- -----------------------------------------------------------
INSERT INTO account_type (name, interest_rate) VALUES
('Savings', 10.00),
('Current', 0.00),
('Fixed Deposit (6m)', 15.00),
('Short-term Deposit', 8.00);

-- -----------------------------------------------------------
-- Loan types
-- -----------------------------------------------------------
INSERT INTO loan_type (name, max_amount, annual_interest_rate, max_installments) VALUES
('Personal Loan', 500000000, 18.00, 36),
('Mortgage Loan', 3000000000, 12.00, 120),
('Car Loan',      2000000000, 15.00, 48);

-- -----------------------------------------------------------
-- Customers (real + vaults + treasury)
-- -----------------------------------------------------------
INSERT INTO customer (full_name, national_code, phone_number, address, registered_by, is_active) VALUES
('Hossein Ahmadi',   '1111111111', '09121112233', 'Tehran, Valiasr St.',   1, 1),
('Zahra Moradi',     '2222222222', '09123334455', 'Isfahan, Chahar Bagh',  1, 1),
('Mohammad Karimi',  '3333333333', '09124445566', 'Kashan, Bazaar',        5, 1),
('Leila Ebrahimi',   '4444444444', '09125556677', 'Shahriar, Main St.',    2, 0);   -- inactive

-- Branch vault customers (hidden from tellers)
INSERT INTO customer (full_name, national_code, phone_number, address, registered_by, is_active) VALUES
('Branch Vault 1', 'VAULT0000000001', '0000000000', 'System Vault', 1, 1),
('Branch Vault 2', 'VAULT0000000002', '0000000000', 'System Vault', 1, 1),
('Branch Vault 3', 'VAULT0000000003', '0000000000', 'System Vault', 1, 1),
('Branch Vault 4', 'VAULT0000000004', '0000000000', 'System Vault', 1, 1),
('Branch Vault 5', 'VAULT0000000005', '0000000000', 'System Vault', 1, 1);

-- Bank Treasury (for interest payments)
INSERT INTO customer (full_name, national_code, phone_number, address, registered_by, is_active) VALUES
('Bank Treasury', 'BANK0000000', '0000000000', 'System Treasury', 1, 1);

-- -----------------------------------------------------------
-- Branch Vault Accounts
-- -----------------------------------------------------------
SET @vault1 = (SELECT id FROM customer WHERE national_code = 'VAULT0000000001');
SET @vault2 = (SELECT id FROM customer WHERE national_code = 'VAULT0000000002');
SET @vault3 = (SELECT id FROM customer WHERE national_code = 'VAULT0000000003');
SET @vault4 = (SELECT id FROM customer WHERE national_code = 'VAULT0000000004');
SET @vault5 = (SELECT id FROM customer WHERE national_code = 'VAULT0000000005');

INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('6037991111111111', @vault1, 1, 100000000000.00, 1, CURDATE(), 'active'),
('6037992222222222', @vault2, 1, 100000000000.00, 1, CURDATE(), 'active'),
('6037993333333333', @vault3, 1, 100000000000.00, 1, CURDATE(), 'active'),
('6037994444444444', @vault4, 1, 100000000000.00, 1, CURDATE(), 'active'),
('6037995555555555', @vault5, 1, 100000000000.00, 1, CURDATE(), 'active');

-- -----------------------------------------------------------
-- Customer Accounts (for real customers)
-- -----------------------------------------------------------
-- Customer 1: two accounts
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('6037991111222233', 1, 1, 15000000.00, 1, CURDATE(), 'active'),   -- Savings
('6037991111222244', 1, 2,  5000000.00, 1, CURDATE(), 'active');   -- Current

-- Customer 2: one account (Fixed Deposit)
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('6037992222333344', 2, 3, 25000000.00, 1, CURDATE(), 'active');

-- Customer 3: one account (Short-term Deposit)
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('6037993333444455', 3, 4, 10000000.00, 5, CURDATE(), 'active');

-- Customer 4 (inactive): no account

-- -----------------------------------------------------------
-- Treasury Account (for interest payments)
-- -----------------------------------------------------------
SET @treasury = (SELECT id FROM customer WHERE national_code = 'BANK0000000');
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('9999999999999999', @treasury, 1, 1000000000000.00, 1, CURDATE(), 'active');

-- -----------------------------------------------------------
-- Cards
-- -----------------------------------------------------------
INSERT INTO card (account_id, card_number, cvv2, expiry_date, status, issued_at) VALUES
(1, '5022291111222233', '123', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(3, '5022292222333344', '456', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW());

-- -----------------------------------------------------------
-- Loan Requests (demo data for Phase 6)
-- -----------------------------------------------------------
-- Pending loan for customer 1
INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status) VALUES
(1, 1, 100000000.00, 24, NOW(), 'pending');

-- Approved loan for customer 2 (with some installments)
INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status, approved_by, approved_at) VALUES
(2, 3, 500000000.00, 36, NOW() - INTERVAL 2 DAY, 'approved', 1, NOW());
SET @approved_loan_id = LAST_INSERT_ID();
INSERT INTO installment (loan_request_id, due_date, amount, paid_amount, status) VALUES
(@approved_loan_id, DATE_ADD(CURDATE(), INTERVAL 1 MONTH), 17800000.00, 0, 'unpaid'),
(@approved_loan_id, DATE_ADD(CURDATE(), INTERVAL 2 MONTH), 17800000.00, 0, 'unpaid'),
(@approved_loan_id, DATE_ADD(CURDATE(), INTERVAL 3 MONTH), 17800000.00, 0, 'unpaid');

-- Rejected loan for customer 3
INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status, approved_by, approved_at) VALUES
(3, 2, 2000000000.00, 96, NOW() - INTERVAL 5 DAY, 'rejected', 6, NOW());