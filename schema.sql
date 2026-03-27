-- SQLite-friendly schema for local development
CREATE TABLE IF NOT EXISTS services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    service_duration INTEGER NOT NULL,
    service_price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS appointment_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_datetime TEXT NOT NULL,
    slot_available INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    client_phone TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    service_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    confirmation_sent INTEGER DEFAULT 0,
    FOREIGN KEY(service_id) REFERENCES services (service_id),
    FOREIGN KEY(slot_id) REFERENCES appointment_slots (slot_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
