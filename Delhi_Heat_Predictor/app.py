import streamlit as st
import requests
import pandas as pd
import joblib
import plotly.graph_objects as go
import math
from datetime import datetime
from pathlib import Path

st.set_page_config(
    page_title="UHIP | Urban Heatwave Intensity Predictor",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a1f35;
    --bg-card-hover: #1f2544;
    --border-dim: #2a3154;
    --border-accent: #3b82f6;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-cyan: #06b6d4;
    --accent-blue: #3b82f6;
    --accent-amber: #f59e0b;
    --accent-red: #ef4444;
    --accent-green: #10b981;
    --accent-violet: #8b5cf6;
    --glow-cyan: rgba(6, 182, 212, 0.15);
    --glow-red: rgba(239, 68, 68, 0.15);
}

.stApp {
    background: linear-gradient(160deg, #0a0e1a 0%, #0f1629 40%, #111827 100%);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: rgba(10, 14, 26, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-dim);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #111827 100%);
    border-right: 1px solid var(--border-dim);
}

section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text-primary);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

h1, h2, h3, h4 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

.dashboard-header {
    background: linear-gradient(135deg, #111827 0%, #1a2744 100%);
    border: 1px solid var(--border-dim);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.dashboard-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-cyan), var(--accent-blue), var(--accent-violet));
}

.dashboard-header::after {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(6, 182, 212, 0.06) 0%, transparent 70%);
    pointer-events: none;
}

.header-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #f1f5f9, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}

.header-subtitle {
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 400;
    letter-spacing: 0.3px;
}

.header-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent-cyan);
    font-family: 'JetBrains Mono', monospace;
    margin-top: 0.8rem;
}

.metric-card {
    background: linear-gradient(145deg, #1a1f35 0%, #151b2e 100%);
    border: 1px solid var(--border-dim);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    border-color: var(--accent-cyan);
    box-shadow: 0 8px 32px rgba(6, 182, 212, 0.08);
    transform: translateY(-2px);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent-cyan);
    opacity: 0;
    transition: opacity 0.3s;
}

.metric-card:hover::before {
    opacity: 1;
}

.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    margin-bottom: 0.6rem;
    font-family: 'JetBrains Mono', monospace;
}

.metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.1;
}

.metric-unit {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 400;
    margin-left: 4px;
}

.risk-panel {
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    border: 1px solid;
    position: relative;
    overflow: hidden;
}

.risk-low {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03));
    border-color: rgba(16, 185, 129, 0.3);
}

.risk-medium {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.03));
    border-color: rgba(245, 158, 11, 0.3);
}

.risk-high {
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.03));
    border-color: rgba(239, 68, 68, 0.3);
    animation: pulse-glow 3s infinite;
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.05); }
    50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.12); }
}

.risk-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
}

.risk-value {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.4rem;
}

.risk-description {
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.5;
    max-width: 480px;
}

.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-dim), transparent);
    margin: 2rem 0;
    border: none;
}

.section-title {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 1.2rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-dim);
}

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-secondary);
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent-green);
    animation: blink 2s infinite;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.model-info-card {
    background: linear-gradient(145deg, #1a1f35, #151b2e);
    border: 1px solid var(--border-dim);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: var(--text-secondary);
    line-height: 1.8;
}

.confidence-bar {
    height: 6px;
    border-radius: 3px;
    background: var(--bg-secondary);
    overflow: hidden;
    margin-top: 8px;
}

.confidence-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-brand {
    text-align: center;
    padding: 1rem 0 1.5rem;
    border-bottom: 1px solid var(--border-dim);
    margin-bottom: 1.5rem;
}

.sidebar-brand-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.3px;
}

.sidebar-brand-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
    margin-top: 4px;
}

.feature-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}

.feature-table th {
    background: var(--bg-secondary);
    color: var(--text-muted);
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-size: 0.68rem;
    border-bottom: 1px solid var(--border-dim);
}

.feature-table td {
    padding: 10px 14px;
    color: var(--text-primary);
    border-bottom: 1px solid rgba(42, 49, 84, 0.5);
}

.feature-table tr:hover td {
    background: rgba(6, 182, 212, 0.03);
}

[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
}

div[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border-dim);
    border-radius: 12px;
}

.idle-state {
    text-align: center;
    padding: 4rem 2rem;
}

.idle-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    opacity: 0.6;
}

.idle-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.8rem;
}

.idle-desc {
    color: var(--text-secondary);
    font-size: 0.95rem;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.6;
}

.footer-bar {
    margin-top: 3rem;
    padding: 1.2rem 0;
    border-top: 1px solid var(--border-dim);
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)


# ─── LOAD MODEL ──────────────────────────────────────────────────────────────
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


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-title">UHIP SYSTEM</div>
    <div class="sidebar-brand-sub">URBAN HEATWAVE INTELLIGENCE</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Control Panel")

API_KEY = st.sidebar.text_input(
    "OpenWeather API Key",
    value="01f0ef0b94a5300bb9ac14a0d4bed884",
    type="password",
    help="Required for live weather data ingestion"
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
<div class="status-indicator">
    <div class="status-dot"></div>
    MODEL LOADED — READY
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("")

predict_btn = st.sidebar.button(
    "RUN PREDICTION",
    use_container_width=True,
    type="primary"
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div class="model-info-card">
    <strong style="color: #06b6d4;">Model Specs</strong><br>
    Algorithm: Random Forest / LR<br>
    Features: 9 meteorological<br>
    Target: Delhi (28.61°N, 77.21°E)<br>
    Calibration: Monotonic Temp.<br>
    Data Source: OpenWeatherMap
</div>
""", unsafe_allow_html=True)


# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <div class="header-title">Urban Heatwave Intensity Predictor</div>
    <div class="header-subtitle">
        Real-time AI-driven thermal risk assessment for Delhi NCR metropolitan region
    </div>
    <div class="header-badge">
        <span>&#9679;</span> LIVE MONITORING &mdash; DELHI 28.6139°N, 77.2090°E
    </div>
</div>
""", unsafe_allow_html=True)


# ─── MAIN CONTENT ────────────────────────────────────────────────────────────
if predict_btn:
    if not API_KEY.strip():
        st.error("Please enter a valid OpenWeather API key.")
        st.stop()

    with st.spinner("Ingesting live meteorological data..."):
        try:
            data = fetch_weather(API_KEY.strip())
        except requests.RequestException as err:
            st.error(f"Weather API request failed: {err}")
            st.stop()

    if "main" not in data:
        st.error("API Error: unexpected response format.")
        st.write(data)
        st.stop()

    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    pressure = data["main"]["pressure"]
    wind = data.get("wind", {}).get("speed", 0.0)
    cloud = data.get("clouds", {}).get("all", 0)
    feels_like = data["main"].get("feels_like", temp)
    condition = data["weather"][0]["main"] if data.get("weather") else "Unknown"
    visibility = data.get("visibility", 0) / 1000

    max_temp = temp + 2
    min_temp = temp - 2
    dew_point = temp - ((100 - humidity) / 5)
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

    if probability < 0.3:
        level = "Low"
        risk_color = "#10b981"
        risk_class = "risk-low"
    elif probability < 0.6:
        level = "Medium"
        risk_color = "#f59e0b"
        risk_class = "risk-medium"
    else:
        level = "High"
        risk_color = "#ef4444"
        risk_class = "risk-high"

    gauge_value = max(0.0, min(float(probability * 100), 100.0))

    # ─── WEATHER TELEMETRY SECTION ───────────────────────────────────────
    st.markdown('<div class="section-title">LIVE WEATHER TELEMETRY</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Temperature</div>
            <div class="metric-value">{temp:.1f}<span class="metric-unit">°C</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Humidity</div>
            <div class="metric-value">{humidity:.0f}<span class="metric-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Wind Speed</div>
            <div class="metric-value">{wind:.1f}<span class="metric-unit">m/s</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Pressure</div>
            <div class="metric-value">{pressure:.0f}<span class="metric-unit">hPa</span></div>
        </div>
        """, unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Cloud Cover</div>
            <div class="metric-value">{cloud}<span class="metric-unit">%</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ─── PREDICTION RESULTS ──────────────────────────────────────────────
    st.markdown('<div class="section-title">PREDICTION ANALYSIS</div>', unsafe_allow_html=True)

    left_col, right_col = st.columns([1.4, 1])

    with left_col:
        # Gauge chart
        needle_angle = math.radians(180 - (gauge_value * 1.8))
        center_x, center_y = 0.5, 0.0
        needle_length = 0.45
        needle_x = center_x + needle_length * math.cos(needle_angle)
        needle_y = center_y + needle_length * math.sin(needle_angle)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_value,
            title={"text": "HEATWAVE INTENSITY INDEX", "font": {"size": 14, "color": "#64748b", "family": "JetBrains Mono"}},
            number={"suffix": "%", "font": {"size": 52, "color": "#f1f5f9", "family": "JetBrains Mono"}},
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": "#475569",
                    "tickfont": {"color": "#64748b", "size": 11, "family": "JetBrains Mono"},
                    "dtick": 10
                },
                "bar": {"color": "rgba(0,0,0,0)", "thickness": 0.05},
                "bgcolor": "#111827",
                "borderwidth": 2,
                "bordercolor": "#2a3154",
                "steps": [
                    {"range": [0, 30], "color": "rgba(16, 185, 129, 0.25)"},
                    {"range": [30, 60], "color": "rgba(245, 158, 11, 0.25)"},
                    {"range": [60, 100], "color": "rgba(239, 68, 68, 0.3)"}
                ],
                "threshold": {
                    "line": {"color": risk_color, "width": 0},
                    "thickness": 0.0,
                    "value": gauge_value
                }
            }
        ))

        fig.add_shape(
            type="line", xref="paper", yref="paper",
            x0=center_x, y0=center_y, x1=needle_x, y1=needle_y,
            line={"color": risk_color, "width": 5}
        )
        fig.add_shape(
            type="circle", xref="paper", yref="paper",
            x0=center_x - 0.025, y0=center_y - 0.025,
            x1=center_x + 0.025, y1=center_y + 0.025,
            fillcolor="#e2e8f0", line={"color": "#94a3b8", "width": 2}
        )

        fig.update_layout(
            margin={"l": 30, "r": 30, "t": 60, "b": 10},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            font={"family": "JetBrains Mono"}
        )

        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        # Risk assessment panel
        heatwave_status = "HEATWAVE DETECTED" if prediction else "NO HEATWAVE"
        status_icon = "⚠" if prediction else "✓"

        st.markdown(f"""
        <div class="risk-panel {risk_class}">
            <div class="risk-label" style="color: {risk_color};">RISK ASSESSMENT</div>
            <div class="risk-value" style="color: {risk_color};">{level.upper()}</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin: 0.8rem 0;">
                {status_icon} {heatwave_status}
            </div>
            <div class="risk-description">
                Calibrated probability: <strong style="color: {risk_color};">{probability*100:.1f}%</strong><br>
                Raw model output: {raw_probability*100:.1f}%
            </div>
            <div class="confidence-bar" style="margin-top: 1.2rem;">
                <div class="confidence-fill" style="width: {gauge_value}%; background: linear-gradient(90deg, {risk_color}, {risk_color}88);"></div>
            </div>
            <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 6px; font-family: 'JetBrains Mono', monospace;">
                CONFIDENCE: {gauge_value:.1f}/100
            </div>
        </div>
        """, unsafe_allow_html=True)

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

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ─── DETAILED ANALYTICS ──────────────────────────────────────────────
    st.markdown('<div class="section-title">DETAILED ANALYTICS</div>', unsafe_allow_html=True)

    an1, an2 = st.columns(2)

    with an1:
        # Feature contribution chart
        feature_names = ["Max Temp", "Min Temp", "Dew Point", "Wind", "Cloud", "Pressure", "Solar Rad", "Max Hum", "Min Hum"]
        feature_vals = [max_temp, min_temp, dew_point, wind, cloud, pressure / 10, solar / 100, max_humidity, min_humidity]

        fig_features = go.Figure(go.Bar(
            x=feature_vals,
            y=feature_names,
            orientation='h',
            marker={
                "color": feature_vals,
                "colorscale": [[0, "#06b6d4"], [0.5, "#8b5cf6"], [1, "#ef4444"]],
                "line": {"width": 0}
            },
            text=[f"{v:.1f}" for v in feature_vals],
            textposition="outside",
            textfont={"family": "JetBrains Mono", "size": 10, "color": "#94a3b8"}
        ))

        fig_features.update_layout(
            title={"text": "Feature Values (Normalized Scale)", "font": {"size": 12, "color": "#64748b", "family": "JetBrains Mono"}},
            margin={"l": 10, "r": 50, "t": 50, "b": 20},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            xaxis={"showgrid": True, "gridcolor": "rgba(42, 49, 84, 0.5)", "zeroline": False, "tickfont": {"color": "#64748b", "family": "JetBrains Mono"}},
            yaxis={"tickfont": {"color": "#94a3b8", "size": 10, "family": "JetBrains Mono"}},
            font={"family": "JetBrains Mono"}
        )

        st.plotly_chart(fig_features, use_container_width=True)

    with an2:
        # Environmental context cards
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 12px;">
            <div class="metric-label">Feels Like Temperature</div>
            <div class="metric-value">{feels_like:.1f}<span class="metric-unit">°C</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 12px;">
            <div class="metric-label">Dew Point</div>
            <div class="metric-value">{dew_point:.1f}<span class="metric-unit">°C</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom: 12px;">
            <div class="metric-label">Visibility</div>
            <div class="metric-value">{visibility:.1f}<span class="metric-unit">km</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Weather Condition</div>
            <div class="metric-value" style="font-size: 1.4rem;">{condition}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ─── MODEL INPUT TABLE ───────────────────────────────────────────────
    with st.expander("MODEL INPUT FEATURES", expanded=False):
        st.dataframe(
            features.style.format("{:.2f}").set_properties(**{
                'background-color': '#111827',
                'color': '#e2e8f0',
                'border-color': '#2a3154',
                'font-family': 'JetBrains Mono, monospace'
            }),
            use_container_width=True
        )

    # ─── FOOTER ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="footer-bar">
        UHIP v2.0 &mdash; Urban Heatwave Intensity Predictor &mdash; Live fetch: {datetime.now().strftime('%d %b %Y, %H:%M:%S')} &mdash; Delhi NCR Region
    </div>
    """, unsafe_allow_html=True)

else:
    # ─── IDLE STATE ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="idle-state">
        <div class="idle-icon">🛰</div>
        <div class="idle-title">System Ready</div>
        <div class="idle-desc">
            The Urban Heatwave Intensity Predictor is standing by.<br>
            Click <strong>RUN PREDICTION</strong> in the control panel to ingest live
            meteorological data and generate a real-time heatwave risk assessment for Delhi NCR.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # Show system status cards in idle state
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">MODEL STATUS</div>
            <div class="metric-value" style="font-size: 1.2rem; color: #10b981;">LOADED</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">DATA SOURCE</div>
            <div class="metric-value" style="font-size: 1.2rem;">OpenWeather</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">LAST CHECK</div>
            <div class="metric-value" style="font-size: 1.2rem;">{datetime.now().strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="footer-bar">
        UHIP v2.0 &mdash; Urban Heatwave Intensity Predictor &mdash; System Idle &mdash; {datetime.now().strftime('%d %b %Y')}
    </div>
    """, unsafe_allow_html=True)
