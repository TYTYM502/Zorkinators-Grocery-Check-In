from food_barcodes import *


def add_item(item, barcode, expr):
    new_food = {
        item : [barcode, expr]
    }
    stock.update(new_food)

entry = input("Scan something please: ")

keys = [k for k, v in stock.items() if v == entry]
print(keys)


    

