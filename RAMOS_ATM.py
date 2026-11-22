#Project1: ATM Simulation|PYTHON|GUI|DSA
#RHON JACOB B. RAMOS|BSIS-2B

import calendar
import ctypes
import os
import tkinter as tk
from datetime import date
from tkinter import ttk, messagebox, filedialog

CARD = "pin.code"          # file on the flash drive that acts as the ATM card
MIN_DEPOSIT = 5000
MAX_DEPOSIT = 500000
BILL = 50                  # cash deposits must be in multiples of 50 (no coins)
WAIT = 30                  # seconds to wait for a flash drive before going back to the menu
NETWORKS = ["SMART", "GLOBE", "DITO", "GOMO", "TNT", "TM"]
FONT = "Arial"             # plain font, like the screens on real ATM machines
BG, SKY, BLUE, DARK = "#FFFFFF", "#E3F2FD", "#42A5F5", "#1565C0"
TEXT, GRAY, RED = "#063561", "#6A91BB", "#D32F2F"


#accounts
def encrypt(pin):
    """Shifts every digit of the PIN by 3."""
    return "".join(str((int(d) + 3) % 10) for d in pin)


def money(x):
    return f"PHP {x:,.2f}"


def norm(text):
    """'Ramos, Rhon Jacob B.' and 'ramos rhon jacob b' count as the same name."""
    return "".join(c for c in text.lower() if c.isalnum())


class Account:                     # one node of the linked list
    def __init__(self, no, name, birthday, contact, pin, balance):
        self.no, self.name, self.birthday, self.contact = no, name, birthday, contact
        self.pin, self.balance, self.next = encrypt(pin), balance, None


class Bank:                        # singly linked list of accounts
    def __init__(self):
        self.head = self.tail = None
        self.next_no = 10001       # 5-digit account numbers, auto-incremented

    def add(self, name, birthday, contact, pin, deposit):
        acc = Account(self.next_no, name, birthday, contact, pin, deposit)
        self.next_no += 1
        if self.head:
            self.tail.next = acc
        else:
            self.head = acc
        self.tail = acc

    def find(self, no):
        acc = self.head
        while acc and acc.no != no:
            acc = acc.next
        return acc

    def login(self, name, no, pin):
        acc = self.find(no)
        if acc and acc.pin == encrypt(pin) and norm(acc.name) == norm(name):
            return acc


#flash drive = ATM card
def find_drive(need_card):
    """First removable drive (that already has the card, if need_card). Windows only."""
    if os.name != "nt":
        return None
    mask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        drive = f"{chr(65 + i)}:\\"
        if mask >> i & 1 and ctypes.windll.kernel32.GetDriveTypeW(drive) == 2:   # 2 = removable
            if not need_card or os.path.isfile(drive + CARD):
                return drive


def save_card(drive, acc_no, encrypted_pin):
    try:
        with open(os.path.join(drive, CARD), "w") as f:
            f.write(f"{acc_no}\n{encrypted_pin}\n")
        return True
    except OSError:
        return False


#input rules
LIMITS = {"pin": 6, "contact": 11, "mobile": 11, "int": 9, "cash": 6}

RULES = {  
    "text":    (lambda t: t != "", "Please fill in this box."),
    "name":    (lambda t: any(c.isalpha() for c in t), "Please enter a name (letters only)."),
    "initial": (lambda t: True, ""),
    "date":    (lambda t: t != "", "Please select a valid birthday (month, day and year)."),
    "contact": (lambda t: len(t) == 11 and t.startswith("09"),
                "Contact number must be 11 digits and start with 09 (e.g. 09123456789)."),
    "pin":     (lambda t: 4 <= len(t) <= 6, "PIN must be 4-6 digits."),
    "mobile":  (lambda t: 1 <= len(t) <= 11, "Mobile number must be 1-11 digits."),
    "int":     (lambda t: t != "", "Please enter the account number."),
    "money":   (lambda t: t.replace(".", "", 1).isdigit() and float(t) > 0,
                "Please enter an amount greater than zero."),
    "cash":    (lambda t: t.isdigit() and 0 < int(t) <= MAX_DEPOSIT and int(t) % BILL == 0,
                f"Cash must be in PHP {BILL} bills (50, 100, 150, 200 ...), no coins. Maximum PHP {MAX_DEPOSIT:,}."),
    "choice":  (lambda t: t != "", "Please choose an option."),
}


def can_type(text, kind):
    """Keystroke filter: only valid characters can be typed."""
    if text == "" or kind == "text":
        return True
    if kind == "name":
        return all(c.isalpha() or c in " -'." for c in text)
    if kind == "initial":
        return text.isalpha() and len(text) <= 1
    if kind == "money":
        return text.replace(".", "", 1).isdigit()
    if kind == "contact" and not "09".startswith(text[:2]):
        return False                                   # must start with 09
    return text.isdigit() and len(text) <= LIMITS[kind]


def check(kind, text):
    """Returns an error message, or None when the text is fine."""
    valid, message = RULES[kind]
    return None if valid(text.strip()) else message


def value_of(kind, text):
    """Converts the typed text into its real value."""
    convert = {"int": int, "money": float, "cash": int, "initial": str.upper, "date": date.fromisoformat,
               "name": lambda t: " ".join(t.split())}
    return convert.get(kind, str)(text.strip())


def step_error(key, kind, text, data):
    """Checks one registration answer."""
    message = check(kind, text)
    if message is None and key == "deposit" and int(text) < MIN_DEPOSIT:
        message = f"Initial deposit must be at least PHP {MIN_DEPOSIT:,}."
    if message is None and key == "pin2" and text != data["pin"]:
        message = "PIN codes do not match. Please try again."
    return message


#themes
def apply_theme(root):
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure("TFrame", background=BG)
    s.configure("TLabel", background=BG, foreground=TEXT, font=(FONT, 13))
    for name, size, color in (("Title", 24, DARK), ("Dlg", 18, DARK), ("Big", 22, TEXT), ("Sub", 12, GRAY),
                              ("Step", 12, BLUE), ("Field", 12, TEXT), ("Err", 12, RED)):
        s.configure(f"{name}.TLabel", font=(FONT, size, "bold"), foreground=color)
    # buttons: name, font size, padding, background, text color, hover color
    for name, size, pad, bg, fg, hover in (("Menu", 16, (10, 16), "#BBDEFB", DARK, "#90CAF9"),
                                           ("Tx", 14, (8, 11), "#BBDEFB", DARK, "#90CAF9"),
                                           ("Btn", 12, (14, 8), "#BBDEFB", DARK, "#90CAF9"),
                                           ("Primary", 12, (14, 8), BLUE, "white", DARK)):
        s.configure(f"{name}.TButton", font=(FONT, size, "bold"), padding=pad, background=bg,
                    foreground=fg, borderwidth=0, relief="flat", focuscolor=bg)
        s.map(f"{name}.TButton", background=[("active", hover)])
    s.configure("TEntry", fieldbackground="white", foreground=TEXT, padding=6,
                bordercolor="#90CAF9", lightcolor="#90CAF9", darkcolor="#90CAF9")
    s.map("TEntry", bordercolor=[("focus", BLUE)], lightcolor=[("focus", BLUE)], darkcolor=[("focus", BLUE)])
    s.configure("TCombobox", fieldbackground="white", background="#BBDEFB", foreground=TEXT,
                arrowcolor=DARK, bordercolor="#90CAF9", padding=4)
    s.map("TCombobox", fieldbackground=[("readonly", "white")], foreground=[("readonly", TEXT)])
    root.option_add("*TCombobox*Listbox.font", (FONT, 13))


def draw_logo(parent, size=100):
    """ATM icon drawn with simple shapes (no image file needed)."""
    k, navy = size / 512, "#0B3C7C"
    c = tk.Canvas(parent, width=size, height=size, bg=BG, highlightthickness=0)

    def box(x1, y1, x2, y2, fill=BLUE):
        c.create_rectangle(x1 * k, y1 * k, x2 * k, y2 * k, fill=fill, outline=navy, width=max(2, 14 * k))

    box(60, 6, 452, 135)                       # ATM sign
    box(97, 135, 415, 506)                     # machine body
    box(127, 165, 385, 305, "#473B3B")         # screen
    for r in range(3):                         # keypad
        for col in range(3):
            box(127 + col * 47, 340 + r * 49, 161 + col * 47, 372 + r * 49)
    box(266, 338, 386, 404)                    # card reader
    box(292, 372, 352, 470)                    # card
    c.create_rectangle(282 * k, 360 * k, 370 * k, 374 * k, fill=navy, outline=navy)
    c.create_text(256 * k, 72 * k, text="ATM", fill=navy, font=(FONT, -round(100 * k), "bold"))
    return c


#small windows
def ok(msg):
    messagebox.showinfo("Success", msg)


def fail(msg):
    messagebox.showerror("Error", msg)


def center(win, parent):
    win.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - win.winfo_reqwidth()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - win.winfo_reqheight()) // 2
    win.geometry(f"+{max(x, 0)}+{max(y, 0)}")


def entry(parent, kind, var, width=26, font=(FONT, 15)):
    e = ttk.Entry(parent, textvariable=var, width=width, font=font, show="*" if kind == "pin" else "")
    e.configure(validate="key", validatecommand=(e.register(can_type), "%P", kind))
    return e


def ask(parent, title, fields, verify=None):
    """Pop-up form. fields = [(key, label, kind)]. Returns a dict of answers, or None if cancelled (ESC)."""
    win = tk.Toplevel(parent, bg=BG)
    win.title(title)
    win.transient(parent)
    win.resizable(False, False)
    body = ttk.Frame(win, padding=28)
    body.pack()
    ttk.Label(body, text=title, style="Dlg.TLabel").pack(anchor="w")
    vars_, answer, first = {}, [None], None
    for key, label, kind in fields:
        ttk.Label(body, text=label, style="Field.TLabel").pack(anchor="w", pady=(10, 2))
        vars_[key] = tk.StringVar()
        if kind == "choice":
            box = ttk.Combobox(body, textvariable=vars_[key], values=NETWORKS, state="readonly",
                               width=26, font=(FONT, 14))
        else:
            box = entry(body, kind, vars_[key], 28)
        box.pack(fill="x", ipady=4)
        first = first or box

    def submit(event=None):
        for key, label, kind in fields:
            message = check(kind, vars_[key].get())
            if message:
                return messagebox.showerror("Invalid input", message, parent=win)
        data = {key: value_of(kind, vars_[key].get()) for key, label, kind in fields}
        message = verify(data) if verify else None
        if message:
            return messagebox.showerror("Invalid input", message, parent=win)
        answer[0] = data
        win.destroy()

    row = ttk.Frame(body)
    row.pack(pady=(20, 0))
    ttk.Button(row, text="OK", command=submit, style="Primary.TButton").pack(side="left", padx=5)
    ttk.Button(row, text="Cancel (Esc)", command=win.destroy, style="Btn.TButton").pack(side="left", padx=5)
    win.bind("<Return>", submit)
    win.bind("<Escape>", lambda e: win.destroy())
    center(win, parent)
    win.grab_set()
    first.focus_set()
    win.wait_window()
    return answer[0]


def wait_for_drive(parent, need_card, note=""):
    """'Insert flash drive' window with a 30-second countdown. Returns (drive, timed_out)."""
    win = tk.Toplevel(parent, bg=BG)
    win.title("Flash Drive (ATM Card)")
    win.transient(parent)
    win.resizable(False, False)
    state = {"drive": None, "timed_out": False, "left": WAIT, "paused": False}

    f = ttk.Frame(win, padding=(40, 28))
    f.pack()
    ttk.Label(f, text="INSERT FLASH DRIVE", style="Dlg.TLabel").pack()
    text = ("Please insert your flash drive (ATM card)." if need_card
            else "Please insert a flash drive to save as your ATM card.")
    ttk.Label(f, text=(note + "\n" if note else "") + text, wraplength=340, justify="center",
              font=(FONT, 13)).pack(pady=(8, 14))
    canvas = tk.Canvas(f, width=70, height=70, bg=BG, highlightthickness=0)     # simple spinner
    canvas.create_oval(8, 8, 62, 62, outline="#DCEBFA", width=7)
    arc = canvas.create_arc(8, 8, 62, 62, start=90, extent=90, style="arc", outline=BLUE, width=7)
    canvas.pack()
    ttk.Label(f, text="LOADING...", font=(FONT, 15, "bold"), foreground=DARK).pack(pady=(8, 0))
    timer = tk.StringVar(value=f"Returning to menu in {WAIT} seconds")
    ttk.Label(f, textvariable=timer, style="Sub.TLabel").pack(pady=(2, 14))

    def loop(n=1):                               # runs every 50 ms
        if not win.winfo_exists():
            return
        canvas.itemconfig(arc, start=(90 - n * 15) % 360)            # spinner
        if n % 10 == 0:                                              # twice a second: look for the drive
            state["drive"] = find_drive(need_card)
            if state["drive"]:
                return win.destroy()
        if n % 20 == 0 and not state["paused"]:                      # once a second: countdown
            state["left"] -= 1
            timer.set(f"Returning to menu in {state['left']} seconds")
            if state["left"] <= 0:                                   # time is up: back to the menu
                state["timed_out"] = True
                return win.destroy()
        win.after(50, loop, n + 1)

    def browse():                                # manual fallback (non-Windows, or an unflagged drive)
        state["paused"] = True
        folder = filedialog.askdirectory(parent=win, title="Choose the flash drive folder")
        state["paused"] = False
        if folder and (not need_card or os.path.isfile(os.path.join(folder, CARD))):
            state["drive"] = folder
            win.destroy()
        elif folder:
            messagebox.showwarning("No card", f"No {CARD} found in that folder.", parent=win)

    row = ttk.Frame(f)
    row.pack()
    ttk.Button(row, text="Browse folder...", command=browse, style="Btn.TButton").pack(side="left", padx=5)
    ttk.Button(row, text="Cancel (Esc)", command=win.destroy, style="Primary.TButton").pack(side="left", padx=5)
    win.bind("<Escape>", lambda e: win.destroy())
    center(win, parent)
    win.grab_set()
    loop()
    win.wait_window()
    return state["drive"], state["timed_out"]


STEPS = [   # key, question, hint, kind  (registration: one question per screen)
    ("surname", "What is your surname?", "Your last name", "name"),
    ("given", "What is your given name?", "Your first name (and second name, if you have one)", "name"),
    ("middle", "What is your middle initial?", "One letter. Leave it blank if you have none, then press Next", "initial"),
    ("birthday", "When is your birthday?", "Select your month, day and year", "date"),
    ("contact", "What is your contact number?", "11 digits, starting with 09", "contact"),
    ("deposit", "Enter your initial deposit", f"PHP {MIN_DEPOSIT:,} to PHP {MAX_DEPOSIT:,}", "cash"),
    ("pin", "Create your PIN code", "4 to 6 digits", "pin"),
    ("pin2", "Confirm your PIN code", "Re-enter the PIN you just created", "pin"),
]


class ATM(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ATM")
        self.configure(bg=BG)
        self.geometry(f"600x{min(800, self.winfo_screenheight() - 80)}")
        self.minsize(560, 600)
        apply_theme(self)
        # On Windows, pressing Alt or F10 puts the window in "menu mode", which pauses the loading
        # animation and countdown. Swallowing these keys keeps everything running.
        for key in ("<Alt_L>", "<Alt_R>", "<KeyRelease-Alt_L>", "<KeyRelease-Alt_R>", "<F10>"):
            self.bind_all(key, lambda e: "break")
        self.bank, self.acc, self.frame = Bank(), None, None
        self.status = tk.StringVar()
        self.main_menu()

    def screen(self, title, subtitle=None, logo=False):
        """Clears the window and starts a fresh page."""
        if self.frame:
            self.frame.destroy()
        self.unbind("<Escape>")
        self.unbind("<Return>")
        self.frame = ttk.Frame(self, padding=(30, 22))
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        if logo:
            draw_logo(self.frame).pack(pady=(0, 10))
        ttk.Label(self.frame, text=title, style="Title.TLabel").pack(pady=(0, 4))
        if subtitle:
            ttk.Label(self.frame, text=subtitle, style="Sub.TLabel").pack(pady=(0, 14))
        return self.frame

    def buttons(self, parent, items, style="Menu.TButton"):
        for text, command in items:
            ttk.Button(parent, text=text, command=command, style=style).pack(fill="x", pady=6)

    #main menu
    def main_menu(self):
        self.acc = None
        f = self.screen("THE ATM SIMULATION", "Please select an option", logo=True)
        self.buttons(f, [("REGISTER NEW ACCOUNT", lambda: self.step(0, {})),
                         ("TRANSACTION", self.login), ("EXIT", self.quit_app)])

    def quit_app(self):
        messagebox.showinfo("Goodbye", "Thank you for using THE ATM SIMULATION. Goodbye!")
        self.destroy()

    # registration
    def birthday_boxes(self, parent, old):
        """Month / Day / Year drop-downs. Returns a function that reads the chosen date."""
        months = list(calendar.month_name)[1:]
        first = (months[old.month - 1], str(old.day), str(old.year)) if old else ("", "", "")
        month, day, year = (tk.StringVar(value=v) for v in first)
        row = ttk.Frame(parent)
        row.pack()
        for col, (label, var, values, width) in enumerate((
                ("Month", month, months, 11),
                ("Day", day, [str(d) for d in range(1, 32)], 4),
                ("Year", year, [str(y) for y in range(2021, 1949, -1)], 6))):
            cell = ttk.Frame(row)
            cell.grid(row=0, column=col, padx=6)
            ttk.Label(cell, text=label, style="Field.TLabel").pack(anchor="w", pady=(0, 4))
            ttk.Combobox(cell, textvariable=var, values=values, state="readonly", width=width,
                         font=(FONT, 16, "bold")).pack(ipady=4)

        def read():
            try:
                return date(int(year.get()), months.index(month.get()) + 1, int(day.get())).isoformat()
            except ValueError:               # nothing chosen yet, or a date like Feb 30
                return ""
        return read

    def step(self, i, data):
        key, question, hint, kind = STEPS[i]
        f = self.screen("ACCOUNT REGISTRATION")
        ttk.Label(f, text=f"STEP {i + 1} OF {len(STEPS)}", style="Step.TLabel").pack(pady=(0, 22))
        ttk.Label(f, text=question, style="Big.TLabel", wraplength=480, justify="center").pack()
        ttk.Label(f, text=hint, style="Sub.TLabel").pack(pady=(4, 16))
        if kind == "date":
            read = self.birthday_boxes(f, data.get("birthday"))
        else:
            var = tk.StringVar(value="" if kind == "pin" else str(data.get(key, "")))
            box = entry(f, kind, var, 22, (FONT, 22, "bold"))
            box.pack(ipady=8)
            box.focus_set()
            read = var.get
        error = tk.StringVar()
        ttk.Label(f, textvariable=error, style="Err.TLabel", wraplength=480, justify="center").pack(pady=(12, 0))

        def next_step(event=None):
            message = step_error(key, kind, read(), data)
            if message:
                return error.set(message)
            data[key] = value_of(kind, read())
            self.step(i + 1, data) if i + 1 < len(STEPS) else self.finish(data)

        def back(event=None):
            self.step(i - 1, data) if i else self.main_menu()

        row = ttk.Frame(f)
        row.pack(side="bottom", pady=(14, 0))
        ttk.Button(row, text="Back" if i else "Cancel", command=back, style="Btn.TButton").pack(side="left", padx=6)
        ttk.Button(row, text="Finish" if i == len(STEPS) - 1 else "Next", command=next_step,
                   style="Primary.TButton").pack(side="left", padx=6)
        self.bind("<Return>", next_step)
        self.bind("<Escape>", back)

    def finish(self, d):
        no = self.bank.next_no
        while True:                          # the flash drive becomes the ATM card
            drive, timed_out = wait_for_drive(self, False)
            if drive is None:
                if not timed_out:            # on a timeout we simply go back to the menu
                    messagebox.showwarning("Registration cancelled",
                                           "Registration cancelled: no flash drive was inserted.")
                return self.main_menu()
            if save_card(drive, no, encrypt(d["pin"])):
                break
            fail("Could not write to that drive. Please try another one.")

        middle = f" {d['middle']}." if d["middle"] else ""
        name = f"{d['surname']}, {d['given']}{middle}"
        self.bank.add(name, d["birthday"].strftime("%m/%d/%Y"), d["contact"], d["pin"], d["deposit"])

        f = self.screen("REGISTRATION SUCCESSFUL!", "Please remember your ATM card details")
        panel = tk.Frame(f, bg=SKY, padx=24, pady=16)
        panel.pack(fill="x", pady=8)
        for label, value in (("FULL NAME", name), ("ACCOUNT NO.", no),
                             ("PIN CODE", "encrypted and saved, not shown"), ("ATM CARD", f"saved to {drive}")):
            tk.Label(panel, text=label, bg=SKY, fg=GRAY, font=(FONT, 11, "bold")).pack(anchor="w")
            tk.Label(panel, text=str(value), bg=SKY, fg=TEXT, font=(FONT, 17, "bold"),
                     wraplength=460, justify="left").pack(anchor="w", pady=(0, 8))
        ttk.Label(f, text="Use your Full Name, Account Number and PIN Code to log in under TRANSACTION.",
                  style="Sub.TLabel", wraplength=470, justify="center").pack(pady=8)
        self.buttons(f, [("BACK TO MAIN MENU", self.main_menu)])

    #login
    def login(self):
        if self.bank.head is None:
            return messagebox.showinfo("No accounts", "No registered accounts yet. Please register first.")
        f = self.screen("ACCOUNT LOGIN", "Enter your account details to log in", logo=True)
        vars_ = {}
        for key, label, kind in (("name", "Full Name (Surname, Given Name M.I.)", "text"),
                                 ("no", "Account Number", "int"), ("pin", "PIN Code", "pin")):
            ttk.Label(f, text=label, style="Field.TLabel").pack(anchor="w", pady=(10, 2))
            vars_[key] = tk.StringVar()
            box = entry(f, kind, vars_[key])
            box.pack(fill="x", ipady=5)
            if key == "name":
                box.focus_set()

        def submit(event=None):
            name, no, pin = (vars_[k].get().strip() for k in ("name", "no", "pin"))
            if not name or not no or len(pin) < 4:
                return fail("Please fill in every field (PIN is 4-6 digits).")
            self.acc = self.bank.login(name, int(no), pin)
            if self.acc is None:
                return fail("Invalid Name, Account Number, or PIN. Please try again.")
            self.tx_menu()

        row = ttk.Frame(f)
        row.pack(pady=22)
        ttk.Button(row, text="Back", command=self.main_menu, style="Btn.TButton").pack(side="left", padx=6)
        ttk.Button(row, text="Login", command=submit, style="Primary.TButton").pack(side="left", padx=6)
        self.bind("<Return>", submit)
        self.bind("<Escape>", lambda e: self.main_menu())

    # ---- transactions
    def tx_menu(self):
        f = self.screen("TRANSACTION MENU", f"Welcome, {self.acc.name}")
        self.buttons(f, [("BALANCE INQUIRY", self.balance), ("WITHDRAW", self.withdraw),
                         ("DEPOSIT", self.deposit), ("FUND TRANSFER", self.transfer),
                         ("CHANGE PIN CODE", self.change_pin), ("MOBILE TOP-UP / LOAD", self.load),
                         ("BACK TO MAIN MENU", self.main_menu)], "Tx.TButton")
        ttk.Label(f, text="Press ESC in any dialog to cancel a transaction.", style="Sub.TLabel").pack(pady=(10, 0))
        self.status.set("")
        ttk.Label(f, textvariable=self.status, style="Err.TLabel").pack()

    def form(self, title, fields, verify=None):
        self.status.set("")
        answers = ask(self, title, fields, verify)
        if answers is None:
            self.status.set("Transaction cancelled.")
        return answers

    def balance(self):
        a = self.acc
        messagebox.showinfo("BALANCE INQUIRY",
                            f"Account No. : {a.no}\nAccount Name: {a.name}\nBalance     : {money(a.balance)}")

    def withdraw(self):
        r = self.form("Withdraw", [("amt", "Amount (PHP)", "money")])
        if r is None:
            return
        if r["amt"] > self.acc.balance:
            return fail("Insufficient balance!")
        self.acc.balance -= r["amt"]
        ok(f"Withdraw successful!\n\nNew balance: {money(self.acc.balance)}")

    def deposit(self):
        r = self.form("Deposit", [("amt", f"Amount (PHP {BILL} bills only, max {MAX_DEPOSIT:,})", "cash")])
        if r is None:
            return
        self.acc.balance += r["amt"]
        ok(f"Deposit successful!\n\nNew balance: {money(self.acc.balance)}")

    def transfer(self):
        r = self.form("Fund Transfer", [("to", "Receiver's Account No.", "int"), ("amt", "Amount (PHP)", "money")])
        if r is None:
            return
        receiver = self.bank.find(r["to"])
        if r["to"] == self.acc.no:
            return fail("You cannot transfer funds to your own account.")
        if receiver is None:
            return fail(f"Fund transfer failed: Account No. {r['to']} is not an enrolled account.")
        if r["amt"] > self.acc.balance:
            return fail("Insufficient balance!")
        self.acc.balance -= r["amt"]
        receiver.balance += r["amt"]
        ok(f"Fund transfer successful!\n\nTransferred {money(r['amt'])} to {receiver.name} "
           f"(Acct No. {receiver.no})\nYour new balance: {money(self.acc.balance)}")

    def load(self):
        r = self.form("Mobile Top-up / Load", [("net", "Network", "choice"),
                                               ("no", "Mobile No. (max 11 digits)", "mobile"),
                                               ("amt", "Amount (PHP)", "money")])
        if r is None:
            return
        if r["amt"] > self.acc.balance:
            return fail("Insufficient balance!")
        self.acc.balance -= r["amt"]
        ok(f"Mobile Top-up / Load successful!\n\nNetwork: {r['net']}\nMobile No.: {r['no']}\n"
           f"Load Amount: {money(r['amt'])}\nNew Balance: {money(self.acc.balance)}")

    def change_pin(self):
        def verify(v):
            if encrypt(v["old"]) != self.acc.pin:
                return "Incorrect current PIN."
            if v["new"] != v["again"]:
                return "PIN codes do not match. Please try again."

        r = self.form("Change PIN", [("old", "Current PIN", "pin"), ("new", "New PIN (4-6 digits)", "pin"),
                                     ("again", "Confirm new PIN", "pin")], verify)
        if r is None:
            return
        self.acc.pin = encrypt(r["new"])
        ok("PIN changed successfully!")
        drive, _ = wait_for_drive(self, True, "Re-insert your flash drive to update your card.")
        if drive is None:
            messagebox.showwarning("Card not updated", "Card update cancelled. NOTE: your old card is now out of "
                                   "sync with your account. Update it before your next login.")
        elif save_card(drive, self.acc.no, self.acc.pin):
            ok("Card updated successfully!")
        else:
            fail("Could not write to the flash drive.")


if __name__ == "__main__":
    ATM().mainloop()
