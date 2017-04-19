PRAGMA foreign_keys = ON;

CREATE TABLE account (
    acc_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    acc_name     VARCHAR(255) NOT NULL,
    acc_currency CHAR(3)
);

CREATE TABLE category (
    cat_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    cat_name VARCHAR(255) NOT NULL
);

CREATE TABLE transact (
    trn_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trn_created     DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    trn_date        DATETIME DEFAULT CURRENT_TIMESTAMP,
    trn_amount      DECIMAL(7,2),
    trn_description VARCHAR(255),
    trn_payee       VARCHAR(255),
    acc_id          INTEGER NOT NULL REFERENCES account(acc_id) ON DELETE CASCADE,
    cat_id          INTEGER REFERENCES category(cat_id) ON DELETE SET NULL
);
