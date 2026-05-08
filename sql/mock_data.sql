USE mydb;

-- -----------------------------------------------------------
-- Country
-- -----------------------------------------------------------
INSERT INTO country (name, iso_code) VALUES ('Iran', 'IR');

-- -----------------------------------------------------------
-- Provinces (two provinces – Tehran & Isfahan)
-- -----------------------------------------------------------
INSERT INTO province (name, country_id) VALUES
('Tehran', 1),
('Isfahan', 1);

-- -----------------------------------------------------------
-- Cities (two per province)
-- -----------------------------------------------------------
INSERT INTO city (name, province_id) VALUES
('Tehran City', 1),
('Shahriar', 1),
('Isfahan City', 2),
('Kashan', 2);

-- -----------------------------------------------------------
-- Branches (one HQ per province, mixed status)
-- -----------------------------------------------------------
INSERT INTO branch (name, is_headquarter, email, phone_number, address, city_id, status) VALUES
('Tehran Central Branch', 1, 'tehran.hq@bank.ir', '+982166711111', 'No. 1, Valiasr Ave.', 1, 1),
('Tehran Shahriar Branch', 0, 'shahriar@bank.ir', '+982166722222', 'Shahriar Main St.', 2, 1),
('Tehran Northern Branch', 0, 'tehran.north@bank.ir', '+982166733333', 'Niavaran Blvd.', 1, 1),
('Isfahan Central Branch', 1, 'isfahan.hq@bank.ir', '+983133344444', 'Chahar Bagh Ave.', 3, 1),
('Kashan Branch', 0, 'kashan@bank.ir', '+983155566666', 'Kashan Bazaar', 4, 1);

-- -----------------------------------------------------------
-- Roles (including the new System Admin)
-- -----------------------------------------------------------
INSERT INTO role (name) VALUES
('Teller'),
('Branch Manager'),
('HelpDesk'),
('System Admin');

-- -----------------------------------------------------------
-- Employees (multiple per branch, covering different roles)
-- -----------------------------------------------------------
INSERT INTO employee (full_name, national_code, phone_number, email, branch_id, role_id, username, password_hash, acount_status, created_at)
VALUES
-- Tehran Central branch (id=1): one manager, one teller
('Ali Rezaei',       '0012345678', '09121111111', 'ali.rezaei@bank.ir',   1, (SELECT id FROM role WHERE name = 'Branch Manager'), 'ali.rezaei',   SHA2('pass123', 256), 1, NOW()),
('Sara Mohammadi',   '0023456789', '09122222222', 'sara.mohammadi@bank.ir', 1, (SELECT id FROM role WHERE name = 'Teller'), 'sara.mohammadi', SHA2('pass123', 256), 1, NOW()),

-- Shahriar branch (id=2): one teller
('Reza Ansari',      '0034567890', '09123333333', 'reza.ansari@bank.ir',   2, (SELECT id FROM role WHERE name = 'Teller'), 'reza.ansari',  SHA2('pass123', 256), 1, NOW()),

-- Tehran Northern branch (id=3): one manager
('Maryam Hosseini',  '0045678901', '09124444444', 'maryam.hosseini@bank.ir',3, (SELECT id FROM role WHERE name = 'Branch Manager'), 'maryam.hosseini', SHA2('pass123', 256), 1, NOW()),

-- Isfahan Central branch (id=4): manager + teller
('Ehsan Karimi',      '0056789012', '09135555555', 'ehsan.karimi@bank.ir',   4, (SELECT id FROM role WHERE name = 'Branch Manager'), 'ehsan.karimi', SHA2('pass123', 256), 1, NOW()),
('Fatemeh Ghasemi',   '0067890123', '09136666666', 'fatemeh.ghasemi@bank.ir',4, (SELECT id FROM role WHERE name = 'Teller'), 'fatemeh.ghasemi', SHA2('pass123', 256), 1, NOW()),

-- Kashan branch (id=5): one teller
('Amir Tavakoli',     '0078901234', '09137777777', 'amir.tavakoli@bank.ir',  5, (SELECT id FROM role WHERE name = 'Teller'), 'amir.tavakoli', SHA2('pass123', 256), 1, NOW()),

-- HelpDesk employee (Tehran Central)
('Neda Safari',       '0089012345', '09138888888', 'neda.safari@bank.ir',    1, (SELECT id FROM role WHERE name = 'HelpDesk'), 'neda.safari',   SHA2('pass123', 256), 1, NOW()),

-- System Admin (for Phase 3)
('Admin User',        '0000000000', '09120000000', 'admin@bank.ir',   1, (SELECT id FROM role WHERE name = 'System Admin'), 'admin',   SHA2('admin123', 256), 1, NOW());

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