from models.productivity_model import train_model, predict_productivity, find_best_hour


# -----------------------------
# TRAIN MODEL
# -----------------------------
model, le = train_model()


# -----------------------------
# TEST INPUT
# -----------------------------
input_data = [21, 1, 70, 1, 1, 1, 0, 35.0]


# -----------------------------
# PREDICT PRODUCTIVITY
# -----------------------------
prediction = predict_productivity(model, le, input_data)

print("🔥 Productivity:", prediction)


# -----------------------------
# FIND BEST HOUR
# -----------------------------
best_hour = find_best_hour(model, input_data)


# -----------------------------
# FORMAT TIME (AM / PM) ✅
# -----------------------------
if best_hour < 12:
    period = "AM"
else:
    period = "PM"

hour_display = best_hour % 12
if hour_display == 0:
    hour_display = 12

print(f"🌟 Best study time: {hour_display} {period}")
