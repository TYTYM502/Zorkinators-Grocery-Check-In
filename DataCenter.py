# This file will be used to create the "item" class that will take in the inputs from the GUI and scanner

import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Item:
    barcode: str
    name: str
    category: str
    storage_location: str
    exp_date: datetime
    purchase_date: datetime
    item_id: Optional[int] = None  # Unique ID for each individual item
    archived: bool = False
    archived_date: Optional[datetime] = None

@dataclass
class Category:
    name: str
    storage_location: str
    recommended_exp_days: int = 7
    warning_threshold_percent: int = 80  # Warn at 80% of shelf life used
    items: List[Item] = field(default_factory=list)

@dataclass
class Storage:
    location: str
    items: List[Item] = field(default_factory=list)

class Inventory:
    def __init__(self, db_path='inventory.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
        self.categories: Dict[str, Category] = {}
        self.storages: Dict[str, Storage] = {}
        self.items: Dict[int, Item] = {}  # Key is item_id, not barcode
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
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        # Load categories
        cursor = self.conn.execute('SELECT * FROM categories')
        for row in cursor:
            cat = Category(
                name=row[0], storage_location=row[1], recommended_exp_days=row[2],
                warning_threshold_percent=row[3] if len(row) > 3 else 80
            )
            self.categories[cat.name.lower()] = cat

        # Load active items (not archived)
        cursor = self.conn.execute('SELECT * FROM items WHERE archived = 0')
        for row in cursor:
            exp_date = datetime.fromisoformat(row[5])
            purchase_date = datetime.fromisoformat(row[6])
            archived_date = datetime.fromisoformat(row[8]) if row[8] else None
            item = Item(
                item_id=row[0], barcode=row[1], name=row[2], category=row[3],
                storage_location=row[4], exp_date=exp_date, purchase_date=purchase_date,
                archived=bool(row[7]), archived_date=archived_date
            )
            self.items[item.item_id] = item
            # Add to category
            cat_key = item.category.lower()
            if cat_key not in self.categories:
                self.categories[cat_key] = Category(name=item.category, storage_location=item.storage_location)
            self.categories[cat_key].items.append(item)
            # Add to storage
            if item.storage_location not in self.storages:
                self.storages[item.storage_location] = Storage(location=item.storage_location)
            self.storages[item.storage_location].items.append(item)

    def save_item(self, item: Item):
        self.conn.execute('''
            INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.item_id, item.barcode, item.name, item.category, item.storage_location,
            item.exp_date.isoformat(), item.purchase_date.isoformat(),
            int(item.archived), item.archived_date.isoformat() if item.archived_date else None
        ))
        self.conn.commit()

    def save_category(self, cat: Category):
        self.conn.execute('''
            INSERT OR REPLACE INTO categories VALUES (?, ?, ?, ?)
        ''', (cat.name, cat.storage_location, cat.recommended_exp_days, cat.warning_threshold_percent))
        self.conn.commit()

    def add_item(self, barcode: str, name: str, category: str, storage_location: str, exp_date: datetime, purchase_date: datetime) -> Item:
        # Normalize category to lowercase for consistency
        category_lower = category.lower()
        
        item = Item(
            item_id=None, barcode=barcode, name=name, category=category, storage_location=storage_location,
            exp_date=exp_date, purchase_date=purchase_date, archived=False
        )
        self.conn.execute('''
            INSERT INTO items (barcode, name, category, storage_location, exp_date, purchase_date, archived, archived_date)
            VALUES (?, ?, ?, ?, ?, ?, 0, NULL)
        ''', (barcode, name, category, storage_location, exp_date.isoformat(), purchase_date.isoformat()))
        self.conn.commit()
        
        # Get the generated item_id
        cursor = self.conn.execute('SELECT last_insert_rowid()')
        item.item_id = cursor.fetchone()[0]
        
        self.items[item.item_id] = item
        if category_lower not in self.categories:
            self.categories[category_lower] = Category(name=category, storage_location=storage_location)
        self.categories[category_lower].items.append(item)
        if storage_location not in self.storages:
            self.storages[storage_location] = Storage(location=storage_location)
        self.storages[storage_location].items.append(item)
        self.save_category(self.categories[category_lower])
        return item

    def get_recommended_exp_date(self, category: str, purchase_date: datetime) -> datetime:
        category_lower = category.lower()
        if category_lower in self.categories:
            days = self.categories[category_lower].recommended_exp_days
            return purchase_date + timedelta(days=days)
        return purchase_date + timedelta(days=7)  # default

    def update_recommended_exp(self, category: str, actual_exp_days: int):
        category_lower = category.lower()
        if category_lower in self.categories:
            cat = self.categories[category_lower]
            # Simple average or something, for now just set
            cat.recommended_exp_days = (cat.recommended_exp_days + actual_exp_days) // 2
            self.save_category(cat)

    def archive_item(self, item_id: int):
        """Mark an item as archived instead of deleting it."""
        if item_id in self.items:
            item = self.items[item_id]
            item.archived = True
            item.archived_date = datetime.now()
            self.save_item(item)
            # Remove from active lists
            self.categories[item.category].items = [i for i in self.categories[item.category].items if i.item_id != item_id]
            self.storages[item.storage_location].items = [i for i in self.storages[item.storage_location].items if i.item_id != item_id]

    def remove_item(self, item_id: int):
        if item_id in self.items:
            self.archive_item(item_id)

    def get_expired_items(self) -> List[Item]:
        now = datetime.now()
        return [item for item in self.items.values() if not item.archived and item.exp_date < now]

    def get_items_by_barcode(self, barcode: str) -> List[Item]:
        """Get all individual items with the same barcode."""
        return [item for item in self.items.values() if item.barcode == barcode and not item.archived]

    def get_quantity_for_barcode(self, barcode: str) -> int:
        """Get total quantity for a specific barcode."""
        return len(self.get_items_by_barcode(barcode))

    def search_items(self, query: str = "", category: str = "", storage: str = "", exp_status: str = "all") -> List[Item]:
        """Search and filter items. exp_status: 'all', 'expired', 'expiring_soon', 'fresh'"""
        results = []
        now = datetime.now()
        
        for item in self.items.values():
            if item.archived:
                continue
            
            # Search by name or barcode
            if query and query.lower() not in item.name.lower() and query not in item.barcode:
                continue
            
            # Filter by category
            if category and item.category != category:
                continue
            
            # Filter by storage location
            if storage and item.storage_location != storage:
                continue
            
            # Filter by expiration status
            if exp_status == "expired" and item.exp_date >= now:
                continue
            elif exp_status == "fresh" and item.exp_date < now:
                continue
            elif exp_status == "expiring_soon":
                cat = self.categories.get(item.category)
                if cat:
                    threshold_days = (item.exp_date - item.purchase_date).days * (cat.warning_threshold_percent / 100)
                    warn_date = item.purchase_date + timedelta(days=threshold_days)
                    if now < warn_date:
                        continue
                else:
                    continue
            
            results.append(item)
        
        return results

    def get_items_warning_expiration(self) -> List[Item]:
        """Get items that should be used soon based on percent threshold."""
        warning_items = []
        now = datetime.now()
        
        for item in self.items.values():
            if item.archived or item.exp_date < now:
                continue
            
            cat = self.categories.get(item.category)
            if cat:
                total_days = (item.exp_date - item.purchase_date).days
                days_used = (now - item.purchase_date).days
                percent_used = (days_used / total_days * 100) if total_days > 0 else 0
                
                if percent_used >= cat.warning_threshold_percent:
                    warning_items.append(item)
        
        return warning_items

    def get_statistics(self) -> dict:
        """Get inventory statistics."""
        active_items = [i for i in self.items.values() if not i.archived]
        expired = self.get_expired_items()
        warning = self.get_items_warning_expiration()
        
        return {
            'total_items': len(active_items),
            'expired_count': len(expired),
            'warning_count': len(warning),
            'categories': len(self.categories),
            'storage_locations': len(self.storages),
            'items_by_category': {cat: len(cat_obj.items) for cat, cat_obj in self.categories.items()},
            'items_by_storage': {storage: len(stor_obj.items) for storage, stor_obj in self.storages.items()},
        }

    def close(self):
        self.conn.close()
