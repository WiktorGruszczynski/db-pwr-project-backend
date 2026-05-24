-- Włącz rozszerzenie pgcrypto dla gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- TABELE
-- ==========================================

-- 1. Tabela users_user
CREATE TABLE users_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN')),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE
);

-- 2. Tabela session
CREATE TABLE session (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    expires_at TIMESTAMP NOT NULL
);

-- 3. Tabela verification_code
CREATE TABLE verification_code (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    code VARCHAR(100) NOT NULL,
    code_type VARCHAR(50) NOT NULL CHECK (code_type IN ('EMAIL_VERIFICATION', 'PASSWORD_RESET')),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela users_follower
CREATE TABLE users_follower (
    follower_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    followed_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, followed_id),
    CONSTRAINT cannot_follow_self CHECK (follower_id <> followed_id)
);

-- 5. Tabela leaderboard_entry
CREATE TABLE leaderboard_entry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    score INTEGER NOT NULL DEFAULT 0 CHECK (score >= 0),
    rank INTEGER CHECK (rank > 0),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabela meals_meal
CREATE TABLE meals_meal (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
);

-- 7. Tabela recipes_recipe
CREATE TABLE recipes_recipe (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    average_rating DOUBLE PRECISION DEFAULT 0.0 CHECK (average_rating >= 0 AND average_rating <= 5),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
);

-- 8. Tabela products_product
CREATE TABLE products_product (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL CHECK (quantity > 0),
    quantity_unit VARCHAR(50) NOT NULL,
    fat DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (fat >= 0),
    carbohydrates DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (carbohydrates >= 0),
    protein DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (protein >= 0),
    energy_kcal DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (energy_kcal >= 0),
    is_global BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    recipe_id UUID REFERENCES recipes_recipe(id) ON DELETE SET NULL
);

-- 9. Tabela meals_mealitem
CREATE TABLE meals_mealitem (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portion DOUBLE PRECISION NOT NULL CHECK (portion > 0),
    meal_id UUID NOT NULL REFERENCES meals_meal(id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products_product(id) ON DELETE CASCADE
);

-- 10. Tabela recipes_ingredient
CREATE TABLE recipes_ingredient (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quantity DOUBLE PRECISION NOT NULL CHECK (quantity > 0),
    unit VARCHAR(50) NOT NULL,
    product_id UUID NOT NULL REFERENCES products_product(id) ON DELETE RESTRICT,
    recipe_id UUID NOT NULL REFERENCES recipes_recipe(id) ON DELETE CASCADE
);

-- 11. Tabela recipes_rating
CREATE TABLE recipes_rating (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rating SMALLINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    recipe_id UUID NOT NULL REFERENCES recipes_recipe(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    UNIQUE (recipe_id, user_id)
);

-- 12. Tabela recipes_comment
CREATE TABLE recipes_comment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    recipe_id UUID NOT NULL REFERENCES recipes_recipe(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES recipes_comment(id) ON DELETE CASCADE
);

-- ==========================================
-- FUNKCJE I WYZWALACZE (TRIGGERS)
-- ==========================================

-- Funkcja obliczająca średnią ocenę dla przepisu
CREATE OR REPLACE FUNCTION update_recipe_average_rating()
RETURNS TRIGGER AS $$
DECLARE
    target_recipe_id UUID;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        target_recipe_id := OLD.recipe_id;
    ELSE
        target_recipe_id := NEW.recipe_id;
    END IF;

    -- Używamy CAST(AVG(...) AS DOUBLE PRECISION), aby wynik pasował do typu kolumny
    UPDATE recipes_recipe
    SET average_rating = (
        SELECT COALESCE(CAST(AVG(rating) AS DOUBLE PRECISION), 0.0) 
        FROM recipes_rating 
        WHERE recipe_id = target_recipe_id
    )
    WHERE id = target_recipe_id;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger wywołujący funkcję po zmianach w tabeli ocen
CREATE TRIGGER trigger_update_average_rating
AFTER INSERT OR UPDATE OR DELETE ON recipes_rating
FOR EACH ROW
EXECUTE FUNCTION update_recipe_average_rating();