import sqlite3
import datetime
import dataclasses
import typing

# class for EACH INDIVIDUAL item
class Item:
    def __init__(self, barcode:int, name:str, category:str, storage_location:str, purchase_date, exp_date, item_id:int, archived:bool, archived_date):
        self.barcode = barcode
        self.name = name
        self.category = category
        self.storage_location = storage_location
        self.purchase_date = purchase_date
        self.exp_date = exp_date
        self.item_id = item_id
        self.archived = archived
        self.archived_date = archived_date

# dataclass that stores the items in each category 
@dataclasses
class Category:
    name: str
    storage_location:str
    recommended_exp_days: int
    warning_threshold_percent: int
    items: list

class Inventory:
    pass