-- =============================================================================
-- SAVING PROJECT - Complete PostgreSQL Schema (Supabase)
-- =============================================================================
-- 
-- SETUP INSTRUCTIONS:
-- 1. Go to Supabase dashboard → SQL Editor
-- 2. Create a new query
-- 3. Copy & paste the ENTIRE contents of this file
-- 4. Execute it (or use "Run" button)
-- 
-- Expected result: 5 tables created in your Supabase project
-- - users
-- - savings_goals
-- - deposits
-- - user_settings
--
-- Note: Supabase automatically handles connections and backups
-- Character encoding: UTF-8 (default in PostgreSQL)
-- =============================================================================

-- Step 1: Create users table
-- =============================================================================
-- Purpose: Store user authentication info
-- Used by: /register, /login endpoints
-- Android app data: username, email, password → stored as name, email, password
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);


-- Step 2: Create savings_goals table
-- =============================================================================
-- Purpose: Store all savings goals (active + archived) for each user
-- Used by: /goals, /goal/<id>, /goal/create, /goal/<id>/update
-- Key columns:
--   - target_amount: What user is saving towards
--   - current_amount: How much they've saved so far
--   - due_date: Optional deadline for the goal
--   - is_archived: false = active, true = archived (shows on separate screen)
-- =============================================================================
CREATE TABLE IF NOT EXISTS savings_goals (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(120) NOT NULL,
    target_amount NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    current_amount NUMERIC(12, 2) DEFAULT 0.00 NOT NULL,
    due_date DATE,
    is_archived BOOLEAN DEFAULT FALSE NOT NULL,
    archived_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for fast queries
    CONSTRAINT fk_savings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_savings_user ON savings_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_savings_archived ON savings_goals(user_id, is_archived);


-- Step 3: Create deposits table
-- =============================================================================
-- Purpose: Store transaction history for each savings goal
-- Used by: /goal/<id>/deposits, /goal/<id>/deposit (POST)
-- Relationship: Many deposits per goal (one-to-many)
-- Note: App automatically sums deposits to calculate current_amount
-- =============================================================================
CREATE TABLE IF NOT EXISTS deposits (
    id SERIAL PRIMARY KEY,
    goal_id INT NOT NULL REFERENCES savings_goals(id) ON DELETE CASCADE,
    amount NUMERIC(12, 2) NOT NULL,
    note VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_deposit_goal FOREIGN KEY (goal_id) REFERENCES savings_goals(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_deposit_goal ON deposits(goal_id);
CREATE INDEX IF NOT EXISTS idx_deposit_created ON deposits(created_at);


-- Step 4: Create user_settings table
-- =============================================================================
-- Purpose: Store user preferences (dark mode, date format)
-- Used by: /settings (GET/POST)
-- Relationship: One settings row per user (1-to-1 with users table)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    dark_mode BOOLEAN DEFAULT FALSE NOT NULL,
    date_format VARCHAR(20) DEFAULT 'DD/MM/YYYY' NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT fk_settings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- =============================================================================
-- SUPABASE-SPECIFIC SETUP (Optional - for better development):
-- =============================================================================
-- Uncomment below if you want to enable Row-Level Security (RLS)
-- This ensures users can only see their own data
-- =============================================================================

-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE savings_goals ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE deposits ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- CREATE POLICY "Users can view own data"
--   ON users FOR SELECT USING (auth.uid()::text = id::text);

-- CREATE POLICY "Users can view own goals"
--   ON savings_goals FOR SELECT USING (user_id = auth.uid()::int);

-- CREATE POLICY "Users can view own deposits"
--   ON deposits FOR SELECT USING (goal_id IN (
--     SELECT id FROM savings_goals WHERE user_id = auth.uid()::int
--   ));

-- CREATE POLICY "Users can view own settings"
--   ON user_settings FOR SELECT USING (user_id = auth.uid()::int);


-- =============================================================================
-- VERIFICATION QUERIES (copy & run each to test):
-- =============================================================================
-- SELECT 'Setup complete!' as status;
-- \dt  (shows all tables)
-- SELECT * FROM information_schema.tables WHERE table_schema = 'public';
-- =============================================================================
