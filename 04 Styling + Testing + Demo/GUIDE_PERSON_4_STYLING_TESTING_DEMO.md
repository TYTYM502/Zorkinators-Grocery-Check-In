# Person 4 Guide: CSS, Testing, and Demo Preparation

## Your Role

You are responsible for making the project:

- readable
- usable
- stable
- presentable

You are mainly working in:

- `static/style.css`
- testing notes
- integration checks
- demo prep documentation

## What CSS Actually Does

Good CSS helps users understand:

- what matters most
- what is clickable
- what is active
- what is archived
- what needs attention

For this app, CSS should improve clarity.

# Part 1: Style the Layout

## Step 1: Open `static/style.css`

Start with structure first:

- page width
- spacing
- cards
- section separation
- tab layout

## Step 2: Style the Header and Dashboard Area

The top of the page should quickly answer:

- what app is this?
- what is the current state of inventory?

## Step 3: Style the Tab Bar

Users should be able to tell:

- which tab is active
- which tabs are available
- that the tabs are clickable

# Part 2: Style the Data Tables

## Step 4: Style the Session Table

This table should feel like a staging area.

Priorities:

- readable spacing
- clearly labeled headers
- obvious action buttons
- status visibility

## Step 5: Style Grouped Inventory

Grouped inventory has 2 levels:

### Summary Row

Shows the barcode group.

### Inner Item Area

Shows the individual serial/item records.

Use CSS so the user can immediately tell the difference.

## Step 6: Style Records View

The Records tab must make active and archived states easy to recognize.

Use visually distinct styles for:

- active records
- archived records

# Part 3: Style Status and Buttons

## Step 7: Style Status States

Make these visually distinct:

- fresh
- expiring soon
- expired

## Step 8: Style Action Buttons

Buttons should reflect purpose.

Examples:

- standard action
- dangerous action like archive
- secondary action

# Part 4: Test the Whole App

## Step 9: Make a Core Feature Test List

Create a checklist with:

### Session

- scan known barcode
- scan unknown barcode
- add new staged item
- edit staged item
- approve session

### Inventory

- grouped row appears
- soonest expiration is shown at top
- details expand properly
- edit inner item works
- archive group works

### Records

- active records appear
- archived records appear
- filters work
- edit record works
- add archived-only record works

### Categories

- create category
- edit category
- recommended expiration changes
- warning threshold affects status

### Checkout

- removing one item works
- quantity decreases
- archived history remains

## Step 10: Turn Checklists Into Checkpoints

Suggested checkpoints:

### Checkpoint 1

- database works
- app starts

### Checkpoint 2

- page loads
- bootstrap data loads

### Checkpoint 3

- session staging works
- approval works

### Checkpoint 4

- grouped inventory works
- records view works

### Checkpoint 5

- archive and checkout work

### Checkpoint 6

- full demo flow works

# Part 5: Demo Preparation

## Step 11: Write a Demo Script

Write a script with:

1. what you open first
2. what you say while showing check-in
3. what you say while showing grouped inventory
4. what you say while showing records/history
5. what you say while showing checkout
6. what you say while showing archived history

## Step 12: Build a Demo Dataset

Prepare a small clean dataset with:

- at least one barcode with multiple item records
- at least one archived record
- at least one expiring soon item
- at least one category rule

## Step 13: Prepare Raspberry Pi Notes

Check:

- Python version
- folder path structure
- startup command
- browser access
- whether the database file is present

# Part 6: Integration Leadership

Ask repeatedly:

1. Does the app still start?
2. Does the UI still make sense?
3. Did a new feature break something old?
4. Is grouped inventory still clear?
5. Are archived records still visible?

## Final Team-Wide Test Flow

Run this exact flow before the demo:

1. start the app
2. open the page
3. scan an unknown barcode
4. fill in item details
5. approve session
6. confirm inventory group appears
7. add another item with same barcode
8. confirm quantity increases
9. expand the group
10. edit one inner item
11. checkout one item
12. confirm quantity decreases
13. archive the remaining group
14. confirm group disappears from active inventory
15. confirm records still show all serial IDs
16. scan the same barcode again
17. confirm the template is remembered

## Final Things You Should Be Able To Explain

1. how the design helps the user understand the app
2. how grouped inventory is visually separated from record details
3. how active vs archived records are shown clearly
4. how the team verified the app step by step
5. how the demo flow proves the project’s main value
