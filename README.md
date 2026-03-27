# Hair-Booking
An appointment booking website for a hair care business.

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

The app creates a local SQLite database at `instance/hair_booking.db` and seeds it
with services and time slots the first time it runs.
