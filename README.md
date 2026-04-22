# Zorkinators Grocery Check-In System

This is a grocery check-in system for CSC 132 that allows users to check in food items via a barcode scanner.

## Features

- **Barcode Scanning**: Input 12-digit barcode numbers via scanner (simulates keyboard input with automatic enter).
- **Item Management**: Store items with name, category, storage location, quantity, expiration date, purchase date, batch number.
- **Categories**: Group items by category with general attributes like storage location and recommended expiration period.
- **Storage Locations**: Organize items by storage location.
- **GUI**: Tkinter-based interface to view inventory, add items, remove items, check expired items.
- **Database Persistence**: Uses SQLite to save data across sessions.

## Files

- **DataCenter.py**: Contains the data models (Item, Category, Storage, Inventory) and database operations.
- **GUI.py**: The main GUI application that interacts with the DataCenter.

## How to Use

1. Run `py GUI.py` to start the application.
2. Scan a barcode or type it in the entry field and press Enter.
3. If the item exists, quantity is incremented.
4. If new, enter item details (name, category, etc.), with recommended expiration date.
5. View items in the table.
6. Use buttons to remove items or check for expired ones.

## Classes

- **Item**: Represents individual food items.
- **Category**: Groups items with general attributes.
- **Storage**: Groups items by storage location.
- **Inventory**: Manages all data and database operations.