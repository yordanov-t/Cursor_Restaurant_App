# Quick Test Guide - Bug Fixes Verification

## 🎯 Critical Tests (Must Pass)

### ✅ Test 1: Modify Reservation (30 seconds)
**What was broken:** Showed "Резервацията не е намерена" error

**Quick Test:**
1. Open app → "Резервации" tab
2. Click any reservation in the list
3. Click "Промени резервация"
4. Change customer name
5. Click "Потвърди"

**✅ Pass Criteria:**
- Dialog opens with correct data
- Changes save successfully
- Tree updates immediately

---

### ✅ Test 2: Delete Reservation (30 seconds)
**What was broken:** Reported success but didn't delete correct record

**Quick Test:**
1. "Резервации" tab
2. Note table number of selected reservation (e.g., "Маса 5")
3. Click "Изтрий резервация" → Confirm
4. Look for that table number in list

**✅ Pass Criteria:**
- Status changes to "Отменена"
- Correct table number was cancelled
- Table button turns green in "Разпределение на масите"

---

### ✅ Test 3: Date Filtering (1 minute)
**What was broken:** Table layout ignored date filters

**Quick Test:**
1. Create reservation for tomorrow
2. Go to "Резервации" tab
3. Set filters to tomorrow's date
4. Go to "Разпределение на масите" tab

**✅ Pass Criteria:**
- Only tomorrow's reserved tables show as red
- Changing date filter updates table colors
- "Всички" shows all future reservations

---

## 🔍 Quick Verification Checklist

After applying fixes, verify these work:

- [ ] Can modify any reservation successfully
- [ ] Can delete any reservation (correct one is cancelled)
- [ ] Date filters affect both tabs consistently
- [ ] Table colors update when reservations change
- [ ] Multiple reservations on same table handled correctly
- [ ] Changes persist after closing/reopening app

---

## 🚨 If Something Breaks

### Symptom: "Резервацията не е намерена" still appears
**Check:** Did visualization.py update correctly?
**Look for:** Line ~270 should have `iid=str(res["id"])`

### Symptom: Wrong reservation is modified/deleted
**Check:** Lines ~424 and ~604 in visualization.py
**Should be:** `res_id = int(selected)` NOT `res_id = values[0]`

### Symptom: Table layout doesn't respect filters
**Check:** refresh_table_layout() function around line 625
**Should have:** `selected_month_bg = self.month_filter_var.get()`

---

## 📝 Test Data Setup (If Needed)

Create test reservations:
1. Today, 19:00, Table 1
2. Tomorrow, 19:00, Table 2
3. Tomorrow, 20:00, Table 3
4. Day after tomorrow, 19:00, Table 4

This gives you:
- ✅ Past/future testing
- ✅ Same table, different times
- ✅ Different tables, same time
- ✅ Multiple dates for filtering

---

## ✨ Expected Behavior Summary

| Action | Before Fix | After Fix |
|--------|------------|-----------|
| Modify reservation | ❌ Error | ✅ Works |
| Delete reservation | ⚠️ Wrong record | ✅ Correct record |
| Date filter → Table layout | ❌ Ignored | ✅ Applied |
| Timezone handling | ⚠️ Inconsistent | ✅ Consistent |

---

## 💡 Pro Tips

1. **Test with real data:** Don't delete your existing reservations
2. **Test edge cases:** Same table, multiple reservations
3. **Test persistence:** Close and reopen app
4. **Test filters:** Try "Всички" and specific dates
5. **Check table layout:** Should always match filter selection

---

## 🎉 Success Criteria

All fixes working if:
- ✅ Can modify ANY reservation without errors
- ✅ Delete removes CORRECT reservation
- ✅ Table layout matches date filter selection
- ✅ No timezone-related bugs
- ✅ All changes persist across app restarts

**Total test time: ~5 minutes**

