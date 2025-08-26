import streamlit as st
import pandas as pd
import base64
from datetime import datetime
from src.agent import WaterIntakeAgent
from src.database import log_intake, get_intake_history

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="AI Water Intake Tracker ",
    page_icon="🥤",
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_anchor = """ 
   <style> 
   .css-1y0tads, .css-1v3fvcr, .css-zt5igj {display: none 
   !important;} 
   .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a
    {display: none !important;} </style> """
st.markdown(hide_anchor, unsafe_allow_html=True)



# -----------------------------
# Function to add background
# -----------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: #E0E0E0 !important;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
        }}
        .welcome-text {{
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.9);
        }}
        .welcome-subtext {{
            text-align: center;
            font-size: 1.2em;
            line-height: 1.6;
            margin-bottom: 30px;
            text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
        }}
        .custom-card {{
            background-color: rgba(0, 0, 50, 0.8);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #E0E0E0;
        }}
        .metric-card {{
            background-color: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .stProgress > div > div > div {{
            background-color: #2193b0;
        }}
        div.stButton > button:first-child {{
            background-color: #4FC3F7;
            color: white;
            font-size: 14px;
            font-weight: bold;
            padding: 6px 16px;
            border: none;
            border-radius: 4px;
            width: 100%;
        }}
        div.stButton > button:hover {{
            background-color: #0288D1;
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background
add_bg_from_local("src/water-drops-texture-background-blue-design.jpg")

# -----------------------------
# Initialize session state
# -----------------------------
if "tracker_started" not in st.session_state:
    st.session_state.tracker_started = False
if "latest_ai_feedback" not in st.session_state:
    st.session_state.latest_ai_feedback = None

# -----------------------------
# Welcome Section
# -----------------------------
if not st.session_state.tracker_started:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="welcome-text"><h1>🥤 Welcome to AI Water Intake Tracker!</h1></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="welcome-subtext">
            <h3> <b>Track your daily water intake</b> and get <b>AI-powered insights</b></h3>
            <h3>to stay <b>hydrated</b> and <b>healthy</b> every day! 🌿</h3>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            if st.button("🚀 Start Tracking", key="start_btn", use_container_width=True):
                st.session_state.tracker_started = True
                st.rerun()

# -----------------------------
# Main Tracker Section
# -----------------------------
if st.session_state.tracker_started:
    st.title("📊 AI Water Intake Tracker")
    st.markdown("💦 Keep logging your water intake and watch your hydration trends grow!")

    # Sidebar
    with st.sidebar:
        st.header("📝 Log Your Water Intake")

        with st.form("intake_form"):
            user_id = st.text_input("👤 User ID:", value="")
            intake_ml = st.number_input("🥤 Water intake (ml):", min_value=0, step=100, value=500)
            intake_time = st.time_input("⏰ Time:", value=datetime.now().time())
            intake_date = st.date_input("📅 Date:", value=datetime.now())

            submitted = st.form_submit_button("✅ Submit Intake")
            if submitted:
                if user_id and intake_ml > 0:
                    timestamp = datetime.combine(intake_date, intake_time)
                    log_intake(user_id, intake_ml, timestamp)
                    st.success(f"✅ Logged *{intake_ml} ml* for *{user_id}*")
                    agent = WaterIntakeAgent()
                    feedback = agent.analyze_intake(intake_ml / 1000)  # liters
                    st.session_state.latest_ai_feedback = feedback
                else:
                    st.error("Please enter a valid user ID and water intake amount.")

        st.markdown("---")
        st.header("🔍 Filter History")
        date_filter = st.selectbox("View intake for:", ["Today", "Last 7 days", "Last 30 days", "All time"])

        st.header("🎯 Daily Goal")
        daily_goal = st.number_input("Daily water goal (ml):", min_value=500, step=100, value=2000)

    # Main Columns
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("📈 Today's Hydration Progress")
        today_intake = 0  # Replace with DB fetch
        progress = min(today_intake / daily_goal, 1.0) if daily_goal > 0 else 0
        progress_col1, progress_col2 = st.columns([3, 1])
        with progress_col1:
            st.progress(progress)
        with progress_col2:
            st.metric("Today's Intake", f"{today_intake} ml", f"{today_intake}/{daily_goal} ml")

        st.header("🤖 AI Feedback")
        if st.session_state.latest_ai_feedback:
            st.markdown(f"<div class='custom-card'>{st.session_state.latest_ai_feedback}</div>", unsafe_allow_html=True)
        else:
            st.info("Log your water intake to see AI feedback here.")

    with col2:
        st.header("📊 Quick Stats")
        stats_data = {
            "Avg Daily Intake": "1,800 ml",
            "Weekly Trend": "+12%",
            "Goal Completion": "75%",
            "Last Intake": "2 hours ago"
        }
        for stat, value in stats_data.items():
            st.markdown(f"<div class='metric-card'><h4>{stat}</h4><h3>{value}</h3></div>", unsafe_allow_html=True)

    st.header("📅 Water Intake History")
    history = get_intake_history(user_id)
    if history:
        df = pd.DataFrame(history, columns=["Date", "Time", "Amount (ml)"])
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export History as CSV",
            data=csv,
            file_name="water_intake_history.csv",
            mime="text/csv",
        )
    else:
        st.info("No intake history found. Start logging your water intake to see your history here.")

    if st.button("← Back to Welcome"):
        st.session_state.tracker_started = False
        st.rerun()

# -----------------------------
# Footer (Always at the bottom)
# -----------------------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        text-align: center;
        padding: 10px 0;
        background-color: rgba(0, 0, 0, 0.5);
        color: #E0E0E0;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
    }
    .footer a {
        color: #E0E0E0;
        margin: 0 10px;
        text-decoration: none;
    }
    .footer a:hover {
        color: #4FC3F7;
    }
    .social-icon {
        width: 24px;
        height: 24px;
        vertical-align: middle;
        margin-right: 5px;
    }
    </style>

    <div class="footer">
        Follow us on:
        <a href="https://www.instagram.com/ankitsingh37272/" target="_blank">
            <img class="social-icon" src="https://cdn-icons-png.flaticon.com/512/174/174855.png">Instagram
        </a>
        |
        <a href="https://www.linkedin.com/in/ankit-singh-b93b18211/" target="_blank">
            <img class="social-icon" src="https://cdn-icons-png.flaticon.com/512/174/174857.png">LinkedIn
        </a>
        |
        <a href="https://x.com/ankitsingh163" target="_blank">
            <img class="social-icon" src="https://cdn-icons-png.flaticon.com/512/733/733579.png">Twitter
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
