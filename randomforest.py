import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# =====================
# 1. Load dataset
# =====================
file_path = "keystroke_dataset.csv"  # change if needed
data = pd.read_csv(file_path)

# =====================
# 2. Select features & labels
# =====================
X = data[["hold_time", "latency_time", "flight_time", "wpm"]]
y = data["user_id"]

# Encode user names into numbers
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# =====================
# 3. Train-test split
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# =====================
# 4. Random Forest Model
# =====================
rf_model = RandomForestClassifier(
    n_estimators=100,   # number of decision trees
    random_state=42,
    max_depth=None,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)

# =====================
# 5. Evaluate
# =====================
y_pred = rf_model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=encoder.classes_))

# =====================
# 6. Predict new input (example)
# =====================
# Replace with real typing features [hold_time, latency_time, flight_time, wpm]
new_input = [[0.07, 0.20, 0.15, 55.0]]

pred_user = rf_model.predict(new_input)
predicted_user = encoder.inverse_transform(pred_user)

print("Predicted User:", predicted_user[0])
