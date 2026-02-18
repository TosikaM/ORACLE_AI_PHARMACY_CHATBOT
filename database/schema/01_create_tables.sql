CREATE TABLE medicines (
    medicine_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    medicine_name VARCHAR2(200) NOT NULL,
    category_name VARCHAR2(100) NOT NULL,
    dosage_form VARCHAR2(50),
    strength VARCHAR2(50),
    manufacturer VARCHAR2(200),
    requires_prescription CHAR(1) DEFAULT 'N',
    is_active CHAR(1) DEFAULT 'Y',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_medicine_name ON medicines(medicine_name);
CREATE INDEX idx_category ON medicines(category_name);
