import csv
import time
import uuid
from pynput import keyboard
import os
from time import perf_counter as timestamp

# === CONFIGURABLE ===
pangram = "the quick brown fox jumps over the lazy dog"
csv_file = "keystroke_dataset.csv"

# === DATA STORAGE ===
data = []
pressed_keys = {}
event_index = 0
prev_key_down_time = None
prev_key_up_time = None
start_time = None
wpm = None

# === USER + SESSION INFO ===
user_id = input("Enter your user ID: ")
session_id = str(uuid.uuid4())

print(f"\nType the following pangram exactly:\n\n>>> {pangram}\n")

# === UTILITIES ===
def is_valid_char(key):
    return hasattr(key, 'char') and key.char is not None and len(key.char) == 1 or key == keyboard.Key.backspace


def on_press(key):
    global event_index, prev_key_down_time, start_time

    try:
        if is_valid_char(key):
            
            if start_time is None:
                start_time = timestamp()  # Start timer on first key press
            

            char = key.char.lower()
            key_code = ord(char)
            key_down_time = timestamp()

            latency_time = (
                key_down_time - prev_key_down_time
                if prev_key_down_time is not None else 0
            )

            # Save press info
            pressed_keys[char] = {
                "char": char,
                "key_code": key_code,
                "key_down_time": key_down_time,
                "event_index": event_index,
                "latency_time": latency_time,
            }

            prev_key_down_time = key_down_time
            event_index += 1

    except AttributeError:
        pass  # Skip special keys

def on_release(key):
    global prev_key_up_time, wpm

    try:
        if is_valid_char(key):
            char = key.char.lower()
            key_up_time = timestamp()

            if char in pressed_keys:
                entry = pressed_keys.pop(char)
                hold_time = key_up_time - entry["key_down_time"]
                flight_time = (
                    entry["key_down_time"] - prev_key_up_time
                    if prev_key_up_time is not None else 0
                )

                # Store complete feature entry
                data.append({
                    "user_id": user_id,
                    "char": char,
                    "key_code": entry["key_code"],
                    "hold_time": round(hold_time, 5),
                    "latency_time": round(entry["latency_time"], 5),
                    "flight_time": round(flight_time, 5),
                    "key_down_time": round(entry["key_down_time"], 5),
                    "key_up_time": round(key_up_time, 5),
                    "event_index": entry["event_index"],
                    "session_id": session_id,
                    "wpm": None  # Temporary, will fill later
                    #"backspace_count": count_bck 
                })

                prev_key_up_time = key_up_time

            # Check pangram completion
            typed_str = ''.join(d['char'] for d in data).replace(' ', '')
            if typed_str == pangram.replace(' ', ''):
                elapsed_minutes = (key_up_time - start_time) / 60
                total_chars = len(pangram)
                wpm = round((total_chars / 5) / elapsed_minutes, 2)

                # Update WPM for all entries in session
                for entry in data:
                    entry["wpm"] = wpm
                

                print(f"\n✅ Pangram typed successfully. Logging complete.")
                print(f"⌨️  WPM: {wpm}")
                return False  # Stop listener

    except AttributeError:
        pass

# === KEYBOARD LISTENER ===
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# === WRITE TO CSV ===
fieldnames = [
    "user_id", "char", "key_code", "hold_time", "latency_time",
    "flight_time", "key_down_time", "key_up_time", "event_index", "session_id", "wpm"
]

# Append if file exists, else write header
try:
    with open(csv_file, 'x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
except FileExistsError:
    with open(csv_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerows(data)

print(f"\n Data saved to: {csv_file}")
print("CSV file saved at:", os.path.abspath("keystroke_dataset.csv"))