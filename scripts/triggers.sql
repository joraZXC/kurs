CREATE OR REPLACE FUNCTION block_expired_contracts()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.contract_term < CURRENT_DATE AND NEW.contract_conditions LIKE '%pending%' THEN
            NEW.contract_conditions := 'cancelled';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER contract_expiration
    BEFORE UPDATE ON Contract
    FOR EACH ROW EXECUTE FUNCTION block_expired_contracts();