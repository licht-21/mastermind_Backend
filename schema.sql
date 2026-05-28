-- =============================================================================
-- Saving Project – complete MySQL schema (mastermind backend)
-- Run in MySQL Workbench or: mysql -u root -p < schema.sql
--
-- Matches: app/routes.py (Flask API) + SavingProject Android app
-- Database name must match config.py → DB_NAME = "saving_db"
-- =============================================================================

CREATE DATABASE IF NOT EXISTS saving_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE saving_db;

-- -----------------------------------------------------------------------------
-- 1) users – sign up / login
--    Android JSON: username, email, password
--    Stored columns: name (from username), email, password
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(80)  NOT NULL COMMENT 'Display name from app signup',
    email      VARCHAR(120) NOT NULL,
    password   VARCHAR(255) NOT NULL COMMENT 'Plain text in current Flask; hash for production',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_name (name)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 2) savings_goals – main savings list (active + archived)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS savings_goals (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    name            VARCHAR(120) NOT NULL,
    target_amount   DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    current_amount  DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    due_date        DATE NULL,
    is_archived     TINYINT(1) NOT NULL DEFAULT 0,
    archived_at     TIMESTAMP NULL DEFAULT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_savings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    KEY idx_savings_user (user_id),
    KEY idx_savings_archived (user_id, is_archived)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3) deposits – history of money added to each goal
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS deposits (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    goal_id     INT NOT NULL,
    amount      DECIMAL(12, 2) NOT NULL,
    note        VARCHAR(255) NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_deposit_goal
        FOREIGN KEY (goal_id) REFERENCES savings_goals(id)
        ON DELETE CASCADE,
    KEY idx_deposit_goal (goal_id),
    KEY idx_deposit_created (created_at)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4) user_settings – dark mode, date format (Settings screen)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_settings (
    user_id       INT PRIMARY KEY,
    dark_mode     TINYINT(1) NOT NULL DEFAULT 0,
    date_format   VARCHAR(20) NOT NULL DEFAULT 'DD/MM/YYYY',
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_settings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- Optional: verify tables
-- -----------------------------------------------------------------------------
-- SHOW TABLES;
-- DESCRIBE users;
-- DESCRIBE savings_goals;
-- DESCRIBE deposits;
-- DESCRIBE user_settings;
