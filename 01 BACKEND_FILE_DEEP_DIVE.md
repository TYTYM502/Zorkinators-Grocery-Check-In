# Backend File Deep Dive

## Purpose of This Document

This file explains the backend of the grocery check-in app in enough detail that a student can:

- understand what each backend file is responsible for
- see how data moves through the system
- understand why the code is shaped the way it is
- rebuild something very similar by hand

This folder’s main code responsibility is split across:

- `DataCenter.py`
- `app.py`

The two files work together, but they do different jobs.

## High-Level Mental Model

Before reading either file, understand this:

- `DataCenter.py` is the data and rule engine.
- `app.py` is the web server and browser-facing controller.

That means:

- `DataCenter.py` decides how inventory data is stored, loaded, searched, grouped, and archived.
- `app.py` decides how browser actions map onto those backend methods.

If you confuse these two responsibilities, the code starts to feel much harder than it really is.

---

## Part 1: Understanding `DataCenter.py`

## What `DataCenter.py` Is For

This file exists to answer the question:

"How should grocery inventory data be represented and managed?"

It contains:

- data classes
- database connection logic
- inventory operations
- archive/history rules
- expiration status logic
- grouping and serialization helpers

Think of this file as the backend "domain logic" file.

It knows what an item is, what a category is, and how inventory should behave.

---

## `Item` Data Class

The `Item` data class represents one real item record.

Important idea:

One barcode does not equal one item.

If two apples have the same barcode but different purchase dates or expiration dates, those are still two different item records.

That is why `Item` has both:

- `barcode`
- `item_id`

### Why each field exists

`barcode`
- identifies the product type

`name`
- the human-readable item name

`category`
- links the item to category rules such as warning thresholds and recommended expiration

`storage_location`
- tells the system where the item belongs

`exp_date`
- used to determine freshness, warning, and expiration

`purchase_date`
- needed to calculate how much of the item’s shelf life has already been used

`item_id`
- the serial ID for that exact stored record

`archived`
- marks whether the item is still active inventory

`archived_date`
- tells you when the record left active inventory

### Why a data class was a good choice

The code could have used plain dictionaries instead of a data class.

But the data class is better here because:

- the fields are explicit
- the code is easier to read
- it is easier to pass complete item objects around
- Python gives you a cleaner constructor automatically

---

## `Category` Data Class

The `Category` class is not just a label.

It stores behavior rules.

That is one of the most important concepts in the project.

A category controls things like:

- default storage location
- recommended shelf life
- warning threshold percent

### Why `warning_threshold_percent` matters

This field is what lets the app say:

- "fresh"
- "expiring soon"
- "expired"

without hardcoding the same rule for every item type.

Example:

- produce may become "expiring soon" once 80% of its shelf life has passed
- another category might use a different threshold

That means categories make the app smarter and more flexible.

---

## `Storage` Data Class

`Storage` is a lighter helper class.

It mainly exists so the backend can group items by storage location in memory.

This is useful for:

- overview counts
- storage summaries
- storage-based filtering

The app could function without this class, but having it makes the code for storage summaries cleaner.

---

## `Inventory` Class

This is the center of backend logic.

If someone asks, "What object really runs inventory behavior?" the answer is `Inventory`.

It is responsible for:

- holding the database connection
- creating tables
- loading active inventory into memory
- saving and updating records
- archive behavior
- grouped inventory behavior
- record history behavior
- item status calculations

If `Item` is one piece of data, `Inventory` is the manager of the whole system.

---

## `__init__`

The constructor does four important jobs:

1. stores the database path
2. opens the SQLite connection
3. ensures tables exist
4. loads current active data into memory

### Why `check_same_thread=False` exists

The app serves browser requests through a threaded HTTP server.

SQLite normally protects connections from being used across threads.

Because this app uses one shared inventory object in the server, the connection needs cross-thread access enabled.

That line was added because the web version of the project started doing real database writes from request handlers.

### What in-memory structures are created

`self.categories`
- normalized category lookup table

`self.storages`
- storage grouping lookup table

`self.items`
- active inventory item lookup keyed by `item_id`

This is an important distinction:

`self.items` is active inventory memory, not the entire history of all database rows.

---

## `_normalize_key`

This is a helper that turns user-entered text into a safer dictionary key.

It strips whitespace and lowercases the string.

Why this matters:

- `Produce`
- `produce`
- ` PRODUCE `

should all behave as the same category in lookups.

This method keeps comparison logic consistent throughout the file.

---

## `create_tables`

This method defines the database structure.

There are two major tables:

### `categories`

Stores category rule data:

- name
- storage location
- recommended expiration days
- warning threshold percent

### `items`

Stores one row per item record:

- item ID
- barcode
- name
- category
- storage location
- expiration date
- purchase date
- archived flag
- archived date

### Why `items` stores one row per item

This is one of the most important design choices in the project.

The database does not store grouped inventory rows.

The database stores one row per real item record.

Grouping by barcode happens later in Python for display purposes.

That is how the app can support:

- different expiration dates for items with the same barcode
- serial ID tracking
- individual checkout behavior
- archived record history

---

## `load_data`

This method rebuilds the backend’s in-memory understanding of active inventory.

It does not load the full history view.

It loads:

- categories
- active items only
- storage groupings

### Why it clears in-memory data first

If the app updates the database and then reloads without clearing old in-memory structures, duplicates can appear in memory.

So `load_data` starts by resetting:

- categories
- storages
- active items

Then it rebuilds them from SQLite.

### Why categories load before items

Items often need to reconnect themselves to category objects in memory.

If categories are loaded first, the app can attach active items to the right category groups more easily.

### Why this matters so much

This method is what keeps the backend’s "live working state" synchronized with the database.

Without it, every update would risk stale in-memory data.

---

## `save_item`

This method writes a complete `Item` back into SQLite.

It uses `INSERT OR REPLACE`, which means:

- new row if needed
- update if it already exists

The method expects the item object to already be correct in memory.

Its job is not to decide business logic.

Its job is just:

"Write this item object into the database."

---

## `_row_to_item`

This is a conversion helper.

It takes a raw SQLite row and turns it into a real `Item` object.

This method is important because SQLite gives back:

- strings
- numbers
- tuples

But the backend wants:

- `datetime` objects
- booleans
- a structured `Item`

This helper keeps conversion logic in one place so other methods do not need to repeat it.

That makes methods like `load_data`, `get_record`, and `get_item_template_by_barcode` cleaner.

---

## `save_category`

This method stores or updates one category in the database.

It is a focused helper:

- input: `Category`
- output: saved category row in SQLite

This method matters because category rules are a real part of the project’s logic.

If the user updates a warning threshold or recommended expiration days, the change needs to survive a restart.

---

## `add_item`

This is a convenience method.

It creates a normal active inventory item by calling `create_record(..., archived=False)`.

That is an important design lesson:

- `create_record` is the general version
- `add_item` is the common active-item case

This makes the rest of the app easier to read.

---

## `create_record`

This is the general item-row creation method.

It can create:

- active records
- archived-only records

That flexibility is what makes it different from `add_item`.

### What it does

1. decides what the archived date should be
2. inserts the row into `items`
3. commits the change
4. gets the new serial ID
5. reloads active inventory memory
6. returns the created record

### Why it may return from `self.items` or `get_record`

If the created record is active, it appears in active memory after reload.

If it is archived-only, it will not appear in active memory, so the backend fetches it directly from the database.

That is a subtle but important detail.

---

## `get_recommended_exp_date`

This method gives the app a suggested expiration date based on:

- item category
- purchase date

If the category exists, it uses that category’s recommended shelf-life days.

If the category is unknown, it falls back to 7 days.

This is the method that makes new-item forms feel smart instead of manual.

---

## `update_recommended_exp`

This is a simple category-learning helper.

It averages old and new expiration-day knowledge into the category’s recommended days.

Right now it is not the most advanced prediction logic, but it demonstrates how the app could adapt over time.

For a student project, it is a useful conceptual placeholder for "learning from usage."

---

## `archive_item`

This method archives one specific item by serial ID.

Important idea:

Archiving is not deleting.

It means:

- keep the row
- set `archived = 1`
- save `archived_date`
- remove it from active inventory memory by reloading active data

This method is the foundation for history preservation.

Without it, the project would lose traceability.

---

## `archive_items_by_barcode`

This method archives all active rows sharing one barcode.

This exists because the Inventory tab groups by barcode.

So the backend needs a group archive behavior that matches that user interface idea.

### Why return row count

The method returns how many rows were archived.

That helps the app produce clear messages like:

- "Archived 3 active items for barcode 12345."

That is useful for both user feedback and debugging.

---

## `remove_item`

This is a thin wrapper that just calls `archive_item`.

It exists for readability and semantic convenience.

In this project, "remove" really means "archive out of active inventory."

---

## `get_expired_items`

This returns active items whose expiration date is already in the past.

This method is useful for summary counts and overview information.

It is intentionally narrower than `get_item_status`.

It only answers:

"Which active items are fully expired?"

---

## `get_items_by_barcode`

This returns all active item records with the same barcode.

It is different from template lookup.

It only looks at currently active rows, not archived history.

This is useful for:

- checkout logic
- counting active quantity for a barcode

---

## `get_item_template_by_barcode`

This is one of the smartest methods in the file.

It looks through all saved records, including archived history, and returns the most recent match for a barcode.

That means the system can still remember a product even when active inventory is empty.

This is the method that makes rescanning an old barcode feel natural.

Without it, the user would have to recreate known products from scratch whenever stock hit zero.

---

## `get_quantity_for_barcode`

This just counts active matches from `get_items_by_barcode`.

It is a helper used when the backend wants quantity without rebuilding a whole group structure.

---

## `search_items`

This is the active inventory search/filter method.

It works on:

- text query
- category
- storage
- expiration status

Important:

It searches active inventory only.

That makes it appropriate for the Inventory tab, not the Records tab.

### Why it uses `get_item_status`

Instead of reimplementing status logic inside the search method, it reuses the dedicated status helper.

That is good design because it avoids duplicate logic.

---

## `get_items_warning_expiration`

This method returns active items that are currently in the "expiring soon" state.

It is a small helper built on top of `get_item_status`.

This is useful for:

- warning counts
- overview summaries

---

## `get_statistics`

This builds the dashboard metrics.

It returns things like:

- total active items
- expired count
- warning count
- number of categories
- number of storage locations
- counts by category
- counts by storage

This method exists because the dashboard needs summary information in one convenient bundle.

It is not a generic data storage method.

It is a frontend-support method.

---

## `update_item`

This updates one existing item record.

It can also change whether the item is archived if the caller provides that argument.

### Why this method rebuilds and reloads

An item update may affect:

- name
- category
- storage
- purchase date
- expiration date
- archive status

Because those changes can affect groupings and active inventory membership, the method reloads active data after saving.

This helps keep in-memory state correct.

---

## `upsert_category`

This is a category create-or-update helper.

Why it exists:

- the app often wants to accept raw category form values
- it is convenient to let one method handle both new and edited categories

This method returns the resulting category object after saving it.

---

## `serialize_item`

This turns an `Item` object into a plain dictionary that the frontend can consume more easily.

The returned dictionary includes:

- item ID
- barcode
- name
- category
- storage location
- purchase date string
- expiration date string
- current computed status
- archive state
- archived date string

### Why serialization exists

The backend likes structured Python objects.

The frontend likes simple JSON-ready dictionaries.

Serialization is the bridge between those two worlds.

---

## `serialize_category`

This does the same kind of translation for category data.

It makes category objects easier to send to the frontend.

---

## `get_inventory_rows`

This returns active inventory as flat serialized rows.

It is a simpler view than grouped inventory.

The current frontend mostly uses grouped inventory instead, but this helper still exists as a useful flat-row representation.

---

## `get_inventory_groups`

This is the method that makes the grouped inventory screen possible.

It:

1. searches matching active items
2. groups them by barcode
3. sorts items inside each group by urgency
4. uses the soonest-expiring item as the group summary leader
5. returns a frontend-friendly structure

This is an excellent example of backend data shaping.

The database stores one row per item.

The frontend wants a grouped barcode view.

This method is the translation layer.

---

## `get_record`

This fetches one exact record by serial ID from the database.

Unlike `self.items`, this can return active or archived records because it queries SQLite directly.

This is useful for record editing and returning archived-only records created outside active inventory.

---

## `get_all_records`

This is for the Records tab.

It loads:

- active records
- archived records

Then it can filter them by:

- search text
- active only
- archived only

Important difference:

This method uses the database directly, not `self.items`.

That is because `self.items` only contains active inventory.

If this method used `self.items`, the whole history feature would be broken.

---

## `get_storage_names` and `get_category_names`

These are convenience helpers that produce sorted lists for frontend dropdowns and datalists.

They make the interface easier to populate without forcing the frontend to reconstruct names manually.

---

## `get_item_status`

This is one of the most important logic methods in the whole project.

It decides whether an item is:

- fresh
- expiring soon
- expired

### Why it is computed instead of stored

Status changes over time.

An item can be fresh today and expiring soon tomorrow without any database row being manually changed.

That means status is an interpretation, not a stored fact.

### What inputs it uses

- current time
- purchase date
- expiration date
- category warning threshold

This makes the category system matter in a meaningful way.

---

## `close`

This closes the SQLite connection when the app shuts down.

It is simple, but important resource cleanup.

---

## Part 2: Understanding `app.py`

## What `app.py` Is For

`app.py` is the browser-facing backend layer.

It is responsible for:

- receiving browser requests
- validating request data
- calling inventory methods
- packaging backend responses as JSON
- serving HTML/CSS/JS files

If `DataCenter.py` is the engine, `app.py` is the dashboard wiring and controls.

---

## Path Constants

At the top of the file:

- `BASE_DIR`
- `STATIC_DIR`
- `TEMPLATE_DIR`

These define where the app expects to find frontend assets.

There are also fallback paths so the server can still work if files are temporarily copied into the root layout instead of the expected folder structure.

That was added to make the app more tolerant of different local copies.

---

## `GroceryWebApp` Class

This class holds application-level state that is above raw inventory data.

Most importantly, it holds:

- the `Inventory` object
- staged session items
- the next temporary session ID

This is important because staged session items are not yet active inventory records.

They are draft items waiting for approval.

That means session state belongs here, not inside the permanent `Inventory` record set.

---

## `_require_date`

This helper converts a `YYYY-MM-DD` string from the frontend into a Python `datetime`.

It is a small but important validation helper.

It ensures that downstream backend methods are working with date objects instead of raw strings.

---

## `snapshot`

This builds the full "page state" payload for the frontend.

It includes:

- statistics
- grouped inventory
- staged session items
- categories
- category names
- storage names
- full records list
- timestamp

This is what powers the frontend bootstrap call.

Instead of making the browser assemble state from lots of tiny requests, this method gives it a single useful bundle.

---

## `scan_barcode`

This is the beginning of the check-in workflow.

It decides:

- known barcode -> use template and create a staged draft item
- unknown barcode -> tell the frontend it needs a full item form

### Why this is a great design

It separates:

- product memory
- actual inventory approval

The scan step does not immediately create active inventory.

It creates a staged session item.

That matches the project’s "approve before inventory" rule.

---

## `create_item`

This creates a new staged session item from a frontend form submission.

Important:

This does not write into active inventory yet.

It only adds a session draft.

That is a critical distinction in the project.

---

## `update_session_item`

This edits one staged session draft item.

Again, this is still pre-approval.

The draft can be corrected before becoming a real inventory record.

That is the main value of having a separate session workflow.

---

## `approve_session`

This is the step that converts session drafts into real inventory rows.

It loops through staged items and calls `inventory.add_item(...)` for each one.

Then it clears the session draft list.

This is the moment where the system moves from:

- temporary draft state
to
- permanent active inventory

---

## `update_inventory_item`

This updates one active inventory record using `inventory.update_item`.

This is used when the user edits an individual record from the inventory or grouped item details.

---

## `create_record`

This supports the Records tab’s ability to create a record directly.

Important:

This can create either:

- active records
- archived-only records

That is why this method uses `inventory.create_record` instead of `add_item`.

---

## `update_record`

This edits a record from the Records tab, including whether it is active or archived.

This is different from ordinary inventory editing because records view is allowed to work with both active and archived history.

---

## `archive_inventory_item`

This archives one specific item by serial ID.

It is a thin app-level wrapper over the deeper inventory behavior.

---

## `archive_inventory_group`

This archives all active items for one barcode using the backend group archive method.

It also turns the numeric row count into a user-friendly message.

This is a good example of what `app.py` does:

- inventory layer performs the rule
- app layer formats the response for the browser

---

## `checkout_barcode`

This powers the checkout/removal workflow.

It:

1. finds active items by barcode
2. sorts them by purchase date
3. chooses the oldest one
4. archives that one record

Why oldest first?

Because that encourages stock rotation.

That is a real business rule, not just a random implementation detail.

---

## `save_category`

This app-level method receives category form data, validates it, and calls `inventory.upsert_category`.

Again, notice the split of responsibility:

- app layer validates request payload shape
- inventory layer performs the real save logic

---

## `_build_session_item`

This creates the internal dictionary used for a staged session item.

It is not yet a database row.

That is why it gets a `session_id`, not an `item_id`.

This is a very important distinction:

- `item_id` belongs to permanent database records
- `session_id` belongs to temporary staged drafts

---

## `_serialize_session_item`

This turns the draft session dictionary into a frontend-friendly payload.

To reuse status logic, it wraps the draft in a lightweight object-like structure and runs the regular item status calculation.

That is a clever design choice because it avoids duplicating status logic just for staged items.

---

## `APP = GroceryWebApp()`

This creates one shared application object.

The request handler uses this same object for browser requests.

That means:

- one shared inventory backend
- one shared session draft state

for the running server instance.

---

## `GroceryRequestHandler`

This class translates browser requests into app actions.

It handles:

- `GET`
- `POST`
- `PUT`
- `DELETE`

This is the real HTTP entry point of the application.

---

## `do_GET`

This method handles:

- the main page
- static files
- bootstrap JSON
- expiration recommendation lookup

### Why bootstrap exists

Instead of making the frontend ask for categories, then records, then inventory, then statistics separately, bootstrap gives it a full state snapshot.

That reduces complexity on the frontend side.

### Why recommendation exists

This lets the frontend ask:

"Given this category and purchase date, what expiration date should I suggest?"

That keeps category rule logic in the backend, where it belongs.

---

## `do_POST`

This handles create-style actions like:

- scan barcode
- create staged session item
- approve session
- checkout
- save category
- create record
- archive inventory group

The method also catches validation errors and turns them into JSON error responses.

---

## `do_PUT`

This handles update-style actions like:

- edit session draft item
- edit active inventory item
- edit a record
- update a category

Important idea:

Different URLs mean different update contexts.

That is why the same item form can support different modes in the frontend.

---

## `do_DELETE`

This currently supports deleting/archiving one inventory item by serial ID through the backend archive wrapper.

The project also has barcode-group archive as a POST action because it behaves more like a command than a simple row delete.

---

## `log_message`

This is overridden so the built-in server does not print noisy logs for every request.

That keeps the console cleaner during development.

---

## `_read_json`

This reads and parses the request body into a Python dictionary.

Without this helper, every POST/PUT route would need repeated body-reading logic.

This is a great example of good backend cleanup.

---

## `_json`

This sends a Python dictionary back to the browser as JSON.

It also sets:

- response status code
- content type
- content length

This helper makes all API responses cleaner and more consistent.

---

## `_serve_file`

This serves HTML, CSS, and JavaScript files.

It also safely handles missing files by returning a 404 JSON response.

This is the low-level file-serving helper behind the page and static asset routes.

---

## `_resolve_template_file` and `_resolve_static_file`

These methods were added so the app could tolerate both:

- the intended `templates/` and `static/` structure
- fallback root-file copies during troubleshooting

They are a good reminder that real projects sometimes need small compatibility helpers when environments drift.

---

## `run`

This starts the web server on `127.0.0.1:8000`.

It also ensures the database connection is closed when the server stops.

This is the actual backend startup entry point.

---

## How to Recreate a Similar Backend From Scratch

If someone wanted to rebuild a similar backend from nothing, the correct order would be:

1. define item and category data classes
2. build the `Inventory` class with a SQLite connection
3. create database tables
4. build load/save helpers
5. build archive/history behavior
6. build status calculations
7. build search and grouping methods
8. build a web app/controller class
9. add request handlers
10. serialize backend data for the frontend

This order matters because the backend logic must exist before the browser can use it.

---

## Final Lessons This Backend Teaches

This backend is a strong learning example because it teaches:

- the difference between records and grouped views
- why archive is better than delete for historical systems
- why status should be computed instead of stored
- how to separate business logic from request handling
- how to use helper methods to keep code readable

If someone understands these two backend files well, they do not just understand this project.

They understand the beginnings of how small real-world web apps are structured.
