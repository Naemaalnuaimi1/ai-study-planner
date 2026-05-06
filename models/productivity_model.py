import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


# -----------------------------
# LOAD + TRAIN MODEL
# -----------------------------
def train_model():

    # Load dataset
    df = pd.read_csv("data/Book3.csv")

    # Encode target (Low, Medium, High → numbers)
    le = LabelEncoder()
    df['productivity_encoded'] = le.fit_transform(df['productivity_level'])

    # Features & target
    X = df.drop(['productivity_level', 'productivity_encoded'], axis=1)
    y = df['productivity_encoded']

    # Train model
    model = RandomForestClassifier()
    model.fit(X, y)

    return model, le


# -----------------------------
# PREDICT PRODUCTIVITY
# -----------------------------
def predict_productivity(model, le, input_data):

    columns = [
        "start_hour",
        "day_of_week",
        "session_duration",
        "pause_count",
        "resume_count",
        "completed",
        "continued_later",
        "focus_score"
    ]

    input_df = pd.DataFrame([input_data], columns=columns)

    prediction = model.predict(input_df)

    return le.inverse_transform(prediction)[0]


# -----------------------------
# FIND BEST STUDY HOUR 🔥 (FINAL FIX)
# -----------------------------
def find_best_hour(model, base_data):

    best_hour = 0
    best_prob = 0

    columns = [
        "start_hour",
        "day_of_week",
        "session_duration",
        "pause_count",
        "resume_count",
        "completed",
        "continued_later",
        "focus_score"
    ]

    # check realistic hours only
    for hour in range(8, 24):

        test_data = base_data.copy()
        test_data[0] = hour

        input_df = pd.DataFrame([test_data], columns=columns)

        # 🔥 use probability instead of label
        probs = model.predict_proba(input_df)[0]

        # High class probability (index 2)
        high_prob = probs[2]

        if high_prob > best_prob:
            best_prob = high_prob
            best_hour = hour

    return best_hour
