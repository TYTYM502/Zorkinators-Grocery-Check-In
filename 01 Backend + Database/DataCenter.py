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

@dataclass
class Storage:
    location: str
    items: List[Item] = field(default_factory=list)

class Inventory:
    def __init__(self, db_path='inventory.db'):
        # database path
        self.db_path = db_path
        # SQLite connection
        self.conn = sqlite3.connect(db_path, check_same_thread= False)
        # create tables
        self.create_tables()
        # variables to access database
        self.categories: Dict[str, Category] = {}
        self.storages: Dict[str, Storage] = {}
        self.items: Dict[int, Item] = {}
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
        self.categories = {}
        self.storages = {}
        self.items = {}

        # load categories
        cursor = self.conn.execute('SELECT * FROM categories')
        # go through database rows
        for row in cursor:
            cat = Category(
                name=row[0],
                storage_location=row[1],
                recommended_exp_days=row[2],
                warning_threshold_percent=row[3]
            )
            self.categories[cat.name.lower()] = cat

        # load non archived items
        cursor = self.conn.execute('SELECT * FROM items WHERE archived = 0')
        for row in cursor:
            exp_date = datetime.fromisoformat(row[5])
            purchase_date = datetime.fromisoformat(row[6])
            # skip archived in row 7 because it is used above
            archived_date = datetime.fromisoformat(row[8]) if row[8] else None

            item = Item(
                item_id=row[0],
                barcode=row[1],
                name=row[2],
                category=row[3],
                storage_location=row[4],
                exp_date=exp_date,
                purchase_date=purchase_date,
                archived=bool(row[7]),
                archived_date=archived_date
            )

            self.items[item.item_id] = item
            
            cat_key = item.category.lower()
            if cat_key not in self.categories:
                self.categories[cat_key] = Category(
                    name=item.category,
                    storage_location=item.storage_location
                )
            self.categories[cat_key].items.append(item)

            storage_key = item.storage_location.lower()
            if storage_key not in self.storages:
                self.storages[storage_key] = Storage(location=item.storage_location)

            self.storages[storage_key].items.append(item)
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()


inventory = Inventory()
print(inventory.categories)
print(inventory.items)
print(inventory.storages)