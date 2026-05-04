# Person 2 Guide: HTML Structure

## Your Role

You are responsible for the structure of the browser interface.

You are mainly working in:

- `templates/index.html`

Your job is not to make it pretty yet.

Your job is to make the page understandable and organized so the rest of the team has something stable to attach behavior and styling to.

Think of yourself as building the rooms of a house before anyone paints the walls or wires the light switches.

## What HTML Actually Does

HTML creates:

- sections
- forms
- buttons
- tables
- containers for JavaScript to fill later

HTML does not:

- store database data
- calculate status
- control business rules

# Part 1: Plan the Page Before Coding

## Step 1: Draw the Page on Paper

Before opening `index.html`, sketch the screen using boxes.

Draw:

1. top header
2. stats area
3. tab bar
4. check-in area
5. inventory area
6. records area
7. overview area
8. checkout area
9. categories area
10. pop-up form area

## Step 2: Understand the Main Sections

Each major feature should get its own section.

### Header

Explains what the app is.

### Stats Area

Shows high-level counts.

### Tab Bar

Lets the user switch between sections.

### Check-In

Barcode scan and staged session review.

### Inventory

Grouped active inventory view.

### Records

All active and archived records together.

### Overview

Summary area.

### Checkout

Remove one item at a time by barcode.

### Categories

Manage category rules.

### Modals

Forms that pop up without leaving the page.

# Part 2: Create the Main Page Shell

## Step 3: Create `index.html`

Start with:

- doctype
- html
- head
- body

### `head`

Contains metadata, stylesheet links, fonts, and scripts.

### `body`

Contains what the user sees.

## Step 4: Build the Header

Include:

- app title
- short description
- maybe a small dashboard panel

## Step 5: Add a Stats Container

Create an empty section where JavaScript can later insert stat cards.

The HTML provides the space.

JavaScript later fills it.

## Step 6: Build the Tab Bar

Make tab controls for:

- Check In
- Inventory
- Records
- Overview
- Checkout
- Categories

# Part 3: Build Each Main Section

## Step 7: Build the Check-In Section

This needs 2 main parts:

### Part A: Barcode Input Area

Include:

- explanation text
- barcode input
- submit button
- message area

### Part B: Session Table

Headers should include:

- session ID
- barcode
- name
- category
- storage
- purchase date
- expiration date
- status
- actions

## Step 8: Build the Inventory Section

This section shows grouped active inventory.

It should have:

### Filter Form

- search box
- category filter
- storage filter
- status filter
- refresh button

### Inventory Table

Headers should include:

- barcode
- name
- category
- storage
- quantity
- soonest expiration
- top status
- details/actions

## Step 9: Build the Records Section

This section shows all records.

It needs:

### Filter Controls

- search by ID/barcode/name
- all
- active only
- archived only

### Records Table

Headers should include:

- serial ID
- barcode
- name
- category
- storage
- purchase date
- expiration date
- active/archived state
- actions

## Step 10: Build the Overview Section

Create containers where JavaScript can later show:

- category breakdown
- storage breakdown

## Step 11: Build the Checkout Section

It only needs:

- explanation
- barcode input
- remove button
- feedback message

## Step 12: Build the Categories Section

Include:

- heading
- short explanation
- add category button
- category table

Headers should include:

- name
- storage
- recommended days
- warning percent
- item count
- actions

# Part 4: Build the Modal Forms

## Step 13: Build the Item Modal

This form will be reused in different modes:

- creating a staged item
- editing a staged item
- editing an active item
- creating a record directly
- editing a record

Include:

- hidden mode field
- hidden target ID field
- barcode field
- name field
- category field
- storage field
- purchase date field
- expiration date field
- archived/active selector for record mode
- save button
- message area

## Step 14: Build the Category Modal

Include:

- category name
- storage location
- recommended expiration days
- warning threshold percent
- save button
- feedback area

## Step 15: Add Datalists and Other Helpers

If the team wants category or storage suggestions, create HTML helpers like datalists.

# Part 5: Make the HTML Friendly for JavaScript

## Step 16: Add IDs Carefully

Every important form, table body, modal, and message area should have a clear ID.

Examples:

- scan form
- session table body
- inventory table body
- records table body
- category table body
- item modal
- category modal

## Step 17: Keep Labels Clear

Use clear button text.

Good examples:

- `Add to Session`
- `Approve Session`
- `Remove 1 Item`
- `Add Record`
- `Archive Group`

## Step 18: Write Short Helper Text

Every section should explain itself in one or two short sentences.

## Checkpoint A

Without JavaScript yet, you should be able to point to:

1. where staged items will appear
2. where grouped inventory will appear
3. where archived records will appear
4. where category rules will appear
5. where checkout happens

## Checkpoint B

Ask your JavaScript teammate:

1. Can you easily find the correct table bodies?
2. Can you easily find the forms?
3. Do the IDs make sense?

## Final Things You Should Be Able To Explain

1. why the app needs tabs
2. why inventory and records are separate views
3. why the item form is reused for multiple modes
4. how the HTML makes JavaScript easier to write
