


from tkinter import *

# Create root window
root = Tk()
root.title("Tkinter App Title")
root.geometry('350x200')

# Label widget
lbl = Label(root, text = "Enter your name: ")
lbl.grid(column = 0, row = 0)

# Entry widget
txt = Entry(root, width = 20)
txt.grid(column = 1, row = 0)

# Button click event
def clicked():
    lbl.configure(text = f"Hello, {txt.get()}!")

# Button widget
btn = Button(root, text = "Greet", fg = "blue", command = clicked)
btn.grid(column = 2, row = 0)

root.mainloop()