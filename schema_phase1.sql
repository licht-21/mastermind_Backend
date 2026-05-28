-- Phase 1: savings goals (run in MySQL Workbench if table missing)
USE saving_db;

CREATE TABLE IF NOT EXISTS savings_goals (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    name            VARCHAR(120) NOT NULL,
    target_amount   DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    current_amount  DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_savings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    KEY idx_savings_user (user_id)
) ENGINE=InnoDB;
