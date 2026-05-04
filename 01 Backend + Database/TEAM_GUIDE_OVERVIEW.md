# Grocery Check-In Team Guide Overview

## Purpose

This project guide is split into 4 separate files so each teammate has a primary build workbook.

These are not meant to isolate teammates from each other.

They are meant to:

- reduce confusion
- clarify ownership
- make it easier to start
- help each person understand what they are building

## Read These In This Order

1. Read this overview first.
2. Each person reads their own file fully.
3. Each person skims the other 3 files so they understand how the pieces connect.

## Team Files

- [Person 1 - Backend and Database Guide](./GUIDE_PERSON_1_BACKEND_DATABASE.md)
- [Person 2 - HTML Structure Guide](./GUIDE_PERSON_2_HTML_STRUCTURE.md)
- [Person 3 - JavaScript and Interaction Guide](./GUIDE_PERSON_3_JAVASCRIPT_INTERACTION.md)
- [Person 4 - CSS, Testing, and Demo Guide](./GUIDE_PERSON_4_STYLING_TESTING_DEMO.md)

## Project Goal

Build a grocery check-in web app with:

- staged session intake
- approval into inventory
- grouped inventory by barcode
- individual serial/item records underneath
- category-based expiration warnings
- checkout/removal flow
- archived records that remain saved
- records view for active and archived items

## Core Rule Everyone Must Understand

There are 3 different "layers" in this project:

1. `SQLite` stores the data.
2. `Python` controls the rules and sends data to the browser.
3. `HTML/CSS/JavaScript` show and update the interface.

If something breaks, always ask which layer is responsible.

## Team Starting Point

All 4 people should meet and agree on:

1. What a session item is.
2. What an inventory item is.
3. Why barcode and serial ID are different.
4. Why archived records are kept instead of deleted.

If the team cannot explain those 4 ideas clearly, stop and discuss them before coding.

## Suggested Ownership

### Person 1

- `DataCenter.py`
- inventory rules
- SQLite logic

### Person 2

- `templates/index.html`
- page structure
- forms
- tables

### Person 3

- `static/app.js`
- rendering
- API calls
- interactivity

### Person 4

- `static/style.css`
- testing
- integration checks
- demo preparation

## Shared Checkpoints

After every major milestone, the team should pause and test together.

At minimum, do shared team tests after:

1. database creation
2. first successful page load
3. session staging
4. approval into inventory
5. grouped inventory
6. records and archive history
7. checkout
8. final demo flow

## Final Advice

Do not try to build everything at once.

Build in this order:

1. backend data model
2. HTML page shell
3. JavaScript rendering
4. styling and testing
5. integration and demo cleanup

That order matters.

If you build the visual side before the data side is stable, the project becomes much harder to understand.
