# Zorkinators Grocery Check-In System

This project is now set up as a browser-based grocery check-in app backed by the existing SQLite inventory database.

## What Changed

- The old Tkinter desktop workflow has been converted into an HTML/CSS/JavaScript interface.
- The Python inventory and database layer in `DataCenter.py` is still reused.
- The new UI adds:
  - a dashboard with live inventory stats
  - a cleaner check-in session flow
  - inventory filtering by category, storage, and freshness
  - category rule management with default expiration guidance
  - a faster checkout flow for removing one scanned item at a time

## Main Files

- `app.py`: Small Python web server and JSON API.
- `DataCenter.py`: Inventory models and SQLite persistence.
- `templates/index.html`: Main HTML shell.
- `static/style.css`: Visual design and responsive layout.
- `static/app.js`: Client-side rendering and interactions.
- `GUI.py`: Original Tkinter version kept for reference.

## How to Run

1. Start the web app with a Python interpreter:
   `python app.py`
2. Open `http://127.0.0.1:8000` in a browser.
3. Scan or type a barcode to add items into the current session.
4. Use the inventory tab to search, edit, or archive items.
5. Use the categories tab to manage shelf-life defaults and warning thresholds.

## Notes

- Data is still stored in `inventory.db`.
- Existing barcodes reuse their saved item details automatically.
- New barcodes open an item form so the product can be saved immediately.
