import tkinter as tk
from tkinter import messagebox, ttk
from pymongo import MongoClient
import re

# =========================
# DATABASE CONNECTION
# =========================
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=3000)
    client.server_info()
    db = client["user_management"]
    collection = db["users"]
except Exception as e:
    messagebox.showerror("Database Error", f"Cannot connect to MongoDB:\n{e}")
    exit()

# =========================
# WINDOW
# =========================
root = tk.Tk()
root.title("Advanced User Management System")
root.geometry("1000x600")
root.configure(bg="#f4f6f9")
tk.Label(root, text="USER MANAGEMENT SYSTEM",
         font=("Arial", 22, "bold"),
         bg="#f4f6f9",
         fg="#2c3e50").pack(pady=15)

# =========================
# FRAMES
# =========================
left_frame = tk.Frame(
    root,
    bg="#2c3e50",   
    padx=15,
    pady=15,
    bd=0
)
left_frame.place(x=20, y=60, width=320, height=500)

right_frame = tk.Frame(
    root,
    bg="#ecf0f1",  
    padx=15,
    pady=15,
    bd=0
)
right_frame.place(x=360, y=60, width=620, height=500)

# =========================
# INPUTS
# =========================
def label(text, row):
    tk.Label(left_frame, text=text, bg="#2b2b40", fg="white").grid(row=row, column=0, sticky="w")

label("First Name", 0)
first_entry = tk.Entry(left_frame)
first_entry.grid(row=0, column=1)

label("Last Name", 1)
last_entry = tk.Entry(left_frame)
last_entry.grid(row=1, column=1)

label("Birth Date (YYYY-MM-DD)", 2)
birth_entry = tk.Entry(left_frame)
birth_entry.grid(row=2, column=1)

label("Birth Place", 3)
place_entry = tk.Entry(left_frame)
place_entry.grid(row=3, column=1)

label("Phone", 4)
phone_entry = tk.Entry(left_frame)
phone_entry.grid(row=4, column=1)

# =========================
# SEARCH
# =========================
search_entry = tk.Entry(right_frame, width=40, fg="gray")
search_entry.pack(pady=5)
search_entry.insert(0, "Search...")

def on_focus_in(event):
    if search_entry.get() == "Search...":
        search_entry.delete(0, tk.END)
        search_entry.config(fg="black")

def on_focus_out(event):
    if search_entry.get() == "":
        search_entry.insert(0, "Search...")
        search_entry.config(fg="gray")

search_entry.bind("<FocusIn>", on_focus_in)
search_entry.bind("<FocusOut>", on_focus_out)

# =========================
# TABLE
# =========================
tree = ttk.Treeview(right_frame,
                    columns=("fname","lname","birth","place","phone"),
                    show="headings")

for col, text, w in [
    ("fname","First Name",120),
    ("lname","Last Name",120),
    ("birth","Birth Date",120),
    ("place","Birth Place",120),
    ("phone","Phone",120)
]:
    tree.heading(col, text=text)
    tree.column(col, width=w)

tree.pack(fill="both", expand=True)

# =========================
# CLEAR
# =========================
def clear():
    for e in [first_entry, last_entry, birth_entry, place_entry, phone_entry]:
        e.delete(0, tk.END)

# =========================
# VALIDATION
# =========================
def validate():
    if any(e.get() == "" for e in [first_entry, last_entry, birth_entry, place_entry, phone_entry]):
        messagebox.showerror("Error", "All fields are required")
        return False

    if not re.match(r"\d{4}-\d{2}-\d{2}", birth_entry.get()):
        messagebox.showerror("Error", "Date must be YYYY-MM-DD")
        return False

    if not phone_entry.get().isdigit():
        messagebox.showerror("Error", "Phone must be numeric")
        return False

    return True

# =========================
# DISPLAY
# =========================
def display_users():
    tree.delete(*tree.get_children())
    users = list(collection.find())

    if not users:
        messagebox.showinfo("Info", "No users found")
        return

    for u in users:
        tree.insert("", "end", values=(
            u.get("first_name",""),
            u.get("last_name",""),
            u.get("birth_date",""),
            u.get("birth_place",""),
            u.get("phone","")
        ))

# =========================
# ADD USER
# =========================
def add_user():
    if not validate():
        return

    if collection.find_one({"phone": phone_entry.get()}):
        messagebox.showerror("Error", "Phone already exists")
        return

    collection.insert_one({
        "first_name": first_entry.get(),
        "last_name": last_entry.get(),
        "birth_date": birth_entry.get(),
        "birth_place": place_entry.get(),
        "phone": phone_entry.get()
    })

    display_users()
    clear()
    messagebox.showinfo("Success", "User added")

# =========================
# SELECT
# =========================
def select_user(event):
    selected = tree.focus()
    if not selected:
        return

    values = tree.item(selected, "values")

    clear()
    first_entry.insert(0, values[0])
    last_entry.insert(0, values[1])
    birth_entry.insert(0, values[2])
    place_entry.insert(0, values[3])
    phone_entry.insert(0, values[4])

tree.bind("<ButtonRelease-1>", select_user)

# =========================
# DELETE
# =========================
def delete_user():
    phone = phone_entry.get()
    if not phone:
        messagebox.showerror("Error", "Select a user")
        return

    user = collection.find_one({"phone": phone})
    if not user:
        messagebox.showerror("Error", "User not found")
        return

    if messagebox.askyesno("Confirm", "Delete user?"):
        collection.delete_one({"phone": phone})
        display_users()
        clear()

# =========================
# UPDATE
# =========================
def update_user():
    if not validate():
        return

    phone = phone_entry.get()

    collection.update_one(
        {"phone": phone},
        {"$set": {
            "first_name": first_entry.get(),
            "last_name": last_entry.get(),
            "birth_date": birth_entry.get(),
            "birth_place": place_entry.get()
        }}
    )

    display_users()
    clear()
    messagebox.showinfo("Success", "Updated successfully")

# =========================
# SEARCH
# =========================
def live_search(event=None):
    key = search_entry.get()
    if key == "Search...":
        return

    tree.delete(*tree.get_children())

    results = collection.find({
        "$or": [
            {"first_name": {"$regex": key, "$options": "i"}},
            {"last_name": {"$regex": key, "$options": "i"}},
            {"phone": {"$regex": key, "$options": "i"}}
        ]
    })

    for u in results:
        tree.insert("", "end", values=(
            u.get("first_name",""),
            u.get("last_name",""),
            u.get("birth_date",""),
            u.get("birth_place",""),
            u.get("phone","")
        ))

search_entry.bind("<KeyRelease>", live_search)

# =========================
# BUTTONS
# =========================
def make_button(parent, text, command, bg, fg="white"):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground="#34495e",
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=10,
        pady=6,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    )

make_button(left_frame, "Add", add_user, "#2ecc71").grid(row=6, column=0, pady=8, padx=5)
make_button(left_frame, "Update", update_user, "#f1c40f", fg="black").grid(row=6, column=1, pady=8, padx=5)
make_button(left_frame, "Delete", delete_user, "#e74c3c").grid(row=7, column=0, pady=8, padx=5)
make_button(left_frame, "Load", display_users, "#3498db").grid(row=7, column=1, pady=8, padx=5)
display_users()
root.mainloop()