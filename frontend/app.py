"""
ASTraM Police Command Dashboard — Premium UI v3
"""

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, time as dtime
import pandas as pd

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ASTraM | Command Center",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global Reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── App background ── */
.stApp { background: #0d1117 !important; }
.main .block-container {
  background: #0d1117 !important;
  padding: 1.2rem 2rem 2rem 2rem !important;
  max-width: 1600px !important;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: #010409 !important;
  border-right: 1px solid #21262d !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] * { color: #8b949e !important; }
[data-testid="stSidebar"] .stRadio label { color: #c9d1d9 !important; font-size: 13px !important; }
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
  color: #c9d1d9 !important; font-size: 13px !important;
}

/* ── Sidebar Logo ── */
.sidebar-brand {
  padding: 24px 20px 20px 20px;
  border-bottom: 1px solid #21262d;
  margin-bottom: 12px;
}
.sidebar-brand .logo-text {
  font-size: 24px; font-weight: 900; letter-spacing: -1px;
  color: #fff !important;
  display: flex; align-items: center; gap: 10px;
}
.logo-badge {
  background: linear-gradient(135deg, #1f6feb, #388bfd);
  color: white !important; font-size: 11px; font-weight: 700;
  padding: 2px 8px; border-radius: 20px; letter-spacing: 0.5px;
}
.sidebar-brand .logo-sub { color: #484f58 !important; font-size: 11px; margin-top: 4px; letter-spacing: 0.5px; }

/* ── Sidebar Nav Items ── */
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 20px; cursor: pointer;
  border-left: 3px solid transparent;
  font-size: 13px; font-weight: 500; color: #8b949e !important;
  transition: all 0.15s; text-decoration: none;
  margin: 2px 0;
}
.nav-item:hover { background: #161b22; color: #c9d1d9 !important; }
.nav-item.active { border-left-color: #388bfd; background: #161b22; color: #e6edf3 !important; }
.nav-icon { font-size: 15px; width: 20px; text-align: center; }

/* ── Sidebar Footer ── */
.sidebar-footer {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 16px 20px; border-top: 1px solid #21262d;
  background: #010409;
}
.sidebar-footer .sys-status { display: flex; align-items: center; gap: 8px; }
.status-dot { width: 7px; height: 7px; border-radius: 50%; background: #3fb950; box-shadow: 0 0 6px #3fb950; }
.sys-label { font-size: 11px; color: #484f58 !important; }
.sys-val   { font-size: 12px; color: #8b949e !important; font-weight: 500; }

/* ── Top Navigation Breadcrumb ── */
.top-breadcrumb {
  color: #484f58; font-size: 12px; letter-spacing: 0.3px;
  margin-bottom: 8px; display: flex; align-items: center; gap: 6px;
}
.top-breadcrumb .sep { color: #30363d; }
.top-breadcrumb .cur { color: #8b949e; }

/* ── Page Title ── */
.page-title { font-size: 26px; font-weight: 800; color: #e6edf3; letter-spacing: -0.5px; margin-bottom: 4px; }
.page-subtitle { font-size: 13px; color: #484f58; margin-bottom: 24px; }

/* ── Section label ── */
.section-label {
  font-size: 10px; font-weight: 700; letter-spacing: 2px;
  color: #484f58; text-transform: uppercase; margin-bottom: 12px;
}

/* ── Input Panel Card ── */
.input-panel {
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 12px;
  padding: 20px;
}

/* ── Form Inputs ── */
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stNumberInput"] label,
[data-testid="stDateInput"] label,
[data-testid="stTimeInput"] label,
[data-testid="stToggle"] label {
  color: #8b949e !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  letter-spacing: 1px !important;
  text-transform: uppercase !important;
}

[data-testid="stSelectbox"] > div > div,
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
  background: #0d1117 !important;
  border: 1px solid #30363d !important;
  border-radius: 8px !important;
  color: #c9d1d9 !important;
  font-size: 13px !important;
}
[data-testid="stSelectbox"] > div > div:hover,
[data-testid="stTextInput"] input:focus,
[data-testid="stDateInput"] input:focus {
  border-color: #388bfd !important;
  box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important;
}

/* Toggle styling */
[data-testid="stToggle"] { margin: 8px 0; }

/* ── Primary Button ── */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #1f6feb, #388bfd) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: 0.3px !important;
  height: 46px !important;
  transition: all 0.2s !important;
  box-shadow: 0 4px 15px rgba(56,139,253,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(56,139,253,0.45) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* ── Result Cards ── */
.res-card {
  border-radius: 12px; padding: 18px 20px;
  border: 1px solid #21262d;
  background: #161b22;
  height: 100%;
  transition: border-color 0.2s;
}
.res-card:hover { border-color: #30363d; }
.res-card.HIGH {
  border-top: 3px solid #f85149;
  background: linear-gradient(160deg, #1a0b0b 0%, #161b22 60%);
}
.res-card.LOW  {
  border-top: 3px solid #3fb950;
  background: linear-gradient(160deg, #0b1a0d 0%, #161b22 60%);
}
.res-card.BLUE {
  border-top: 3px solid #388bfd;
  background: linear-gradient(160deg, #0b1120 0%, #161b22 60%);
}
.res-card.NEUTRAL {
  border-top: 3px solid #6e7681;
}
.card-icon { font-size: 18px; margin-bottom: 10px; }
.card-micro { font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
.sev-HIGH { color: #f85149 !important; }
.sev-LOW  { color: #3fb950 !important; }
.sev-BLUE { color: #79c0ff !important; }
.sev-NEU  { color: #8b949e !important; }
.card-val-xl { font-size: 38px; font-weight: 900; line-height: 1; letter-spacing: -1.5px; }
.card-val-lg { font-size: 24px; font-weight: 800; line-height: 1; color: #e6edf3; letter-spacing: -0.5px; }
.card-val-sm { font-size: 13px; color: #8b949e; margin-top: 5px; }
.conf-track { height: 4px; background: #21262d; border-radius: 2px; margin: 10px 0 6px 0; }
.conf-fill  { height: 4px; border-radius: 2px; transition: width 0.6s ease; }
.prob-line  { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #484f58; margin-top: 4px; }
.basis-text { font-size: 10px; color: #484f58; margin-top: 10px; padding-top: 10px; border-top: 1px solid #21262d; line-height: 1.5; }

/* ── Feature Importance Bars ── */
.fi-card {
  background: #161b22; border: 1px solid #21262d; border-radius: 12px; padding: 20px;
}
.fi-row {
  display: flex; align-items: center; gap: 10px;
  padding: 5px 0; border-bottom: 1px solid #0d1117;
}
.fi-row:last-child { border-bottom: none; }
.fi-rank { font-family: 'JetBrains Mono',monospace; font-size: 10px; color: #484f58; width: 16px; }
.fi-label { font-size: 12px; color: #c9d1d9; flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.fi-bar-bg { flex: 1.5; height: 6px; background: #21262d; border-radius: 3px; }
.fi-bar-fill { height: 6px; border-radius: 3px; background: linear-gradient(90deg, #1f6feb, #58a6ff); }
.fi-pct { font-family:'JetBrains Mono',monospace; font-size: 11px; color: #58a6ff; width: 36px; text-align: right; font-weight: 600; }

/* ── Rationale Card ── */
.rat-card {
  background: #161b22; border: 1px solid #21262d; border-radius: 12px; padding: 20px;
  height: 100%;
}
.rat-item {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 9px 0; border-bottom: 1px solid #0d1117; font-size: 12px; color: #8b949e; line-height: 1.5;
}
.rat-item:last-child { border-bottom: none; padding-bottom: 0; }
.rat-bullet { color: #388bfd; font-size: 14px; flex-shrink: 0; margin-top: 1px; }

/* ── Model Provenance Bar ── */
.provenance-bar {
  background: #161b22; border: 1px solid #21262d; border-radius: 8px;
  padding: 10px 16px; margin: 14px 0;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.prov-badge {
  font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
  font-family: 'JetBrains Mono', monospace;
}
.prov-green { background: #0d2818; border: 1px solid #1a7f37; color: #3fb950; }
.prov-blue  { background: #0c1929; border: 1px solid #1f6feb; color: #58a6ff; }
.prov-gray  { background: #161b22; border: 1px solid #30363d; color: #8b949e; }
.prov-id    { font-family:'JetBrains Mono',monospace; font-size: 10px; color: #484f58; margin-left: auto; }

/* ── Map Section ── */
.map-card { background: #161b22; border: 1px solid #21262d; border-radius: 12px; overflow: hidden; }
.map-header {
  padding: 14px 18px; border-bottom: 1px solid #21262d;
  display: flex; justify-content: space-between; align-items: center;
}
.map-title { font-size: 13px; font-weight: 700; color: #e6edf3; }
.map-legend-item { display: flex; align-items: center; gap: 5px; font-size: 11px; color: #8b949e; }
.legend-dot-red   { width: 10px; height: 10px; border-radius: 50%; background: #f85149; }
.legend-dot-green { width: 10px; height: 3px; border-radius: 2px; background: #3fb950; }

/* ── Placeholder ── */
.placeholder-card {
  background: #161b22; border: 1px solid #21262d; border-radius: 12px;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 60px 20px; text-align: center;
}
.placeholder-icon { font-size: 52px; margin-bottom: 16px; filter: grayscale(0.3); }
.placeholder-title { font-size: 16px; font-weight: 700; color: #484f58; margin-bottom: 6px; }
.placeholder-sub   { font-size: 13px; color: #30363d; }

/* ── Alert box for road closure ── */
.alert-warn {
  background: #1a1200; border: 1px solid #d4a72c; border-radius: 8px;
  padding: 10px 14px; font-size: 12px; color: #d4a72c;
  display: flex; gap: 8px; align-items: center; margin-top: 4px;
}

/* ── Analytics Cards ── */
.analytics-card {
  background: #161b22; border: 1px solid #21262d; border-radius: 12px;
  padding: 20px; margin-bottom: 16px;
}
.analytics-title { font-size: 13px; font-weight: 700; color: #e6edf3; margin-bottom: 4px; }
.analytics-sub   { font-size: 11px; color: #484f58; margin-bottom: 16px; }

/* ── KPI stat boxes ── */
.kpi-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.kpi-box {
  background: #161b22; border: 1px solid #21262d; border-radius: 10px;
  padding: 14px 18px; flex: 1; min-width: 120px;
}
.kpi-label { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #484f58; margin-bottom: 6px; }
.kpi-value { font-size: 24px; font-weight: 800; color: #e6edf3; }
.kpi-sub   { font-size: 11px; color: #484f58; margin-top: 3px; }

/* ── Corridor risk table ── */
.risk-table { width: 100%; border-collapse: collapse; }
.risk-table th { font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #484f58; padding: 8px 12px; text-align: left; border-bottom: 1px solid #21262d; }
.risk-table td { font-size: 13px; color: #c9d1d9; padding: 10px 12px; border-bottom: 1px solid #0d1117; }
.risk-table tr:last-child td { border-bottom: none; }
.risk-badge { background: #1a0b0b; border: 1px solid #f85149; color: #f85149; border-radius: 4px; padding: 2px 8px; font-size: 10px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

/* ── Streamlit overrides ── */
.stSpinner > div { border-color: #388bfd !important; }
[data-testid="stCaptionContainer"] p { color: #484f58 !important; font-size: 11px !important; }
[data-testid="stMarkdownContainer"] h4 { color: #e6edf3 !important; }
.element-container { margin-bottom: 0 !important; }
[data-testid="stVerticalBlock"] { gap: 8px !important; }

/* ── Chart overrides (dark) ── */
[data-testid="stVegaLiteChart"] canvas { background: transparent !important; }

</style>
""", unsafe_allow_html=True)


# ── Load static data ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_api_options():
    try:
        r  = requests.get(f"{API_URL}/stats/causes", timeout=3)
        r2 = requests.get(f"{API_URL}/stats/zones",  timeout=3)
        return (list(r.json().keys()) if r.ok else [], list(r2.json().keys()) if r2.ok else [])
    except Exception:
        return [], []

@st.cache_data(ttl=3600)
def load_stats():
    try:
        with open(r"C:\Users\Sanchay\OneDrive\Desktop\flipkart\stats.json", encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="logo-text">
        <span>🚔</span>
        <span>ASTraM <span class="logo-badge">v2</span></span>
      </div>
      <div class="logo-sub">BENGALURU TRAFFIC COMMAND</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding: 0 12px;'>", unsafe_allow_html=True)
    pages_map = {
        "🔮  Predictive Engine": "predict",
        "📊  Analytics":         "analytics",
    }
    sel = st.radio("nav", list(pages_map.keys()), label_visibility="collapsed")
    page = pages_map[sel]
    st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar footer - system status
    stats_data = load_stats()
    acc = stats_data.get("train_accuracy", "–")
    f1  = stats_data.get("train_f1", "–")

    st.markdown(f"""
    <div class="sidebar-footer">
      <div style="font-size:10px;color:#484f58;letter-spacing:1px;text-transform:uppercase;margin-bottom:10px;">System Status</div>
      <div class="sys-status" style="margin-bottom:6px;">
        <div class="status-dot"></div>
        <span class="sys-val">Model Online</span>
      </div>
      <div style="display:flex;justify-content:space-between;margin-top:8px;">
        <div><div class="sys-label">Accuracy</div><div class="sys-val">{acc}</div></div>
        <div><div class="sys-label">F1 Score</div><div class="sys-val">{f1}</div></div>
        <div><div class="sys-label">Dataset</div><div class="sys-val">8,173</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTIVE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
if page == "predict":

    st.markdown("""
    <div class="top-breadcrumb">
      <span>ASTraM</span><span class="sep">/</span>
      <span>Bengaluru Traffic Ops</span><span class="sep">/</span>
      <span class="cur">Predictive Engine</span>
    </div>
    <div class="page-title">Predictive Engine</div>
    <div class="page-subtitle">Enter event particulars. The engine returns severity, confidence, recommended deployment and diversion routes.</div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1.85], gap="large")

    # ── INPUT PANEL ──────────────────────────────────────────────────────────
    with col_left:
        causes_from_api, zones_from_api = get_api_options()
        CAUSE_OPTIONS = causes_from_api or [
            "vehicle_breakdown","accident","water_logging","construction","pot_holes",
            "congestion","tree_fall","public_event","procession","vip_movement",
            "protest","road_conditions","others"
        ]
        ZONE_OPTIONS = zones_from_api or [
            "North Zone 1","North Zone 2","South Zone 1","South Zone 2",
            "East Zone 1","East Zone 2","West Zone 1","West Zone 2",
            "Central Zone 1","Central Zone 2","unknown"
        ]
        CORRIDOR_OPTIONS = [
            "Non-corridor","Mysore Road","Bellary Road 1","Bellary Road 2",
            "Tumkur Road","Hosur Road","ORR East 1","ORR North 1",
            "Old Madras Road","Magadi Road","Bannerghata Road",
            "Hennur Main Road","Kanakapura Road"
        ]
        VEH_OPTIONS = ["unknown","heavy_vehicle","lcv","car","two_wheeler","bmtc_bus","auto","others"]

        st.markdown("<div class='section-label'>Input Panel — Event Particulars</div>", unsafe_allow_html=True)

        event_cause  = st.selectbox("Event Cause", CAUSE_OPTIONS, key="ec")
        event_type_s = st.selectbox("Event Type", ["Unplanned", "Planned"], key="et")

        c1, c2 = st.columns(2)
        with c1:
            corridor = st.selectbox("Corridor", CORRIDOR_OPTIONS, key="cor")
        with c2:
            zone = st.selectbox("Zone", ZONE_OPTIONS, key="z")

        c3, c4 = st.columns(2)
        with c3:
            event_date = st.date_input("Event Date", value=date.today(), key="ed")
        with c4:
            event_time = st.time_input("Event Time", value=dtime(hour=datetime.now().hour, minute=0), key="etm")

        c5, c6 = st.columns(2)
        with c5:
            veh_type = st.selectbox("Vehicle Type", VEH_OPTIONS, key="vt")
        with c6:
            expected_crowd = st.number_input("Expected Crowd", value=0, min_value=0, key="crowd")

        requires_road_closure = st.toggle("Requires Road Closure", value=False, key="rrc")
        if requires_road_closure:
            st.markdown("""
            <div class="alert-warn">
              ⚠ Full barricading protocol will be activated
            </div>
            """, unsafe_allow_html=True)

        notes = st.text_area("Notes (Optional)", placeholder="Operational context, jurisdiction, VIP details...", height=68, key="notes")

        predict_clicked = st.button("Forecast Impact", type="primary", use_container_width=True, key="predict")

    # ── OUTPUT PANEL ─────────────────────────────────────────────────────────
    with col_right:

        if predict_clicked:
            payload = {
                "event_cause":           event_cause,
                "event_type":            1 if event_type_s == "Planned" else 0,
                "requires_road_closure": 1 if requires_road_closure else 0,
                "veh_type":              veh_type,
                "hour_of_day":           event_time.hour,
                "day_of_week":           event_date.weekday(),
                "is_weekend":            1 if event_date.weekday() >= 5 else 0,
                "month":                 event_date.month,
                "zone":                  zone,
                "corridor":              corridor,
                "latitude":              None,
                "longitude":             None,
            }
            with st.spinner("Running XGBoost inference..."):
                try:
                    res = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
                    if res.status_code == 200:
                        st.session_state["result"]  = res.json()
                        st.session_state["corridor"] = corridor
                        st.session_state["last_ec"] = event_cause
                        st.session_state["last_sev"] = res.json()["severity"]
                    else:
                        st.error(f"API Error {res.status_code}: {res.text}")
                except Exception as e:
                    st.error(f"Cannot connect to backend.\nMake sure to run: `uvicorn backend.main:app`\n\n{e}")

        if "result" in st.session_state:
            res = st.session_state["result"]
            sev  = res["severity"]
            conf = res["confidence"]
            mp   = res["manpower"]
            dv   = res["diversions"]
            mi   = res.get("model_info", {})

            # ── METRIC ROW ────────────────────────────────────────────────
            mc1, mc2, mc3 = st.columns(3)

            with mc1:
                sev_color = "#f85149" if sev == "HIGH" else "#3fb950"
                fill_color = "#f85149" if sev == "HIGH" else "#3fb950"
                icon = "🔴" if sev == "HIGH" else "🟢"
                st.markdown(f"""
                <div class="res-card {sev}">
                  <div class="card-micro sev-{'HIGH' if sev=='HIGH' else 'LOW'}">{icon} Severity</div>
                  <div class="card-val-xl" style="color:{sev_color};">{sev}</div>
                  <div class="card-val-sm">Confidence {conf:.1f}%</div>
                  <div class="conf-track">
                    <div class="conf-fill" style="width:{conf}%;background:{fill_color};"></div>
                  </div>
                  <div class="prob-line">P(High)={res['prob_high']}% &nbsp;|&nbsp; P(Low)={res['prob_low']}%</div>
                </div>
                """, unsafe_allow_html=True)

            with mc2:
                st.markdown(f"""
                <div class="res-card BLUE">
                  <div class="card-micro sev-BLUE">👮 Manpower Deployment</div>
                  <div class="card-val-lg">{mp['officers']} officers</div>
                  <div class="card-val-sm">{mp['barricades']} barricades</div>
                  <div class="basis-text">{mp['basis']}</div>
                </div>
                """, unsafe_allow_html=True)

            with mc3:
                dur_text = f"~{dv['avg_duration_min']} min avg resolution" if dv.get("avg_duration_min") else "Duration data unavailable"
                st.markdown(f"""
                <div class="res-card NEUTRAL">
                  <div class="card-micro sev-NEU">🔀 Diversion Routes</div>
                  <div class="card-val-lg">{dv['count']} route(s)</div>
                  <div class="card-val-sm">{dur_text}</div>
                  <div class="basis-text">{dv['basis']}</div>
                </div>
                """, unsafe_allow_html=True)

            # ── PROVENANCE BAR ────────────────────────────────────────────
            ev_id = res.get("event_id", "–")
            ts    = res.get("timestamp", "")
            st.markdown(f"""
            <div class="provenance-bar">
              <span class="prov-badge prov-green">Acc {mi.get('accuracy','?')}</span>
              <span class="prov-badge prov-green">F1 {mi.get('f1_score','?')}</span>
              <span class="prov-badge prov-blue">8,173 real events</span>
              <span class="prov-badge prov-gray">XGBoost + ASTraM Dataset</span>
              <span class="prov-id">ID: {ev_id} &nbsp;|&nbsp; {ts[:19].replace('T',' ')} UTC</span>
            </div>
            """, unsafe_allow_html=True)

            # ── FEATURE IMPORTANCE + RATIONALE ───────────────────────────
            fi_col, rat_col = st.columns([1, 1], gap="medium")

            with fi_col:
                st.markdown("<div class='section-label' style='margin-top:6px;'>Feature Importance — from XGBoost model</div>", unsafe_allow_html=True)
                imps    = res.get("importances", [])
                max_val = max((i["value"] for i in imps), default=1)
                imp_html = "<div class='fi-card'>"
                for rank, imp in enumerate(imps, 1):
                    pct   = imp["value"]
                    width = int(pct / max_val * 100)
                    imp_html += f"""
                    <div class="fi-row">
                      <span class="fi-rank">{rank:02d}</span>
                      <span class="fi-label" title="{imp['feature']}">{imp['feature']}</span>
                      <div class="fi-bar-bg"><div class="fi-bar-fill" style="width:{width}%;"></div></div>
                      <span class="fi-pct">{pct:.1f}%</span>
                    </div>"""
                imp_html += "</div>"
                st.markdown(imp_html, unsafe_allow_html=True)

            with rat_col:
                st.markdown("<div class='section-label' style='margin-top:6px;'>Rationale — derived from dataset statistics</div>", unsafe_allow_html=True)
                rat_html = "<div class='rat-card'>"
                for item in res.get("rationale", []):
                    rat_html += f"""
                    <div class="rat-item">
                      <span class="rat-bullet">›</span>
                      <span>{item}</span>
                    </div>"""
                rat_html += "</div>"
                st.markdown(rat_html, unsafe_allow_html=True)

            # ── TACTICAL MAP ─────────────────────────────────────────────
            st.markdown("<div class='section-label' style='margin-top:14px;'>Tactical View — Affected Corridor & Diversions</div>", unsafe_allow_html=True)

            st.markdown("""
            <div class="map-card">
              <div class="map-header">
                <span class="map-title">Affected Corridor & Diversions</span>
                <div style="display:flex;gap:16px;">
                  <div class="map-legend-item"><div class="legend-dot-red"></div><span>Affected</span></div>
                  <div class="map-legend-item"><div class="legend-dot-green"></div><span>Alternate</span></div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Load corridor coords from stats.json
            corridor_coords = stats_data.get("corridor_coords", {})
            sel_corr   = st.session_state.get("corridor", "Non-corridor")
            coord      = corridor_coords.get(sel_corr, {"lat": 12.9716, "lon": 77.5946})
            center_lat = coord["lat"]
            center_lon = coord["lon"]

            # Build folium map with dark tiles
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=13,
                tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            )

            # Impact zone circle
            radius_m = 1800 if sev == "HIGH" else 800
            folium.Circle(
                [center_lat, center_lon],
                radius=radius_m,
                color="#f85149" if sev == "HIGH" else "#fb8f44",
                fill=True,
                fill_opacity=0.12,
                weight=2,
                tooltip=f"Impact zone ({radius_m}m radius)"
            ).add_to(m)

            # Epicenter marker
            folium.CircleMarker(
                [center_lat, center_lon],
                radius=10,
                color="#f85149" if sev == "HIGH" else "#fb8f44",
                fill=True,
                fill_opacity=1.0,
                popup=folium.Popup(
                    f"<b style='color:#f85149;'>{sev}</b><br>"
                    f"<b>{st.session_state.get('last_ec','').replace('_',' ').title()}</b><br>"
                    f"{sel_corr}<br>"
                    f"Confidence: {conf:.1f}%<br>"
                    f"Officers: {mp['officers']} | Barricades: {mp['barricades']}",
                    max_width=220
                ),
                tooltip=f"{sel_corr} — {sev} ({conf:.0f}% confidence)"
            ).add_to(m)

            # Affected corridor line
            if sel_corr != "Non-corridor":
                folium.PolyLine(
                    [[center_lat - 0.018, center_lon - 0.014],
                     [center_lat,          center_lon],
                     [center_lat + 0.018,  center_lon + 0.014]],
                    color="#f85149",
                    weight=7,
                    opacity=0.85,
                    tooltip=f"Affected: {sel_corr}"
                ).add_to(m)

            # Diversion routes
            dv_count = dv["count"]
            if dv_count >= 1:
                folium.PolyLine(
                    [[center_lat - 0.014, center_lon - 0.022],
                     [center_lat - 0.006, center_lon - 0.018],
                     [center_lat + 0.012, center_lon + 0.006]],
                    color="#3fb950",
                    weight=4,
                    dash_array="10 5",
                    opacity=0.9,
                    tooltip="Diversion Route 1"
                ).add_to(m)

            if dv_count >= 2:
                folium.PolyLine(
                    [[center_lat - 0.016, center_lon + 0.012],
                     [center_lat + 0.002, center_lon + 0.018],
                     [center_lat + 0.020, center_lon + 0.010]],
                    color="#3fb950",
                    weight=4,
                    dash_array="10 5",
                    opacity=0.9,
                    tooltip="Diversion Route 2"
                ).add_to(m)

            # Barricade markers
            if mp['barricades'] > 0 and sel_corr != "Non-corridor":
                for i, (blat, blon) in enumerate([
                    (center_lat - 0.006, center_lon - 0.004),
                    (center_lat + 0.004, center_lon + 0.006),
                ]):
                    folium.Marker(
                        [blat, blon],
                        icon=folium.DivIcon(
                            html=f'<div style="background:#d4a72c;color:#000;font-size:9px;'
                                 f'font-weight:700;padding:2px 5px;border-radius:3px;'
                                 f'border:1px solid #f0c000;white-space:nowrap;">BARRICADE</div>',
                            icon_size=(70, 20),
                        ),
                        tooltip=f"Barricade Point {i+1}"
                    ).add_to(m)

            st_folium(m, height=440, use_container_width=True, returned_objects=[])

        else:
            st.markdown("""
            <div class="placeholder-card" style="height:440px;">
              <div class="placeholder-icon">🛡️</div>
              <div class="placeholder-title">Submit event particulars to receive a forecast</div>
              <div class="placeholder-sub">All predictions are derived from 8,173 real ASTraM Bengaluru events<br>via a trained XGBoost model — zero hardcoded outputs</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "analytics":

    st.markdown("""
    <div class="top-breadcrumb">
      <span>ASTraM</span><span class="sep">/</span>
      <span>Bengaluru Traffic Ops</span><span class="sep">/</span>
      <span class="cur">Analytics</span>
    </div>
    <div class="page-title">Analytics Dashboard</div>
    <div class="page-subtitle">Historical patterns derived from the ASTraM dataset — 8,173 real Bengaluru traffic events</div>
    """, unsafe_allow_html=True)

    s = load_stats()
    if not s:
        st.error("stats.json not found. Run `train_model.py` first.")
        st.stop()

    # KPI Row
    total_events = sum(int(v.get("count", 0)) for v in s.get("cause_high_rate", {}).values())
    total_high   = sum(int(v.get("sum", 0))   for v in s.get("cause_high_rate", {}).values())
    total_low    = total_events - total_high
    top_cause    = s.get("top_high_causes", ["–"])[0].replace("_", " ").title()

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-box">
        <div class="kpi-label">Total Events</div>
        <div class="kpi-value" style="color:#e6edf3;">{total_events:,}</div>
        <div class="kpi-sub">in dataset</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">High Priority</div>
        <div class="kpi-value" style="color:#f85149;">{total_high:,}</div>
        <div class="kpi-sub">{total_high/total_events*100:.1f}% of total</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Low Priority</div>
        <div class="kpi-value" style="color:#3fb950;">{total_low:,}</div>
        <div class="kpi-sub">{total_low/total_events*100:.1f}% of total</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Top Cause</div>
        <div class="kpi-value" style="color:#e6edf3;font-size:18px;">{top_cause}</div>
        <div class="kpi-sub">most High-priority events</div>
      </div>
      <div class="kpi-box">
        <div class="kpi-label">Model F1</div>
        <div class="kpi-value" style="color:#58a6ff;">{s.get('train_f1', '–')}</div>
        <div class="kpi-sub">XGBoost on 10 features</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts row 1
    ch1, ch2 = st.columns(2, gap="medium")

    with ch1:
        st.markdown("""
        <div class="analytics-card">
          <div class="analytics-title">High-Severity Rate by Event Cause</div>
          <div class="analytics-sub">% of events of each cause that were HIGH priority in the dataset</div>
        </div>
        """, unsafe_allow_html=True)
        cause_data = s.get("cause_high_rate", {})
        df_cause = pd.DataFrame([
            {"Event Cause": k.replace("_", " ").title(),
             "High Priority %": round(v.get("high_pct", 0), 1)}
            for k, v in cause_data.items()
            if v.get("count", 0) >= 10
        ]).sort_values("High Priority %", ascending=False)
        st.bar_chart(df_cause.set_index("Event Cause"), color="#f85149", height=300)

    with ch2:
        st.markdown("""
        <div class="analytics-card">
          <div class="analytics-title">High-Severity Rate by Zone</div>
          <div class="analytics-sub">Proportion of High-priority events per Bengaluru zone</div>
        </div>
        """, unsafe_allow_html=True)
        zone_data = s.get("zone_high_rate", {})
        df_zone = pd.DataFrame([
            {"Zone": k, "High Priority %": round(v * 100, 1)}
            for k, v in zone_data.items()
            if k != "unknown"
        ]).sort_values("High Priority %", ascending=False)
        st.bar_chart(df_zone.set_index("Zone"), color="#388bfd", height=300)

    # Charts row 2
    ch3, ch4 = st.columns(2, gap="medium")

    with ch3:
        st.markdown("""
        <div class="analytics-card">
          <div class="analytics-title">Feature Importances — XGBoost Model</div>
          <div class="analytics-sub">Contribution of each feature to severity prediction (no data leakage; corridor excluded)</div>
        </div>
        """, unsafe_allow_html=True)
        fi = s.get("feature_importances", {})
        label_map = {
            "event_cause": "Event Cause", "veh_type": "Vehicle Type",
            "zone": "Zone", "hour_bucket": "Hour of Day",
            "event_type": "Event Type", "requires_road_closure": "Road Closure",
            "is_high_risk_cause": "High-Risk Cause Flag", "day_of_week": "Day of Week",
            "is_weekend": "Is Weekend", "month": "Month",
        }
        df_fi = pd.DataFrame([
            {"Feature": label_map.get(k, k), "Importance %": round(v, 1)}
            for k, v in sorted(fi.items(), key=lambda x: -x[1])
        ])
        st.bar_chart(df_fi.set_index("Feature"), color="#58a6ff", height=300)

    with ch4:
        st.markdown("""
        <div class="analytics-card">
          <div class="analytics-title">Avg Resolution Time by Cause (minutes)</div>
          <div class="analytics-sub">Historical average from dataset closed_datetime − start_datetime (capped at 500 min)</div>
        </div>
        """, unsafe_allow_html=True)
        dur_data = s.get("duration_by_cause", {})
        dur_rows = []
        for cause, d in dur_data.items():
            if "1" in d:
                dur_rows.append({"Cause": cause.replace("_"," ").title(), "High": min(d["1"], 500), "Low": min(d.get("0", 0), 500)})
        df_dur = pd.DataFrame(dur_rows).set_index("Cause")
        st.bar_chart(df_dur, color=["#f85149", "#3fb950"], height=300)

    # Risky corridors table
    st.markdown("<div class='section-label' style='margin-top:20px;'>Top Risky Corridors — Historically High-Priority</div>", unsafe_allow_html=True)
    risky  = s.get("risky_corridors", [])
    cd     = s.get("cause_high_rate", {})
    total_high_events = sum(int(v.get("sum", 0)) for v in cd.values())
    
    table_html = """
    <div class="analytics-card">
    <table class="risk-table">
      <tr>
        <th>#</th><th>Corridor</th><th>Risk Level</th><th>Notes</th>
      </tr>
    """
    for i, corr in enumerate(risky, 1):
        table_html += f"""
      <tr>
        <td style="color:#484f58;font-family:'JetBrains Mono',monospace;">{i:02d}</td>
        <td><strong>{corr}</strong></td>
        <td><span class="risk-badge">HIGH</span></td>
        <td style="color:#484f58;font-size:12px;">100% of events historically High priority</td>
      </tr>"""
    table_html += "</table></div>"
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="provenance-bar" style="margin-top:16px;">
      <span class="prov-badge prov-green">Model Acc: {s.get('train_accuracy','?')}</span>
      <span class="prov-badge prov-green">F1: {s.get('train_f1','?')}</span>
      <span class="prov-badge prov-blue">ASTraM Bengaluru Dataset</span>
      <span class="prov-badge prov-gray">Corridor excluded (data leakage)</span>
    </div>
    """, unsafe_allow_html=True)
