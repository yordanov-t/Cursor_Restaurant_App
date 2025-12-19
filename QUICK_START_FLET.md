# 🚀 Quick Start - Flet UI

## Installation

```bash
# Install Flet (if not already installed)
pip install flet
```

## Running the App

### Modern Flet UI (Default)
```bash
python main_app.py
```

### Legacy Tkinter UI (Fallback)
```bash
python main_app.py --legacy
```

---

## What's New in Flet UI?

### ✨ Modern Professional Design
- Dark theme by default
- Clean card-based layout
- Smooth animations
- Responsive grid layout

### 🎯 Same Functionality
- All filters (date + time)
- Reservations list
- Table layout visualization
- Admin panel

### 🔄 Improved Architecture
- UI-agnostic core services
- Centralized datetime logic
- Shared filter context
- Better code organization

---

## Quick Tour

### 1. Reservations Screen
**Features:**
- Filter by month, day, hour (00-23), minute (00/15/30/45)
- Status filter (Reserved/Cancelled)
- Table filter (1-50)
- Delete reservations (click trash icon)

**Time-Aware Display:**
- Shows ongoing reservations at selected time
- Shows future reservations
- Sorted by start time

### 2. Table Layout Screen
**Visual States:**
- 🔴 Red = Currently occupied
- 🟠 Orange = Will be occupied within 30 min
- 🟢 Green = Available

**Features:**
- Real-time occupancy at selected time
- "Заета в HH:MM" labels for soon-occupied tables
- 50-table grid (10×5 layout)

### 3. Admin Panel
**Login:**
- Username: `admin`
- Password: `password`

**Features:**
- Waiter management (add/delete)
- Auto-logout on tab change
- Reports (coming soon)
- Backup/restore (coming soon)

---

## Testing Checklist

### Quick Verification (3 minutes)

1. **Launch**
   ```bash
   python main_app.py
   ```
   ✅ Flet window opens with dark theme

2. **Filters**
   - Set time to current hour
   - Check reservations list updates
   ✅ Filters work

3. **Table Layout**
   - Click "Разпределение на масите"
   - Check table colors
   ✅ Tables show states

4. **Admin**
   - Navigate to Admin tab
   - Login with admin/password
   ✅ Admin access granted

---

## Folder Structure

```
Cursor_Restaurant_App/
├── core/                    # Business logic (UI-agnostic)
│   ├── time_utils.py
│   ├── reservation_service.py
│   └── table_layout_service.py
├── ui_flet/                 # Flet UI screens
│   ├── reservations_screen.py
│   ├── table_layout_screen.py
│   └── admin_screen.py
├── flet_app.py             # Flet entry point
├── legacy_tk_ui.py         # Tkinter backup
├── main_app.py             # Main entry (UI selector)
├── db.py                   # Database layer
└── restaurant.db           # SQLite database
```

---

## Key Improvements

### Before (Tkinter)
- ⚠️ Monolithic 1170-line file
- ⚠️ UI tightly coupled to business logic
- ⚠️ Hard to test

### After (Flet)
- ✅ Core services (UI-agnostic)
- ✅ Modular screen components
- ✅ Testable business logic
- ✅ Modern, professional UI
- ✅ Legacy fallback preserved

---

## Troubleshooting

### Issue: "Module 'flet' not found"
**Solution:**
```bash
pip install flet
```

### Issue: Flet window doesn't open
**Solution:**
1. Check Python version (need 3.9+)
2. Try legacy UI: `python main_app.py --legacy`
3. Check terminal for error messages

### Issue: No reservations showing
**Solution:**
1. Check filter settings (set to "Всички" to see all)
2. Verify database has data
3. Run legacy UI to confirm data exists

### Issue: Want old UI back
**Solution:**
```bash
python main_app.py --legacy
```

---

## 📞 Support

**Documentation:**
- `FLET_MIGRATION_GUIDE.md` - Full technical guide
- `TIME_FILTER_IMPLEMENTATION.md` - Time filtering details
- `BUG_FIXES_SUMMARY.md` - Bug fix history

**Testing:**
- See `FLET_MIGRATION_GUIDE.md` for 10 detailed test cases

---

## 🎯 Current Status

**Working Features:**
- ✅ Filters (date + time)
- ✅ Reservations list (time-aware)
- ✅ Delete reservations
- ✅ Table layout (with states)
- ✅ Admin login
- ✅ Waiter management

**Coming Soon:**
- 🚧 Create reservation form
- 🚧 Edit reservation form
- 🚧 Reports with charts
- 🚧 Backup/restore dialogs

**Note:** Core services for create/edit are ready. Only UI forms need to be added.

---

**Enjoy the modern UI! 🎉**

