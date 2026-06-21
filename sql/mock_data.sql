-- ============================================================
-- COMPREHENSIVE MOCK DATA – All Branches & Features
-- ============================================================
USE mydb;

-- Country / Province / City / Branch (unchanged structure)
INSERT INTO country (name, iso_code) VALUES ('Iran', 'IR');
INSERT INTO province (name, country_id) VALUES ('Tehran', 1), ('Isfahan', 1);
INSERT INTO city (name, province_id) VALUES
('Tehran City', 1), ('Shahriar', 1), ('Isfahan City', 2), ('Kashan', 2);
INSERT INTO branch (name, is_headquarter, email, phone_number, address, city_id, status) VALUES
('Tehran Central Branch', 1, 'tehran.hq@bank.ir', '+982166711111', 'No.1 Valiasr Ave.', 1, 1),
('Tehran Shahriar Branch', 0, 'shahriar@bank.ir', '+982166722222', 'Shahriar Main St.', 2, 1),
('Tehran Northern Branch', 0, 'tehran.north@bank.ir', '+982166733333', 'Niavaran Blvd.', 1, 1),
('Isfahan Central Branch', 1, 'isfahan.hq@bank.ir', '+983133344444', 'Chahar Bagh Ave.', 3, 1),
('Kashan Branch', 0, 'kashan@bank.ir', '+983155566666', 'Kashan Bazaar', 4, 1);

-- Roles
INSERT INTO role (name) VALUES ('Teller'), ('Branch Manager'), ('HelpDesk'), ('System Admin');

-- Employees (all branches)
INSERT INTO employee (full_name, national_code, phone_number, email, branch_id, role_id, username, password_hash, acount_status, created_at) VALUES
-- Tehran Central (branch 1)
('Ali Rezaei',       '0012345678', '09121111111', 'ali.rezaei@bank.ir',         1, (SELECT id FROM role WHERE name='Branch Manager'), 'ali.rezaei',      SHA2('pass123',256), 1, NOW()),
('Sara Mohammadi',   '0023456789', '09122222222', 'sara.mohammadi@bank.ir',     1, (SELECT id FROM role WHERE name='Teller'),          'sara.mohammadi',   SHA2('pass123',256), 1, NOW()),
('Neda Safari',      '0089012345', '09138888888', 'neda.safari@bank.ir',         1, (SELECT id FROM role WHERE name='HelpDesk'),        'neda.safari',      SHA2('pass123',256), 1, NOW()),
('Admin User',       '0000000000', '09120000000', 'admin@bank.ir',               1, (SELECT id FROM role WHERE name='System Admin'),    'admin',            SHA2('admin123',256), 1, NOW()),

-- Tehran Shahriar (branch 2)
('Reza Ansari',      '0034567890', '09123333333', 'reza.ansari@bank.ir',         2, (SELECT id FROM role WHERE name='Teller'),          'reza.ansari',      SHA2('pass123',256), 1, NOW()),

-- Tehran Northern (branch 3)
('Maryam Hosseini',  '0045678901', '09124444444', 'maryam.hosseini@bank.ir',     3, (SELECT id FROM role WHERE name='Branch Manager'),  'maryam.hosseini',  SHA2('pass123',256), 1, NOW()),

-- Isfahan Central (branch 4)
('Ehsan Karimi',     '0056789012', '09135555555', 'ehsan.karimi@bank.ir',        4, (SELECT id FROM role WHERE name='Branch Manager'),  'ehsan.karimi',     SHA2('pass123',256), 1, NOW()),
('Fatemeh Ghasemi',  '0067890123', '09136666666', 'fatemeh.ghasemi@bank.ir',     4, (SELECT id FROM role WHERE name='Teller'),          'fatemeh.ghasemi',  SHA2('pass123',256), 1, NOW()),

-- Kashan (branch 5)
('Amir Tavakoli',    '0078901234', '09137777777', 'amir.tavakoli@bank.ir',        5, (SELECT id FROM role WHERE name='Teller'),          'amir.tavakoli',    SHA2('pass123',256), 1, NOW());

-- Account types
INSERT INTO account_type (name, interest_rate) VALUES
('Savings', 10.00), ('Current', 0.00), ('Fixed Deposit (6m)', 15.00), ('Short-term Deposit', 8.00);

-- Loan types
INSERT INTO loan_type (name, max_amount, annual_interest_rate, max_installments) VALUES
('Personal Loan', 500000000, 18.00, 36),
('Mortgage Loan', 3000000000, 12.00, 120),
('Car Loan',      2000000000, 15.00, 48);

-- --------------------------------------------------------------------
-- Customers (real + vaults + treasury)
-- Real customers spread across branches
-- --------------------------------------------------------------------
INSERT INTO customer (full_name, national_code, phone_number, address, registered_by, is_active) VALUES
('Hossein Ahmadi',   '1111111111', '09121112233', 'Tehran, Valiasr St.',   1, 1),   -- by Ali Rezaei (branch1)
('Zahra Moradi',     '2222222222', '09123334455', 'Isfahan, Chahar Bagh',  7, 1),   -- by Ehsan Karimi (branch4)
('Mohammad Karimi',  '3333333333', '09124445566', 'Kashan, Bazaar',        9, 1),   -- by Amir Tavakoli (branch5)
('Leila Ebrahimi',   '4444444444', '09125556677', 'Shahriar, Main St.',    5, 0),   -- by Reza Ansari (branch2) – inactive
('Saeed Rahimi',     '5555555555', '09126667788', 'Tehran, Niavaran',      6, 1),   -- by Maryam Hosseini (branch3)
('Nasrin Lotfi',     '6666666666', '09127778899', 'Isfahan, Chahar Bagh',  7, 1),   -- by Ehsan Karimi (branch4)
('Parviz Faghihi',   '7777777777', '09128889900', 'Kashan, Bazaar',        9, 1);   -- by Amir Tavakoli (branch5)

-- Vault customers (one per branch)
INSERT INTO customer (full_name, national_code, phone_number, address, registered_by, is_active) VALUES
('Branch Vault 1','VAULT0000000001','0000000000','System Vault',1,1),
('Branch Vault 2','VAULT0000000002','0000000000','System Vault',1,1),
('Branch Vault 3','VAULT0000000003','0000000000','System Vault',1,1),
('Branch Vault 4','VAULT0000000004','0000000000','System Vault',1,1),
('Branch Vault 5','VAULT0000000005','0000000000','System Vault',1,1);

-- Treasury
INSERT INTO customer (full_name, national_code, phone_number, address, registered_by, is_active) VALUES
('Bank Treasury','BANK0000000','0000000000','System Treasury',1,1);

-- Customer logins
INSERT INTO customer_login (customer_id, username, password_hash, status) VALUES
(1, 'hossein',   SHA2('pass123',256), 'active'),
(2, 'zahra',     SHA2('pass123',256), 'active'),
(3, 'mohammad',  SHA2('pass123',256), 'active'),
(5, 'saeed',     SHA2('pass123',256), 'active'),
(6, 'nasrin',    SHA2('pass123',256), 'active'),
(7, 'parviz',    SHA2('pass123',256), 'active');

-- --------------------------------------------------------------------
-- Accounts
-- First, fetch IDs for vault customers and treasury
-- --------------------------------------------------------------------
SET @v1 = (SELECT id FROM customer WHERE national_code='VAULT0000000001');
SET @v2 = (SELECT id FROM customer WHERE national_code='VAULT0000000002');
SET @v3 = (SELECT id FROM customer WHERE national_code='VAULT0000000003');
SET @v4 = (SELECT id FROM customer WHERE national_code='VAULT0000000004');
SET @v5 = (SELECT id FROM customer WHERE national_code='VAULT0000000005');
SET @treasury_cust = (SELECT id FROM customer WHERE national_code='BANK0000000');

-- Branch vault accounts
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('VAULT1111111111', @v1, 1, 100000000000.00, 1, CURDATE(), 'active'),
('VAULT2222222222', @v2, 1, 100000000000.00, 1, CURDATE(), 'active'),
('VAULT3333333333', @v3, 1, 100000000000.00, 1, CURDATE(), 'active'),
('VAULT4444444444', @v4, 1, 100000000000.00, 1, CURDATE(), 'active'),
('VAULT5555555555', @v5, 1, 100000000000.00, 1, CURDATE(), 'active');

-- Treasury account
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
('TREASURY0000001', @treasury_cust, 1, 1000000000000.00, 1, CURDATE(), 'active');

-- Customer accounts (each real customer has at least one account)
INSERT INTO account (account_number, customer_id, account_type_id, balance, openend_by, opening_date, status) VALUES
-- Hossein Ahmadi (Tehran Central)
('ACC1000000000001', 1, 1, 15000000.00, 1, CURDATE(), 'active'),  -- Savings
('ACC1000000000002', 1, 2,  5000000.00, 1, CURDATE(), 'active'),  -- Current
-- Zahra Moradi (Isfahan Central)
('ACC2000000000001', 2, 3, 25000000.00, 7, CURDATE(), 'active'),  -- Fixed Deposit
('ACC2000000000002', 2, 1,  8000000.00, 7, CURDATE(), 'active'),  -- Savings
-- Mohammad Karimi (Kashan)
('ACC3000000000001', 3, 4, 10000000.00, 9, CURDATE(), 'active'),  -- Short-term
-- Leila Ebrahimi (inactive, no account)
-- Saeed Rahimi (Tehran Northern)
('ACC4000000000001', 5, 1, 12000000.00, 6, CURDATE(), 'active'),  -- Savings
-- Nasrin Lotfi (Isfahan Central)
('ACC5000000000001', 6, 2, 3000000.00, 8, CURDATE(), 'active'),   -- Current
-- Parviz Faghihi (Kashan)
('ACC6000000000001', 7, 3, 40000000.00, 9, CURDATE(), 'active');  -- Fixed Deposit

-- --------------------------------------------------------------------
-- Cards (at least one per account, some inactive)
-- Use account numbers to fetch IDs for card insertion
-- --------------------------------------------------------------------
SET @acc1  = (SELECT id FROM account WHERE account_number='ACC1000000000001');
SET @acc2  = (SELECT id FROM account WHERE account_number='ACC1000000000002');
SET @acc3  = (SELECT id FROM account WHERE account_number='ACC2000000000001');
SET @acc4  = (SELECT id FROM account WHERE account_number='ACC2000000000002');
SET @acc5  = (SELECT id FROM account WHERE account_number='ACC3000000000001');
SET @acc6  = (SELECT id FROM account WHERE account_number='ACC4000000000001');
SET @acc7  = (SELECT id FROM account WHERE account_number='ACC5000000000001');
SET @acc8  = (SELECT id FROM account WHERE account_number='ACC6000000000001');

INSERT INTO card (account_id, card_number, cvv2, expiry_date, status, issued_at) VALUES
(@acc1, '5022291111000001', '111', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc1, '5022291111000002', '222', DATE_ADD(CURDATE(), INTERVAL 2 YEAR), 'inactive', NOW()), -- lost card
(@acc2, '5022291111000003', '333', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc3, '5022292222000001', '444', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc4, '5022292222000002', '555', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc5, '5022293333000001', '666', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc6, '5022294444000001', '777', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc7, '5022295555000001', '888', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW()),
(@acc8, '5022296666000001', '999', DATE_ADD(CURDATE(), INTERVAL 3 YEAR), 'active', NOW());

-- --------------------------------------------------------------------
-- Transactions (mix of deposit, withdrawal, transfer, interest)
-- We'll rely on triggers to adjust balances automatically.
-- --------------------------------------------------------------------
SET @vault1  = (SELECT id FROM account WHERE account_number='VAULT1111111111');
SET @vault4  = (SELECT id FROM account WHERE account_number='VAULT4444444444');
SET @vault5  = (SELECT id FROM account WHERE account_number='VAULT5555555555');
SET @treasury = (SELECT id FROM account WHERE account_number='TREASURY0000001');

-- Deposits
INSERT INTO `transaction` (from_account_id, to_account_id, amount, transaction_type, description, created_by, created_at, status) VALUES
(@vault1, @acc1, 2000000.00, 'deposit', 'Initial deposit', 2, NOW(), 'completed'),            -- Sara Mohammadi (Tehran Central)
(@vault4, @acc3, 5000000.00, 'deposit', 'Cash deposit', 8, NOW(), 'completed'),                 -- Fatemeh Ghasemi (Isfahan)
(@vault5, @acc5, 1500000.00, 'deposit', 'Opening deposit', 9, NOW(), 'completed');               -- Amir Tavakoli (Kashan)

-- Withdrawals
INSERT INTO `transaction` (from_account_id, to_account_id, amount, transaction_type, description, created_by, created_at, status) VALUES
(@acc1, @vault1, 500000.00, 'withdrawal', 'ATM cash', 2, NOW(), 'completed'),
(@acc4, @vault4, 1000000.00, 'withdrawal', 'Over-the-counter', 8, NOW(), 'completed');

-- Transfers between customer accounts
INSERT INTO `transaction` (from_account_id, to_account_id, amount, transaction_type, description, created_by, created_at, status) VALUES
(@acc2, @acc1, 1000000.00, 'transfer', 'Move to savings', 2, NOW(), 'completed'),               -- Hossein's current -> savings
(@acc6, @acc4, 2000000.00, 'transfer', 'Transfer to Zahra', 2, NOW(), 'completed');             -- Saeed's savings -> Zahra's savings

-- Interest payments (from treasury)
INSERT INTO `transaction` (from_account_id, to_account_id, amount, transaction_type, description, created_by, created_at, status) VALUES
(@treasury, @acc1, 12500.00, 'interest', 'Monthly interest', 1, NOW(), 'completed'),
(@treasury, @acc3, 21000.00, 'interest', 'Monthly interest', 1, NOW(), 'completed'),
(@treasury, @acc6, 10000.00, 'interest', 'Monthly interest', 1, NOW(), 'completed');

-- --------------------------------------------------------------------
-- Loan Requests
-- One pending, one approved (with installments), one rejected
-- --------------------------------------------------------------------
-- Pending loan for Hossein Ahmadi (customer1)
INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status) VALUES
(1, 1, 100000000.00, 24, NOW(), 'pending');

-- Approved loan for Zahra Moradi (customer2) – Car loan, 36 months
INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status, approved_by, approved_at) VALUES
(2, 3, 500000000.00, 36, NOW() - INTERVAL 2 DAY, 'approved', 7, NOW());
SET @approved1 = LAST_INSERT_ID();
-- Installments: some future, one overdue unpaid, one paid
INSERT INTO installment (loan_request_id, due_date, amount, paid_amount, status) VALUES
(@approved1, DATE_ADD(CURDATE(), INTERVAL 1 MONTH), 17800000.00, 0, 'unpaid'),
(@approved1, DATE_ADD(CURDATE(), INTERVAL 2 MONTH), 17800000.00, 0, 'unpaid'),
(@approved1, DATE_SUB(CURDATE(), INTERVAL 5 DAY), 17800000.00, 0, 'unpaid'),   -- overdue
(@approved1, DATE_SUB(CURDATE(), INTERVAL 35 DAY), 17800000.00, 17800000.00, 'paid');

-- Rejected loan for Mohammad Karimi (customer3)
INSERT INTO loan_request (customer_id, loan_type_id, amount, installments, requested_at, status, approved_by, approved_at) VALUES
(3, 2, 2000000000.00, 96, NOW() - INTERVAL 5 DAY, 'rejected', 6, NOW());
