-- === Complex ===
CREATE TABLE IF NOT EXISTS complex (
    complex_id SERIAL NOT NULL,
    complex_rigging VARCHAR(100),
    complex_address VARCHAR(100) NOT NULL,
    CONSTRAINT pk_complex PRIMARY KEY (complex_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS complex_pk ON complex (complex_id);

-- === Organizer ===
CREATE TABLE IF NOT EXISTS organizer (
    organizer_id SERIAL NOT NULL,
    user_id INT4 UNIQUE,
    organizer_affiliation VARCHAR(100) NOT NULL,
    organizer_fio VARCHAR(100),
    CONSTRAINT pk_organizer PRIMARY KEY (organizer_id),
    CONSTRAINT fk_organizer_user FOREIGN KEY (user_id)
        REFERENCES auth_user (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS organizer_pk ON organizer (organizer_id);

-- === Contract ===
CREATE TABLE IF NOT EXISTS contract (
    contract_id SERIAL NOT NULL,
    organizer_id INT4,
    contract_conditions VARCHAR(100) NOT NULL,
    contract_cost DECIMAL(10,2) NOT NULL,
    contract_term DATE NOT NULL,
    CONSTRAINT pk_contract PRIMARY KEY (contract_id),
    CONSTRAINT fk_contract_slave_organizer FOREIGN KEY (organizer_id)
        REFERENCES organizer (organizer_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS contract_pk ON contract (contract_id);
CREATE INDEX IF NOT EXISTS slave_fk ON contract (organizer_id);

-- === Employer ===
CREATE TABLE IF NOT EXISTS employer (
    employer_id SERIAL NOT NULL,
    employer_post VARCHAR(100) NOT NULL,
    employer_fio VARCHAR(100),
    CONSTRAINT pk_employer PRIMARY KEY (employer_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS employer_pk ON employer (employer_id);

-- === Zone ===
CREATE TABLE IF NOT EXISTS zone (
    zone_id SERIAL NOT NULL,
    employer_id INT4,
    contract_id INT4,
    complex_id INT4 NOT NULL,
    zone_equipment VARCHAR(100),
    zone_square INT2,
    zone_type VARCHAR(100) NOT NULL,
    event_id INT4,
    CONSTRAINT pk_zone PRIMARY KEY (zone_id),
    CONSTRAINT fk_zone_consists_complex FOREIGN KEY (complex_id)
        REFERENCES complex (complex_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_zone_give_contract FOREIGN KEY (contract_id)
        REFERENCES contract (contract_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_zone_work_employer FOREIGN KEY (employer_id)
        REFERENCES employer (employer_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_zone_event FOREIGN KEY (event_id)
        REFERENCES event (event_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS zone_pk ON zone (zone_id);
CREATE INDEX IF NOT EXISTS work_fk ON zone (employer_id);
CREATE INDEX IF NOT EXISTS give_fk ON zone (contract_id);
CREATE INDEX IF NOT EXISTS consists_fk ON zone (complex_id);
CREATE INDEX IF NOT EXISTS zone_event_fk ON zone (event_id);

-- === Event ===
CREATE TABLE IF NOT EXISTS event (
    event_id SERIAL NOT NULL,
    zone_id INT4 NOT NULL,
    organizer_id INT4 NOT NULL,
    event_date_time DATE NOT NULL,
    event_format VARCHAR(100) NOT NULL,
    event_exhibits VARCHAR(100),
    CONSTRAINT pk_event PRIMARY KEY (event_id),
    CONSTRAINT fk_event_depends_zone FOREIGN KEY (zone_id)
        REFERENCES zone (zone_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_event_act_organizer FOREIGN KEY (organizer_id)
        REFERENCES organizer (organizer_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS event_pk ON event (event_id);
CREATE INDEX IF NOT EXISTS plan_fk ON event (organizer_id);
CREATE INDEX IF NOT EXISTS depends_fk ON event (zone_id);

-- === Man ===
CREATE TABLE IF NOT EXISTS man (
    man_id SERIAL NOT NULL,
    man_fio VARCHAR(100),
    role VARCHAR(20) NOT NULL DEFAULT 'visitor',
    CONSTRAINT pk_man PRIMARY KEY (man_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS man_pk ON man (man_id);

-- === Ticket ===
CREATE TABLE IF NOT EXISTS ticket (
    ticket_id SERIAL NOT NULL,
    user_id INT4 NOT NULL,
    event_id INT4 NOT NULL,
    ticket_number VARCHAR(50) NOT NULL,
    ticket_type VARCHAR(50) NOT NULL,
    ticket_cost DECIMAL(10,2) NOT NULL,
    CONSTRAINT pk_ticket PRIMARY KEY (ticket_id),
    CONSTRAINT fk_ticket_based_event FOREIGN KEY (event_id)
        REFERENCES event (event_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ticket_buy_user FOREIGN KEY (user_id)
        REFERENCES auth_user (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS ticket_pk ON ticket (ticket_id);
CREATE INDEX IF NOT EXISTS buy_fk ON ticket (user_id);
CREATE INDEX IF NOT EXISTS based_fk ON ticket (event_id);

-- === Control ===
CREATE TABLE IF NOT EXISTS control (
    event_id INT4 NOT NULL,
    employer_id INT4 NOT NULL,
    CONSTRAINT pk_control PRIMARY KEY (event_id, employer_id),
    CONSTRAINT fk_control_control_event FOREIGN KEY (event_id)
        REFERENCES event (event_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_control_control_employer FOREIGN KEY (employer_id)
        REFERENCES employer (employer_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS control_pk ON control (event_id, employer_id);
CREATE INDEX IF NOT EXISTS control2_fk ON control (employer_id);
CREATE INDEX IF NOT EXISTS control_fk ON control (event_id);

-- === Review ===
CREATE TABLE IF NOT EXISTS review (
    review_id SERIAL NOT NULL,
    zone_id INT4 NOT NULL,
    event_id INT4 NOT NULL,
    man_id INT4 NOT NULL,
    review_text TEXT NOT NULL,
    rating INT2,
    created_at DATE NOT NULL,
    CONSTRAINT pk_review PRIMARY KEY (review_id),
    CONSTRAINT fk_review_event FOREIGN KEY (event_id)
        REFERENCES event (event_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_review_zone FOREIGN KEY (zone_id)
        REFERENCES zone (zone_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    CONSTRAINT fk_review_man FOREIGN KEY (man_id)
        REFERENCES man (man_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

CREATE UNIQUE INDEX IF NOT EXISTS review_pk ON review (review_id);

-- === Function: calculate_rental_cost ===
CREATE OR REPLACE FUNCTION calculate_rental_cost(zone_id INT, start_date DATE, end_date DATE)
    RETURNS DECIMAL AS $$
    DECLARE
        zone_square INT2;
        base_price DECIMAL := 100.00; -- Базовая ставка за кв.м
        days_count INT;
    BEGIN
        SELECT zone_square INTO zone_square FROM zone WHERE zone_id = zone_id;
        days_count := (end_date - start_date) + 1;
        RETURN zone_square * base_price * days_count;
    END;
    $$ LANGUAGE plpgsql;

-- === Trigger: block_expired_contracts ===
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
    BEFORE UPDATE ON contract
    FOR EACH ROW EXECUTE FUNCTION block_expired_contracts();