import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

import uuid
from pynput import keyboard
from time import perf_counter as timestamp

# =====================
# 1. Load dataset
# =====================
csv_file = "keystroke_dataset.csv"
data = pd.read_csv(csv_file)

X = data[["hold_time", "latency_time", "flight_time", "wpm"]]
y = data["user_id"]

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

print("✅ Model trained successfully")
print("Accuracy on test set:", accuracy_score(y_test, rf_model.predict(X_test)))
print("\nClassification Report:\n", classification_report(y_test, rf_model.predict(X_test), target_names=encoder.classes_))

# =====================
# 2. Capture new typing data
# =====================
pangram = "the quick brown fox jumps over the lazy dog"
print(f"\nType the following pangram exactly:\n\n>>> {pangram}\n")

pressed_keys = {}
data_new = []
typed_chars = []  # <-- new: store typed characters
prev_key_down_time = None
prev_key_up_time = None
start_time = None
wpm = None
event_index = 0

def is_valid_char(key):
    return hasattr(key, 'char') and key.char is not None and len(key.char) == 1

def on_press(key):
    global prev_key_down_time, start_time, event_index
    try:
        if is_valid_char(key):
            if start_time is None:
                start_time = timestamp()
            char = key.char.lower()
            key_down_time = timestamp()
            latency_time = key_down_time - prev_key_down_time if prev_key_down_time else 0
            pressed_keys[char] = {
                "char": char,
                "key_down_time": key_down_time,
                "latency_time": latency_time,
                "event_index": event_index,
            }
            prev_key_down_time = key_down_time
            event_index += 1
    except AttributeError:
        pass

def on_release(key):
    global prev_key_up_time, wpm, typed_chars
    try:
        if is_valid_char(key):
            char = key.char.lower()
            key_up_time = timestamp()
            if char in pressed_keys:
                entry = pressed_keys.pop(char)
                hold_time = key_up_time - entry["key_down_time"]
                flight_time = entry["key_down_time"] - prev_key_up_time if prev_key_up_time else 0

                data_new.append({
                    "hold_time": round(hold_time, 5),
                    "latency_time": round(entry["latency_time"], 5),
                    "flight_time": round(flight_time, 5),
                })
                prev_key_up_time = key_up_time
                typed_chars.append(char)  # <-- add character to tracker

            # ✅ Check pangram completion
            if ''.join(typed_chars) == pangram.replace(" ", ""):
                elapsed_minutes = (key_up_time - start_time) / 60
                total_chars = len(pangram)
                wpm = round((total_chars / 5) / elapsed_minutes, 2)
                for entry in data_new:
                    entry["wpm"] = wpm
                print(f"\n✅ Pangram typed successfully. WPM: {wpm}")
                return False  # <-- stop listener
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# =====================
# 3. Prediction
# =====================
if data_new:
    # Average features over session (like dataset rows)
    avg_features = {
        "hold_time": sum(d["hold_time"] for d in data_new) / len(data_new),
        "latency_time": sum(d["latency_time"] for d in data_new) / len(data_new),
        "flight_time": sum(d["flight_time"] for d in data_new) / len(data_new),
        "wpm": data_new[0]["wpm"]
    }

    new_input = [[avg_features["hold_time"], avg_features["latency_time"], avg_features["flight_time"], avg_features["wpm"]]]
    pred_user = rf_model.predict(new_input)
    predicted_user = encoder.inverse_transform(pred_user)

    print("\n🎯 Predicted User:", predicted_user[0])
    actual_user = input("Enter the actual user ID who typed: ")
    if actual_user == predicted_user[0]:
        print("✅ Verification Successful! User matches.")
    else:
        print("❌ Verification Failed! Predicted:", predicted_user[0], "but actual:", actual_user)
else:
    print("⚠️ No data captured.")
