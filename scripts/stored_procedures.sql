CREATE OR REPLACE FUNCTION calculate_rental_cost(zone_id INT, start_date DATE, end_date DATE)
RETURNS DECIMAL AS $$
DECLARE
    zone_square INT2;
    base_price DECIMAL := 100.00; 
    days_count INT;
BEGIN
    SELECT zone_square INTO zone_square FROM zone WHERE zone_id = zone_id;
    days_count := (end_date - start_date) + 1;
    RETURN zone_square * base_price * days_count;
END;
$$ LANGUAGE plpgsql;