CREATE OR REPLACE PROCEDURE AddNewEvent(
 p_zone_id INT,
 p_organizer_id INT,
 p_event_date_time DATE,
 p_event_format VARCHAR(100),
 p_event_exhibits VARCHAR(100),
 OUT result_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
 zone_exists BOOLEAN;
 organizer_exists BOOLEAN;
BEGIN
 SELECT EXISTS (SELECT 1 FROM Zone WHERE zone_id = p_zone_id)
INTO zone_exists;
 SELECT EXISTS (SELECT 1 FROM Organizer WHERE organizer_id =
p_organizer_id) INTO organizer_exists;
 IF NOT zone_exists THEN
 result_message := 'ошибка: зона с указанным ID не существует.';
 RETURN;
 ELSIF NOT organizer_exists THEN
 result_message := 'ошибка: организатор с указанным ID не
существует.';
 RETURN;
 ELSE
 INSERT INTO Event (
 zone_id,
 organizer_id,
 event_date_time,
 event_format,
 event_exhibits
 ) VALUES (
 p_zone_id,
 p_organizer_id,
 p_event_date_time,
 p_event_format,
 p_event_exhibits
 );
 result_message := 'Событие успешно добавлено.';

 END IF;
END;
$$;


CREATE OR REPLACE FUNCTION check_review_rating()
RETURNS TRIGGER AS $$
BEGIN
 IF NEW.review_rating < 1 OR NEW.review_rating > 5 THEN
 RAISE EXCEPTION 'Оценка должна быть от 1 до 5';
 END IF;
 RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_check_review_rating
BEFORE INSERT OR UPDATE ON Review
FOR EACH ROW
EXECUTE FUNCTION check_review_rating();
CREATE TRIGGER trigger_set_review_created_at
BEFORE INSERT ON Review
FOR EACH ROW
EXECUTE FUNCTION set_review_created_at();



