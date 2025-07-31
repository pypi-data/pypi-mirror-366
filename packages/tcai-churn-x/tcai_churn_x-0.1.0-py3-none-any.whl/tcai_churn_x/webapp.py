def run_app():
    from flask import Flask, render_template, request
    import os
    import pickle
    import pandas as pd

    BASE_DIR = os.path.dirname(__file__)
    MODEL_DIR = os.path.join(BASE_DIR, "model")

    with open(os.path.join(MODEL_DIR, "best_model.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "encoder.pkl"), "rb") as f:
        encoders = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f:
        scaler = pickle.load(f)

    app = Flask(__name__, template_folder="templates")

    def make_prediction(input_data):
        df = pd.DataFrame([input_data])
        for col, enc in encoders.items():
            df[col] = enc.transform(df[col])
        numeric_cols = ["tenure", "MonthlyCharges", "TotalCharges"]
        df[numeric_cols] = scaler.transform(df[numeric_cols])
        pred = model.predict(df)[0]
        prob = model.predict_proba(df)[0][1]
        return ("Churn" if pred else "No Churn", prob)

    @app.route("/", methods=["GET", "POST"])
    def index():
        prediction = probability = None
        if request.method == "POST":
            input_data = {
                'gender': request.form['gender'],
                'SeniorCitizen': int(request.form['SeniorCitizen']),
                'Partner': request.form['Partner'],
                'Dependents': request.form['Dependents'],
                'tenure': int(request.form['tenure']),
                'PhoneService': request.form['PhoneService'],
                'MultipleLines': request.form['MultipleLines'],
                'InternetService': request.form['InternetService'],
                'OnlineSecurity': request.form['OnlineSecurity'],
                'OnlineBackup': request.form['OnlineBackup'],
                'DeviceProtection': request.form['DeviceProtection'],
                'TechSupport': request.form['TechSupport'],
                'StreamingTV': request.form['StreamingTV'],
                'StreamingMovies': request.form['StreamingMovies'],
                'Contract': request.form['Contract'],
                'PaperlessBilling': request.form['PaperlessBilling'],
                'PaymentMethod': request.form['PaymentMethod'],
                'MonthlyCharges': float(request.form['MonthlyCharges']),
                'TotalCharges': float(request.form['TotalCharges']),
            }
            prediction, probability = make_prediction(input_data)
        return render_template("index.html", prediction=prediction, probability=probability)

    app.run(debug=True)

if __name__ == "__main__":
    run_app()