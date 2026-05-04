# Grocery Check-In App From Scratch Guide

## What This Guide Is

This is a build-by-hand learning guide for recreating a project very similar to this grocery check-in app.

This guide is intentionally:

- detailed
- beginner-friendly
- step-by-step
- focused on understanding, not copying

This is not meant to be a short summary.

It is meant to answer questions like:

- "What do I do first?"
- "What file do I make?"
- "Why am I making this before that?"
- "How do I know if this stage is working?"
- "What should each teammate be doing?"

If you follow this guide carefully, you should end with:

- a working project
- a better understanding of web apps
- enough confidence to explain the project in a demo
- enough understanding to expand it later

---

## What You Are Building

You are building a grocery inventory web app with these core features:

1. A staging session where scanned items go first.
2. An approval step that moves staged items into active inventory.
3. Inventory grouped by barcode.
4. Individual items under a barcode group with their own serial IDs and expiration dates.
5. Category rules that suggest expiration dates and warning thresholds.
6. A checkout flow to remove one item at a time.
7. Archived records that stay saved forever.
8. A records page to view active and archived items together.

---

## Who This Is For

This guide assumes the reader:

- knows basic Python
- does not yet know how to build a web app
- may recognize HTML structure but cannot comfortably write it alone
- is working on Windows
- may eventually run the finished project on a Raspberry Pi

---

## The Exact Stack

You asked for the exact stack used by the current reference project.

That stack is:

- Python
- SQLite
- HTML
- CSS
- JavaScript
- a small Python web server

No large framework is required.

That is good for learning, because you can see more of what is happening yourself.

---

## Read This Before You Start

If you are new to web apps, the biggest source of confusion is not syntax.

It is not understanding what part of the program is responsible for what.

Before touching code, memorize this:

### HTML

HTML creates the structure of the page.

Examples:

- headings
- forms
- buttons
- tables
- sections

HTML does not decide what happens when you click.

### CSS

CSS changes how the page looks.

Examples:

- color
- layout
- spacing
- fonts
- button styles

CSS does not store data.

### JavaScript

JavaScript makes the page interactive.

Examples:

- handling button clicks
- sending data to Python
- receiving data from Python
- drawing rows in a table
- opening and closing modals

### Python Backend

Python is the "brain" behind the page.

Examples:

- receiving requests from JavaScript
- storing data
- checking rules
- computing warnings
- returning results

### SQLite

SQLite stores the information permanently.

Examples:

- item records
- categories
- archive history

If you close the app, SQLite is what allows the data to still exist later.

---

## The 3-Layer Mental Model

When something happens in the app, think of it as passing through 3 layers.

### Example: User scans a barcode

1. The browser form captures the barcode.
2. JavaScript sends it to Python.
3. Python checks the database.
4. Python sends back a result.
5. JavaScript updates the page.

That is the general pattern for almost everything in this project.

If you remember that, debugging becomes much easier.

---

## Team Plan for 4 People

Your team has 4 people. Use that to your advantage.

Suggested role split:

### Person 1: Backend + Database Lead

Main focus:

- `DataCenter.py`
- SQLite tables
- inventory logic
- archive logic
- expiration logic

### Person 2: HTML + Page Layout Lead

Main focus:

- `templates/index.html`
- tab layout
- forms
- tables
- modal structure

### Person 3: JavaScript + Interaction Lead

Main focus:

- `static/app.js`
- API calls
- rendering
- filters
- event handling
- group expand/collapse behavior

### Person 4: Styling + Testing + Demo Lead

Main focus:

- `static/style.css`
- visual cleanup
- checkpoint testing
- bug tracking
- Raspberry Pi prep

Important:

No teammate should only know their own file.

After every phase, the person who built it should explain it to the others.

---

## How To Use This Guide

Do not read this like a textbook from top to bottom in one sitting.

Use it like a workbook.

For each phase:

1. Read the goal.
2. Read the explanation.
3. Build the required files or functions.
4. Complete the checkpoint.
5. Only then move on.

If a checkpoint fails, stop there.

Do not continue adding more code.

---

## Project Folder You Should Build

By the end, your folder should look like this:

```text
project-root/
  app.py
  DataCenter.py
  inventory.db
  templates/
    index.html
  static/
    style.css
    app.js
  README.md
```

You do not need every file immediately.

You will create them in stages.

---

## Very First Setup

Before Phase 1, create a new clean project folder.

### Step 1

Make a folder for the project.

Suggested name:

`grocery-check-in`

### Step 2

Inside it, create:

- `DataCenter.py`
- `app.py`
- a folder named `templates`
- a folder named `static`

### Step 3

Open the folder in your editor.

### Step 4

Create a plain text note for your team with:

- who owns which workstream
- what the first checkpoint is
- how branches will be named

---

# Phase 1: Start With the Data Model

## Goal of This Phase

At the end of this phase, you should have:

- a Python file that defines the app's core data structures
- a SQLite database that can be created automatically
- a clear understanding of what an item record is

This phase happens before any web page exists.

That is on purpose.

If your data model is not clear, the rest of the app becomes confusing.

---

## What To Build in This Phase

Open `DataCenter.py`.

You are going to build:

1. an `Item` data class
2. a `Category` data class
3. optionally a `Storage` data class
4. an `Inventory` class
5. a SQLite connection
6. table creation methods

---

## What an Item Really Is

Before coding, define an item in plain English.

An item is not "milk" in general.

An item is one individual stored record of something.

That means two gallons of milk with the same barcode may still be two different item records because:

- they may have different purchase dates
- they may have different expiration dates
- they may be checked out at different times

This is why you need:

- `barcode`
- `item_id`

They are not the same.

### Barcode

Identifies the product type.

Example:

- all identical cereal boxes may share a barcode

### Item ID

Identifies one stored record in your database.

Example:

- cereal box record 17
- cereal box record 18

Both could have the same barcode, but they are still different records.

---

## Step-By-Step: Build `Item`

In `DataCenter.py`, start by importing the tools you need.

You should research and understand why these are needed:

- `sqlite3`
- `datetime`
- `dataclass`
- `field`
- typing helpers like `Dict`, `List`, and `Optional`

Then create an `Item` data class.

It should contain:

- `barcode`
- `name`
- `category`
- `storage_location`
- `exp_date`
- `purchase_date`
- `item_id`
- `archived`
- `archived_date`

Do not move on until everyone can explain what each field means.

### Mini Check

Ask your team:

1. Why does `item_id` need to be optional at first?
2. Why should `archived` be stored instead of deleting rows?
3. Why do we need both purchase date and expiration date?

---

## Step-By-Step: Build `Category`

Now create a `Category` data class.

This is not just a label.

It should help define behavior.

Useful fields:

- `name`
- `storage_location`
- `recommended_exp_days`
- `warning_threshold_percent`
- `items`

### Why This Exists

Suppose the user enters:

- produce
- dairy
- frozen

Those categories should help the app decide:

- where items should usually be stored
- how long items usually last
- when to warn the user

---

## Step-By-Step: Build `Inventory`

Now create an `Inventory` class.

This class will hold:

- the database connection
- loaded categories
- loaded active items
- helper methods for the whole app

At first, your `__init__` should do only a few things:

1. store the database path
2. open the database connection
3. create tables
4. load existing data

---

## Step-By-Step: Open SQLite

Inside `Inventory.__init__`, open a SQLite connection.

For this project, use a file database like:

`inventory.db`

The connection is what lets Python talk to the database.

### Important Note

Later, because the web server handles browser requests, you may need to allow the SQLite connection to be used safely in that context.

That is a later detail.

For now, just understand:

- SQLite stores the data
- Python must connect to it

---

## Step-By-Step: Create Tables

Write a method such as `create_tables`.

At minimum, create:

### `categories` table

Should include columns like:

- name
- storage location
- recommended expiration days
- warning threshold percent

### `items` table

Should include columns like:

- item ID
- barcode
- name
- category
- storage location
- expiration date
- purchase date
- archived
- archived date

### Why Create Tables Early

Because everything else depends on having a place to store the data.

---

## First Real Checkpoint

At this point, stop coding and prove these things:

1. Running a small Python script creates `inventory.db`.
2. The database file actually exists in the folder.
3. The tables are present.

### How To Check

You can:

- use a SQLite viewer
- use Python to query table names
- temporarily print success messages

### If This Fails

Do not move on.

Nothing else matters until the database is being created correctly.

---

# Phase 2: Load and Save Real Data

## Goal of This Phase

By the end of this phase, your backend should be able to:

- create item records
- create category records
- load active items from the database
- keep active inventory in memory for quick use

---

## Why We Load Data Into Memory

You might ask:

"If the database already has the data, why load it into dictionaries and lists?"

Because:

- repeated database reads can be slower
- grouped calculations are easier in Python
- the app often needs active items ready to use

So you use both:

- SQLite for permanent storage
- Python structures for active working data

---

## Step-By-Step: `load_data`

Create a method that:

1. clears old in-memory dictionaries
2. loads categories from SQLite
3. loads active items from SQLite
4. connects items back to categories and storage locations

This step is important because your app needs a consistent picture of active inventory.

### What "Active" Means

Active means:

- not archived
- currently part of inventory

Archived records still exist in the database, but should not appear as active inventory.

---

## Step-By-Step: `save_category`

Create a method that stores category information into the database.

This method should:

- insert a new category if it does not exist
- update it if it already exists

You do not need to memorize SQL words.

But you do need to understand the purpose:

- save the category so it can be reused later

---

## Step-By-Step: `add_item`

Create a method that saves one active item into the database.

Important:

This method should create one record for one item.

If you call it twice with the same barcode, that should usually mean two item records.

That is exactly what you want.

### What This Method Should Do

1. create an item row in SQLite
2. get the new item ID from the database
3. update in-memory active structures
4. ensure the category exists

---

## Checkpoint 2

Write a tiny test script and prove:

1. you can create a category
2. you can add one item
3. you can add another item with the same barcode
4. both records exist
5. they have different item IDs

If this is not true, stop and fix it.

This checkpoint is one of the most important in the whole project.

---

# Phase 3: Status Logic and Archive Logic

## Goal of This Phase

By the end of this phase, your backend should understand:

- fresh items
- expiring soon items
- expired items
- archived items

This is where the project begins to feel like a real system instead of just a database.

---

## Archived Does Not Mean Deleted

This is one of the most important rules in the app.

When an item leaves active inventory, you do not want to erase history.

Instead:

- mark it archived
- store when it was archived
- hide it from active inventory
- still allow it to appear in records/history

That design choice makes later features possible.

---

## Step-By-Step: `archive_item`

Build a method that marks a single item record as archived.

It should:

1. update the database row
2. set `archived = true`
3. store the archived date
4. reload active inventory data

### Why Reload?

Because the active inventory list in memory needs to match the database again.

---

## Step-By-Step: `archive_items_by_barcode`

Now build a method that archives all active items with the same barcode.

This supports the grouped inventory behavior.

Example:

If active inventory contains:

- item 5 with barcode `111`
- item 9 with barcode `111`
- item 12 with barcode `111`

then group archive should archive all three.

---

## Step-By-Step: `get_item_status`

This method decides if an item is:

- `fresh`
- `expiring_soon`
- `expired`

### How To Think About It

Start with dates.

If current time is later than expiration date:

- the item is expired

If not expired:

1. calculate total shelf life
2. calculate how far through shelf life the item is
3. use the category threshold percent

### Example

Purchase date: April 1  
Expiration date: April 11  
Total shelf life: 10 days  
Warning threshold: 80%

That means once 80% of shelf life has passed, the item should become `expiring_soon`.

That means the last 20% of the time is the warning zone.

---

## Checkpoint 3

Manually test these cases:

1. item with a future date far away
2. item close to expiration
3. item already expired
4. item archived

Make sure your team can explain why each got its result.

---

# Phase 4: Remember Items Even After Archive

## Goal of This Phase

By the end of this phase, the app should remember what a barcode means even if all active items with that barcode are gone.

This matters because:

- if everything is archived
- and the barcode is scanned again later
- the user should not have to re-create the product from scratch

---

## Step-By-Step: Template Lookup

Create a method like:

`get_item_template_by_barcode`

This should:

- search the database
- include archived rows
- return the most recent saved match

### Why This Matters

Suppose all active bananas are gone.

If someone scans the banana barcode later, the app should still know:

- name
- category
- typical storage location

That makes the app feel smart and practical.

---

## Checkpoint 4

Test this exact flow:

1. add an item
2. approve it into inventory
3. archive the group
4. scan the same barcode again
5. confirm the app still recognizes it

If this fails, your app will feel frustrating in real use.

---

# Phase 5: Build the Web Server

## Goal of This Phase

Now you are connecting the backend to the browser.

By the end of this phase:

- Python should serve a page
- Python should serve CSS and JavaScript files
- Python should return JSON for the frontend

---

## What File To Work In

Open `app.py`.

This file will become the backend entry point.

It is responsible for:

- starting the server
- defining API routes
- holding staged session items
- connecting the browser to the inventory backend

---

## Build Order for `app.py`

Do this in order:

1. import modules
2. create a web app class
3. store the inventory object
4. store session items in memory
5. create route handlers
6. start the server

Do not try to build every route at once.

Start with one route that proves the server works.

---

## Your First Server Goal

Before making the real app, get this working:

1. the server starts
2. opening `http://127.0.0.1:8000` gives a page

If you cannot do that, do not keep going.

That is the first web milestone.

---

## Step-By-Step: Session Draft in Memory

The staged session should live in Python memory, not in active inventory.

That means the app class should hold:

- a list of session items
- a way to assign session-only IDs

These are not yet database records.

That is important.

### Why?

Because the user wants to review items before approving them into inventory.

---

## Required API Ideas

You do not need to implement every route at once.

Build in this order:

### Basic loading

- `GET /`
- `GET /api/bootstrap`

### Session flow

- `POST /api/session/scan`
- `POST /api/session/items`
- `PUT /api/session/items/{id}`
- `POST /api/session/approve`

### Inventory flow

- `PUT /api/items/{id}`
- `POST /api/inventory/archive-group`

### Other features

- `POST /api/checkout`
- `POST /api/categories`
- `POST /api/records`
- `PUT /api/records/{id}`

---

## Checkpoint 5

You should be able to prove:

1. the server starts with one command
2. the browser can load the page
3. the bootstrap route returns JSON
4. scanning a barcode can return either:
   - known item template
   - request for new item details

---

# Phase 6: Build the HTML Shell

## Goal of This Phase

At the end of this phase, your page should exist visually, even if it does not fully work yet.

You are building the structure only.

---

## What File To Work In

Open:

`templates/index.html`

---

## What To Put On The Page

Build these major sections:

1. header
2. stat summary area
3. tab bar
4. check-in section
5. inventory section
6. records section
7. overview section
8. checkout section
9. categories section
10. modal dialogs for editing/adding items

---

## Important Beginner Reminder

When writing HTML, think in boxes.

Each section is a container.

Inside the container are:

- headings
- explanatory text
- forms
- tables

If you get overwhelmed, sketch the screen on paper first.

---

## Suggested Build Order for HTML

1. page title and header
2. tab buttons
3. check-in panel
4. inventory panel
5. records panel
6. overview panel
7. checkout panel
8. categories panel
9. modal forms

Only after the page structure feels organized should you move on.

---

## Checkpoint 6

Without using JavaScript yet, you should be able to open the page and visually point to:

- where a barcode gets entered
- where session items will appear
- where grouped inventory will appear
- where archived records will appear
- where categories will be managed

If the page layout is confusing now, it will be worse later.

---

# Phase 7: Build JavaScript Rendering

## Goal of This Phase

At the end of this phase, the page should be able to:

- load data from Python
- display session items
- display grouped inventory
- display records
- respond to button clicks and forms

---

## What File To Work In

Open:

`static/app.js`

---

## The First JavaScript Pattern To Learn

Most frontend behavior in this app follows this pattern:

1. get page elements
2. listen for user action
3. send request to backend
4. receive response
5. update the page

That is the cycle.

You will repeat it many times.

---

## Suggested JavaScript Build Order

1. create a `state` object
2. grab page elements into an `elements` object
3. write `loadState()`
4. write `render()`
5. write `renderSessionItems()`
6. write `renderInventory()`
7. write `renderRecords()`
8. write submit handlers
9. write modal helpers

Do not jump randomly between parts.

---

## What `loadState()` Should Do

This function should:

1. call the bootstrap route
2. receive JSON
3. store that JSON inside `state`
4. call `render()`

This becomes the refresh engine of your interface.

Whenever something changes successfully, load the state again.

---

## What `render()` Should Do

This function should call the smaller rendering functions.

Example idea:

- render stats
- render session items
- render grouped inventory
- render records
- render categories

This keeps the project organized.

---

## Rendering Session Items

Session items should be shown as a plain table.

Each row should include:

- session ID
- barcode
- name
- category
- storage
- purchase date
- expiration date
- status
- edit option

Remember:

These are not yet active inventory rows.

---

## Rendering Grouped Inventory

This is one of the trickiest parts of the frontend.

The Inventory tab should show one top row per barcode group.

That top row should show:

- barcode
- name
- category
- storage
- quantity
- soonest expiration date
- top status

When clicked, it should expand and reveal the individual item records underneath.

Those inner records should show:

- serial ID
- purchase date
- expiration date
- status
- edit option

The archive action for the Inventory tab should happen at the group level.

That means:

- the group row archives all active items with that barcode
- the individual inner rows do not need their own archive button in that view

---

## Rendering Records

The Records tab is your all-history view.

It should show:

- active records
- archived records
- serial IDs
- barcodes
- item names
- category
- storage
- purchase date
- expiration date
- active/archived state

This view is very important for your demo because it proves history is preserved.

---

## Checkpoint 7

By the end of this phase, prove:

1. the page loads real backend data
2. session table updates
3. grouped inventory updates
4. expanding groups shows inner items
5. records page shows both active and archived entries

---

# Phase 8: Build Forms and Editing

## Goal of This Phase

At the end of this phase, users should be able to:

- add staged items
- edit staged items
- approve staged items
- edit inventory records
- add records directly
- edit archived records
- create archived-only records

---

## Important Concept: Different Save Modes

Not every "save" means the same thing.

In this app, there are several save modes:

### Session create

Adds an item into the staged session.

### Session edit

Updates a staged item before approval.

### Inventory edit

Updates an active inventory record.

### Record create

Adds a record directly, possibly archived-only.

### Record edit

Edits a record from the all-records view.

You need to understand which mode you are in before saving.

This is why many apps use hidden fields or mode variables in forms.

---

## Checkpoint 8

Prove these exact flows:

1. create a new staged item
2. edit it before approval
3. approve it
4. edit the resulting active record
5. create a direct archived record
6. edit that archived record later

If these work, your form logic is in a strong place.

---

# Phase 9: Build Category Management

## Goal of This Phase

At the end of this phase, categories should influence behavior, not just labeling.

---

## What Categories Control

Categories should help define:

- usual storage location
- recommended shelf-life days
- warning threshold percent

Example:

`produce` might mean:

- storage: cooler
- recommended days: 7
- warning percent: 80

### What That Means in the App

If the user chooses category `produce`, the app can:

- suggest a storage location
- suggest an expiration date
- determine warning status later

---

## Checkpoint 9

Prove:

1. a category can be added
2. a category can be edited
3. category data appears in the page
4. recommendation logic changes when category changes
5. warning status changes based on category rules

---

# Phase 10: Build Checkout

## Goal of This Phase

At the end of this phase, scanning a barcode in checkout should remove one active item.

---

## What Rule To Use

You need a rule for which matching item gets removed first.

The current project uses oldest purchase date first.

That is a good rule because it encourages stock rotation.

### Flow

1. user enters barcode
2. backend finds active items with that barcode
3. backend picks the oldest one
4. backend archives that one
5. frontend refreshes the grouped inventory and records view

---

## Checkpoint 10

Prove:

1. checkout removes exactly one active item
2. the group quantity decreases
3. the removed record still exists in archived records

---

# Phase 11: Build Styling

## Goal of This Phase

Now make the app understandable and presentable.

Do not try to make it beautiful before it works.

Now that it works, styling matters.

---

## What To Style First

Focus on the most important usability areas:

1. tab navigation
2. forms
3. session table
4. grouped inventory display
5. records table
6. status colors
7. buttons
8. modal layout

### Status Should Be Easy To Read

Use distinct visual styles for:

- fresh
- expiring soon
- expired
- archived

If someone has to read every row carefully, the design is not helping enough.

---

## Checkpoint 11

Ask a teammate not responsible for CSS:

1. Can you tell where to start?
2. Can you tell what is active and archived?
3. Can you find expiring items quickly?
4. Can you tell how grouped inventory works?

If they hesitate, improve the UI.

---

# Phase 12: Full Integration Testing

## Goal of This Phase

At the end of this phase, the app should behave like one connected system.

This is where many teams discover bugs between features.

---

## Full Demo Test Flow

Run this full scenario:

1. create a category
2. scan an unknown barcode
3. add item details into session
4. approve session
5. confirm inventory group appears
6. expand the group
7. edit one underlying item
8. add another item with the same barcode
9. confirm the group quantity increases
10. checkout one item
11. confirm quantity decreases
12. archive the remaining group
13. confirm active inventory no longer shows that barcode
14. confirm records still show all related serial IDs
15. scan the same barcode again
16. confirm the product template is remembered

If all 16 steps work, your project is in excellent shape.

---

## The Most Common Beginner Confusions

### Confusion 1: "Why not just use barcode as the main ID?"

Because one barcode can correspond to multiple real item records.

### Confusion 2: "Why not just delete old items?"

Because then you lose history and cannot remember templates.

### Confusion 3: "Why do we need both grouped inventory and all records?"

Because grouped inventory is easier for daily use, while all records are better for history and tracing serial IDs.

### Confusion 4: "Why does the session exist separately?"

Because it gives the user a review step before changing active inventory.

### Confusion 5: "Why use JavaScript at all?"

Because the page needs to update based on backend data without rebuilding the entire interface manually every time.

---

## Weekly Team Plan

## Week 1

Team goal:

- database exists
- item and category model exists
- items can be added and loaded

Person 1:

- build `DataCenter.py` structure

Person 2:

- sketch page layout on paper or document

Person 3:

- read about basic JavaScript DOM interaction and fetch requests

Person 4:

- create testing checklist and style ideas

Checkpoint:

- database and models work

## Week 2

Team goal:

- Python web server starts
- HTML shell exists
- bootstrap route works

Checkpoint:

- browser loads the page and basic data

## Week 3

Team goal:

- session flow works
- approval works
- inventory renders

Checkpoint:

- you can stage and approve items

## Week 4

Team goal:

- grouped inventory works
- records view works
- categories influence behavior

Checkpoint:

- active and archived history both work

## Week 5

Team goal:

- checkout works
- group archive works
- record editing works

Checkpoint:

- all core project features work

## Week 6

Team goal:

- styling
- testing
- demo practice
- Raspberry Pi preparation

Checkpoint:

- demo flow works without confusion

---

## Stretch Goals

These are optional.

Do not do them until the core project is stable.

- better search and sort
- export to CSV
- charts in overview
- undo archive
- low stock warnings
- scanner hardware testing
- cleaner mobile layout

---

## Raspberry Pi Demo Notes

Because the app is created on Windows but demoed on Raspberry Pi:

1. avoid Windows-only path assumptions
2. keep file structure simple
3. confirm Python version on the Pi
4. test startup command before demo day
5. prepare a small clean demo database

### Demo Day Advice

Bring:

- a stable sample database
- a backup copy
- a written demo script
- a list of "if something breaks, do this" recovery steps

---

## Final "Are We Ready?" Checklist

Your team is ready when everyone can explain:

1. the difference between session items and inventory items
2. why grouped inventory still needs separate item records
3. why archived records are stored instead of deleted
4. how barcode scan reaches the backend
5. how status is calculated
6. how categories influence expiration logic
7. how checkout works
8. how group archive works

If only one teammate knows those answers, the team is not ready.

If all four teammates can explain them, the team is ready.

---

## The Best Way To Use This Guide Next

If you feel lost right now, do not try to build the full app immediately.

Start with only these 3 tasks:

1. Create `DataCenter.py` with the data classes and database table creation.
2. Make sure `inventory.db` is created successfully.
3. Write one temporary Python test that adds two items with the same barcode.

That is your true starting point.

After that, come back to Phase 2.

---

## Final Advice

Build this project in this order:

1. data model
2. save/load logic
3. archive/status logic
4. web server
5. HTML shell
6. JavaScript rendering
7. editing flows
8. categories
9. checkout
10. styling
11. integration

Do not reverse that order.

If you try to make the interface first without understanding the data, you will get lost quickly.

If you build the data and behavior first, the interface becomes much easier to reason about.
