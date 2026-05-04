# Person 3 Guide: JavaScript and Interaction

## Your Role

You are responsible for making the page behave like an app.

You are mainly working in:

- `static/app.js`

You connect:

- the HTML structure
- the Python backend
- the user’s actions

## What JavaScript Does in This Project

JavaScript handles:

- clicks and form submissions
- sending requests to Python
- receiving JSON
- updating tables and messages
- opening and closing modals
- filtering
- expanding grouped inventory rows

## The Most Important Pattern

Almost every feature follows this pattern:

1. the user does something
2. JavaScript catches it
3. JavaScript sends data to Python
4. Python responds
5. JavaScript redraws the page

# Part 1: Start Small

## Step 1: Open `static/app.js`

Start with structure, not every feature at once.

Create:

- a `state` object
- an `elements` object
- a `loadState()` function
- a `render()` function

## Step 2: Build a `state` Object

The `state` object is the frontend’s memory.

It can hold:

- latest backend data
- inventory filters
- record filters

## Step 3: Build an `elements` Object

This stores references to important HTML elements.

Examples:

- table bodies
- forms
- message areas
- modals
- filters

# Part 2: Load Data From the Backend

## Step 4: Build `loadState()`

This function should:

1. build the query string from filters
2. call the bootstrap route
3. read JSON
4. store it in `state`
5. call `render()`

## Step 5: Build `render()`

This function should call smaller functions like:

- `renderStats()`
- `renderSessionItems()`
- `renderInventory()`
- `renderRecords()`
- `renderCategories()`

## Checkpoint A

At this point, your JavaScript should be able to:

1. fetch bootstrap data
2. store it
3. call render functions

# Part 3: Render the Session Table

## Step 6: Build `renderSessionItems()`

The session table should show staged items, not active inventory.

Each row should show:

- session ID
- barcode
- name
- category
- storage
- purchase date
- expiration date
- status
- edit action

## Step 7: Handle Empty State

If there are no session items, render a helpful empty message row.

## Checkpoint B

Prove:

1. session items appear after staging
2. empty session shows a helpful message
3. clicking edit identifies the correct session item

# Part 4: Render Grouped Inventory

## Step 8: Understand Grouped Inventory Before Coding It

The Inventory tab is not a flat list of every item.

It is a grouped summary view.

Each backend group should include:

- barcode
- name
- category
- storage location
- quantity
- soonest expiration date
- top status
- inner list of real item records

## Step 9: Build `renderInventory()`

This function should:

1. loop through barcode groups
2. render one summary row per group
3. create a hidden details row underneath
4. put the individual records inside the hidden area

### Summary Row

Should show:

- barcode
- name
- category
- storage
- quantity
- earliest expiration
- top status
- show/hide button
- archive group button

### Inner Records

Should show:

- serial ID
- purchase date
- expiration date
- status
- edit button

## Step 10: Add Expand/Collapse Behavior

When the show button is clicked:

1. find the matching hidden row
2. toggle hidden/not hidden
3. update button text

## Step 11: Add Group Archive Behavior

When group archive is clicked:

1. confirm with the user
2. send barcode to backend
3. show response message
4. reload state

## Checkpoint C

Prove:

1. grouped rows appear
2. expanding shows the individual records
3. the soonest expiration date is shown at the top
4. archiving a group removes it from active inventory
5. history still exists in records view

# Part 5: Render All Records

## Step 12: Build `renderRecords()`

The Records tab shows:

- active records
- archived records
- serial IDs
- barcode numbers
- names
- dates
- current state

## Step 13: Build Record Filters

Use frontend filter state for:

- search query
- all/active/archived choice

## Step 14: Add Record Editing

When the user clicks record edit:

1. find the matching record in state
2. open the modal
3. pre-fill the record values
4. show active/archived choice

## Checkpoint D

Prove:

1. active and archived records both show
2. filters work
3. record edit opens the correct row

# Part 6: Build Form Submissions

## Step 15: Build Scan Form Submission

When scan form submits:

1. prevent page reload
2. read barcode
3. send it to Python
4. read response

If barcode is known:

- add staged item automatically

If unknown:

- open item modal

## Step 16: Build Item Save Submission

One form supports multiple modes:

- session create
- session edit
- inventory edit
- record create
- record edit

Your save logic should:

1. read the mode
2. build the payload
3. choose the correct route
4. send request
5. show result
6. close modal on success
7. reload state

## Step 17: Build Approve Session

This should:

1. call session approve route
2. show result message
3. reload state

## Step 18: Build Checkout Submission

This should:

1. read barcode
2. send request
3. show result
4. reload state

## Step 19: Build Category Form Submission

This should:

1. collect category fields
2. send them to backend
3. show result
4. reload state

## Checkpoint E

Prove:

1. known barcode scan creates session draft
2. unknown barcode opens item form
3. session approval works
4. checkout works
5. category save works
6. record create works

# Part 7: Build Modal Behavior

## Step 20: Build `openItemModal()`

This function needs to:

1. decide the mode
2. set form title text
3. fill fields
4. fill hidden IDs
5. control whether barcode is editable
6. control whether archived selector is visible
7. show the modal

## Step 21: Build Recommended Expiration Updates

If the user changes:

- category
- purchase date

the frontend can ask the backend for a recommended expiration date.

## Final Things You Should Be Able To Explain

1. how the page gets its initial data
2. how grouped inventory is rendered
3. how one form supports multiple save modes
4. why reload-after-success is useful
5. how frontend state helps keep the interface organized
