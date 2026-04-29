# Person 1 Guide: Backend and Database

## Your Role

You are responsible for the data and logic foundation of the project.

That means you are building the part that answers questions like:

- What is an item?
- How is an item stored?
- What happens when an item is archived?
- How do we know if an item is fresh or expiring soon?
- How does the system remember a barcode after inventory is empty?

You are mainly working in:

- `DataCenter.py`
- `app.py`

## Your First Job

Before writing code, write down these rules in plain English.

### Rule 1

A barcode identifies a product type, not one individual item.

### Rule 2

An item record needs its own serial ID because multiple items can share a barcode.

### Rule 3

Archived items are not deleted.

### Rule 4

Session items are not active inventory yet.

### Rule 5

Inventory groups by barcode for display, but the database still stores individual item records.

If you cannot explain those 5 rules, do not start coding yet.

## What You Are Building First

You are not starting with web pages.

You are starting with the data model because the whole app depends on it.

Think of yourself as building the engine before the dashboard.

# Part 1: Build `DataCenter.py`

## Step 1: Create the File and Imports

Open `DataCenter.py`.

Start by importing the modules you need.

### `sqlite3`

This lets Python talk to SQLite databases.

Without this, you cannot save data permanently.

### `datetime`

You need this because the app compares dates constantly.

Examples:

- purchase date
- expiration date
- archived date
- determining whether something is expired

### `dataclass`

This makes it easier to define structured data objects like `Item` and `Category`.

### `typing`

These help explain the shapes of your data.

Examples:

- `List[Item]`
- `Dict[str, Category]`
- `Optional[int]`

## Step 2: Build the `Item` Data Class

Now define an `Item`.

Each field exists for a reason.

### `barcode`

This identifies the product type.

### `name`

This is the human-readable item name.

### `category`

This connects the item to category rules.

### `storage_location`

This helps the user know where the item belongs.

### `purchase_date`

This matters because shelf-life calculations begin here.

### `exp_date`

This is the final date used to determine freshness or expiration.

### `item_id`

This is the serial ID for one individual record in the database.

Make this optional at first because the database usually creates it for you.

### `archived`

This tells the app whether the item is still active inventory.

### `archived_date`

This tells you when the record left active inventory.

## Step 3: Build the `Category` Data Class

A category is not just a label.

It gives the app rules.

Useful fields:

- `name`
- `storage_location`
- `recommended_exp_days`
- `warning_threshold_percent`
- `items`

### Why This Exists

The category helps the app answer:

- where items belong
- how long they usually last
- when warning status should begin

## Step 4: Build the `Inventory` Class

This class is the center of your backend data logic.

It should eventually manage:

- database connection
- categories
- active items
- record lookup
- status calculations
- archive behavior

When first creating the class, keep the constructor simple.

It should:

1. remember the database path
2. open a SQLite connection
3. create tables if needed
4. load existing data

## Step 5: Open SQLite

Open the SQLite database in the constructor.

Use a file like `inventory.db`.

That means:

- if the file does not exist, SQLite can create it
- if it already exists, your project reuses it

## Step 6: Create Tables

Write a method like `create_tables`.

Make 2 tables first:

### `categories`

This stores category behavior.

Columns should include:

- name
- storage location
- recommended expiration days
- warning threshold percent

### `items`

This stores one row per item record.

Columns should include:

- item ID
- barcode
- name
- category
- storage location
- expiration date
- purchase date
- archived
- archived date

### Why This Shape Matters

You are not storing grouped barcode rows in the database.

You are storing one row per real item record.

Grouping happens later in Python for display.

## Checkpoint A

Stop here and prove the following:

1. `inventory.db` is created.
2. Both tables exist.
3. You understand why the `items` table stores one row per individual item.

# Part 2: Build Save and Load Logic

## Step 7: Build `load_data`

This method reloads active inventory into memory.

Start by clearing your in-memory structures.

Then:

1. load categories from SQLite
2. load only active items from SQLite
3. rebuild any helpful dictionaries

### Important Rule

Active inventory and full history are not the same thing.

`load_data` should focus on active inventory.

## Step 8: Build a Helper to Convert Database Rows Into `Item` Objects

When you fetch a row from SQLite, it comes back as a tuple.

A helper like `_row_to_item` makes your code easier to read.

It should:

1. take the SQLite row
2. turn date strings into `datetime` objects
3. return a real `Item`

## Step 9: Build `save_category`

This method should store or update category data.

In plain English:

- if the category already exists, update it
- if not, create it

## Step 10: Build `create_record`

This method should save one item record into the database.

Think of it as:

"Save one row with all the data I give you."

It should be able to create:

- active inventory records
- archived-only records

## Step 11: Build `add_item`

This can be a convenience method that calls `create_record` with `archived=False`.

## Checkpoint B

Prove:

1. you can save a category
2. you can add an active item
3. you can add a second active item with the same barcode
4. they get different item IDs
5. they both appear in active inventory data

# Part 3: Build Archive and History Logic

## Step 12: Build `archive_item`

This method archives one item by serial ID.

In plain English:

- do not delete the record
- mark it archived
- store the archived date
- reload active inventory

## Step 13: Build `archive_items_by_barcode`

This is the grouped archive behavior.

If the user archives barcode group `12345`, all active rows with that barcode should become archived.

## Step 14: Build `get_item_template_by_barcode`

This should:

- search the database by barcode
- include archived rows
- return the most recent matching record

### Why?

So if active inventory is empty for that barcode, the system still remembers:

- item name
- category
- storage location

## Checkpoint C

Prove this exact flow:

1. add an item
2. archive it
3. confirm it no longer appears in active inventory
4. confirm it still exists in database history
5. confirm the barcode can still be used as a template

# Part 4: Build Expiration Logic

## Step 15: Build `get_recommended_exp_date`

This method uses category settings to recommend an expiration date.

The idea is:

- if the category has recommended days, add those days to purchase date
- otherwise use a simple default like 7 days

## Step 16: Build `get_item_status`

This method decides if the item is:

- fresh
- expiring soon
- expired

### How To Think About It

First ask:

"Is the expiration date already in the past?"

If yes:

- it is expired

If not:

1. calculate total shelf life
2. get category warning threshold
3. figure out if the item is in its final warning zone

## Step 17: Build Search and Group Methods

Now create:

- `search_items`
- `get_inventory_groups`
- `get_all_records`

### `search_items`

This should search active inventory only.

### `get_inventory_groups`

This should take active items and group them by barcode.

### `get_all_records`

This should return everything:

- active
- archived

## Checkpoint D

Prove:

1. two items with same barcode can have different expiration dates
2. grouped inventory shows one barcode summary
3. that summary knows which expiration date is soonest
4. full records include archived history too

# Part 5: Build the Backend API in `app.py`

## Step 18: Create the App Class

Open `app.py`.

Create an app-level class that stores:

- the `Inventory` object
- staged session items
- session IDs

### Why Session Items Live Here

Because session items are not yet active inventory.

## Step 19: Build Session Methods

You need methods for:

- scanning a barcode
- creating a staged item
- editing a staged item
- approving the session

### Approve Session Logic

When the session is approved:

- each staged item becomes a real active record in SQLite
- the session list clears

## Step 20: Build API Routes

Build in this order:

1. `GET /`
2. `GET /api/bootstrap`
3. session routes
4. inventory update/archive routes
5. category route
6. checkout route
7. records routes

## Checkpoint E

Prove:

1. server starts
2. page route works
3. bootstrap route returns JSON
4. session approve writes staged items into active inventory
5. group archive works from the backend

## What To Tell Your Team

By the time you finish your role, you should be able to explain:

1. why barcode and item ID are different
2. why archived rows stay saved
3. why grouped inventory is created in Python, not stored directly in SQLite
4. why session items are separate from inventory
5. how the backend decides item status
