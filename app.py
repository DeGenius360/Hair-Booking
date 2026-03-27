from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, time, timedelta

from flask import (
    Flask,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

SCHEMA_SQL = """
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
    FOREIGN KEY(service_id) REFERENCES services(service_id),
    FOREIGN KEY(slot_id) REFERENCES appointment_slots(slot_id)
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);
"""

DEFAULT_SERVICES = [
    ("Classic Haircut", 45, 35.0),
    ("Protective Braids", 120, 120.0),
    ("Silk Press", 90, 85.0),
    ("Deep Conditioning", 60, 55.0),
]

DEFAULT_SLOT_TIMES = [time(9, 0), time(11, 0), time(14, 0), time(16, 0)]


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        DATABASE=os.path.join(app.instance_path, "hair_booking.db"),
    )
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        init_db()

    @app.template_filter("format_datetime")
    def format_datetime(value: str | datetime) -> str:
        if not value:
            return ""
        if isinstance(value, str):
            parsed = datetime.fromisoformat(value)
        else:
            parsed = value
        return parsed.strftime("%b %d, %Y %I:%M %p")

    @app.route("/", methods=["GET"])
    def index() -> str:
        db = get_db()
        services = db.execute(
            "SELECT service_id, service_name, service_duration, service_price "
            "FROM services ORDER BY service_name"
        ).fetchall()
        slots = db.execute(
            "SELECT slot_id, slot_datetime FROM appointment_slots "
            "WHERE slot_available = 1 ORDER BY slot_datetime"
        ).fetchall()
        return render_template("index.html", services=services, slots=slots)

    @app.route("/book", methods=["POST"])
    def book() -> str:
        client_name = request.form.get("client_name", "").strip()
        client_phone = request.form.get("client_phone", "").strip()
        service_id = request.form.get("service_id", "").strip()
        slot_id = request.form.get("slot_id", "").strip()

        if not client_name or not client_phone or not service_id or not slot_id:
            flash("Please complete all fields before booking.", "error")
            return redirect(url_for("index"))

        db = get_db()
        service = db.execute(
            "SELECT service_id, service_name, service_duration, service_price "
            "FROM services WHERE service_id = ?",
            (service_id,),
        ).fetchone()
        slot = db.execute(
            "SELECT slot_id, slot_datetime, slot_available "
            "FROM appointment_slots WHERE slot_id = ?",
            (slot_id,),
        ).fetchone()

        if service is None or slot is None:
            flash("Please choose a valid service and time slot.", "error")
            return redirect(url_for("index"))

        with db:
            updated = db.execute(
                "UPDATE appointment_slots SET slot_available = 0 "
                "WHERE slot_id = ? AND slot_available = 1",
                (slot_id,),
            ).rowcount
            if updated == 0:
                flash("That time slot was just booked. Please choose another.", "error")
                return redirect(url_for("index"))

            db.execute(
                "INSERT INTO appointments "
                "(client_name, client_phone, appointment_time, service_id, slot_id) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    client_name,
                    client_phone,
                    slot["slot_datetime"],
                    service["service_id"],
                    slot["slot_id"],
                ),
            )
            appointment_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        appointment = {
            "appointment_id": appointment_id,
            "client_name": client_name,
            "client_phone": client_phone,
            "appointment_time": slot["slot_datetime"],
            "service_name": service["service_name"],
            "service_price": service["service_price"],
            "service_duration": service["service_duration"],
        }
        return render_template("confirmation.html", appointment=appointment)

    @app.route("/appointments", methods=["GET"])
    def appointments() -> str:
        db = get_db()
        entries = db.execute(
            "SELECT a.appointment_id, a.client_name, a.client_phone, "
            "a.appointment_time, s.service_name, s.service_price "
            "FROM appointments a "
            "JOIN services s ON a.service_id = s.service_id "
            "ORDER BY a.appointment_time"
        ).fetchall()
        return render_template("appointments.html", appointments=entries)

    return app


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA_SQL)
    seed_services(db)
    seed_slots(db)
    db.commit()


def seed_services(db: sqlite3.Connection) -> None:
    existing = db.execute("SELECT COUNT(*) FROM services").fetchone()[0]
    if existing:
        return
    db.executemany(
        "INSERT INTO services (service_name, service_duration, service_price) "
        "VALUES (?, ?, ?)",
        DEFAULT_SERVICES,
    )


def seed_slots(db: sqlite3.Connection) -> None:
    existing = db.execute("SELECT COUNT(*) FROM appointment_slots").fetchone()[0]
    if existing:
        return
    start_date = date.today()
    for day_offset in range(7):
        slot_date = start_date + timedelta(days=day_offset)
        for slot_time in DEFAULT_SLOT_TIMES:
            slot_dt = datetime.combine(slot_date, slot_time)
            db.execute(
                "INSERT INTO appointment_slots (slot_datetime, slot_available) "
                "VALUES (?, ?)",
                (slot_dt.isoformat(), 1),
            )


app = create_app()


@app.teardown_appcontext
def close_db(exception: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
