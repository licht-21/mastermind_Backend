-- Phase 2: archive, due date, user settings
USE saving_db;

ALTER TABLE savings_goals
    ADD COLUMN due_date DATE NULL AFTER current_amount,
    ADD COLUMN is_archived TINYINT(1) NOT NULL DEFAULT 0 AFTER due_date,
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
