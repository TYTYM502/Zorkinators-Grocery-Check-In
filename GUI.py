


from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from DataCenter import Inventory, Item, Category
from functools import partial

# Create inventory
inventory = Inventory()

# Create root window
root = Tk()
root.title("Grocery Check-In System")
root.geometry('1000x700')

# Create notebook (tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)

# ======================= ENTER TAB =======================
enter_frame = ttk.Frame(notebook)
notebook.add(enter_frame, text="Enter")

barcode_label = Label(enter_frame, text="Scan Barcode:", font=("Arial", 12))
barcode_label.pack(pady=10)

barcode_entry = Entry(enter_frame, width=30, font=("Arial", 12))
barcode_entry.pack(pady=5)
barcode_entry.focus()

session_items = []  # Items added in current session

# Treeview for session items
columns = ('ID', 'Barcode', 'Name', 'Category', 'Storage', 'Exp Date')
session_tree = ttk.Treeview(enter_frame, columns=columns, show='headings', height=15)
for col in columns:
    session_tree.heading(col, text=col)
    session_tree.column(col, width=130)
session_tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

scrollbar_session = ttk.Scrollbar(enter_frame, orient=VERTICAL, command=session_tree.yview)
session_tree.configure(yscroll=scrollbar_session.set)
scrollbar_session.pack(side=RIGHT, fill=Y)

def refresh_session_tree():
    for item in session_tree.get_children():
        session_tree.delete(item)
    for item in session_items:
        session_tree.insert('', END, values=(
            item.item_id, item.barcode, item.name, item.category, item.storage_location,
            item.exp_date.strftime('%Y-%m-%d')
        ))

def open_new_item_window(barcode):
    """Open window for entering new item details."""
    item_window = Toplevel(root)
    item_window.title(f"Add Item - Barcode: {barcode}")
    item_window.geometry('500x350')
    
    # Name
    Label(item_window, text="Item Name:").pack(pady=5)
    name_entry = Entry(item_window, width=40)
    name_entry.pack(pady=5)
    
    # Category
    Label(item_window, text="Category:").pack(pady=5)
    category_var_new = StringVar()
    category_combo_new = ttk.Combobox(item_window, textvariable=category_var_new, width=37)
    category_combo_new['values'] = list(inventory.categories.keys())
    category_combo_new.pack(pady=5)
    
    # Storage Location
    Label(item_window, text="Storage Location:").pack(pady=5)
    storage_var_new = StringVar()
    storage_combo_new = ttk.Combobox(item_window, textvariable=storage_var_new, width=37)
    storage_combo_new['values'] = list(inventory.storages.keys())
    storage_combo_new.pack(pady=5)
    
    # Purchase Date
    Label(item_window, text="Purchase Date (YYYY-MM-DD):").pack(pady=5)
    purchase_entry = Entry(item_window, width=40)
    purchase_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    purchase_entry.pack(pady=5)
    
    # Expiration Date (with recommendation)
    Label(item_window, text="Expiration Date (YYYY-MM-DD):").pack(pady=5)
    exp_entry = Entry(item_window, width=40)
    
    def update_recommended_exp(*args):
        cat = category_var_new.get().strip()
        if cat:
            recommended = inventory.get_recommended_exp_date(cat, datetime.now())
            exp_entry.delete(0, END)
            exp_entry.insert(0, recommended.strftime('%Y-%m-%d'))
    
    category_var_new.trace_add('write', update_recommended_exp)
    exp_entry.pack(pady=5)
    
    def save_item():
        name = name_entry.get().strip()
        category = category_var_new.get().strip()
        storage = storage_var_new.get().strip()
        
        if not all([name, category, storage]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return
        
        try:
            purchase_date = datetime.strptime(purchase_entry.get(), '%Y-%m-%d')
            exp_date = datetime.strptime(exp_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
        
        item = inventory.add_item(barcode, name, category, storage, exp_date, purchase_date)
        session_items.append(item)
        refresh_session_tree()
        messagebox.showinfo("Success", f"Item {name} added!")
        item_window.destroy()
    
    Button(item_window, text="Save", command=save_item, bg="green", fg="white", width=20).pack(pady=15)

def process_barcode(event=None):
    barcode = barcode_entry.get().strip()
    if not barcode:
        return
    barcode_entry.delete(0, END)
    
    existing = inventory.get_items_by_barcode(barcode)
    if existing:
        # Add to session with same details
        item = existing[0]  # Use first as template
        new_item = inventory.add_item(barcode, item.name, item.category, item.storage_location, 
                                     item.exp_date, datetime.now())
        session_items.append(new_item)
        messagebox.showinfo("Item Found", f"Added {item.name} to session.")
    else:
        # New item
        open_new_item_window(barcode)
    
    refresh_session_tree()

barcode_entry.bind('<Return>', process_barcode)

def edit_session_item():
    selected = session_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to edit.")
        return
    
    item_id = int(session_tree.item(selected[0], 'values')[0])
    # Find item in session_items
    edit_item = None
    for item in session_items:
        if item.item_id == item_id:
            edit_item = item
            break
    
    if not edit_item:
        messagebox.showerror("Error", "Item not found.")
        return
    
    edit_window = Toplevel(root)
    edit_window.title(f"Edit Session Item - {edit_item.name}")
    edit_window.geometry('500x280')
    
    Label(edit_window, text="Name:").pack(pady=5)
    name_entry = Entry(edit_window, width=40)
    name_entry.insert(0, edit_item.name)
    name_entry.pack(pady=5)
    
    Label(edit_window, text="Category:").pack(pady=5)
    category_var_edit = StringVar(value=edit_item.category)
    category_combo_edit = ttk.Combobox(edit_window, textvariable=category_var_edit, width=37)
    category_combo_edit['values'] = list(inventory.categories.keys())
    category_combo_edit.pack(pady=5)
    
    Label(edit_window, text="Storage Location:").pack(pady=5)
    storage_var_edit = StringVar(value=edit_item.storage_location)
    storage_combo_edit = ttk.Combobox(edit_window, textvariable=storage_var_edit, width=37)
    storage_combo_edit['values'] = list(inventory.storages.keys())
    storage_combo_edit.pack(pady=5)
    
    Label(edit_window, text="Expiration Date (YYYY-MM-DD):").pack(pady=5)
    exp_entry = Entry(edit_window, width=40)
    exp_entry.insert(0, edit_item.exp_date.strftime('%Y-%m-%d'))
    exp_entry.pack(pady=5)
    
    def save_changes():
        edit_item.name = name_entry.get()
        edit_item.category = category_var_edit.get()
        edit_item.storage_location = storage_var_edit.get()
        try:
            edit_item.exp_date = datetime.strptime(exp_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return
        messagebox.showinfo("Success", "Item updated!")
        refresh_session_tree()
        edit_window.destroy()
    
    Button(edit_window, text="Save Changes", command=save_changes, bg="green", fg="white", width=20).pack(pady=15)

button_frame = Frame(enter_frame)
button_frame.pack(pady=10)

Button(button_frame, text="Edit Selected", command=edit_session_item, bg="orange", fg="white", width=15).pack(side=LEFT, padx=5)
Button(button_frame, text="Approve Session", command=lambda: session_items.clear() or refresh_session_tree(), bg="green", fg="white", width=20).pack(side=LEFT, padx=5)
refresh_session_tree()

# ======================= INVENTORY TAB =======================
inventory_frame = ttk.Frame(notebook)
notebook.add(inventory_frame, text="Inventory")

# Search/Filter Frame
search_frame = Frame(inventory_frame)
search_frame.pack(pady=10, fill=X, padx=10)

Label(search_frame, text="Category:").pack(side=LEFT, padx=5)
category_var = StringVar()
category_combo = ttk.Combobox(search_frame, textvariable=category_var, width=15)
category_combo.pack(side=LEFT, padx=5)

Label(search_frame, text="Storage:").pack(side=LEFT, padx=5)
storage_var = StringVar()
storage_combo = ttk.Combobox(search_frame, textvariable=storage_var, width=15)
storage_combo.pack(side=LEFT, padx=5)

Label(search_frame, text="Status:").pack(side=LEFT, padx=5)
status_var = StringVar(value="all")
status_combo = ttk.Combobox(search_frame, textvariable=status_var, values=["all", "fresh", "expiring_soon", "expired"], width=15)
status_combo.pack(side=LEFT, padx=5)

Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
search_entry = Entry(search_frame, width=20)
search_entry.pack(side=LEFT, padx=5)

# Treeview for inventory
inv_columns = ('ID', 'Barcode', 'Name', 'Category', 'Qty', 'Storage', 'Exp Date', 'Warning')
inv_tree = ttk.Treeview(inventory_frame, columns=inv_columns, show='headings', height=20)
for col in inv_columns:
    inv_tree.heading(col, text=col, command=lambda c=col: sort_by_column(c, False))
    inv_tree.column(col, width=100)
inv_tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

scrollbar_inv = ttk.Scrollbar(inventory_frame, orient=VERTICAL, command=inv_tree.yview)
inv_tree.configure(yscroll=scrollbar_inv.set)
scrollbar_inv.pack(side=RIGHT, fill=Y)

# Sorting variables
sort_column = None
sort_reverse = False

def sort_by_column(col, reverse):
    global sort_column, sort_reverse
    sort_column = col
    sort_reverse = reverse
    refresh_inventory(sort=True)

def refresh_inventory(sort=False):
    for item in inv_tree.get_children():
        inv_tree.delete(item)
    
    # Update combo boxes
    category_combo['values'] = list(inventory.categories.keys())
    storage_combo['values'] = list(inventory.storages.keys())
    
    query = search_entry.get()
    category = category_var.get()
    storage = storage_var.get()
    status = status_var.get()
    
    results = inventory.search_items(query, category, storage, status)
    
    # Group by barcode to show quantity
    by_barcode = {}
    for item in results:
        if item.barcode not in by_barcode:
            by_barcode[item.barcode] = []
        by_barcode[item.barcode].append(item)
    
    warning_items = {i.item_id for i in inventory.get_items_warning_expiration()}
    
    # Prepare data for sorting
    data = []
    for barcode, items in by_barcode.items():
        first = items[0]
        qty = len(items)
        warning = "⚠" if any(i.item_id in warning_items for i in items) else ""
        data.append((
            first.item_id, barcode, first.name, first.category, qty, first.storage_location,
            first.exp_date.strftime('%Y-%m-%d'), warning
        ))
    
    # Sort if requested
    if sort and sort_column:
        col_index = inv_columns.index(sort_column)
        try:
            # Try to convert to number for numeric columns
            data.sort(key=lambda x: float(x[col_index]) if col_index in [0, 4] else x[col_index], reverse=sort_reverse)
        except (ValueError, TypeError):
            data.sort(key=lambda x: x[col_index], reverse=sort_reverse)
    
    # Insert sorted data
    for row in data:
        inv_tree.insert('', END, values=row)

def edit_selected_item():
    selected = inv_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to edit.")
        return
    
    item_id = int(inv_tree.item(selected[0], 'values')[0])
    if item_id not in inventory.items:
        messagebox.showerror("Error", "Item not found.")
        return
    
    item = inventory.items[item_id]
    
    edit_window = Toplevel(root)
    edit_window.title(f"Edit Item - {item.name}")
    edit_window.geometry('500x300')
    
    Label(edit_window, text="Name:").pack(pady=5)
    name_entry = Entry(edit_window, width=40)
    name_entry.insert(0, item.name)
    name_entry.pack(pady=5)
    
    Label(edit_window, text="Category:").pack(pady=5)
    category_entry = Entry(edit_window, width=40)
    category_entry.insert(0, item.category)
    category_entry.pack(pady=5)
    
    Label(edit_window, text="Storage Location:").pack(pady=5)
    storage_entry = Entry(edit_window, width=40)
    storage_entry.insert(0, item.storage_location)
    storage_entry.pack(pady=5)
    
    Label(edit_window, text="Expiration Date (YYYY-MM-DD):").pack(pady=5)
    exp_entry = Entry(edit_window, width=40)
    exp_entry.insert(0, item.exp_date.strftime('%Y-%m-%d'))
    exp_entry.pack(pady=5)
    
    def save_changes():
        item.name = name_entry.get()
        item.category = category_entry.get()
        item.storage_location = storage_entry.get()
        try:
            item.exp_date = datetime.strptime(exp_entry.get(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")
            return
        inventory.save_item(item)
        messagebox.showinfo("Success", "Item updated!")
        refresh_inventory()
        edit_window.destroy()
    
    Button(edit_window, text="Save Changes", command=save_changes, bg="green", fg="white", width=20).pack(pady=15)

def remove_selected_item():
    selected = inv_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an item to remove.")
        return
    item_id = int(inv_tree.item(selected[0], 'values')[0])
    if messagebox.askyesno("Confirm", "Archive this item?"):
        inventory.archive_item(item_id)
        refresh_inventory()

inv_button_frame = Frame(inventory_frame)
inv_button_frame.pack(pady=10)

Button(inv_button_frame, text="Edit Selected", command=edit_selected_item, bg="orange", fg="white", width=15).pack(side=LEFT, padx=5)
Button(inv_button_frame, text="Remove Selected", command=remove_selected_item, bg="red", fg="white", width=15).pack(side=LEFT, padx=5)

search_entry.bind('<KeyRelease>', lambda e: refresh_inventory())
category_var.trace_add('write', lambda *args: refresh_inventory())
storage_var.trace_add('write', lambda *args: refresh_inventory())
status_var.trace_add('write', lambda *args: refresh_inventory())
refresh_inventory()

# ======================= OVERVIEW TAB =======================
overview_frame = ttk.Frame(notebook)
notebook.add(overview_frame, text="Overview")

def refresh_overview():
    for widget in overview_frame.winfo_children():
        widget.destroy()
    
    stats = inventory.get_statistics()
    
    title = Label(overview_frame, text="Inventory Overview", font=("Arial", 16, "bold"))
    title.pack(pady=20)
    
    info_text = f"""
Total Items: {stats['total_items']}
Total Categories: {stats['categories']}
Storage Locations: {stats['storage_locations']}

⚠ Items Expiring Soon: {stats['warning_count']}
❌ Expired Items: {stats['expired_count']}

Items by Category:
{chr(10).join([f"  {cat}: {count}" for cat, count in stats['items_by_category'].items()])}

Items by Storage Location:
{chr(10).join([f"  {loc}: {count}" for loc, count in stats['items_by_storage'].items()])}
    """
    
    info_label = Label(overview_frame, text=info_text, font=("Arial", 11), justify=LEFT)
    info_label.pack(padx=20, pady=10)
    
    Button(overview_frame, text="Refresh", command=refresh_overview, bg="blue", fg="white", width=20).pack(pady=20)

refresh_overview()

# ======================= CHECKOUT TAB =======================
checkout_frame = ttk.Frame(notebook)
notebook.add(checkout_frame, text="Checkout")

Label(checkout_frame, text="Scan Item to Remove from Inventory:", font=("Arial", 12)).pack(pady=10)

checkout_entry = Entry(checkout_frame, width=30, font=("Arial", 12))
checkout_entry.pack(pady=5)

def process_checkout(event=None):
    barcode = checkout_entry.get().strip()
    if not barcode:
        return
    checkout_entry.delete(0, END)
    
    items = inventory.get_items_by_barcode(barcode)
    if items:
        # Remove the oldest item (first in list)
        inventory.archive_item(items[0].item_id)
        messagebox.showinfo("Removed", f"Removed 1x {items[0].name}")
        refresh_inventory()
    else:
        messagebox.showwarning("Not Found", f"Barcode {barcode} not found.")

checkout_entry.bind('<Return>', process_checkout)
Label(checkout_frame, text="Scan or enter barcode and press Enter to remove 1 item from inventory.").pack(pady=20, padx=20)

# ======================= CATEGORY MANAGEMENT TAB =======================
category_frame = ttk.Frame(notebook)
notebook.add(category_frame, text="Categories")

cat_button_frame = Frame(category_frame)
cat_button_frame.pack(pady=10)

Button(cat_button_frame, text="Add Category", command=lambda: open_category_window(), bg="green", fg="white", width=20).pack(side=LEFT, padx=5)

cat_columns = ('Name', 'Storage Location', 'Rec. Days', 'Warning %')
cat_tree = ttk.Treeview(category_frame, columns=cat_columns, show='headings', height=15)
for col in cat_columns:
    cat_tree.heading(col, text=col)
    cat_tree.column(col, width=150)
cat_tree.pack(padx=10, pady=10, fill=BOTH, expand=True)

def refresh_categories():
    for item in cat_tree.get_children():
        cat_tree.delete(item)
    for cat_name, cat in inventory.categories.items():
        cat_tree.insert('', END, values=(
            cat_name, cat.storage_location, cat.recommended_exp_days, cat.warning_threshold_percent
        ))

def open_category_window(cat_name=None):
    is_edit = cat_name is not None
    cat_window = Toplevel(root)
    cat_window.title("Add Category" if not is_edit else f"Edit {cat_name}")
    cat_window.geometry('400x350')
    
    if is_edit:
        cat = inventory.categories[cat_name]
    
    Label(cat_window, text="Category Name:").pack(pady=5)
    name_entry = Entry(cat_window, width=40)
    if is_edit:
        name_entry.insert(0, cat_name)
        name_entry.config(state='readonly')
    name_entry.pack(pady=5)
    
    Label(cat_window, text="Storage Location:").pack(pady=5)
    storage_entry = Entry(cat_window, width=40)
    if is_edit:
        storage_entry.insert(0, cat.storage_location)
    storage_entry.pack(pady=5)
    
    Label(cat_window, text="Recommended Expiration Days:").pack(pady=5)
    days_entry = Entry(cat_window, width=40)
    if is_edit:
        days_entry.insert(0, str(cat.recommended_exp_days))
    else:
        days_entry.insert(0, "7")
    days_entry.pack(pady=5)
    
    Label(cat_window, text="Warning Threshold (%):").pack(pady=5)
    warning_entry = Entry(cat_window, width=40)
    if is_edit:
        warning_entry.insert(0, str(cat.warning_threshold_percent))
    else:
        warning_entry.insert(0, "80")
    warning_entry.pack(pady=5)
    
    def save_category():
        name = name_entry.get().strip()
        storage = storage_entry.get().strip()
        try:
            days = int(days_entry.get())
            warning = int(warning_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Days and Warning must be integers.")
            return
        
        if not all([name, storage]):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        
        if is_edit:
            cat = inventory.categories[name]
            cat.storage_location = storage
            cat.recommended_exp_days = days
            cat.warning_threshold_percent = warning
        else:
            cat = Category(name=name, storage_location=storage, recommended_exp_days=days, warning_threshold_percent=warning)
            inventory.categories[name] = cat
        
        inventory.save_category(cat)
        messagebox.showinfo("Success", "Category saved!")
        refresh_categories()
        cat_window.destroy()
    
    Button(cat_window, text="Save", command=save_category, bg="green", fg="white", width=20).pack(pady=20)

def edit_category():
    selected = cat_tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select a category to edit.")
        return
    cat_name = cat_tree.item(selected[0], 'values')[0]
    open_category_window(cat_name)

Button(cat_button_frame, text="Edit Selected", command=edit_category, bg="orange", fg="white", width=20).pack(side=LEFT, padx=5)
refresh_categories()

# Add tab change event to refresh displayed tab
def on_tab_change(event):
    selected_tab = notebook.select()
    tab_text = notebook.tab(selected_tab, "text")
    if tab_text == "Inventory":
        refresh_inventory()
    elif tab_text == "Overview":
        refresh_overview()
    elif tab_text == "Categories":
        refresh_categories()

notebook.bind("<<NotebookTabChanged>>", on_tab_change)

root.mainloop()
inventory.close()