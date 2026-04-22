import tkinter as tk
from datetime import datetime
from tkinter import messagebox


# Mock database (Pantry, expiry dates=YYYY-MM-DD)
pantry = [
    ("Rice", "2026-05-10"),
    ("Beans", "2026-12-12"),
    ("Pasta", "2026-04-22"),
    ("Cereal", "2026-04-07"),
    ("Oats", "2026-10-20"),
]

# Shopping list
shopping_list = []

shopping_list.clear

def update_display():
    pantry_list.delete(0, tk.END)

    today = datetime.today().date()

    expiring_today = []

    for item, expiry in pantry:
        expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
        text = f"{item}     |       {expiry} "
        days_left = (expiry_date - today).days

        if expiry_date == today:
            expiring_today.append(item)

        if days_left < 0 or days_left <= 2:
            if item not in shopping_list:
                shopping_list.append(item)

    
        pantry_list.insert(tk.END, text)
        index = pantry_list.size() - 1

        # Colour coding
        if expiry_date < today:
            pantry_list.itemconfig(index, fg="red")
        elif (expiry_date - today).days <= 2:
            pantry_list.itemconfig(index, fg="orange")
        else:
            pantry_list.itemconfig(index, fg="white")

    if expiring_today:
        alert_label.config(
            text=f" Expires Today: {','.join(expiring_today)}",
            fg="yellow"
        )
    else:
        alert_label.config(text="")

    shopping_listbox.delete(0, tk.END)

    for item in shopping_list:
        shopping_listbox.insert(tk.END, item)
    

    # Auto-refresh after 60 seconds
    root.after(60000, update_display)

def add_item():
    item =  item_entry.get()
    expiry = date_entry.get()

    # Basic validation
    if not item or not expiry:
        messagebox.showwarning("Missing Info", "Please fill both fields.")
        return
        
    try:
        datetime.strptime(expiry, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Invalid Date", "Use format YYYY-MM-DD")
        return 
        

    pantry.append((item, expiry))
    item_entry.delete(0, tk.END)
    date_entry.delete(0, tk.END)
   

    update_display()

def delete_item():
    selected = pantry_list.curselection()
    if not selected:
        return
    
    index = selected[0]
    del pantry[index]
    update_display()




# Main window
root = tk.Tk()
root.title("Shelf Sync")

# Fullscreen mode (for raspberry pi)
#root.attributes("-fullscreen", True)
#root.configure(bg="black")

# Exit fullscreen (using ESC)
#root.bind("<Escape>", lambda e: root.destroy())

# Title
title = tk.Label(
    root, 
    text = "Pantry Status",
    font=("Script", 32, "bold"),
    bg="black",
    fg="white",
)
title.pack(pady=20)

# Pantry List
pantry_list = tk.Listbox(
    root, 
    font=("Times New Roman", 24),
    bg="black",
    fg="white",
    width=50,
    height=1,
    highlightthickness=0,
    bd=0
)
pantry_list.pack(pady=20)

# Shopping list display
shopping_label = tk.Label(
    root, 
    text="Shopping List",
    font=("Script", 24),
    bg="black",
    fg="white"
)
shopping_label.pack(pady=10)

shopping_listbox = tk.Listbox(
    root, 
    font=("Times New Roman", 24),
    bg="black",
    fg="white",
    width=50 ,
    height=5,
    highlightthickness=0,
    bd=0
)
shopping_listbox.pack(pady=20)

alert_label = tk.Label(root, text="", font=("Arial", 20, "bold"), bg="black")
alert_label.pack()

# Input 
input_frame = tk.Frame(root, bg="black")
input_frame.pack(pady=10)

tk.Label(input_frame, text="Item", bg="black", fg="white", font=("Arial", 14)).grid(row=0, column=0)
tk.Label(input_frame, text="Expiry (YYYY-MM-DD)", bg="black", fg="white", font=("Arial", 14)).grid(row=0, column=1)



item_entry = tk.Entry(input_frame, font=("Arial", 18))
item_entry.grid(row=0, column=0, padx=10)
item_entry.insert(0, "Item")

root.bind("<Return>", lambda e: add_item())

date_entry = tk.Entry(input_frame, font=("Arial", 18))
date_entry.grid(row=0, column=1, padx=10)
date_entry.insert(0, "YYYY-MM-DD")

add_button = tk.Button(input_frame, text="Add", font=("Arial", 16), command=add_item)
add_button.grid(row=0, column=2, padx=10)

delete_button = tk.Button(root, text="Delete", font=("Times New Roman", 16,), command=delete_item)


# Start auto-loading
update_display()

# Run app
root.mainloop()        
