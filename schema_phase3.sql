-- Phase 3: deposit history
USE saving_db;

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
