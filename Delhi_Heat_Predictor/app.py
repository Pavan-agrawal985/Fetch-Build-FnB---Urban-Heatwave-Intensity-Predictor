import streamlit as st
import requests
import pandas as pd
import joblib
import plotly.graph_objects as go

st.set_page_config(
    page_title="Delhi Heat Predictor",
    page_icon="🌡️",
    layout="wide"
)

# Load Model
model = joblib.load("delhi_heat_model.pkl")
scaler = joblib.load("scaler.pkl")

st.title("🌡️ Delhi Heat Intensity Predictor")
st.markdown("AI Powered Urban Heat Prediction — Delhi Only")

st.sidebar.header("Delhi Live Prediction")

API_KEY = st.sidebar.text_input("01f0ef0b94a5300bb9ac14a0d4bed884")

if st.sidebar.button("Predict Delhi Heat"):

    # Delhi Coordinates
    url = f"https://api.openweathermap.org/data/2.5/weather?lat=28.6139&lon=77.2090&appid=01f0ef0b94a5300bb9ac14a0d4bed884&units=metric"

    response = requests.get(url)
    data = response.json()

    if "main" not in data:
        st.error("API Error")
        st.write(data)
        st.stop()

    # Extract Weather
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = data["wind"]["speed"]
    cloud = data["clouds"]["all"]

    # Feature Engineering
    max_temp = temp + 2
    min_temp = temp - 2
    dew_point = temp - ((100 - humidity)/5)
    solar = 500
    max_humidity = humidity + 5
    min_humidity = humidity - 5

    features = pd.DataFrame([{
        "max_temperature": max_temp,
        "min_temperature": min_temp,
        "dew_point": dew_point,
        "wind_speed": wind,
        "cloud_cover": cloud,
        "pressure_surface_level": pressure,
        "solar_radiation": solar,
        "max_humidity": max_humidity,
        "min_humidity": min_humidity
    }])

    # Prediction
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    # Risk Level
    if probability < 0.3:
        level = "Low"
        color = "green"
    elif probability < 0.6:
        level = "Medium"
        color = "orange"
    else:
        level = "High"
        color = "red"

    # Weather Cards
    col1, col2, col3 = st.columns(3)

    col1.metric("Delhi Temperature", f"{temp} °C")
    col2.metric("Humidity", f"{humidity}%")
    col3.metric("Wind Speed", f"{wind} m/s")

    st.divider()

    # Final Output
    st.subheader("Delhi Heatwave Prediction")

    col1, col2 = st.columns(2)

    col1.metric("Heatwave", "YES" if prediction else "NO")
    col2.metric("Probability", f"{probability*100:.2f}%")

    st.markdown(f"### Risk Level: :{color}[{level}]")

    # Gauge Chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability*100,
        title={'text': "Delhi Heat Risk"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 30], 'color': "green"},
                {'range': [30, 60], 'color': "orange"},
                {'range': [60, 100], 'color': "red"}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Delhi Climate AI System")