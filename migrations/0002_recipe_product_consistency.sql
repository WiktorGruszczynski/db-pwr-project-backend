-- ==========================================
-- SPÓJNOŚĆ AUTO-PRODUKTÓW Z PRZEPISAMI
-- ==========================================
-- Auto-produkt (products_product z recipe_id IS NOT NULL) trzyma wartości
-- odżywcze obliczone ze składników przepisu, znormalizowane do 100 g.
--
-- Te triggery pilnują, żeby auto-produkt był zawsze aktualny:
--   1) gdy zmienia się skład przepisu (recipes_ingredient INSERT/UPDATE/DELETE),
--   2) gdy zmieniają się wartości produktu używanego jako składnik
--      (propagacja w górę łańcucha — np. zmiana w "sos sojowy" przelicza
--      auto-produkt "sos teryiaki", a potem "kurczak teryiaki").

-- ------------------------------------------------------------
-- Funkcja przeliczająca auto-produkt jednego przepisu
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION recalc_recipe_auto_product(p_recipe_id UUID)
RETURNS VOID AS $$
DECLARE
    total_qty       DOUBLE PRECISION;
    total_fat       DOUBLE PRECISION;
    total_carbs     DOUBLE PRECISION;
    total_protein   DOUBLE PRECISION;
    total_kcal      DOUBLE PRECISION;
BEGIN
    SELECT
        SUM(i.quantity),
        SUM(p.fat            * i.quantity / p.quantity),
        SUM(p.carbohydrates  * i.quantity / p.quantity),
        SUM(p.protein        * i.quantity / p.quantity),
        SUM(p.energy_kcal    * i.quantity / p.quantity)
    INTO total_qty, total_fat, total_carbs, total_protein, total_kcal
    FROM recipes_ingredient i
    JOIN products_product   p ON p.id = i.product_id
    WHERE i.recipe_id = p_recipe_id;

    -- Brak składników (np. w trakcie pełnej podmiany) — nic nie aktualizujemy.
    IF total_qty IS NULL OR total_qty = 0 THEN
        RETURN;
    END IF;

    -- Normalizacja do 100 g (konwencja całej bazy produktów).
    UPDATE products_product
    SET quantity      = 100,
        quantity_unit = 'g',
        fat           = total_fat     * 100.0 / total_qty,
        carbohydrates = total_carbs   * 100.0 / total_qty,
        protein       = total_protein * 100.0 / total_qty,
        energy_kcal   = total_kcal    * 100.0 / total_qty
    WHERE recipe_id = p_recipe_id;
END;
$$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- Trigger #1: zmiana składników -> przelicz auto-produkt przepisu
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION trg_ingredient_changed()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        PERFORM recalc_recipe_auto_product(OLD.recipe_id);
        RETURN OLD;
    END IF;

    PERFORM recalc_recipe_auto_product(NEW.recipe_id);

    -- Rzadki przypadek: ktoś zmienił przypisanie składnika do innego przepisu.
    IF (TG_OP = 'UPDATE' AND OLD.recipe_id IS DISTINCT FROM NEW.recipe_id) THEN
        PERFORM recalc_recipe_auto_product(OLD.recipe_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_ingredient_changed
AFTER INSERT OR UPDATE OR DELETE ON recipes_ingredient
FOR EACH ROW
EXECUTE FUNCTION trg_ingredient_changed();


-- ------------------------------------------------------------
-- Trigger #2: zmiana wartości w produkcie -> propagacja w górę
-- Działa na wartościach odżywczych i quantity (bo skalowanie składników
-- używa p.quantity). Klauzula WHEN unika rekursji, gdy przeliczenie
-- wyprodukowało te same wartości; pg_trigger_depth jest ostatecznym
-- bezpiecznikiem na patologiczne cykle.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION trg_product_propagate()
RETURNS TRIGGER AS $$
DECLARE
    dependent_recipe UUID;
BEGIN
    IF pg_trigger_depth() > 10 THEN
        RAISE EXCEPTION
            'Wykryto cykliczną zależność produktów/przepisów (głębokość > 10) dla produktu %',
            NEW.id;
    END IF;

    FOR dependent_recipe IN
        SELECT DISTINCT recipe_id
        FROM recipes_ingredient
        WHERE product_id = NEW.id
    LOOP
        PERFORM recalc_recipe_auto_product(dependent_recipe);
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_product_nutrition_changed
AFTER UPDATE OF quantity, fat, carbohydrates, protein, energy_kcal
ON products_product
FOR EACH ROW
WHEN (OLD.quantity      IS DISTINCT FROM NEW.quantity
   OR OLD.fat           IS DISTINCT FROM NEW.fat
   OR OLD.carbohydrates IS DISTINCT FROM NEW.carbohydrates
   OR OLD.protein       IS DISTINCT FROM NEW.protein
   OR OLD.energy_kcal   IS DISTINCT FROM NEW.energy_kcal)
EXECUTE FUNCTION trg_product_propagate();


-- ------------------------------------------------------------
-- Backfill: przelicz istniejące auto-produkty, żeby dane były zgodne
-- z nową logiką (idempotentne — Python liczy tak samo).
-- ------------------------------------------------------------
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT DISTINCT recipe_id FROM products_product WHERE recipe_id IS NOT NULL
    LOOP
        PERFORM recalc_recipe_auto_product(r.recipe_id);
    END LOOP;
END $$;
