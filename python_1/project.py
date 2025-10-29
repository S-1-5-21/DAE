#!/usr/bin/env python3

import json
import os
import shutil
import sys
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROGRAM_FILENAME = Path(sys.argv[0]).stem if sys.argv and sys.argv[0] else "pf_tracker"
SUMMARY_FILENAME = f"{PROGRAM_FILENAME}_summary.json"
BACKUP_SUFFIX = ".backup"

INCOME_CATEGORIES = ["Salary", "Gift", "Investment", "Other"]
EXPENSE_CATEGORIES = ["Food", "Housing", "Transportation", "Entertainment", "Health", "Education", "Other"]

DEFAULT_SUMMARY = {
    "income": {c: 0.0 for c in INCOME_CATEGORIES},
    "expenses": {c: 0.0 for c in EXPENSE_CATEGORIES},
}

# Window
WINDOW_WIDTH = 1390
WINDOW_HEIGHT = 770

# Colors
GRADIENT_TOP = "#004D1A"
GRADIENT_BOTTOM = "#9CFF00"
CONTENT_BG = "#1C1C1C"
GLOW_COLOR = "#9CFF00"
BTN_GRAD_TOP = "#00C853"
BTN_GRAD_BOTTOM = "#9CFF00"
BTN_TEXT = "#1C1C1C"

# Box sizes
MAIN_BOX_HEIGHT = 500
SUMMARY_BOX_HEIGHT = 500
OTHER_BOX_HEIGHT = 420
BOX_WIDTH = 640
BUTTON_WIDTH = 360
BUTTON_HEIGHT = 52

# --------------------------------------------------
# File utilities
# --------------------------------------------------

def _summary_path():
    try:
        return Path(__file__).resolve().parent / SUMMARY_FILENAME
    except Exception:
        return Path.cwd() / SUMMARY_FILENAME


def load_summary_data():
    path = _summary_path()
    if not path.exists():
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SUMMARY, f, indent=4)
        messagebox.showinfo("Summary File Created", f"Created '{SUMMARY_FILENAME}'.")
        return json.loads(json.dumps(DEFAULT_SUMMARY))

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        path.unlink(missing_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SUMMARY, f, indent=4)
        messagebox.showwarning("Corrupted File Replaced", "Corrupted summary file replaced with a new blank file.")
        return json.loads(json.dumps(DEFAULT_SUMMARY))
    except Exception as e:
        messagebox.showerror("File Error", f"Unable to read summary file:\n{e}")
        return json.loads(json.dumps(DEFAULT_SUMMARY))

    repairs = []
    repaired = False

    for section, expected in (("income", INCOME_CATEGORIES), ("expenses", EXPENSE_CATEGORIES)):
        if section not in data or not isinstance(data[section], dict):
            data[section] = {k: 0.0 for k in expected}
            repairs.append(f"Added or replaced section '{section}'.")
            repaired = True
        else:
            # Ensure proper keys and numeric values
            for cat in expected:
                if cat not in data[section]:
                    data[section][cat] = 0.0
                    repairs.append(f"Added missing '{cat}' in '{section}'.")
                    repaired = True
                try:
                    data[section][cat] = float(data[section][cat])
                except Exception:
                    data[section][cat] = 0.0
                    repairs.append(f"Reset invalid value for '{cat}' in '{section}'.")
                    repaired = True

    if repaired:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        messagebox.showinfo("Repairs Made", "\n".join(repairs))

    return data


def save_summary_data(data):
    path = _summary_path()
    backup = path.with_suffix(path.suffix + BACKUP_SUFFIX)
    try:
        if path.exists():
            shutil.copyfile(path, backup)
    except Exception:
        pass
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Save Error", f"Could not save summary. Backup preserved as '{backup.name}'.\nDetails: {e}")
        return False
    try:
        if backup.exists():
            backup.unlink()
    except Exception:
        pass
    return True


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def validate_number(txt):
    s = str(txt).strip()
    if not s:
        return False, "No input provided."
    try:
        v = float(s)
    except ValueError:
        return False, "Number is invalid or input was not a number.\nExample: 500; 503.81\nNo Symbols."
    if v <= 0:
        return False, "Value must be greater than 0."
    return True, v


def interp_color(c1, c2, t):
    def h2r(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r1, g1, b1 = h2r(c1)
    r2, g2, b2 = h2r(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def format_currency(val):
    try:
        return f"${float(val):,.2f}"
    except Exception:
        return "$0.00"


# --------------------------------------------------
# GUI Classes
# --------------------------------------------------

class GradientBackground:
    def __init__(self, root, width, height, color1, color2):
        self.root = root
        self.width = width
        self.height = height
        self.color1 = color1
        self.color2 = color2
        self.canvas = tk.Canvas(root, width=width, height=height, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.draw_gradient()

    def draw_gradient(self):
        self.canvas.delete("all")
        steps = max(150, self.height // 3)
        for i in range(steps):
            t = i / (steps - 1)
            color = interp_color(self.color1, self.color2, t)
            y1 = int(i * (self.height / steps))
            y2 = int((i + 1) * (self.height / steps))
            self.canvas.create_rectangle(0, y1, self.width, y2, outline=color, fill=color)


class GlowButton(tk.Canvas):
    """Gradient button that glows and is clickable."""
    def __init__(self, parent, text, command, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, font=None):
        super().__init__(parent, width=width, height=height, bd=0, highlightthickness=0, cursor="hand2")
        self.text = text
        self.command = command
        self.font = font or ("Helvetica", 13, "bold")
        self.width = width
        self.height = height
        self.normal_top = BTN_GRAD_TOP
        self.normal_bottom = BTN_GRAD_BOTTOM
        self.hover_top = BTN_GRAD_BOTTOM
        self.hover_bottom = BTN_GRAD_TOP
        self.glow_color = GLOW_COLOR
        self.text_color = BTN_TEXT
        self._draw_button(self.normal_top, self.normal_bottom)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", lambda e: self.command())

    def _draw_button(self, top, bottom):
        self.delete("all")
        steps = 40
        for i in range(steps):
            t = i / (steps - 1)
            color = interp_color(top, bottom, t)
            y1 = int(i * (self.height / steps))
            y2 = int((i + 1) * (self.height / steps))
            self.create_rectangle(0, y1, self.width, y2, outline=color, fill=color)
        self.create_rectangle(2, 2, self.width - 2, self.height - 2, outline=self.glow_color, width=2)
        self.create_text(self.width // 2, self.height // 2, text=self.text, font=self.font, fill=self.text_color)

    def _on_enter(self, event):
        self._draw_button(self.hover_top, self.hover_bottom)

    def _on_leave(self, event):
        self._draw_button(self.normal_top, self.normal_bottom)


class ContentBox:
    """Dark rectangular box with static border and fade-in pulse animation (outline only)."""
    def __init__(self, bg_canvas, width, height):
        self.canvas = tk.Canvas(bg_canvas.canvas.master, width=width, height=height, highlightthickness=0, bg=bg_canvas.canvas.master["bg"])
        self.bg_color = CONTENT_BG
        self.border_color = GLOW_COLOR
        self.fill_id = self.canvas.create_rectangle(0, 0, width, height, fill=self.bg_color, outline="")
        self.outline_id = self.canvas.create_rectangle(2, 2, width - 2, height - 2, outline=self.border_color, width=2)
        self.inner_frame = tk.Frame(self.canvas, bg=self.bg_color)
        pad = 12
        self.canvas.create_window(pad, pad, window=self.inner_frame, anchor="nw", width=width - 2 * pad, height=height - 2 * pad)
        self._anim_in_progress = False

    def get_widget(self):
        return self.canvas

    def animate_pulse(self):
        if self._anim_in_progress:
            return
        self._anim_in_progress = True
        steps = 8
        def step_up(i=0):
            if i > steps:
                self.canvas.itemconfig(self.outline_id, outline=self.border_color)
                self._anim_in_progress = False
                return
            t = i / steps
            color = interp_color(self.border_color, "#FFFFFF", t * 0.4)
            self.canvas.itemconfig(self.outline_id, outline=color)
            self.canvas.after(30, step_up, i + 1)
        step_up(0)


# --------------------------------------------------
# Main Application
# --------------------------------------------------

class PFTrackerApp:
    def __init__(self, root):
        self.root = root
        root.title("Personal Finance Tracker")
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        root.resizable(False, False)

        import tkinter.font as tkfont
        fams = set(tkfont.families())
        for f in ["Poppins", "Montserrat", "Helvetica", "Arial"]:
            if f in fams:
                self.font_family = f
                break
        else:
            self.font_family = "Helvetica"

        self.FONT_TITLE = (self.font_family, 20, "bold")
        self.FONT_SUB = (self.font_family, 12)
        self.FONT_BTN = (self.font_family, 13, "bold")
        self.FONT_NORMAL = (self.font_family, 11)
        self.FONT_FOOTER = (self.font_family, 9, "italic")

        self.bg = GradientBackground(root, WINDOW_WIDTH, WINDOW_HEIGHT, GRADIENT_TOP, GRADIENT_BOTTOM)
        self.frames = {}
        self._build_main()
        self._build_income()
        self._build_expense()
        self._build_summary()
        self.show_page("main")

    def _clear(self):
        for info in self.frames.values():
            if "win_id" in info:
                try:
                    self.bg.canvas.delete(info["win_id"])
                except Exception:
                    pass

    def show_page(self, key):
        self._clear()
        self.bg.draw_gradient()
        info = self.frames[key]
        box = info["box"]
        win_id = self.bg.canvas.create_window(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, window=box.get_widget(), anchor="c")
        info["win_id"] = win_id
        box.animate_pulse()
        if info.get("on_show"):
            info["on_show"]()

# --------------------------------------------------
# All 4 Pages For Each Option
# --------------------------------------------------

    def _build_main(self):
        box = ContentBox(self.bg, BOX_WIDTH, MAIN_BOX_HEIGHT)
        inner = box.inner_frame
        tk.Label(inner, text="Personal Finance Tracker", font=self.FONT_TITLE, fg=GRADIENT_BOTTOM, bg=CONTENT_BG).pack(pady=(10, 6))
        tk.Label(inner, text="Select an option below:", font=self.FONT_SUB, fg="white", bg=CONTENT_BG).pack(pady=(0, 12))

        btn_area = tk.Frame(inner, bg=CONTENT_BG)
        btn_area.pack()
        GlowButton(btn_area, "Add Income", lambda: self.show_page("income"), font=self.FONT_BTN).pack(pady=8)
        GlowButton(btn_area, "Add Expense", lambda: self.show_page("expense"), font=self.FONT_BTN).pack(pady=8)
        GlowButton(btn_area, "View Summary Report", lambda: self.show_page("summary"), font=self.FONT_BTN).pack(pady=8)
        GlowButton(btn_area, "Exit Program", self._on_exit, font=self.FONT_BTN).pack(pady=8)

        tk.Label(inner, text="© 2025 Personal Finance Tracker", font=self.FONT_FOOTER, fg="#CCCCCC", bg=CONTENT_BG).pack(pady=(16, 0))
        self.frames["main"] = {"box": box}

    def _build_income(self):
        box = ContentBox(self.bg, BOX_WIDTH, OTHER_BOX_HEIGHT)
        inner = box.inner_frame
        tk.Label(inner, text="Add Income", font=self.FONT_TITLE, fg=GRADIENT_BOTTOM, bg=CONTENT_BG).pack(pady=(8, 10))
        tk.Label(inner, text="Enter income amount:", font=self.FONT_NORMAL, fg="white", bg=CONTENT_BG).pack()
        self.income_entry = tk.Entry(inner, width=34, font=self.FONT_NORMAL)
        self.income_entry.pack(pady=6)
        tk.Label(inner, text="Select income category:", font=self.FONT_NORMAL, fg="white", bg=CONTENT_BG).pack()
        self.income_var = tk.StringVar(value=INCOME_CATEGORIES[0])
        ttk.OptionMenu(inner, self.income_var, INCOME_CATEGORIES[0], *INCOME_CATEGORIES).pack(pady=6)
        btns = tk.Frame(inner, bg=CONTENT_BG)
        btns.pack(pady=8)
        GlowButton(btns, "Submit Income", self._submit_income, font=self.FONT_BTN).pack(pady=6)
        GlowButton(btns, "Return to Main Menu", lambda: self.show_page("main"), font=self.FONT_BTN).pack(pady=6)
        self.frames["income"] = {"box": box}

    def _build_expense(self):
        box = ContentBox(self.bg, BOX_WIDTH, OTHER_BOX_HEIGHT)
        inner = box.inner_frame
        tk.Label(inner, text="Add Expense", font=self.FONT_TITLE, fg=GRADIENT_BOTTOM, bg=CONTENT_BG).pack(pady=(8, 10))
        tk.Label(inner, text="Enter expense amount:", font=self.FONT_NORMAL, fg="white", bg=CONTENT_BG).pack()
        self.expense_entry = tk.Entry(inner, width=34, font=self.FONT_NORMAL)
        self.expense_entry.pack(pady=6)
        tk.Label(inner, text="Select expense category:", font=self.FONT_NORMAL, fg="white", bg=CONTENT_BG).pack()
        self.expense_var = tk.StringVar(value=EXPENSE_CATEGORIES[0])
        ttk.OptionMenu(inner, self.expense_var, EXPENSE_CATEGORIES[0], *EXPENSE_CATEGORIES).pack(pady=6)
        btns = tk.Frame(inner, bg=CONTENT_BG)
        btns.pack(pady=8)
        GlowButton(btns, "Submit Expense", self._submit_expense, font=self.FONT_BTN).pack(pady=6)
        GlowButton(btns, "Return to Main Menu", lambda: self.show_page("main"), font=self.FONT_BTN).pack(pady=6)
        self.frames["expense"] = {"box": box}

    def _build_summary(self):
        box = ContentBox(self.bg, BOX_WIDTH, SUMMARY_BOX_HEIGHT)
        inner = box.inner_frame
        tk.Label(inner, text="Summary Report", font=self.FONT_TITLE, fg=GRADIENT_BOTTOM, bg=CONTENT_BG).pack(pady=(8, 10))
        self.summary_frame = tk.Frame(inner, bg=CONTENT_BG)
        self.summary_frame.pack(fill="both", expand=True)
        btns = tk.Frame(inner, bg=CONTENT_BG)
        btns.pack(pady=8)
        GlowButton(btns, "Return to Main Menu", lambda: self.show_page("main"), font=self.FONT_BTN).pack(pady=6)
        self.frames["summary"] = {"box": box, "on_show": self._populate_summary}

# --------------------------------------------------
# The 4 Options That The User Can Choose
# --------------------------------------------------

    def _submit_income(self):
        valid, val = validate_number(self.income_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", val)
            return
        data = load_summary_data()
        cat = self.income_var.get()
        data["income"][cat] += val
        if save_summary_data(data):
            messagebox.showinfo("Success", "Income added successfully.")
            self.income_entry.delete(0, "end")
            self.show_page("main")

    def _submit_expense(self):
        valid, val = validate_number(self.expense_entry.get())
        if not valid:
            messagebox.showerror("Invalid Input", val)
            return
        data = load_summary_data()
        cat = self.expense_var.get()
        data["expenses"][cat] += val
        if save_summary_data(data):
            messagebox.showinfo("Success", "Expense added successfully.")
            self.expense_entry.delete(0, "end")
            self.show_page("main")

    def _populate_summary(self):
        for w in self.summary_frame.winfo_children():
            w.destroy()
        rep = calculate_summary()
        if rep is None:
            tk.Label(self.summary_frame, text="No entries yet.", bg=CONTENT_BG, fg="white", font=self.FONT_NORMAL).pack(anchor="w")
            return
        tk.Label(self.summary_frame, text=f"Total Income: {format_currency(rep['total_income'])}", bg=CONTENT_BG, fg="white", font=self.FONT_NORMAL).pack(anchor="w")
        tk.Label(self.summary_frame, text=f"Total Expenses: {format_currency(rep['total_expenses'])}", bg=CONTENT_BG, fg="white", font=self.FONT_NORMAL).pack(anchor="w")
        net = rep["net_balance"]
        net_color = "#9CFF00" if net > 0 else "#FF6B6B" if net < 0 else "#FFFFFF"
        tk.Label(self.summary_frame, text=f"Net Balance: {format_currency(net)}", bg=CONTENT_BG, fg=net_color, font=(self.font_family, 12, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(self.summary_frame, text="Income by Category:", bg=CONTENT_BG, fg="#9CFF00", font=(self.font_family, 11, "bold")).pack(anchor="w")
        for cat in INCOME_CATEGORIES:
            tk.Label(self.summary_frame, text=f"  {cat}: {format_currency(rep['income'].get(cat, 0.0))}", bg=CONTENT_BG, fg="white", font=self.FONT_NORMAL).pack(anchor="w")
        tk.Label(self.summary_frame, text="Expenses by Category:", bg=CONTENT_BG, fg="#9CFF00", font=(self.font_family, 11, "bold")).pack(anchor="w", pady=(8, 0))
        for cat in EXPENSE_CATEGORIES:
            tk.Label(self.summary_frame, text=f"  {cat}: {format_currency(rep['expenses'].get(cat, 0.0))}", bg=CONTENT_BG, fg="white", font=self.FONT_NORMAL).pack(anchor="w")

    def _on_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            d = load_summary_data()
            save_summary_data(d)
            self.root.quit()


# --------------------------------------------------
# Summary Calculator
# --------------------------------------------------

def calculate_summary():
    data = load_summary_data()
    total_income = sum(float(v) for v in data.get("income", {}).values())
    total_expenses = sum(float(v) for v in data.get("expenses", {}).values())
    if total_income == 0 and total_expenses == 0:
        return None
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": total_income - total_expenses,
        "income": data.get("income", {}),
        "expenses": data.get("expenses", {}),
    }


# --------------------------------------------------
# Start
# --------------------------------------------------

def main():
    try:
        root = tk.Tk()
    except Exception:
        traceback.print_exc()
        return
    try:
        app = PFTrackerApp(root)
        root.mainloop()
    except Exception:
        traceback.print_exc()
        messagebox.showerror("Fatal Error", "An unexpected error occurred. See console for details.")


if __name__ == "__main__":
    main()