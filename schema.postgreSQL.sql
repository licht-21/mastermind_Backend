-- =============================================================================
-- SAVING PROJECT - Complete MySQL Schema (All-in-One)
-- =============================================================================
-- 
-- SETUP INSTRUCTIONS:
-- 1. Open MySQL Workbench or terminal
-- 2. Copy & paste the ENTIRE contents of this file
-- 3. Execute it all at once
-- 
-- Terminal option:
--   mysql -u root -p < SCHEMA_COMPLETE.sql
-- 
-- Expected result: 5 tables created in 'saving_db' database
-- - users
-- - savings_goals
-- - deposits
-- - user_settings
--
-- Database: saving_db (matches config.py)
-- Character set: UTF-8 (utf8mb4)
-- =============================================================================

-- Step 1: Create database
-- =============================================================================
CREATE DATABASE IF NOT EXISTS saving_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE saving_db;


-- Step 2: Create users table
-- =============================================================================
-- Purpose: Store user authentication info
-- Used by: /register, /login endpoints
-- Android app data: username, email, password → stored as name, email, password
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(80)  NOT NULL COMMENT 'Display name from app signup',
    email      VARCHAR(120) NOT NULL,
    password   VARCHAR(255) NOT NULL COMMENT 'Hash in production; plain text in dev',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE KEY uq_users_email (email),
    KEY idx_users_name (name)
) ENGINE=InnoDB
  CHARSET utf8mb4
  COLLATE utf8mb4_unicode_ci;


-- Step 3: Create savings_goals table
-- =============================================================================
-- Purpose: Store all savings goals (active + archived) for each user
-- Used by: /goals, /goal/<id>, /goal/create, /goal/<id>/update
-- Key columns:
--   - target_amount: What user is saving towards
--   - current_amount: How much they've saved so far
--   - due_date: Optional deadline for the goal
--   - is_archived: 0 = active, 1 = archived (shows on separate screen)
-- =============================================================================
CREATE TABLE IF NOT EXISTS savings_goals (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    name            VARCHAR(120) NOT NULL COMMENT 'Goal name (e.g., "Vacation", "Car")',
    target_amount   DECIMAL(12, 2) NOT NULL DEFAULT 0.00 COMMENT 'Target amount to save',
    current_amount  DECIMAL(12, 2) NOT NULL DEFAULT 0.00 COMMENT 'Amount saved so far',
    due_date        DATE NULL COMMENT 'Optional deadline',
    is_archived     TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=active, 1=archived',
    archived_at     TIMESTAMP NULL DEFAULT NULL COMMENT 'When it was archived',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_savings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    
    -- Indexes for fast queries
    KEY idx_savings_user (user_id),
    KEY idx_savings_archived (user_id, is_archived) COMMENT 'Fast lookup of active goals'
) ENGINE=InnoDB
  CHARSET utf8mb4
  COLLATE utf8mb4_unicode_ci;


-- Step 4: Create deposits table
-- =============================================================================
-- Purpose: Store transaction history for each savings goal
-- Used by: /goal/<id>/deposits, /goal/<id>/deposit (POST)
-- Relationship: Many deposits per goal (one-to-many)
-- Auto-updates: savings_goals.current_amount when deposits are added
-- =============================================================================
CREATE TABLE IF NOT EXISTS deposits (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    goal_id     INT NOT NULL,
    amount      DECIMAL(12, 2) NOT NULL COMMENT 'Amount deposited',
    note        VARCHAR(255) NULL COMMENT 'Optional memo (e.g., "Weekly savings")',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_deposit_goal
        FOREIGN KEY (goal_id) REFERENCES savings_goals(id)
        ON DELETE CASCADE,
    
    -- Indexes for fast queries
    KEY idx_deposit_goal (goal_id),
    KEY idx_deposit_created (created_at) COMMENT 'Fast date-based lookups'
) ENGINE=InnoDB
  CHARSET utf8mb4
  COLLATE utf8mb4_unicode_ci;


-- Step 5: Create user_settings table
-- =============================================================================
-- Purpose: Store user preferences (dark mode, date format)
-- Used by: /settings (GET/POST)
-- Relationship: One settings row per user (1-to-1 with users table)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_settings (
    user_id       INT PRIMARY KEY,
    dark_mode     TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=light, 1=dark',
    date_format   VARCHAR(20) NOT NULL DEFAULT 'DD/MM/YYYY' COMMENT 'Date display format',
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_settings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB
  CHARSET utf8mb4
  COLLATE utf8mb4_unicode_ci;


-- =============================================================================
-- VERIFICATION QUERIES (copy & run each to test):
-- =============================================================================
-- SELECT 'Setup complete!' as status;
-- SHOW TABLES;
-- DESCRIBE users;
-- DESCRIBE savings_goals;
-- DESCRIBE deposits;
-- DESCRIBE user_settings;
-- =============================================================================
