import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# class for EACH INDIVIDUAL item
@dataclass
class Item:
    barcode: int
    name: str
    category: str
    storage_location: str
    purchase_date: datetime
    exp_date: datetime
    item_id: Optional[int] = None
    archived: bool = False
    archived_date: Optional[datetime] = None

# dataclass that stores the items in each category 
@dataclass
class Category:
    name: str
    storage_location:str
    recommended_exp_days: int = 7
    warning_threshold_percent: int = 80
    items: List[Item] = field(default_factory = list)

class Inventory:
    def __init__(self, db_path='inventory.db'):
        # database path
        self.db_path = db_path
        # SQLite connection
        self.conn = sqlite3.connect(db_path, check_same_thread= False)
        # create tables
        self.create_tables()
        # load existing data
        self.load_data()

    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY,
                storage_location TEXT,
                recommended_exp_days INTEGER,
                warning_threshold_percent INTEGER DEFAULT 80              
            )                      
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS items (
                item_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT,
                name TEXT,
                category TEXT,
                storage_location TEXT,
                expiration_date TEXT,
                purchase_date TEXT,
                archived INTEGER DEFAULT 0,
                archived_date TEXT
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Placeholder for Part 2
        pass

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()