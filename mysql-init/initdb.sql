

--                 Database 
CREATE DATABASE IF NOT EXISTS bank;


-- People:  Persons, Employees, Customers,
--          EmployeePositions, CustomerTypes

USE bank;

CREATE TABLE IF NOT EXISTS Persons
(
    person_id           INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    address_id          INT NOT NULL,
    last_name           VARCHAR(255) NOT NULL,
    first_name          VARCHAR(255) NOT NULL,
    date_of_birth       DATE NOT NULL,
    email               VARCHAR(255) UNIQUE,
    phone_number        VARCHAR(50) UNIQUE NOT NULL,
    ssn                 VARCHAR(50) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Employees
(
    employee_id         INT NOT NULL PRIMARY KEY,  -- references Persons.person_id (no AUTO_INCREMENT)
    position_id         INT NOT NULL,
    branch_id           INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS EmployeePositions
(
    position_id         INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    employee_position   VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Customers
(
    customer_id         INT NOT NULL PRIMARY KEY,  -- references Persons.person_id (no AUTO_INCREMENT)
    type_id             INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS CustomerTypes
(
    type_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    customer_type       VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- Bank elements:   Branches, Accounts,
--                  AccountTypes, AccountStatus,
-- =========================

CREATE TABLE IF NOT EXISTS Branches
(
    branch_id           INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    address_id          INT NOT NULL,
    branch_name         VARCHAR(255) UNIQUE NOT NULL,
    swift_code          VARCHAR(11) UNIQUE NOT NULL,
    phone_number        VARCHAR(50) UNIQUE NOT NULL,
    CHECK (CHAR_LENGTH(swift_code) = 8 OR CHAR_LENGTH(swift_code) = 11)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Accounts
(
    account_id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    type_id             INT NOT NULL,
    status_id           INT NOT NULL,
    customer_id         INT NOT NULL,
    branch_id           INT NOT NULL,
    account_number      VARCHAR(100) UNIQUE NOT NULL,
    balance             DECIMAL(18,2) NOT NULL,
    date_opened         DATE NOT NULL,
    date_closed         DATE,
    CHECK (date_closed IS NULL OR date_closed >= date_opened)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS AccountTypes
(
    type_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    account_type        VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS AccountStatus
(
    status_id           INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    account_status      VARCHAR(255) UNIQUE NOT NULL,
    reason              VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- Cash flows:  Loans, LoanPayments, Transactions,
--              LoanTypes, LoanStatus, TransactionTypes
-- =========================

CREATE TABLE IF NOT EXISTS Loans
(
    loan_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    type_id             INT NOT NULL,
    status_id           INT NOT NULL,
    customer_id         INT NOT NULL,
    amount              DECIMAL(18,2) NOT NULL,
    interest_rate       DECIMAL(8,4) NOT NULL,
    term                INT NOT NULL, -- months
    loan_start_date     DATE NOT NULL,
    loan_end_date       DATE NOT NULL,
    CHECK (amount >= 0 AND term >= 0 AND loan_end_date > loan_start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LoanPayments
(
    loan_payment_id     INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    loan_id             INT NOT NULL,
    scheduled_amount    DECIMAL(18,2) NOT NULL,
    principal           DECIMAL(18,2) NOT NULL,
    interest            DECIMAL(18,2) NOT NULL,
    actual_amount       DECIMAL(18,2),
    scheduled_date      DATE NOT NULL,
    paid_date           DATE,
    CHECK (scheduled_amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Transactions
(
    transaction_id      INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    type_id             INT NOT NULL,
    loan_payment_id     INT,
    employee_id         INT,
    from_account_id     INT NOT NULL,
    to_account_id       INT,
    amount              DECIMAL(18,2) NOT NULL,
    transaction_date    DATE NOT NULL,
    CHECK (amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LoanTypes
(
    type_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    loan_type           VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS LoanStatus
(
    status_id           INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    loan_status         VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS TransactionTypes
(
    type_id             INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    transaction_type    VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- Others:  Addresses, AddressTypes
-- =========================

CREATE TABLE IF NOT EXISTS Addresses
(
    address_id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    address_type_id     INT NOT NULL,
    street              VARCHAR(255) NOT NULL,
    postal_code         VARCHAR(20) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    country             VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS AddressTypes
(
    address_type_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    address_type    VARCHAR(255) UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================
-- Foreign key constraints (added after table creation)
-- =========================

ALTER TABLE Persons
  ADD CONSTRAINT fk_persons_address
    FOREIGN KEY (address_id) REFERENCES Addresses(address_id);

ALTER TABLE Employees
  ADD CONSTRAINT fk_employees_person
    FOREIGN KEY (employee_id) REFERENCES Persons(person_id) ON DELETE CASCADE,
  ADD CONSTRAINT fk_employees_position
    FOREIGN KEY (position_id) REFERENCES EmployeePositions(position_id),
  ADD CONSTRAINT fk_employees_branch
    FOREIGN KEY (branch_id) REFERENCES Branches(branch_id);

ALTER TABLE Customers
  ADD CONSTRAINT fk_customers_person
    FOREIGN KEY (customer_id) REFERENCES Persons(person_id) ON DELETE CASCADE,
  ADD CONSTRAINT fk_customers_type
    FOREIGN KEY (type_id) REFERENCES CustomerTypes(type_id);

ALTER TABLE Branches
  ADD CONSTRAINT fk_branches_address
    FOREIGN KEY (address_id) REFERENCES Addresses(address_id);

ALTER TABLE Accounts
  ADD CONSTRAINT fk_accounts_type
    FOREIGN KEY (type_id) REFERENCES AccountTypes(type_id),
  ADD CONSTRAINT fk_accounts_status
    FOREIGN KEY (status_id) REFERENCES AccountStatus(status_id),
  ADD CONSTRAINT fk_accounts_customer
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE,
  ADD CONSTRAINT fk_accounts_branch
    FOREIGN KEY (branch_id) REFERENCES Branches(branch_id);

ALTER TABLE Loans
  ADD CONSTRAINT fk_loans_type
    FOREIGN KEY (type_id) REFERENCES LoanTypes(type_id),
  ADD CONSTRAINT fk_loans_status
    FOREIGN KEY (status_id) REFERENCES LoanStatus(status_id),
  ADD CONSTRAINT fk_loans_customer
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id);

ALTER TABLE LoanPayments
  ADD CONSTRAINT fk_loanpayments_loan
    FOREIGN KEY (loan_id) REFERENCES Loans(loan_id);

ALTER TABLE Transactions
  ADD CONSTRAINT fk_transactions_type
    FOREIGN KEY (type_id) REFERENCES TransactionTypes(type_id),
  ADD CONSTRAINT fk_transactions_loanpayment
    FOREIGN KEY (loan_payment_id) REFERENCES LoanPayments(loan_payment_id),
  ADD CONSTRAINT fk_transactions_employee
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
  ADD CONSTRAINT fk_transactions_from_account
    FOREIGN KEY (from_account_id) REFERENCES Accounts(account_id),
  ADD CONSTRAINT fk_transactions_to_account
    FOREIGN KEY (to_account_id) REFERENCES Accounts(account_id);

ALTER TABLE Addresses
  ADD CONSTRAINT fk_addresses_addresstype
    FOREIGN KEY (address_type_id) REFERENCES AddressTypes(address_type_id);

