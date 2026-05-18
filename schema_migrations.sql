-- =============================================================================
-- Saving Project – migrations (existing database already on Phase 1 only)
-- Run ONLY if you already have saving_db without Phase 2/3 columns.
-- Fresh install: use schema.sql instead.
-- =============================================================================

USE saving_db;

-- Phase 2: archive + due date + settings
-- Skip any line that errors with "Duplicate column name"
ALTER TABLE savings_goals
    ADD COLUMN due_date DATE NULL AFTER current_amount;
ALTER TABLE savings_goals
    ADD COLUMN is_archived TINYINT(1) NOT NULL DEFAULT 0 AFTER due_date;
ALTER TABLE savings_goals
    ADD COLUMN archived_at TIMESTAMP NULL DEFAULT NULL AFTER is_archived;

CREATE TABLE IF NOT EXISTS user_settings (
    user_id       INT PRIMARY KEY,
    dark_mode     TINYINT(1) NOT NULL DEFAULT 0,
    date_format   VARCHAR(20) NOT NULL DEFAULT 'DD/MM/YYYY',
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_settings_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Phase 3: deposit history
CREATE TABLE IF NOT EXISTS deposits (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    goal_id     INT NOT NULL,
    amount      DECIMAL(12, 2) NOT NULL,
    note        VARCHAR(255) NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_deposit_goal
        FOREIGN KEY (goal_id) REFERENCES savings_goals(id)
        ON DELETE CASCADE,
    KEY idx_deposit_goal (goal_id)
) ENGINE=InnoDB;
