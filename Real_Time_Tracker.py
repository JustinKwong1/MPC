import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# === PAGE SETTINGS ===
st.set_page_config(page_title="MPC Data Tracker", layout="wide")
st.title("📡 MPC + Sensor Data Realtime Monitor")

# === AUTO-REFRESH (every 5 minutes) ===
st.markdown("""
    <meta http-equiv="refresh" content="300">
""", unsafe_allow_html=True)
st.caption(f"🔄 Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# === DATABASE SETTINGS ===
DB_FILE = 'weather_data.db'

def load_latest_two_entries():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query('SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 2', conn)
    conn.close()
    return df[::-1].reset_index(drop=True)  # Reverse so latest is index 1

# === LOAD DATA ===
df_latest_two = load_latest_two_entries()

st.subheader("System Status")

if df_latest_two.empty or len(df_latest_two) < 2:
    st.error("Not enough data to compare. Need at least two entries.")
else:
    current = df_latest_two.iloc[1]
    previous = df_latest_two.iloc[0]

    # Timestamp-based system status
    timestamp_obj = pd.to_datetime(current['timestamp'])
    latest_time_str = timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')
    time_diff = datetime.now() - timestamp_obj

    # === 3-COLUMN LAYOUT ===
    for col in df_latest_two.columns:
        if col == 'timestamp':
            continue

        val_current = current[col]
        val_previous = previous[col]

        label_col, status_col = st.columns([3, 1])

        with label_col:
            st.markdown(f"**{col}**: {val_current}")

        with status_col:
            if pd.isna(val_current):
                st.markdown('<span style="color: white; background-color: red; padding: 2px 6px; border-radius: 6px; font-size: 0.8rem;">❌ missing</span>', unsafe_allow_html=True)
            elif val_current == val_previous:
                st.markdown('<span style="color: black; background-color: yellow; padding: 2px 6px; border-radius: 6px; font-size: 0.8rem;">⚠️ unchanged</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color: white; background-color: green; padding: 2px 6px; border-radius: 6px; font-size: 0.8rem;">✅ OK</span>', unsafe_allow_html=True)

    
    # === OPTIONAL: LAST 20 ENTRIES ===
    st.markdown("---")
    if st.checkbox("Show last 20 entries"):
        conn = sqlite3.connect(DB_FILE)
        df_recent = pd.read_sql_query('SELECT * FROM weather_data ORDER BY timestamp DESC LIMIT 20', conn)
        conn.close()
        df_recent['timestamp'] = pd.to_datetime(df_recent['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        st.dataframe(df_recent)
