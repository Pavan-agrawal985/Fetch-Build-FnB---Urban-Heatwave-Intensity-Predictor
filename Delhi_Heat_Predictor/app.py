import streamlit as st
import requests
import pandas as pd
import joblib
import plotly.graph_objects as go
import math
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="Delhi Heat Predictor",
    page_icon="🌡️",
    layout="wide"
)

@st.cache_resource
def load_model():
    base_dir = Path(__file__).resolve().parent
    return joblib.load(base_dir / "delhi_heat_model.pkl")


@st.cache_data(ttl=300, show_spinner=False)
def fetch_weather(api_key: str):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat=28.6139&lon=77.2090&appid={api_key}&units=metric"
    )
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()


model = load_model()


def monotonic_temperature_calibration(
    model_obj,
    base_temp: float,
    humidity: float,
    wind: float,
    cloud: float,
    pressure: float,
    solar: float = 500.0
) -> float:
    # Enforce non-decreasing probability with temperature for fixed context.
    calibrated = 0.0
    start_temp = 30
    end_temp = int(max(start_temp, round(base_temp)))
    humidity = max(0.0, min(100.0, float(humidity)))

    for t in range(start_temp, end_temp + 1):
        t = float(t)
        row = pd.DataFrame([{
            "max_temperature": t + 2,
            "min_temperature": t - 2,
            "dew_point": t - ((100 - humidity) / 5),
            "wind_speed": float(wind),
            "cloud_cover": float(cloud),
            "pressure_surface_level": float(pressure),
            "solar_radiation": float(solar),
            "max_humidity": min(100, humidity + 5),
            "min_humidity": max(0, humidity - 5)
        }])
        p = float(model_obj.predict_proba(row)[0][1])
        calibrated = max(calibrated, p)

    return calibrated

st.title("🌡️ Delhi Heat Intensity Predictor")
st.markdown("AI Powered Urban Heat Prediction — Delhi Only")

st.sidebar.header("Delhi Live Prediction")

API_KEY = st.sidebar.text_input(
    "OpenWeather API Key",
    value="01f0ef0b94a5300bb9ac14a0d4bed884",
    type="password"
)

if st.sidebar.button("Predict Delhi Heat"):
    if not API_KEY.strip():
        st.error("Please enter a valid OpenWeather API key.")
        st.stop()

    try:
        data = fetch_weather(API_KEY.strip())
    except requests.RequestException as err:
        st.error(f"Weather API request failed: {err}")
        st.stop()

    if "main" not in data:
        st.error("API Error: unexpected response format.")
        st.write(data)
        st.stop()

    # Extract Weather
    #temp=50
    #humidity=15
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = data.get("wind", {}).get("speed", 0.0)
    cloud = data.get("clouds", {}).get("all", 0)
    feels_like = data["main"].get("feels_like", temp)
    condition = data["weather"][0]["main"] if data.get("weather") else "Unknown"
    visibility = data.get("visibility", 0) / 1000
    

    # Feature Engineering
    max_temp = temp + 2
    min_temp = temp - 2
    dew_point = temp - ((100 - humidity)/5)
    solar = 500
    max_humidity = min(100, humidity + 5)
    min_humidity = max(0, humidity - 5)

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
    raw_probability = float(model.predict_proba(features)[0][1])
    probability = monotonic_temperature_calibration(
        model_obj=model,
        base_temp=float(temp),
        humidity=float(humidity),
        wind=float(wind),
        cloud=float(cloud),
        pressure=float(pressure),
        solar=float(solar)
    )
    prediction = int(probability >= 0.5)

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

    col4, col5 = st.columns(2)
    col4.metric("Pressure", f"{pressure} hPa")
    col5.metric("Cloud Cover", f"{cloud}%")

    st.divider()

    # Final Output
    st.subheader("Delhi Heatwave Prediction")

    col1, col2 = st.columns(2)

    col1.metric("Heatwave", "YES" if prediction else "NO")
    col2.metric("Probability", f"{probability*100:.2f}%")

    st.markdown(f"### Risk Level: :{color}[{level}]")

    # Stable semicircle gauge + correctly anchored red hand indicator.
    gauge_value = max(0.0, min(float(probability * 100), 100.0))
    needle_angle = math.radians(180 - (gauge_value * 1.8))
    # For Plotly semicircle gauge, the dial center is at bottom-middle.
    center_x, center_y = 0.5, 0.0
    needle_length = 0.48
    needle_x = center_x + needle_length * math.cos(needle_angle)
    needle_y = center_y + needle_length * math.sin(needle_angle)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gauge_value,
        title={"text": "Delhi Heat Risk"},
        number={"suffix": "", "font": {"size": 64, "color": "#E5E7EB"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 2, "tickcolor": "#D1D5DB"},
            "bar": {"color": "rgba(0,0,0,0)", "thickness": 0.12},
            "bgcolor": "#070B18",
            "steps": [
                {"range": [0, 30], "color": "#16A34A"},
                {"range": [30, 60], "color": "#F59E0B"},
                {"range": [60, 100], "color": "#EF4444"}
            ],
            "threshold": {
                "line": {"color": "#E11D2E", "width": 0},
                "thickness": 0.0,
                "value": gauge_value
            }
        }
    ))

    # Draw a true red hand from center to current value.
    fig.add_shape(
        type="line",
        xref="paper",
        yref="paper",
        x0=center_x,
        y0=center_y,
        x1=needle_x,
        y1=needle_y,
        line={"color": "#E11D2E", "width": 7}
    )
    fig.add_shape(
        type="circle",
        xref="paper",
        yref="paper",
        x0=center_x - 0.03,
        y0=center_y - 0.03,
        x1=center_x + 0.03,
        y1=center_y + 0.03,
        fillcolor="#D9DEE8",
        line={"color": "#94A3B8", "width": 2}
    )

    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 30, "b": 10},
        paper_bgcolor="#070B18",
        plot_bgcolor="#070B18",
        height=460
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed result dashboard
    st.subheader("Detailed Heat Dashboard")
    d1, d2, d3 = st.columns(3)
    d1.metric("Dew Point", f"{dew_point:.1f} °C")
    d2.metric("Visibility", f"{visibility:.1f} km")
    d3.metric("Weather Condition", condition)

    st.progress(gauge_value / 100)
    st.caption(f"Live fetch time: {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")
    st.caption(f"Raw model: {raw_probability*100:.2f}% | Calibrated: {probability*100:.2f}%")

    risk_note = (
        "Low risk. Continue monitoring as conditions can change rapidly."
        if level == "Low"
        else "Moderate risk. Stay hydrated, avoid prolonged direct sun exposure."
        if level == "Medium"
        else "High heat risk. Limit outdoor exposure and follow heat advisory precautions."
    )
    if level == "Low":
        st.success(risk_note)
    elif level == "Medium":
        st.warning(risk_note)
    else:
        st.error(risk_note)

    with st.expander("Model Input Features Used"):
        st.dataframe(features, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Delhi Climate AI System")