-- Table for Services offered
CREATE TABLE services (
    service_id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    service_duration INTEGER NOT NULL,
    service_price DECIMAL(10, 2) NOT NULL
);

-- Table for Appointment Slots
CREATE TABLE appointment_slots (
    slot_id SERIAL PRIMARY KEY,
    slot_datetime TIMESTAMP NOT NULL,
    slot_available BOOLEAN NOT NULL
);

-- Table for Appointments
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    client_phone VARCHAR(20) NOT NULL,
    appointment_time TIMESTAMP NOT NULL,
    service_id INTEGER REFERENCES services (service_id),
    slot_id INTEGER REFERENCES appointment_slots (slot_id),
    confirmation_sent BOOLEAN DEFAULT false
);

-- Table for Users (for authentication)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
