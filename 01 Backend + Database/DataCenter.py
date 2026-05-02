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
        # The web UI serves requests on background threads, so the SQLite
        # connection needs cross-thread access enabled.
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()
        self.categories: Dict[str, Category] = {}
        self.storages: Dict[str, Storage] = {}
        self.items: Dict[int, Item] = {}  # Key is item_id, not barcode
        self.load_data()

    @staticmethod
    def _normalize_key(value: str) -> str:
        return value.strip().lower()

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
        self.categories = {}
        self.storages = {}
        self.items = {}

        # Load categories
        cursor = self.conn.execute('SELECT * FROM categories')
        for row in cursor:
            cat = Category(
                name=row[0], storage_location=row[1], recommended_exp_days=row[2],
                warning_threshold_percent=row[3] if len(row) > 3 else 80
            )
            self.categories[self._normalize_key(cat.name)] = cat

        # Load active items (not archived)
        cursor = self.conn.execute('SELECT * FROM items WHERE archived = 0')
        for row in cursor:
            item = self._row_to_item(row)
            self.items[item.item_id] = item
            # Add to category
            cat_key = self._normalize_key(item.category)
            if cat_key not in self.categories:
                self.categories[cat_key] = Category(name=item.category, storage_location=item.storage_location)
            self.categories[cat_key].items.append(item)
            # Add to storage (case-insensitive)
            storage_key = self._normalize_key(item.storage_location)
            if storage_key not in self.storages:
                self.storages[storage_key] = Storage(location=item.storage_location)
            self.storages[storage_key].items.append(item)

    def save_item(self, item: Item):
        self.conn.execute('''
            INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.item_id, item.barcode, item.name, item.category, item.storage_location,
            item.exp_date.isoformat(), item.purchase_date.isoformat(),
            int(item.archived), item.archived_date.isoformat() if item.archived_date else None
        ))
        self.conn.commit()

    def _row_to_item(self, row) -> Item:
        exp_date = datetime.fromisoformat(row[5])
        purchase_date = datetime.fromisoformat(row[6])
        archived_date = datetime.fromisoformat(row[8]) if row[8] else None
        return Item(
            item_id=row[0], barcode=row[1], name=row[2], category=row[3],
            storage_location=row[4], exp_date=exp_date, purchase_date=purchase_date,
            archived=bool(row[7]), archived_date=archived_date
        )

    def save_category(self, cat: Category):
        self.conn.execute('''
            INSERT OR REPLACE INTO categories VALUES (?, ?, ?, ?)
        ''', (cat.name, cat.storage_location, cat.recommended_exp_days, cat.warning_threshold_percent))
        self.conn.commit()

    def add_item(self, barcode: str, name: str, category: str, storage_location: str, exp_date: datetime, purchase_date: datetime) -> Item:
        return self.create_record(barcode, name, category, storage_location, exp_date, purchase_date, archived=False)

    def create_record(
        self,
        barcode: str,
        name: str,
        category: str,
        storage_location: str,
        exp_date: datetime,
        purchase_date: datetime,
        archived: bool = False,
    ) -> Item:
        archived_date = datetime.now().isoformat() if archived else None
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
        self.conn.commit()
        item_id = self.conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        category_key = self._normalize_key(category)
        if category_key not in self.categories:
            self.save_category(Category(name=category, storage_location=storage_location))
        self.load_data()
        if not archived and item_id in self.items:
            return self.items[item_id]
        return self.get_record(item_id)

    def get_recommended_exp_date(self, category: str, purchase_date: datetime) -> datetime:
        category_lower = self._normalize_key(category)
        if category_lower in self.categories:
            days = self.categories[category_lower].recommended_exp_days
            return purchase_date + timedelta(days=days)
        return purchase_date + timedelta(days=7)  # default

    def update_recommended_exp(self, category: str, actual_exp_days: int):
        category_lower = self._normalize_key(category)
        if category_lower in self.categories:
            cat = self.categories[category_lower]
            # Simple average or something, for now just set
            cat.recommended_exp_days = (cat.recommended_exp_days + actual_exp_days) // 2
            self.save_category(cat)

    def archive_item(self, item_id: int):
        """Mark an item as archived instead of deleting it."""
        self.conn.execute(
            'UPDATE items SET archived = 1, archived_date = ? WHERE item_id = ?',
            (datetime.now().isoformat(), item_id),
        )
        self.conn.commit()
        self.load_data()

    def archive_items_by_barcode(self, barcode: str) -> int:
        cursor = self.conn.execute(
            'UPDATE items SET archived = 1, archived_date = ? WHERE barcode = ? AND archived = 0',
            (datetime.now().isoformat(), barcode),
        )
        self.conn.commit()
        self.load_data()
        return cursor.rowcount

    def remove_item(self, item_id: int):
        if item_id in self.items:
            self.archive_item(item_id)

    def get_expired_items(self) -> List[Item]:
        now = datetime.now()
        return [item for item in self.items.values() if not item.archived and item.exp_date < now]

    def get_items_by_barcode(self, barcode: str) -> List[Item]:
        """Get all individual items with the same barcode."""
        return [item for item in self.items.values() if item.barcode == barcode and not item.archived]

    def get_item_template_by_barcode(self, barcode: str) -> Optional[Item]:
        """Get the most recent saved record for a barcode, including archived items."""
        cursor = self.conn.execute(
            '''
            SELECT item_id, barcode, name, category, storage_location, exp_date, purchase_date, archived, archived_date
            FROM items
            WHERE barcode = ?
            ORDER BY purchase_date DESC, item_id DESC
            LIMIT 1
            ''',
            (barcode,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        return self._row_to_item(row)

    def get_quantity_for_barcode(self, barcode: str) -> int:
        """Get total quantity for a specific barcode."""
        return len(self.get_items_by_barcode(barcode))

    def search_items(self, query: str = "", category: str = "", storage: str = "", exp_status: str = "all") -> List[Item]:
        """Search and filter items. exp_status: 'all', 'expired', 'expiring_soon', 'fresh'"""
        results = []
        
        for item in self.items.values():
            if item.archived:
                continue
            
            # Search by name or barcode
            if query and query.lower() not in item.name.lower() and query not in item.barcode:
                continue
            
            # Filter by category
            if category and self._normalize_key(item.category) != self._normalize_key(category):
                continue
            
            # Filter by storage location
            if storage and self._normalize_key(item.storage_location) != self._normalize_key(storage):
                continue
            
            # Filter by expiration status
            item_status = self.get_item_status(item)
            if exp_status != "all" and item_status != exp_status:
                continue
            
            results.append(item)
        
        return results

    def get_items_warning_expiration(self) -> List[Item]:
        """Get items that should be used soon based on percent threshold."""
        return [
            item for item in self.items.values()
            if not item.archived and self.get_item_status(item) == "expiring_soon"
        ]

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

    def update_item(
        self,
        item_id: int,
        name: str,
        category: str,
        storage_location: str,
        exp_date: datetime,
        purchase_date: datetime,
        archived: Optional[bool] = None,
    ):
        existing = self.get_record(item_id)
        if not existing:
            raise KeyError(f"Item {item_id} not found")

        archived_value = existing.archived if archived is None else archived
        archived_date = existing.archived_date
        if archived_value and archived_date is None:
            archived_date = datetime.now()
        if not archived_value:
            archived_date = None

        item = Item(
            item_id=item_id,
            barcode=existing.barcode,
            name=name.strip(),
            category=category.strip(),
            storage_location=storage_location.strip(),
            exp_date=exp_date,
            purchase_date=purchase_date,
            archived=archived_value,
            archived_date=archived_date,
        )
        self.save_item(item)
        category_key = self._normalize_key(item.category)
        if category_key not in self.categories:
            self.save_category(Category(name=item.category, storage_location=item.storage_location))
        self.load_data()
        return self.get_record(item_id)

    def upsert_category(self, name: str, storage_location: str, recommended_exp_days: int, warning_threshold_percent: int):
        key = self._normalize_key(name)
        if key in self.categories:
            cat = self.categories[key]
            cat.storage_location = storage_location.strip()
            cat.recommended_exp_days = recommended_exp_days
            cat.warning_threshold_percent = warning_threshold_percent
        else:
            cat = Category(
                name=name.strip(),
                storage_location=storage_location.strip(),
                recommended_exp_days=recommended_exp_days,
                warning_threshold_percent=warning_threshold_percent,
            )
            self.categories[key] = cat
        self.save_category(cat)
        return cat

    def serialize_item(self, item: Item) -> dict:
        return {
            "item_id": item.item_id,
            "barcode": item.barcode,
            "name": item.name,
            "category": item.category,
            "storage_location": item.storage_location,
            "exp_date": item.exp_date.strftime("%Y-%m-%d"),
            "purchase_date": item.purchase_date.strftime("%Y-%m-%d"),
            "status": self.get_item_status(item),
            "archived": item.archived,
            "archived_date": item.archived_date.strftime("%Y-%m-%d") if item.archived_date else "",
        }

    def serialize_category(self, cat: Category) -> dict:
        return {
            "name": cat.name,
            "storage_location": cat.storage_location,
            "recommended_exp_days": cat.recommended_exp_days,
            "warning_threshold_percent": cat.warning_threshold_percent,
            "item_count": len(cat.items),
        }

    def get_inventory_rows(self, query: str = "", category: str = "", storage: str = "", exp_status: str = "all") -> List[dict]:
        results = self.search_items(query, category, storage, exp_status)
        results.sort(key=lambda item: (item.exp_date, item.name.lower(), item.item_id or 0))
        return [self.serialize_item(item) for item in results]

    def get_inventory_groups(self, query: str = "", category: str = "", storage: str = "", exp_status: str = "all") -> List[dict]:
        grouped: Dict[str, List[Item]] = {}
        for item in self.search_items(query, category, storage, exp_status):
            grouped.setdefault(item.barcode, []).append(item)

        groups = []
        for barcode, items in grouped.items():
            items.sort(key=lambda item: (item.exp_date, item.purchase_date, item.item_id or 0))
            top = items[0]
            groups.append({
                "barcode": barcode,
                "name": top.name,
                "category": top.category,
                "storage_location": top.storage_location,
                "quantity": len(items),
                "top_exp_date": top.exp_date.strftime("%Y-%m-%d"),
                "top_status": self.get_item_status(top),
                "items": [self.serialize_item(item) for item in items],
            })

        groups.sort(key=lambda group: (group["top_exp_date"], group["name"].lower(), group["barcode"]))
        return groups

    def get_record(self, item_id: int) -> Optional[Item]:
        row = self.conn.execute(
            '''
            SELECT item_id, barcode, name, category, storage_location, exp_date, purchase_date, archived, archived_date
            FROM items
            WHERE item_id = ?
            ''',
            (item_id,),
        ).fetchone()
        if not row:
            return None
        return self._row_to_item(row)

    def get_all_records(self, query: str = "", record_status: str = "all") -> List[dict]:
        rows = self.conn.execute(
            '''
            SELECT item_id, barcode, name, category, storage_location, exp_date, purchase_date, archived, archived_date
            FROM items
            ORDER BY item_id DESC
            '''
        ).fetchall()
        records = [self._row_to_item(row) for row in rows]

        filtered = []
        for item in records:
            if query and query.lower() not in item.name.lower() and query not in item.barcode and query not in str(item.item_id):
                continue
            if record_status == "active" and item.archived:
                continue
            if record_status == "archived" and not item.archived:
                continue
            filtered.append(self.serialize_item(item))

        return filtered

    def get_storage_names(self) -> List[str]:
        return sorted(storage.location for storage in self.storages.values())

    def get_category_names(self) -> List[str]:
        return sorted(category.name for category in self.categories.values())

    def get_item_status(self, item: Item) -> str:
        now = datetime.now()
        if item.exp_date < now:
            return "expired"

        category = self.categories.get(self._normalize_key(item.category))
        if not category:
            return "fresh"

        total_seconds = (item.exp_date - item.purchase_date).total_seconds()
        if total_seconds <= 0:
            return "expiring_soon"

        remaining_seconds = max((item.exp_date - now).total_seconds(), 0)
        remaining_threshold = total_seconds * (1 - (category.warning_threshold_percent / 100))

        if remaining_seconds <= remaining_threshold:
            return "expiring_soon"
        return "fresh"

    def close(self):
        self.conn.close()