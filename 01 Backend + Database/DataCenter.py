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
                exp_date TEXT,
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

            item = self._row_to_item(row)

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

    # "-> Item" makes the function show that it turns into an Item
    def _row_to_item(self, row) -> Item:
        # converts SQL database time from string to datetime format
        exp_date = datetime.fromisoformat(row[5])
        purchase_date = datetime.fromisoformat(row[6])
        # checks if there is actually an archived date
        archived_date = datetime.fromisoformat(row[8]) if row[8] else None

        item = Item(
            item_id=row[0],
            barcode=row[1],
            name=row[2],
            category=row[3],
            storage_location=row[4],
            exp_date=exp_date,
            purchase_date=purchase_date,
            # converts 0 or 1 in database into False or True in python
            archived=bool(row[7]),
            archived_date=archived_date
        )

        return item

    # ": Category" is a type hint
    def save_category(self, cat: Category):
        self.conn.execute(
            # question marks are placeholders
            '''
            INSERT OR REPLACE INTO categories VALUES (?, ?, ?, ?)
            ''',
            (cat.name, cat.storage_location, cat.recommended_exp_days, cat.warning_threshold_percent)
            )
        # publishes changes kind of like GitHub
        self.conn.commit()

    def create_record(
        self,
        barcode: str,
        name: str,
        category: str,
        storage_location: str,
        exp_date: datetime,
        purchase_date: datetime,
        archived: bool = False
    ):
        # whether archived date should be set
        archived_date = datetime.now().isoformat() if archived else None
        # run SQL insert
        self.conn.execute(
            '''
            INSERT INTO items (barcode, name, category, storage_location, exp_date, purchase_date, archived, archived_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                barcode, 
                name,
                category,
                storage_location,
                exp_date.isoformat(),
                purchase_date.isoformat(),
                int(archived),
                archived_date,
            ),
        )
        # commit the change
        self.conn.commit()
        # get new item ID
        item_id = self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        # reload active inventory
        self.load_data()
        # return created record
        if not archived and item_id in self.items:
            return self.items[item_id]
        return self.get_record(item_id)

    def add_item(
        self, 
        barcode: str,
        name: str,
        category: str,
        storage_location: str,
        exp_date: datetime,
        purchase_date: datetime
    ):
        return self.create_record(
            barcode,
            name,
            category,
            storage_location,
            exp_date,
            purchase_date,
            archived=False
        )

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()   
def main():
    exp_date = datetime(2026, 5, 22)
    purchase_date = datetime(2026, 4, 30)
    inventory = Inventory()
    item = inventory.add_item("123456789123", "Peanutbutter", "Jar", "Pantry", exp_date, purchase_date)

#main()