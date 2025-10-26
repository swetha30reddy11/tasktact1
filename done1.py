import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import json, os

FILE = "tasks.json"


# ---------------- Task Functions ----------------r

def load_tasks():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            tasks = json.load(f)
            # Ensure old tasks have "priority"
            for t in tasks:
                if "priority" not in t:
                    t["priority"] = "Medium"
            return tasks
    return []


def save_tasks(tasks):
    with open(FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def add_task():
    task = task_entry.get().strip()
    category = category_var.get()
    due_date = due_entry.get_date().strftime("%Y-%m-%d")
    priority = priority_var.get()
    if task:
        tasks.append({"task": task, "done": False, "category": category, "due_date": due_date, "priority": priority})
        save_tasks(tasks)
        update_tree()
        task_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Please enter a valid task.")


def mark_done():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Select Task", "Please select a task to mark done.")
        return
    global tasks
    for item in selected:
        idx = int(tree.item(item, "text"))
        tasks[idx]["done"] = True
    save_tasks(tasks)
    update_tree()


def delete_task():
    global tasks
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Select Task", "Please select a task to delete.")
        return
    for item in selected:
        idx = int(tree.item(item, "text"))
        tasks[idx] = None
    tasks = [t for t in tasks if t]
    save_tasks(tasks)
    update_tree()


def clear_all():
    global tasks
    if messagebox.askyesno("Confirm", "Clear all tasks?"):
        tasks.clear()
        save_tasks(tasks)
        update_tree()


def filter_tasks(view):
    current_view.set(view)
    update_tree()


def search_task(*args):
    update_tree()


# ---------------- Treeview Update ----------------
def update_tree():
    tree.delete(*tree.get_children())
    query = search_var.get().lower()
    for idx, t in enumerate(tasks):
        # Filter based on current view
        if current_view.get() == "Completed" and not t["done"]:
            continue
        if current_view.get() == "Pending" and t["done"]:
            continue
        # Filter based on search query
        if query and query not in t["task"].lower():
            continue
        tree.insert("", tk.END, text=str(idx),
                    values=(t["task"], t["category"], t["due_date"], t.get("priority", "Medium")))
        item_id = tree.get_children()[-1]

        # Color tags
        if t["done"]:
            tree.item(item_id, tags=("done",))
        elif datetime.strptime(t["due_date"], "%Y-%m-%d") < datetime.now():
            tree.item(item_id, tags=("overdue",))
        else:
            tree.item(item_id, tags=("pending",))

    tree.tag_configure("done", foreground="green")
    tree.tag_configure("pending", foreground="red")
    tree.tag_configure("overdue", foreground="orange")

    # Update progress and stats
    update_progress()
    update_stats()


# ---------------- Progress and Stats ----------------
def update_progress():
    if not tasks:
        progress["value"] = 0
        return
    done = sum(1 for t in tasks if t["done"])
    progress["value"] = (done / len(tasks)) * 100


def update_stats():
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    stats_label.config(text=f"Total: {total} | Completed: {done} | Pending: {pending}")


# ---------------- GUI ----------------
root = tk.Tk()
root.title("📝 TaskTact - Task Manager")
root.geometry("950x600")
root.configure(bg="#f5f7fa")

current_view = tk.StringVar(value="All")

# ---------------- Sidebar ----------------
sidebar = tk.Frame(root, bg="#34495e", width=200)
sidebar.pack(side=tk.LEFT, fill="y")

tk.Label(sidebar, text=" Task Filters ", font=("Segoe UI", 14, "bold"),
         bg="#34495e", fg="white").pack(pady=20)

btn_style = {"font": ("Segoe UI", 11), "bd": 0, "relief": "flat", "fg": "white"}

tk.Button(sidebar, text="All Tasks", bg="#2c3e50", **btn_style,
          command=lambda: filter_tasks("All")).pack(fill="x", padx=10, pady=5)
tk.Button(sidebar, text="Completed ✅", bg="#27ae60", **btn_style,
          command=lambda: filter_tasks("Completed")).pack(fill="x", padx=10, pady=5)
tk.Button(sidebar, text="Pending 🕓", bg="#c0392b", **btn_style,
          command=lambda: filter_tasks("Pending")).pack(fill="x", padx=10, pady=5)

# ---------------- Content Frame ----------------
content_frame = tk.Frame(root, bg="#f5f7fa")
content_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=10, pady=10)

# Search bar
search_var = tk.StringVar()
search_entry = ttk.Entry(content_frame, textvariable=search_var, font=("Segoe UI", 12))
search_entry.pack(fill="x", pady=5)
search_var.trace("w", search_task)

# Input frame
input_frame = tk.LabelFrame(content_frame, text="Add Task", font=("Segoe UI", 12, "bold"),
                            bg="#f5f7fa", fg="#2c3e50", padx=10, pady=10)
input_frame.pack(pady=10, fill="x")

task_entry = ttk.Entry(input_frame, width=30, font=("Segoe UI", 11))
task_entry.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

tk.Label(input_frame, text="Category:", bg="#f5f7fa", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", padx=5)
category_var = tk.StringVar(value="General")
category_menu = ttk.Combobox(input_frame, textvariable=category_var, values=["Work", "Study", "Personal", "Other"],
                             state="readonly", width=15)
category_menu.grid(row=1, column=1, pady=2)

tk.Label(input_frame, text="Due Date:", bg="#f5f7fa", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", padx=5)
due_entry = DateEntry(input_frame)
due_entry.grid(row=2, column=1, pady=2)

tk.Label(input_frame, text="Priority:", bg="#f5f7fa", font=("Segoe UI", 11)).grid(row=3, column=0, sticky="w", padx=5)
priority_var = tk.StringVar(value="Medium")
priority_menu = ttk.Combobox(input_frame, textvariable=priority_var, values=["High", "Medium", "Low"],
                             state="readonly", width=15)
priority_menu.grid(row=3, column=1, pady=2)

ttk.Button(input_frame, text="Add Task", command=add_task).grid(row=4, column=0, columnspan=2, pady=10)

# Treeview for tasks
columns = ("Task", "Category", "Due Date", "Priority")
tree = ttk.Treeview(content_frame, columns=columns, show="headings", selectmode="extended")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200)
tree.pack(fill="both", expand=True, pady=5)

# Style Treeview
style = ttk.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), foreground="#2c3e50")
style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

# Progress bar
progress = ttk.Progressbar(content_frame, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=5)

# Stats label
stats_label = tk.Label(content_frame, text="", font=("Segoe UI", 11, "bold"), bg="#f5f7fa", fg="#2c3e50")
stats_label.pack(pady=5)

# Buttons
btn_frame = tk.Frame(content_frame, bg="#f5f7fa")
btn_frame.pack(pady=10)
ttk.Button(btn_frame, text="Mark Done ✅", command=mark_done).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Delete 🗑️", command=delete_task).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Clear All ❌", command=clear_all).grid(row=0, column=2, padx=5)

# ---------------- Load tasks ----------------
tasks = load_tasks()
update_tree()

root.mainloop()

