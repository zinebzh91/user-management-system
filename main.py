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
root.configure(bg="#1e1e2f")

tk.Label(root, text="USER MANAGEMENT SYSTEM",
         font=("Arial", 18, "bold"),
         bg="#1e1e2f", fg="white").pack(pady=10)

# =========================
# FRAMES
# =========================
left_frame = tk.Frame(root, bg="#2b2b40", padx=10, pady=10)
left_frame.place(x=20, y=60, width=320, height=500)

right_frame = tk.Frame(root, bg="#2b2b40", padx=10, pady=10)
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
search_entry = tk.Entry(right_frame, width=40)
search_entry.pack(pady=5)
search_entry.insert(0, "Search...")

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
# DISPLAY USERS (WITH CONDITION)
# =========================
def display_users():
    try:
        tree.delete(*tree.get_children())

        users = list(collection.find())

        # ✔ شرط: لا يوجد مستخدمين
        if len(users) == 0:
            messagebox.showinfo("Info", "No users found in database")
            return

        for u in users:
            tree.insert("", "end", values=(
                u.get("first_name",""),
                u.get("last_name",""),
                u.get("birth_date",""),
                u.get("birth_place",""),
                u.get("phone","")
            ))

        messagebox.showinfo("Success", "Users loaded successfully")

    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to load users:\n{str(e)}")

# =========================
# CLEAR FORM
# =========================
def clear():
    first_entry.delete(0, tk.END)
    last_entry.delete(0, tk.END)
    birth_entry.delete(0, tk.END)
    place_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)

# =========================
# VALIDATION
# =========================
def validate_inputs():
    if first_entry.get()=="" or last_entry.get()=="" or birth_entry.get()=="" or place_entry.get()=="" or phone_entry.get()=="":
        messagebox.showerror("Validation Error", "All fields are required")
        return False

    if not re.match(r"\d{4}-\d{2}-\d{2}", birth_entry.get()):
        messagebox.showerror("Validation Error", "Date must be YYYY-MM-DD")
        return False

    if not phone_entry.get().isdigit():
        messagebox.showerror("Validation Error", "Phone must be numeric")
        return False

    return True

# =========================
# ADD USER
# =========================
def add_user():
    try:
        if not validate_inputs():
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
        messagebox.showinfo("Success", "User added successfully")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# =========================
# SELECT USER
# =========================
def select_user(event):
    selected = tree.focus()
    if not selected:
        return

    values = tree.item(selected, "values")

    first_entry.delete(0, tk.END)
    first_entry.insert(0, values[0])

    last_entry.delete(0, tk.END)
    last_entry.insert(0, values[1])

    birth_entry.delete(0, tk.END)
    birth_entry.insert(0, values[2])

    place_entry.delete(0, tk.END)
    place_entry.insert(0, values[3])

    phone_entry.delete(0, tk.END)
    phone_entry.insert(0, values[4])

tree.bind("<ButtonRelease-1>", select_user)

# =========================
# DELETE USER
# =========================
def delete_user():
    try:
        phone = phone_entry.get()

        if phone == "":
            messagebox.showerror("Error", "Select a user")
            return

        user = collection.find_one({"phone": phone})
        if not user:
            messagebox.showerror("Error", "User not found")
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                      f"Delete {user['first_name']} {user['last_name']}?")

        if confirm:
            collection.delete_one({"phone": phone})
            display_users()
            clear()
            messagebox.showinfo("Success", "User deleted")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# =========================
# UPDATE USER
# =========================
def update_user():
    try:
        phone = phone_entry.get()

        if phone == "":
            messagebox.showerror("Error", "Phone required")
            return

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
        messagebox.showinfo("Success", "User updated")

    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# =========================
# LIVE SEARCH
# =========================
def live_search(event=None):
    key = search_entry.get()

    tree.delete(*tree.get_children())

    results = collection.find({
        "$or": [
            {"first_name": {"$regex": key, "$options": "i"}},
            {"last_name": {"$regex": key, "$options": "i"}},
            {"birth_date": {"$regex": key, "$options": "i"}},
            {"birth_place": {"$regex": key, "$options": "i"}},
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
tk.Button(left_frame, text="Add", command=add_user, bg="green", fg="white", width=10).grid(row=6, column=0)
tk.Button(left_frame, text="Update", command=update_user, bg="orange", fg="white", width=10).grid(row=6, column=1)
tk.Button(left_frame, text="Delete", command=delete_user, bg="red", fg="white", width=10).grid(row=7, column=0)
tk.Button(left_frame, text="Load", command=display_users, bg="blue", fg="white", width=10).grid(row=7, column=1)

# =========================
# INITIAL LOAD
# =========================
display_users()

root.mainloop()