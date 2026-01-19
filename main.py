import streamlit as st
from datetime import date
from modules import database as db
from views import academics, finance, health, timer

# Version: 1.3 - Added focus mode toggle (with/without rev meter)
# Page config
st.set_page_config(page_title="Life OS Dashboard", page_icon="🧭", layout="wide")

# Initialize mobile mode in session state
if 'mobile_mode' not in st.session_state:
    st.session_state.mobile_mode = False

# FORCE LIGHT MODE WITH INLINE CSS + MOBILE RESPONSIVE
mobile_css = """
/* MOBILE MODE OVERRIDES */
.block-container {
  padding: 1rem 0.5rem !important;
  max-width: 100% !important;
}

[data-testid="stSidebar"] {
  display: none !important;
}

.stMetric {
  font-size: 0.9rem !important;
}

.stMetricValue {
  font-size: 1.2rem !important;
}

h1 {
  font-size: 1.5rem !important;
}

h2 {
  font-size: 1.2rem !important;
}

.apple-card {
  padding: 16px !important;
  margin-bottom: 12px !important;
}

.stButton button {
  width: 100% !important;
  padding: 0.75rem !important;
}

input, .stDateInput, .stTextInput, .stSelectbox {
  font-size: 16px !important;
}

.stExpander {
  margin: 8px 0 !important;
}
""" if st.session_state.mobile_mode else ""

css_base = '''
<style>
:root {
  --bg: #f5f5f7;
  --text: #0f172a;
  --card: #ffffff;
  --muted: #475569;
  --shadow: 0 10px 30px rgba(0, 0, 0, 0.07);
  --radius: 16px;
  --accent: #007aff;
}

/* FORCE EVERYTHING TO LIGHT MODE */
html, body, [class*="css"], .stApp, .main, .block-container, section {
  background: #f5f5f7 !important;
  color: #0f172a !important;
}

/* SIDEBAR: FORCE WHITE BACKGROUND AND DARK TEXT */
[data-testid="stSidebar"] {
  background: #ffffff !important;
  border-right: 1px solid #e5e5ea !important;
}

[data-testid="stSidebar"] *,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: #0f172a !important;
  background-color: transparent !important;
}

.stMetricValue,
.stMetricLabel {
  color: #0f172a !important;
  font-weight: 600 !important;
}

/* Radio buttons - make them look like navigation pills */
[data-testid="stSidebar"] [role="radiogroup"] label {
  color: #0f172a !important;
  padding: 12px 16px !important;
  border-radius: 10px !important;
  margin: 4px 0 !important;
  transition: all 0.2s ease !important;
}

[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: #f5f5f7 !important;
}

.apple-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.07);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-bottom: 20px;
  color: #0f172a !important;
}

.apple-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.1);
}

h1, h2, h3, p, li, label, span, div, a {
  color: #0f172a !important;
}

div[data-baseweb="input"] > div,
.stDateInput input,
.stSelectbox [data-baseweb="select"] {
  background: #ffffff !important;
  color: #000000 !important;
  border: 1px solid #d1d1d6 !important;
  border-radius: 10px !important;
}

.stButton button {
  background: #007aff;
  color: #fff;
  border-radius: 10px;
  border: none;
  padding: 0.5rem 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.stButton button:hover {
  background: #0051d5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

''' + mobile_css + '''
</style>
'''

st.markdown(css_base, unsafe_allow_html=True)

# Initialize DB
db.init_db()

# Mobile toggle at the top
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("<h1 style='margin-bottom: 0;'>Life OS Dashboard</h1>", unsafe_allow_html=True)
with col2:
    if st.button("📱" if not st.session_state.mobile_mode else "💻", help="Toggle Mobile/Desktop Mode"):
        st.session_state.mobile_mode = not st.session_state.mobile_mode
        st.rerun()

st.caption("Track your progress across academics, finance, and health")
st.write("")

# Conditional navigation based on mode
if st.session_state.mobile_mode:
    # Mobile: Use horizontal tabs instead of sidebar
    view = st.radio("", ["📚 Academics", "💰 Finance", "💪 Health", "⏱️ Timer"], horizontal=True, label_visibility="collapsed")
    st.write("---")
else:
    # Desktop: Use sidebar
    st.sidebar.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🎯</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("<h2 style='text-align: center; margin-top: 0; font-size: 24px;'>2026 Goals</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #e5e5ea;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center; font-weight: 600; margin-bottom: 12px; color: #86868b;'>NAVIGATE</p>", unsafe_allow_html=True)

    view = st.sidebar.radio("Navigation", ["📚 Academics", "💰 Finance", "💪 Health", "⏱️ Timer"], label_visibility="collapsed")

    st.sidebar.markdown("<hr style='margin: 20px 0; border: none; border-top: 1px solid #e5e5ea;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align: center; font-size: 12px; color: #86868b; margin-top: 40px;'>Life OS Dashboard v1.0<br>Track • Analyze • Achieve</p>", unsafe_allow_html=True)

if "Academics" in view:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    academics.render()
    st.markdown('</div>', unsafe_allow_html=True)
elif "Finance" in view:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    finance.render()
    st.markdown('</div>', unsafe_allow_html=True)
elif "Health" in view:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    health.render()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="apple-card">', unsafe_allow_html=True)
    timer.render()
    st.markdown('</div>', unsafe_allow_html=True)
