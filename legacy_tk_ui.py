import tkinter as tk
from tkinter import messagebox, simpledialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from db import DBManager
from datetime import datetime, timedelta, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from zoneinfo import ZoneInfo

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

# Bulgarian month names
BULGARIAN_MONTHS = [
    "Януари", "Февруари", "Март", "Април", "Май", "Юни",
    "Юли", "Август", "Септември", "Октомври", "Ноември", "Декември"
]
BULGARIAN_MONTH_TO_NUM = {
    "Януари": 1,
    "Февруари": 2,
    "Март": 3,
    "Април": 4,
    "Май": 5,
    "Юни": 6,
    "Юли": 7,
    "Август": 8,
    "Септември": 9,
    "Октомври": 10,
    "Ноември": 11,
    "Декември": 12
}

class AppUI:
    # Reservation duration constant (90 minutes = 1h30m)
    RESERVATION_DURATION_MINUTES = 90
    
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.admin_logged_in = False

        # Main window: Bulgarian title + "cyborg" theme
        self.window = ttk.Window(
            title="Ресторант Хъшове",
            themename="cyborg",
            size=(900, 600)
        )
        self.window.resizable(True, True)

        # Attempt to set a custom PNG logo/icon
        try:
            self.window.iconphoto(False, tk.PhotoImage(file="logo.png"))
        except Exception:
            pass

        # Notebook for main tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Bind a callback to detect tab switches (to auto-logout if leaving admin tab)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_main_tab_changed)

        # Create main tabs
        self.create_reservations_tab()
        self.create_table_layout_tab()
        self.create_admin_tab()  # This has the single-window login approach.

    # ----------------------------------------------------------------
    # Detect if user leaves admin tab -> auto logout
    # Also synchronize table layout when switching to it
    # ----------------------------------------------------------------
    def on_main_tab_changed(self, event):
        """
        Handle tab change events.
        - Auto-logout when leaving admin tab
        - Refresh table layout when switching to it (ensures filter synchronization)
        """
        current_tab_id = self.notebook.index("current")
        current_tab_text = self.notebook.tab(current_tab_id, "text")

        # If user is leaving the admin tab and is currently logged in, log out
        if current_tab_text != "Администраторски панел" and self.admin_logged_in:
            self.logout_admin()
        
        # If user switches to table layout tab, refresh it to reflect current filters
        if current_tab_text == "Разпределение на масите":
            self.refresh_table_layout()
            self.update_table_layout_filter_label()

    # ----------------------------------------------------------------
    # Reservations Tab
    # ----------------------------------------------------------------
    def create_reservations_tab(self):
        self.res_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.res_tab, text="Резервации")

        # Date filters in first row
        filter_frame = ttk.Frame(self.res_tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 0))

        # MONTH Filter (default to current month)
        ttk.Label(filter_frame, text="Месец:").pack(side="left", padx=(0,5))
        self.month_filter_var = tk.StringVar()
        month_filter_values = ["Всички"] + BULGARIAN_MONTHS
        current_month_num = date.today().month
        current_month_name = BULGARIAN_MONTHS[current_month_num - 1]
        self.month_filter_var.set(current_month_name)

        self.month_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.month_filter_var,
            values=month_filter_values,
            state="readonly",
            width=12
        )
        self.month_filter_combo.pack(side="left", padx=(0,15))
        self.month_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_date_filter_changed())

        # DAY Filter (default to current day)
        ttk.Label(filter_frame, text="Ден:").pack(side="left", padx=(0,5))
        self.day_filter_var = tk.StringVar()
        day_values = ["Всички"] + [str(d) for d in range(1, 32)]
        current_day_str = str(date.today().day)
        self.day_filter_var.set(current_day_str)

        self.day_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.day_filter_var,
            values=day_values,
            state="readonly",
            width=5
        )
        self.day_filter_combo.pack(side="left", padx=(0,15))
        self.day_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_date_filter_changed())

        # STATUS Filter (default = "Резервирана")
        ttk.Label(filter_frame, text="Статус:").pack(side="left", padx=(0,5))
        self.status_filter_var = tk.StringVar(value="Резервирана")
        status_values = ["Резервирана", "Отменена", "Всички"]
        self.status_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter_var,
            values=status_values,
            state="readonly",
            width=12
        )
        self.status_filter_combo.pack(side="left", padx=(0,15))
        self.status_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_reservations_tree())

        # TABLE Filter
        ttk.Label(filter_frame, text="Маса:").pack(side="left", padx=(0,5))
        # Now 50 tables
        table_values = ["Всички"] + [str(i) for i in range(1, 51)]
        self.table_filter_var = tk.StringVar(value="Всички")
        self.table_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.table_filter_var,
            values=table_values,
            state="readonly",
            width=8
        )
        self.table_filter_combo.pack(side="left", padx=(0,15))
        self.table_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_reservations_tree())

        # Time filters in second row
        time_filter_frame = ttk.Frame(self.res_tab)
        time_filter_frame.pack(fill="x", padx=10, pady=(5, 0))

        ttk.Label(time_filter_frame, text="Час:").pack(side="left", padx=(0,5))
        
        # HOUR Filter
        self.hour_filter_var = tk.StringVar(value="Всички")
        hour_values = ["Всички"] + [f"{h:02d}" for h in range(24)]
        self.hour_filter_combo = ttk.Combobox(
            time_filter_frame,
            textvariable=self.hour_filter_var,
            values=hour_values,
            state="readonly",
            width=8
        )
        self.hour_filter_combo.pack(side="left", padx=(0,10))
        self.hour_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_time_filter_changed())
        
        ttk.Label(time_filter_frame, text="Минути:").pack(side="left", padx=(0,5))
        
        # MINUTE Filter (00, 15, 30, 45)
        self.minute_filter_var = tk.StringVar(value="Всички")
        minute_values = ["Всички", "00", "15", "30", "45"]
        self.minute_filter_combo = ttk.Combobox(
            time_filter_frame,
            textvariable=self.minute_filter_var,
            values=minute_values,
            state="readonly",
            width=8
        )
        self.minute_filter_combo.pack(side="left", padx=(0,10))
        self.minute_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.on_time_filter_changed())
        
        # Helper text
        ttk.Label(
            time_filter_frame,
            text="(показва резервации, които започват в/след избраното време)",
            font=("TkDefaultFont", 8, "italic")
        ).pack(side="left", padx=(10,0))

        # TreeView
        columns = (
            "table_number",
            "time_slot",
            "customer_name",
            "additional_info",
            "phone_number",
            "waiter_name",
            "status"
        )
        self.res_tree = ttk.Treeview(
            self.res_tab,
            columns=columns,
            show="headings",
            height=12
        )
        self.res_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Headings + columns
        self.res_tree.heading("table_number", text="Маса", anchor="center")
        self.res_tree.column("table_number", anchor="center", width=60, stretch=True)

        self.res_tree.heading("time_slot", text="Час", anchor="center")
        self.res_tree.column("time_slot", anchor="center", width=120, stretch=True)

        self.res_tree.heading("customer_name", text="Клиент", anchor="center")
        self.res_tree.column("customer_name", anchor="center", width=100, stretch=True)

        self.res_tree.heading("additional_info", text="Доп. информация", anchor="w")
        self.res_tree.column("additional_info", anchor="w", width=300, stretch=True)

        self.res_tree.heading("phone_number", text="Телефон", anchor="center")
        self.res_tree.column("phone_number", anchor="center", width=100, stretch=True)

        self.res_tree.heading("waiter_name", text="Сервитьор", anchor="center")
        self.res_tree.column("waiter_name", anchor="center", width=100, stretch=True)

        self.res_tree.heading("status", text="Статус", anchor="center")
        self.res_tree.column("status", anchor="center", width=80, stretch=True)

        # Buttons
        btn_frame = ttk.Frame(self.res_tab)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Създай резервация", command=self.open_create_reservation_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Промени резервация", command=self.open_modify_reservation_window).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Изтрий резервация", command=self.delete_reservation).pack(side="left", padx=5)

        self.refresh_reservations_tree()

    def on_date_filter_changed(self):
        """
        Callback when date filters (month or day) change.
        Updates both reservations tree and table layout to maintain synchronization.
        """
        self.refresh_reservations_tree()
        self.refresh_table_layout()
    
    def on_time_filter_changed(self):
        """
        Callback when time filters (hour or minute) change.
        Updates both reservations tree and table layout to maintain synchronization.
        """
        self.refresh_reservations_tree()
        self.refresh_table_layout()

    def get_selected_datetime(self):
        """
        Combine selected date and time filters into a timezone-aware datetime.
        Returns None if date/time is not fully specified.
        Returns (year, month, day, hour, minute) as a timezone-aware datetime or None.
        """
        from zoneinfo import ZoneInfo
        from datetime import datetime
        
        selected_month_bg = self.month_filter_var.get()
        selected_day_str = self.day_filter_var.get()
        selected_hour_str = self.hour_filter_var.get()
        selected_minute_str = self.minute_filter_var.get()
        
        # If any component is "Всички", we can't form a specific datetime
        if (selected_month_bg == "Всички" or selected_day_str == "Всички" or 
            selected_hour_str == "Всички" or selected_minute_str == "Всички"):
            return None
        
        # Get current year (could be extended to allow year selection)
        current_year = date.today().year
        
        try:
            month_num = BULGARIAN_MONTH_TO_NUM.get(selected_month_bg)
            day_num = int(selected_day_str)
            hour_num = int(selected_hour_str)
            minute_num = int(selected_minute_str)
            
            # Create timezone-aware datetime for Europe/Sofia
            dt = datetime(current_year, month_num, day_num, hour_num, minute_num,
                         tzinfo=ZoneInfo("Europe/Sofia"))
            return dt
        except (ValueError, TypeError):
            return None

    def refresh_reservations_tree(self):
        """
        Refresh the reservations tree with time-aware filtering.
        
        Time-aware logic:
        - If a specific time is selected, show:
          A) Ongoing reservations (that overlap the selected time)
          B) Future reservations (that start at/after the selected time)
        - Sort by start time ascending
        """
        for item in self.res_tree.get_children():
            self.res_tree.delete(item)

        all_reservations = self.db.get_reservations()

        selected_month_bg = self.month_filter_var.get()
        selected_day_str  = self.day_filter_var.get()
        selected_status   = self.status_filter_var.get()
        selected_table    = self.table_filter_var.get()
        
        # Get selected datetime if available
        selected_dt = self.get_selected_datetime()

        filtered = []
        for res in all_reservations:
            try:
                res_start = datetime.strptime(res["time_slot"], "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            
            # Calculate reservation end time (start + 90 minutes)
            res_end = res_start + timedelta(minutes=self.RESERVATION_DURATION_MINUTES)

            # Filter by month
            if selected_month_bg != "Всички":
                numeric_month = BULGARIAN_MONTH_TO_NUM.get(selected_month_bg, None)
                if numeric_month and res_start.month != numeric_month:
                    continue

            # Filter by day
            if selected_day_str != "Всички":
                if res_start.day != int(selected_day_str):
                    continue
            
            # Time-aware filtering
            if selected_dt is not None:
                # Convert selected_dt to naive for comparison (both are in Europe/Sofia context)
                selected_naive = selected_dt.replace(tzinfo=None)
                
                # Check if reservation overlaps or is in the future
                # Include if:
                # 1) Reservation is ongoing at selected time: res_start < selected_time < res_end
                # 2) Reservation starts at or after selected time: res_start >= selected_time
                
                is_ongoing = res_start < selected_naive < res_end
                is_future = res_start >= selected_naive
                
                if not (is_ongoing or is_future):
                    continue

            # Status filter
            if selected_status != "Всички":
                db_status = res["status"]
                if db_status == "Reserved":
                    db_status_bg = "Резервирана"
                elif db_status == "Cancelled":
                    db_status_bg = "Отменена"
                else:
                    db_status_bg = db_status
                if db_status_bg != selected_status:
                    continue

            # Table filter
            if selected_table != "Всички":
                if str(res["table_number"]) != selected_table:
                    continue

            filtered.append(res)

        # Sort by start time ascending
        def sort_key(r):
            try:
                return datetime.strptime(r["time_slot"], "%Y-%m-%d %H:%M")
            except ValueError:
                return datetime.now(ZoneInfo("Europe/Sofia"))
        filtered.sort(key=sort_key)

        for res in filtered:
            if res["status"] == "Reserved":
                display_status = "Резервирана"
            elif res["status"] == "Cancelled":
                display_status = "Отменена"
            else:
                display_status = res["status"]

            waiter_name = self.get_waiter_name(res["waiter_id"])
            additional_info = res["additional_info"] or ""
            phone = res["phone_number"] or ""

            # FIX: Store reservation ID as TreeView iid for reliable identification
            self.res_tree.insert(
                "",
                "end",
                iid=str(res["id"]),  # Use database ID as item identifier
                values=(
                    res["table_number"],
                    res["time_slot"],
                    res["customer_name"],
                    additional_info,
                    phone,
                    waiter_name,
                    display_status
                )
            )

    def get_waiter_name(self, waiter_id):
        if waiter_id is None:
            return ""
        waiters = self.db.get_waiters()
        for w in waiters:
            if w["id"] == waiter_id:
                return w["name"]
        return ""

    # ----------------------------------------------------------------
    # CREATE Reservation (Bulgarian months)
    # ----------------------------------------------------------------
    def open_create_reservation_window(self):
        win = ttk.Toplevel(self.window)
        win.title("Създай резервация")
        win.grab_set()

        ttk.Label(win, text="Маса:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        table_entry = ttk.Entry(win)
        table_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Клиент:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        customer_entry = ttk.Entry(win)
        customer_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        phone_entry = ttk.Entry(win)
        phone_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(win, text="Допълнителна информация:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        info_text = tk.Text(win, width=40, height=5)
        info_text.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(win, text="Сервитьор:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        waiter_names = [w["name"] for w in self.db.get_waiters()]
        waiter_var = tk.StringVar()
        waiter_combo = ttk.Combobox(win, textvariable=waiter_var, values=waiter_names, state="readonly")
        waiter_combo.grid(row=4, column=1, padx=5, pady=5)
        if waiter_names:
            waiter_combo.current(0)

        # Default times
        current_time = datetime.now(ZoneInfo("Europe/Sofia"))
        default_time = current_time + timedelta(hours=1)
        default_year = default_time.year
        default_month = default_time.month
        default_day = default_time.day
        default_hour = default_time.hour
        default_minute = "00"

        ttk.Label(win, text="Година:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        year_values = [str(default_year), str(default_year + 1)]
        year_var = tk.StringVar(value=str(default_year))
        year_combo = ttk.Combobox(win, textvariable=year_var, values=year_values, state="readonly")
        year_combo.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(win, text="Месец:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        bulgarian_months = BULGARIAN_MONTHS
        default_month_name = bulgarian_months[default_month - 1]
        month_var = tk.StringVar(value=default_month_name)
        month_combo = ttk.Combobox(win, textvariable=month_var, values=bulgarian_months, state="readonly", width=12)
        month_combo.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(win, text="Ден:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        day_values = [str(d) for d in range(1, 32)]
        day_var = tk.StringVar(value=str(default_day))
        day_combo = ttk.Combobox(win, textvariable=day_var, values=day_values, state="readonly")
        day_combo.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(win, text="Час (0-23):").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        hour_values = [f"{h:02d}" for h in range(24)]
        hour_var = tk.StringVar(value=f"{default_hour:02d}")
        hour_combo = ttk.Combobox(win, textvariable=hour_var, values=hour_values, state="readonly")
        hour_combo.grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(win, text="Минути:").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        minute_values = ["00", "15", "30", "45"]
        minute_var = tk.StringVar(value=default_minute)
        minute_combo = ttk.Combobox(win, textvariable=minute_var, values=minute_values, state="readonly")
        minute_combo.grid(row=9, column=1, padx=5, pady=5)

        def submit():
            try:
                table_num = int(table_entry.get().strip())
                customer = customer_entry.get().strip()
                phone = phone_entry.get().strip()
                additional_info = info_text.get("1.0", "end-1c").strip()

                chosen_year = year_var.get()
                chosen_month_name = month_var.get()
                chosen_month_num = BULGARIAN_MONTH_TO_NUM.get(chosen_month_name, 1)
                chosen_day = day_var.get()
                chosen_hour = hour_var.get()
                chosen_min = minute_var.get()

                time_slot = f"{chosen_year}-{chosen_month_num:02d}-{int(chosen_day):02d} {chosen_hour}:{chosen_min}"

                waiter_name = waiter_var.get()
                waiter_id = None
                for w in self.db.get_waiters():
                    if w["name"] == waiter_name:
                        waiter_id = w["id"]
                        break

                if not (table_num and customer and phone and waiter_id):
                    messagebox.showerror("Грешка", "Моля, попълнете всички задължителни полета.")
                    return

                success = self.db.create_reservation(
                    table_number=table_num,
                    time_slot=time_slot,
                    customer_name=customer,
                    phone_number=phone,
                    additional_info=additional_info,
                    waiter_id=waiter_id
                )
                if not success:
                    messagebox.showerror("Конфликт в резервациите",
                                         "Тази маса вече е резервирана в рамките на 1ч30м от зададения час.")
                else:
                    messagebox.showinfo("Успешно", "Резервацията е създадена успешно.")
                    win.destroy()
                    self.refresh_reservations_tree()
                    self.refresh_table_layout()

            except ValueError:
                messagebox.showerror("Грешка", "Номерът на масата трябва да е цяло число.")
            except Exception as e:
                messagebox.showerror("Грешка", str(e))

        ttk.Button(win, text="Потвърди", command=submit).grid(row=10, column=0, columnspan=2, pady=10)

    # ----------------------------------------------------------------
    # MODIFY Reservation (Bulgarian months)
    # ----------------------------------------------------------------
    def open_modify_reservation_window(self):
        selected = self.res_tree.focus()
        if not selected:
            messagebox.showwarning("Внимание", "Моля, изберете резервация за промяна.")
            return

        # FIX: Use TreeView iid (which is the database ID) instead of column values
        res_id = int(selected)

        # Fetch the current reservation details from DB
        reservations = self.db.get_reservations()
        current = None
        for r in reservations:
            if r["id"] == res_id:
                current = r
                break
        if not current:
            messagebox.showerror("Грешка", "Резервацията не е намерена.")
            return

        try:
            dt = datetime.strptime(current["time_slot"], "%Y-%m-%d %H:%M")
            curr_year  = dt.year
            curr_month = dt.month
            curr_day   = dt.day
            curr_hour  = dt.hour
            curr_min   = dt.minute
        except (ValueError, TypeError):
            dt = None
            curr_year  = 2025
            curr_month = 1
            curr_day   = 1
            curr_hour  = 0
            curr_min   = 0

        win = ttk.Toplevel(self.window)
        win.title("Промени резервация")
        win.grab_set()

        ttk.Label(win, text="Маса:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        table_entry = ttk.Entry(win)
        table_entry.insert(0, current["table_number"])
        table_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Клиент:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        customer_entry = ttk.Entry(win)
        customer_entry.insert(0, current["customer_name"])
        customer_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        phone_entry = ttk.Entry(win)
        phone_entry.insert(0, current["phone_number"] or "")
        phone_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(win, text="Допълнителна информация:").grid(row=3, column=0, padx=5, pady=5, sticky="nw")
        info_text = tk.Text(win, width=40, height=5)
        info_text.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        info_text.insert("1.0", current["additional_info"] or "")

        ttk.Label(win, text="Сервитьор:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        waiter_names = [w["name"] for w in self.db.get_waiters()]
        waiter_var = tk.StringVar()
        waiter_combo = ttk.Combobox(win, textvariable=waiter_var, values=waiter_names, state="readonly")
        waiter_combo.grid(row=4, column=1, padx=5, pady=5)

        current_waiter = self.get_waiter_name(current["waiter_id"])
        if current_waiter in waiter_names:
            waiter_combo.set(current_waiter)
        elif waiter_names:
            waiter_combo.current(0)

        ttk.Label(win, text="Статус:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        status_var = tk.StringVar()
        db_status = current["status"]
        if db_status == "Reserved":
            default_status_bg = "Резервирана"
        elif db_status == "Cancelled":
            default_status_bg = "Отменена"
        else:
            default_status_bg = db_status
        status_values = ["Резервирана", "Отменена"]
        status_combo = ttk.Combobox(win, textvariable=status_var, values=status_values, state="readonly")
        status_combo.grid(row=5, column=1, padx=5, pady=5)
        status_combo.set(default_status_bg)

        ttk.Label(win, text="Година:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        year_values = [str(curr_year), str(curr_year + 1)]
        year_var = tk.StringVar(value=str(curr_year))
        year_combo = ttk.Combobox(win, textvariable=year_var, values=year_values, state="readonly")
        year_combo.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(win, text="Месец:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
        if 1 <= curr_month <= 12:
            curr_month_name = BULGARIAN_MONTHS[curr_month - 1]
        else:
            curr_month_name = "Януари"
        month_var = tk.StringVar(value=curr_month_name)
        month_combo = ttk.Combobox(win, textvariable=month_var, values=BULGARIAN_MONTHS, state="readonly", width=12)
        month_combo.grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(win, text="Ден:").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        day_values = [str(d) for d in range(1, 32)]
        day_var = tk.StringVar(value=str(curr_day))
        day_combo = ttk.Combobox(win, textvariable=day_var, values=day_values, state="readonly")
        day_combo.grid(row=8, column=1, padx=5, pady=5)

        ttk.Label(win, text="Час (0-23):").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        hour_values = [f"{h:02d}" for h in range(24)]
        hour_var = tk.StringVar(value=f"{curr_hour:02d}")
        hour_combo = ttk.Combobox(win, textvariable=hour_var, values=hour_values, state="readonly")
        hour_combo.grid(row=9, column=1, padx=5, pady=5)

        ttk.Label(win, text="Минути:").grid(row=10, column=0, padx=5, pady=5, sticky="w")
        minute_values = ["00", "15", "30", "45"]
        minute_str = f"{curr_min:02d}"
        if minute_str not in minute_values:
            minute_str = "00"
        minute_var = tk.StringVar(value=minute_str)
        minute_combo = ttk.Combobox(win, textvariable=minute_var, values=minute_values, state="readonly")
        minute_combo.grid(row=10, column=1, padx=5, pady=5)

        def submit_modify():
            try:
                table_num = int(table_entry.get().strip())
                customer = customer_entry.get().strip()
                phone = phone_entry.get().strip()
                additional_info = info_text.get("1.0", "end-1c").strip()

                chosen_year  = year_var.get()
                chosen_month_name = month_var.get()
                chosen_month_num = BULGARIAN_MONTH_TO_NUM.get(chosen_month_name, 1)
                chosen_day   = day_var.get()
                chosen_hour  = hour_var.get()
                chosen_min   = minute_var.get()
                time_slot = f"{chosen_year}-{chosen_month_num:02d}-{int(chosen_day):02d} {chosen_hour}:{chosen_min}"

                waiter_name = waiter_var.get()
                waiter_id = None
                for w in self.db.get_waiters():
                    if w["name"] == waiter_name:
                        waiter_id = w["id"]
                        break

                chosen_status_bg = status_var.get()
                if chosen_status_bg == "Резервирана":
                    chosen_status_db = "Reserved"
                else:
                    chosen_status_db = "Cancelled"

                if not (table_num and customer and phone and waiter_id and time_slot):
                    messagebox.showerror("Грешка", "Всички задължителни полета трябва да са попълнени.")
                    return

                success = self.db.update_reservation(
                    reservation_id=res_id,
                    table_number=table_num,
                    time_slot=time_slot,
                    customer_name=customer,
                    phone_number=phone,
                    additional_info=additional_info,
                    waiter_id=waiter_id,
                    status=chosen_status_db
                )
                if not success:
                    messagebox.showerror("Конфликт в резервациите",
                                         "Налична е друга резервация в рамките на 1ч30м от зададения час.")
                else:
                    messagebox.showinfo("Успешно", "Резервацията е променена успешно.")
                    win.destroy()
                    self.refresh_reservations_tree()
                    self.refresh_table_layout()

            except ValueError:
                messagebox.showerror("Грешка", "Номерът на масата трябва да е цяло число.")
            except Exception as e:
                messagebox.showerror("Грешка", str(e))

        ttk.Button(win, text="Потвърди", command=submit_modify).grid(row=11, column=0, columnspan=2, pady=10)

    def delete_reservation(self):
        selected = self.res_tree.focus()
        if not selected:
            messagebox.showwarning("Внимание", "Моля, изберете резервация за изтриване.")
            return
        
        # FIX: Use TreeView iid (which is the database ID) instead of column values
        res_id = int(selected)
        
        confirm = messagebox.askyesno("Потвърди", "Наистина ли искате да отмените тази резервация?")
        if confirm:
            self.db.delete_reservation(res_id)
            messagebox.showinfo("Изтрито", "Резервацията е отменена.")
            self.refresh_reservations_tree()
            self.refresh_table_layout()  # Also refresh table layout after deletion

    # ----------------------------------------------------------------
    # Table Layout Tab
    # ----------------------------------------------------------------
    def create_table_layout_tab(self):
        self.table_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.table_tab, text="Разпределение на масите")

        # Filter context label (shows current date and time selection)
        self.table_filter_context_frame = ttk.Frame(self.table_tab)
        self.table_filter_context_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ttk.Label(
            self.table_filter_context_frame,
            text="Дата и час:",
            font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(0, 5))
        
        self.table_filter_label = ttk.Label(
            self.table_filter_context_frame,
            text="",
            font=("TkDefaultFont", 9)
        )
        self.table_filter_label.pack(side="left")
        
        # Legend for table colors
        legend_frame = ttk.Frame(self.table_tab)
        legend_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ttk.Label(
            legend_frame,
            text="Легенда:",
            font=("TkDefaultFont", 9, "bold")
        ).pack(side="left", padx=(0, 10))
        
        # Red indicator - currently occupied
        red_indicator = ttk.Label(legend_frame, text="● Заета сега", foreground="#dc3545")
        red_indicator.pack(side="left", padx=(0, 10))
        
        # Orange indicator - soon occupied (within 30 minutes)
        orange_indicator = ttk.Label(legend_frame, text="● Заета след 30 мин", foreground="#fd7e14")
        orange_indicator.pack(side="left", padx=(0, 10))
        
        # Green indicator - available
        green_indicator = ttk.Label(legend_frame, text="● Свободна", foreground="#28a745")
        green_indicator.pack(side="left")

        # Table buttons container
        tables_frame = ttk.Frame(self.table_tab)
        tables_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 50 tables with labels underneath for "soon occupied" indicator
        self.table_buttons = {}
        self.table_labels = {}  # Labels for "soon occupied" messages
        for i in range(50):
            table_num = i + 1
            
            # Container for each table (button + label)
            table_container = ttk.Frame(tables_frame)
            table_container.grid(row=i // 5, column=i % 5, padx=10, pady=10)
            
            # Table button
            btn = ttk.Button(table_container, text=f"Маса {table_num}", width=15)
            btn.pack()
            self.table_buttons[table_num] = btn
            
            # Label for "soon occupied" message (hidden by default)
            lbl = ttk.Label(
                table_container, 
                text="", 
                font=("TkDefaultFont", 7),
                foreground="#fd7e14"
            )
            lbl.pack()
            self.table_labels[table_num] = lbl
        
        self.update_table_layout_filter_label()
        self.refresh_table_layout()

    def refresh_table_layout(self):
        """
        Refresh table layout with time-aware occupancy logic.
        
        Shows:
        - Red: Currently occupied at selected time
        - Orange: Will be occupied within 30 minutes ("soon occupied")
        - Green: Available
        """
        reservations = self.db.get_reservations()
        
        # Use consistent timezone for datetime comparisons
        now = datetime.now(ZoneInfo("Europe/Sofia"))
        
        # Get selected datetime (if time is specified)
        selected_dt = self.get_selected_datetime()
        
        # Tracking dictionaries
        occupied_tables = {}  # Currently occupied at selected time
        soon_occupied_tables = {}  # Will be occupied within 30 minutes
        
        for res in reservations:
            try:
                res_start = datetime.strptime(res["time_slot"], "%Y-%m-%d %H:%M")
                res_end = res_start + timedelta(minutes=self.RESERVATION_DURATION_MINUTES)
            except ValueError:
                continue
            
            # Only consider "Reserved" status
            if res["status"] != "Reserved":
                continue
            
            table_num = res["table_number"]
            
            # Time-aware logic
            if selected_dt is not None:
                # Specific time selected - check occupancy at that exact time
                selected_naive = selected_dt.replace(tzinfo=None)
                
                # Check if table is occupied at selected time
                # Occupied if: res_start <= selected_time < res_end
                is_occupied = res_start <= selected_naive < res_end
                
                if is_occupied:
                    occupied_tables[table_num] = res_start
                else:
                    # Check if "soon occupied" (starts within next 30 minutes)
                    # Soon occupied if: selected_time < res_start <= selected_time + 30 min
                    soon_threshold = selected_naive + timedelta(minutes=30)
                    
                    if selected_naive < res_start <= soon_threshold:
                        # Only mark as "soon occupied" if not already occupied
                        if table_num not in occupied_tables:
                            soon_occupied_tables[table_num] = res_start
            else:
                # No specific time selected - fall back to date-based logic
                selected_month_bg = self.month_filter_var.get()
                selected_day_str = self.day_filter_var.get()
                
                # Apply month filter
                if selected_month_bg != "Всички":
                    numeric_month = BULGARIAN_MONTH_TO_NUM.get(selected_month_bg, None)
                    if numeric_month and res_start.month != numeric_month:
                        continue
                
                # Apply day filter
                if selected_day_str != "Всички":
                    if res_start.day != int(selected_day_str):
                        continue
                
                # For "Всички" dates, only show future reservations
                if selected_month_bg == "Всички" and selected_day_str == "Всички":
                    if res_start >= now:
                        occupied_tables[table_num] = res_start
                else:
                    # For specific date, show all reservations
                    occupied_tables[table_num] = res_start
        
        # Update button colors and labels
        for table_num in self.table_buttons.keys():
            btn = self.table_buttons[table_num]
            lbl = self.table_labels[table_num]
            
            if table_num in occupied_tables:
                # Currently occupied - red
                btn.configure(style="danger.TButton")
                lbl.config(text="")
            elif table_num in soon_occupied_tables:
                # Soon occupied - orange
                btn.configure(style="warning.TButton")
                # Show reservation start time
                res_time = soon_occupied_tables[table_num]
                lbl.config(text=f"Заета в {res_time.strftime('%H:%M')}")
            else:
                # Available - green
                btn.configure(style="success.TButton")
                lbl.config(text="")

    def update_table_layout_filter_label(self):
        """
        Update the filter context label in the table layout tab.
        Shows which date and time is currently selected for viewing.
        """
        selected_month_bg = self.month_filter_var.get()
        selected_day_str = self.day_filter_var.get()
        selected_hour_str = self.hour_filter_var.get()
        selected_minute_str = self.minute_filter_var.get()
        
        # Build date part
        if selected_month_bg == "Всички" and selected_day_str == "Всички":
            date_text = "Всички бъдещи резервации"
        elif selected_month_bg != "Всички" and selected_day_str == "Всички":
            date_text = f"{selected_month_bg} (всички дни)"
        elif selected_month_bg == "Всички" and selected_day_str != "Всички":
            date_text = f"Ден {selected_day_str} (всички месеци)"
        else:
            date_text = f"{selected_day_str} {selected_month_bg}"
        
        # Build time part
        if selected_hour_str != "Всички" and selected_minute_str != "Всички":
            time_text = f" в {selected_hour_str}:{selected_minute_str}"
        elif selected_hour_str != "Всички":
            time_text = f" час {selected_hour_str}"
        else:
            time_text = ""
        
        filter_text = date_text + time_text
        self.table_filter_label.config(text=filter_text)

    # ----------------------------------------------------------------
    # Admin Tab with single-window login
    # ----------------------------------------------------------------
    def create_admin_tab(self):
        """When user clicks 'Администраторски панел', they see a login form.
           If login fails or user cancels, switch to 'Резервации' tab.
           If success, show sub-tabs: Waiter Management, Reports, Backup/Restore, plus a Logout option.
        """
        self.admin_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_tab, text="Администраторски панел")

        # A frame for the login form (username/password)
        self.admin_login_frame = ttk.Frame(self.admin_tab)
        self.admin_login_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(self.admin_login_frame, text="Потребителско име:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.admin_user_entry = ttk.Entry(self.admin_login_frame)
        self.admin_user_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.admin_login_frame, text="Парола:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.admin_pass_entry = ttk.Entry(self.admin_login_frame, show="*")
        self.admin_pass_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self.admin_login_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Вход", command=self.attempt_admin_login).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Отказ", command=self.cancel_admin_login).pack(side="left", padx=5)

        self.admin_sub_notebook = None  # created only after success

    def attempt_admin_login(self):
        username = self.admin_user_entry.get().strip()
        password = self.admin_pass_entry.get().strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            messagebox.showinfo("Успех", "Добре дошли, Администратор!")
            self.admin_logged_in = True
            self.admin_login_frame.pack_forget()
            self.create_admin_sub_notebook()
        else:
            messagebox.showerror("Грешка", "Невалидни администраторски данни.")
            self.notebook.select(self.res_tab)

    def cancel_admin_login(self):
        """If user clicks cancel, go back to Reservations tab."""
        self.notebook.select(self.res_tab)

    def create_admin_sub_notebook(self):
        """Create the sub-tabs for Waiter Management, Reports, Backup/Restore, plus a Logout button."""
        self.admin_sub_notebook = ttk.Notebook(self.admin_tab)
        self.admin_sub_notebook.pack(fill="both", expand=True)

        # 1) Waiter Management tab
        self.waiter_tab = ttk.Frame(self.admin_sub_notebook)
        self.admin_sub_notebook.add(self.waiter_tab, text="Управление на сервитьори")

        ttk.Label(self.waiter_tab, text="Управление на сервитьори:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.waiters_listbox = tk.Listbox(self.waiter_tab, height=5)
        self.waiters_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        btn_frame = ttk.Frame(self.waiter_tab)
        btn_frame.grid(row=2, column=0, pady=10, sticky="w")
        ttk.Button(btn_frame, text="Добави сервитьор", command=self.add_waiter).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Изтрий сервитьор", command=self.remove_waiter).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Промени сервитьор", command=self.modify_waiter).pack(side="left", padx=5)

        ttk.Label(self.waiter_tab, text="История на смените:").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.shifts_listbox = tk.Listbox(self.waiter_tab, height=10, width=40)
        self.shifts_listbox.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")

        self.waiter_tab.grid_rowconfigure(1, weight=1)
        self.waiter_tab.grid_columnconfigure(1, weight=1)

        self.refresh_waiters_listbox()
        self.refresh_shifts_listbox()

        # 2) Reports tab
        self.reports_tab = ttk.Frame(self.admin_sub_notebook)
        self.admin_sub_notebook.add(self.reports_tab, text="Отчети")

        btn_frame2 = ttk.Frame(self.reports_tab)
        btn_frame2.pack(pady=10)
        ttk.Button(btn_frame2, text="Дневен отчет", command=lambda: self.generate_report("daily")).pack(side="left", padx=5)
        ttk.Button(btn_frame2, text="Седмичен отчет", command=lambda: self.generate_report("weekly")).pack(side="left", padx=5)
        ttk.Button(btn_frame2, text="Месечен отчет", command=lambda: self.generate_report("monthly")).pack(side="left", padx=5)

        self.report_canvas_frame = ttk.Frame(self.reports_tab)
        self.report_canvas_frame.pack(fill="both", expand=True)

        # 3) Backup/Restore tab
        self.backup_tab = ttk.Frame(self.admin_sub_notebook)
        self.admin_sub_notebook.add(self.backup_tab, text="Архивиране / Възстановяване")

        ttk.Button(self.backup_tab, text="Архивирай базата", command=self.backup_db).pack(pady=10)
        ttk.Button(self.backup_tab, text="Възстанови базата", command=self.restore_db).pack(pady=10)

        # 4) Logout button
        logout_frame = ttk.Frame(self.admin_tab)
        logout_frame.pack(pady=5, anchor="e")  # right side
        ttk.Button(logout_frame, text="Излез", command=self.logout_admin).pack()

    # Logout logic
    def logout_admin(self):
        """Log out the admin user, remove sub-notebook, show the login form again."""
        self.admin_logged_in = False
        if self.admin_sub_notebook:
            self.admin_sub_notebook.destroy()
            self.admin_sub_notebook = None

        # Re-show the login frame
        self.admin_login_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Clear username/password
        self.admin_user_entry.delete(0, tk.END)
        self.admin_pass_entry.delete(0, tk.END)

    # Waiter management
    def refresh_waiters_listbox(self):
        if not hasattr(self, "waiters_listbox"):
            return
        self.waiters_listbox.delete(0, tk.END)
        for waiter in self.db.get_waiters():
            self.waiters_listbox.insert(tk.END, f"ID {waiter['id']}: {waiter['name']}")

    def refresh_shifts_listbox(self):
        if not hasattr(self, "shifts_listbox"):
            return
        self.shifts_listbox.delete(0, tk.END)
        shifts = self.db.get_shifts()
        for shift in shifts:
            waiter_name = self.get_waiter_name(shift["waiter_id"])
            self.shifts_listbox.insert(tk.END, f"{waiter_name} в {shift['shift_date']}")

    def add_waiter(self):
        name = simpledialog.askstring("Добави сервитьор", "Име на новия сервитьор:", parent=self.window)
        if name:
            self.db.add_waiter(name)
            self.refresh_waiters_listbox()
            messagebox.showinfo("Успешно", f"Сервитьор '{name}' е добавен.")

    def remove_waiter(self):
        selection = self.waiters_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Моля, изберете сервитьор за изтриване.")
            return
        index = selection[0]
        item = self.waiters_listbox.get(index)
        waiter_id = int(item.split(":")[0].replace("ID", "").strip())
        self.db.remove_waiter(waiter_id)
        self.refresh_waiters_listbox()
        messagebox.showinfo("Успешно", "Сервитьорът е изтрит.")

    def modify_waiter(self):
        selection = self.waiters_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Моля, изберете сервитьор за промяна.")
            return
        index = selection[0]
        item = self.waiters_listbox.get(index)
        waiter_id = int(item.split(":")[0].replace("ID", "").strip())
        new_name = simpledialog.askstring("Промени сервитьор", "Ново име на сервитьора:", parent=self.window)
        if new_name:
            self.db.update_waiter(waiter_id, new_name)
            self.refresh_waiters_listbox()
            messagebox.showinfo("Успешно", "Името на сервитьора е променено.")

    # ----------------------------------------------------------------
    # Reports (in Admin Panel)
    # ----------------------------------------------------------------
    def generate_report(self, period):
        data = self.db.generate_report(period)
        # Show all 50 tables, even if zero reservations
        counts = {}
        for i in range(1, 51):
            counts[i] = 0
        for res in data:
            table = res["table_number"]
            if 1 <= table <= 50:
                counts[table] += 1

        fig, ax = plt.subplots(figsize=(5, 4))
        tables = list(counts.keys())
        res_counts = list(counts.values())
        ax.bar(tables, res_counts, color='skyblue')
        ax.set_xlabel("Маса")
        ax.set_ylabel("Брой резервации")
        ax.set_title(f"Отчет: {period}")

        for widget in self.report_canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.report_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ----------------------------------------------------------------
    # Backup/Restore (in Admin Panel)
    # ----------------------------------------------------------------
    def backup_db(self):
        backup_file = self.db.backup_database()
        messagebox.showinfo("Архивиране", f"Базата е архивирана в {backup_file}.")

    def restore_db(self):
        confirm = messagebox.askyesno("Възстановяване", "Това ще изтрие текущата база. Сигурни ли сте?")
        if confirm:
            self.db.restore_database()
            messagebox.showinfo("Възстановяване", "Базата е възстановена от архив.")
            self.refresh_reservations_tree()
            self.refresh_table_layout()
            self.refresh_waiters_listbox()
            self.refresh_shifts_listbox()
