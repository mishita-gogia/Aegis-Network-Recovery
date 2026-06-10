import streamlit as st
import os
import requests
from openai import OpenAI

# --- PAGE SETUP ---
st.set_page_config(page_title="Aegis-Net | Autonomous Recovery", page_icon="🛡️", layout="wide")

# Professional Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .agent-card { padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; background-color: #1a1c24; margin-bottom: 20px; }
    .stButton>button { background-color: #ff4b4b; color: white; font-weight: bold; width: 100%; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- NVIDIA API LOGIC ---
# This looks for your secret key
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY")

def call_nvidia_agent(role_prompt, user_input):
    if not NVIDIA_API_KEY:
        return "⚠️ Error: No NVIDIA API Key found in Secrets."
    
    client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
    try:
        completion = client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

# --- DASHBOARD UI ---
st.title("🛡️ AEGIS-NET COMMAND CENTER")
st.markdown("### Team Code Flake!! | *Far Away by Zuup*")

with st.sidebar:
    st.header("⚙️ System Controls")
    scenario = st.selectbox("Select Incident", ["Train Derailment", "Tunnel Collapse", "Chemical Spill"])
    incident_data = st.text_area("Input Sensor Feed", f"ALERT: {scenario} detected in Sector 4. Multiple casualties reported. Structural damage confirmed.")
    st.divider()
    st.info("Powered by NVIDIA NIM & Llama-3-70B")

if st.button("🚨 INITIALIZE AUTONOMOUS RECOVERY"):
    # START AGENTIC CHAIN
    col1, col2 = st.columns(2)

    with st.status("📡 Scout Agent analyzing hazards...", expanded=True):
        scout_report = call_nvidia_agent("You are a crisis scout. Identify primary hazards and severity.", incident_data)
        st.write("Analysis Complete.")

    with col1:
        st.markdown(f"<div class='agent-card'><h4>🛰️ Scout Intelligence</h4><p>{scout_report}</p></div>", unsafe_allow_html=True)

    with st.status("🚛 Logistics Agent planning resource deployment...", expanded=True):
        logistics_plan = call_nvidia_agent("You are a logistics strategist. Plan emergency vehicle routes and transit rerouting based on the scout report.", scout_report)
        st.write("Strategy Finalized.")

    with col2:
        st.markdown(f"<div class='agent-card' style='border-left-color: #ffaa00;'><h4>🚛 Logistics Strategy</h4><p>{logistics_plan}</p></div>", unsafe_allow_html=True)

    with st.status("📢 Dispatcher Agent drafting emergency alerts...", expanded=True):
        final_alerts = call_nvidia_agent("You are an emergency dispatcher. Draft a technical brief for the Mayor and a red alert SMS for the public.", logistics_plan)
        st.write("Communications Dispatched.")

    st.success("✅ RECOVERY PROTOCOL GENERATED")
    st.markdown("### 📢 Official Communication Logs")
    st.write(final_alerts)
