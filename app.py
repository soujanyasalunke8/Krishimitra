
from flask import Flask, render_template, request
import joblib
import pandas as pd
import numpy as np
import os
import sqlite3
from database import register_buyer as save_buyer 
app = Flask(__name__)

# Load trained machine learning model
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "best_crop_price_model.pkl"
)

model = joblib.load(MODEL_PATH)

# Load cleaned agricultural dataset
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "cleaned_agriculture_data.csv"
)

dataset = pd.read_csv(DATA_PATH)

# Extract unique dropdown options
states = sorted(dataset["State"].dropna().astype(str).unique())
districts = sorted(dataset["District"].dropna().astype(str).unique())
markets = sorted(dataset["Market"].dropna().astype(str).unique())
commodities = sorted(dataset["Commodity"].dropna().astype(str).unique())
varieties = sorted(dataset["Variety"].dropna().astype(str).unique())
grades = sorted(dataset["Grade"].dropna().astype(str).unique())
# Create State-District mapping
district_map = (
    dataset.groupby("State")["District"]
    .apply(lambda x: sorted(x.dropna().astype(str).unique()))
    .to_dict()
)
market_map = (
    dataset.groupby("District")["Market"]
    .apply(lambda x: sorted(x.dropna().astype(str).unique()))
    .to_dict()
)
@app.route("/")
def home():
    return render_template(
        "index.html",
        states=states,
        districts=districts,
        markets=markets,
        commodities=commodities,
        varieties=varieties,
        grades=grades,
        district_map=district_map,
        market_map=market_map
    )



@app.route("/predict", methods=["POST"])
def predict():

    try:
        # Get input from farmer
        state = request.form["state"]
        district = request.form["district"]
        market = request.form["market"]
        commodity = request.form["commodity"]
        variety = request.form["variety"]
        grade = request.form["grade"]
        season = request.form["season"]
        future_date = pd.to_datetime(request.form["future_date"])

        # Prepare input data
        data = pd.DataFrame([{
            "State": state,
            "District": district,
            "Market": market,
            "Commodity": commodity,
            "Variety": variety,
            "Grade": grade,
            "Season": season,
        }])

        # Generate date features
        data["Year"] = future_date.year
        data["Month"] = future_date.month
        data["Day"] = future_date.day
        data["DayOfWeek"] = future_date.dayofweek
        data["Quarter"] = future_date.quarter

        data["Month_sin"] = np.sin(
            2 * np.pi * future_date.month / 12
        )
        data["Month_cos"] = np.cos(
            2 * np.pi * future_date.month / 12
        )

        data["DayOfYear_sin"] = np.sin(
            2 * np.pi * future_date.dayofyear / 365.25
        )
        data["DayOfYear_cos"] = np.cos(
            2 * np.pi * future_date.dayofyear / 365.25
        )

        # Arrange features in training order
        features = [
            "State", "District", "Market",
            "Commodity", "Variety", "Grade", "Season",
            "Year", "Month", "Day", "DayOfWeek",
            "Quarter", "Month_sin", "Month_cos",
            "DayOfYear_sin", "DayOfYear_cos"
        ]
        print(data[features].to_string(index=False))
        # Predict crop price
        predicted_price = model.predict(data[features])[0]
        
        return render_template(
        "index.html",
         prediction=round(float(predicted_price), 2),
         crop=commodity,
         market=market,
         prediction_date=future_date.strftime("%d-%m-%Y"),
         states=states,
         districts=districts,
         markets=markets,
         commodities=commodities,
         varieties=varieties,
         grades=grades,
         district_map=district_map,
         market_map=market_map
        )

    except Exception as e:
        return render_template(
            "index.html",
            error=str(e)
        )

# Farmer Registration Module

@app.route("/farmer-register")
def farmer_register():
    return render_template("farmer_register.html")


@app.route("/register_farmer", methods=["POST"])
def register_farmer():

    name = request.form["name"]
    phone = request.form["phone"]
    village = request.form["village"]
    state = request.form["state"]
    district = request.form["district"]
    crop = request.form["crop"]

    conn = sqlite3.connect(
        os.path.join(os.path.dirname(__file__), "krishimitra.db")
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO farmers
        (name, phone, village, state, district, crop)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, phone, village, state, district, crop))

    conn.commit()
    conn.close()

    return """
        <h2>Farmer Registered Successfully!</h2>
        <a href="/farmer-register">Register Another Farmer</a>
    """

# Buyer Registration Module

@app.route("/buyer-register")
def buyer_register():
    return render_template("buyer_register.html")


@app.route("/register_buyer", methods=["POST"])
def register_buyer_route():

    buyer_name = request.form["buyer_name"]
    mobile = request.form["mobile"]
    email = request.form["email"]
    business_type = request.form["business_type"]
    state = request.form["state"]
    district = request.form["district"]
    crop = request.form["crop"]

    save_buyer(
        buyer_name, mobile, email,
        business_type, state, district, crop
    )

    return """
    <h2>Buyer Registered Successfully!</h2>
    <a href="/buyer-register">Register Another Buyer</a>
    """


if __name__ == "__main__":
    app.run(debug=True)
