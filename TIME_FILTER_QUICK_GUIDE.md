# Quick Test Guide - Time Filter Feature

## 🎯 What Was Implemented

**Time-based filtering with hour/minute selection and "soon occupied" indicators.**

Now you can:
- Select specific hour and minute (00/15/30/45)
- See which tables are occupied at that exact time
- Get warnings for tables becoming occupied within 30 minutes

---

## ⚡ Super Quick Test (3 minutes)

### Test 1: Time Filter Controls ✅
1. Open "Резервации" tab
2. **VERIFY:** See "Час:" and "Минути:" dropdowns below date filters
3. Select hour "17", minute "30"
4. **VERIFY:** Reservations list updates

### Test 2: "Soon Occupied" Indicator ✅
1. Create reservation: Table 10, today, one hour from now
2. Set filters to current time
3. Go to "Разпределение на масите"
4. **VERIFY:** Table 10 shows 🟠 orange with "Заета в HH:MM"

### Test 3: Currently Occupied ✅
1. Create reservation: Table 20, today, 30 minutes ago
2. Set filters to current time
3. "Разпределение на масите" tab
4. **VERIFY:** Table 20 shows 🔴 red (occupied, ends in 60 minutes)

---

## 🎨 Visual Indicators

### In Table Layout:

**🔴 Red = "Заета сега"**
- Table currently occupied at selected time
- Reservation overlaps the selected hour:minute

**🟠 Orange = "Заета след 30 мин"**
- Table will become occupied within next 30 minutes
- Shows reservation start time: "Заета в 17:45"

**🟢 Green = "Свободна"**
- Table available at selected time
- No reservation for 30+ minutes

---

## 🕐 Time Logic Explained

### Reservation Duration: 90 minutes (1h30m)

**Example at 17:30:**

| Reservation Start | Status at 17:30 | Color | Why? |
|-------------------|-----------------|-------|------|
| 16:00 | Ended | 🟢 | Ended at 17:30 (not shown as ongoing) |
| 16:30 | Occupied | 🔴 | Ends at 18:00 (still 30 min left) |
| 17:00 | Occupied | 🔴 | Ends at 18:30 (still 60 min left) |
| 17:30 | Occupied | 🔴 | Just started (90 min ahead) |
| 17:45 | Soon | 🟠 | Starts in 15 min (within 30 min) |
| 18:00 | Soon | 🟠 | Starts in 30 min (exactly threshold) |
| 18:01 | Available | 🟢 | Starts in 31 min (too far) |
| 19:00 | Available | 🟢 | Starts in 90 min (too far) |

---

## 📋 Detailed Test Scenarios

### Scenario 1: Ongoing Reservations (5 minutes)

**Setup:**
```
Create reservations for today:
- Table 1: 16:30
- Table 2: 17:00
- Table 3: 17:30
- Table 4: 19:00
- Table 5: 15:00
```

**Test at 17:30:**
1. Set filters: Today, 17:30
2. "Резервации" tab → **VERIFY:** Shows tables 1, 2, 3, 4 (NOT table 5)
3. "Разпределение на масите" → **VERIFY:**
   - Table 1: 🔴 Red (16:30, ends 18:00)
   - Table 2: 🔴 Red (17:00, ends 18:30)
   - Table 3: 🔴 Red (17:30, ends 19:00)
   - Table 4: 🟢 Green (19:00, not yet)
   - Table 5: 🟢 Green (15:00, already ended)

**✅ Pass:** Shows ongoing + future, correct colors

---

### Scenario 2: "Soon Occupied" Detection (5 minutes)

**Setup:**
```
Current time: 17:30
Create reservations:
- Table 10: 17:45 (15 min away)
- Table 11: 18:00 (30 min away)
- Table 12: 18:01 (31 min away)
- Table 13: 19:00 (90 min away)
```

**Test:**
1. Set filters: Today, 17:30
2. "Разпределение на масите" → **VERIFY:**
   - Table 10: 🟠 Orange + "Заета в 17:45"
   - Table 11: 🟠 Orange + "Заета в 18:00"
   - Table 12: 🟢 Green (no label)
   - Table 13: 🟢 Green (no label)

**✅ Pass:** Exactly 30-minute threshold works

---

### Scenario 3: Time Progression (10 minutes)

**Setup:** Same as Scenario 2

**Test sequence:**

**At 17:30:**
- Table 10: 🟠 "Заета в 17:45" (15 min away)
- Table 11: 🟠 "Заета в 18:00" (30 min away)

**Change to 17:45:**
- Table 10: 🔴 Red (NOW occupied!)
- Table 11: 🟠 "Заета в 18:00" (15 min away now)
- Table 12: 🟠 "Заета в 18:01" (16 min away now)

**Change to 18:00:**
- Table 10: 🔴 Red (still occupied until 19:15)
- Table 11: 🔴 Red (NOW occupied!)
- Table 12: 🔴 Red (NOW occupied!)
- Table 13: 🟢 Green (60 min away)

**✅ Pass:** Colors update correctly as time progresses

---

## 🔍 Edge Cases to Test

### Edge Case 1: Exactly 30 Minutes
- At 17:30, reservation at 18:00
- **Expected:** 🟠 Orange "soon occupied"
- **Why:** 30 minutes exactly counts as "soon"

### Edge Case 2: Just Over 30 Minutes
- At 17:30, reservation at 18:01
- **Expected:** 🟢 Green available
- **Why:** 31 minutes is NOT "soon"

### Edge Case 3: Reservation Ending
- At 18:00, reservation that started at 16:30 (ends 18:00)
- **Expected:** 🟢 Green available
- **Why:** End time is exclusive (`<` not `<=`)

### Edge Case 4: Cancelled Reservations
- Cancelled reservation at 17:30
- Status filter set to "Всички"
- **Expected in Reservations:** Shows cancelled
- **Expected in Layout:** 🟢 Green (ignored)

### Edge Case 5: No Time Selected
- Hour: "Всички", Minute: "Всички"
- **Expected:** Falls back to date-only filtering
- **Expected:** No "soon" indicators (needs specific time)

---

## 🚨 Common Issues & Solutions

### Issue: Orange indicator not showing
**Check:**
- Is specific time selected? (not "Всички")
- Is reservation within exactly 30 minutes?
- Is table NOT already occupied?

### Issue: Wrong tables showing as occupied
**Check:**
- What time is selected?
- What's the reservation duration? (always 90 min)
- Is reservation status "Reserved"? (not "Cancelled")

### Issue: "Soon" label showing wrong time
**Check:**
- Label should show reservation START time
- Format: "Заета в HH:MM"
- Language: Bulgarian

---

## 💡 Quick Tips

1. **Time is optional** - Can still use date-only filters
2. **15-minute increments** - Minutes locked to 00/15/30/45
3. **90-minute duration** - All reservations occupy table for 1h30m
4. **Status matters** - Only "Reserved" affects table layout
5. **Synchronization** - Both tabs always show same time context

---

## ✅ Success Checklist

Feature working correctly if:
- ✅ Time filters visible in both tabs
- ✅ Reservations list shows ongoing + future
- ✅ Table layout shows red for occupied
- ✅ Table layout shows orange for "soon"
- ✅ Orange label shows correct start time
- ✅ Green tables are truly available
- ✅ 30-minute threshold precise
- ✅ No cancelled reservations affect layout

**Total test time: ~5 minutes for quick verification**

---

## 🎉 What to Expect

### Before Time Filters:
- ❌ Only date-based filtering
- ❌ No time-of-day context
- ⚠️ "Is table free?" unclear

### After Time Filters:
- ✅ Select exact hour and minute
- ✅ See occupancy at specific time
- ✅ Get advance warning (30 min)
- ✅ Plan reservations better
- ✅ Avoid double bookings

**Professional restaurant management! 🎯**

