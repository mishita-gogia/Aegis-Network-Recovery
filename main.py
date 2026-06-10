import streamlit as st
import os
import time
import requests
from openai import OpenAI

# --- CONFIGURATION ---
st.set_page_config(page_title="Aegis-Net | Autonomous Recovery", page_icon="🛡️", layout="wide")

# Custom CSS for Cyberpunk / Command Center Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 5px; border: none; height: 3em; }
    .stButton>button:hover { background-color: #ff3333; border: 1px solid white; }
    .agent-card { padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; background-color: #1a1c24; margin-bottom: 20px; }
    .status-ready { color: #00ff00; font-weight: bold; }
    </style>
    """, unsafe_content_label=True)

# --- API SETUP ---
# It looks for the key in Secrets first, then sidebar
api_key = os.environ.get("NVIDIA_API_KEY") or st.sidebar.text_input("Enter NVIDIA API Key", type="password")

def call_nvidia(prompt):
    if not api_key:
        st.error("Missing NVIDIA API Key!")
        return "ERROR"
    
    client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key)
    try:
        completion = client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"System Error: {str(e)}"

# --- APP UI ---
st.title("🛡️ AEGIS-NET")
st.subheader("Multi-Agent Autonomous Infrastructure Recovery System")

with st.sidebar:
    st.image("https://img.icons8.com/nolan/512/security-shield.png", width=100)
    st.markdown("### System Status: <span class='status-ready'>ONLINE</span>", unsafe_allow_html=True)
    st.divider()
    scenario = st.selectbox("Select Crisis Scenario", [
        "High-Speed Rail Derailment", 
        "Tunnel Structural Collapse", 
        "Hazardous Chemical Leak",
        "Bridge Failure - Critical Link"
    ])
    raw_input = st.text_area("Live Sensor Data Input", "A cargo train has derailed in Sector 7. Smoke detected. Nearby Northbound track is still active.")

# --- THE AGENTIC ENGINE ---
if st.button("🚨 INITIALIZE RECOVERY PROTOCOL"):
    if not api_key:
        st.warning("Please provide an API Key in the sidebar or Secrets.")
    else:
        col1, col2 = st.columns([1, 1])

        # STEP 1: SCOUT AGENT
        with st.status("🛰️ Scout Agent: Analyzing Hazards...", expanded=True) as status:
            scout_output = call_nvidia(f"You are the Scout AI. Analyze this crisis and list hazards: {raw_input}")
            time.sleep(1) # Visual delay for the "Wow" factor
            status.update(label="🛰️ Analysis Complete", state="complete")
        
        with col1:
            st.markdown(f"<div class='agent-card'><h4>🛰️ Scout Intelligence Report</h4><p>{scout_output}</p></div>", unsafe_allow_html=True)

        # STEP 2: LOGISTICS AGENT
        with st.status("🚛 Logistics AI: Orchestrating Resources...", expanded=True) as status:
            logistics_output = call_nvidia(f"You are the Logistics Manager. Based on this report: {scout_output}, create a resource deployment plan.")
            time.sleep(1)
            status.update(label="🚛 Logistics Strategy Finalized", state="complete")
        
        with col2:
            st.markdown(f"<div class='agent-card' style='border-left: 5px solid #ffaa00;'><h4>🚛 Deployment Strategy</h4><p>{logistics_output}</p></div>", unsafe_allow_html=True)

        # STEP 3: DISPATCHER AGENT
        with st.status("📢 Dispatcher: Issuing Emergency Alerts...", expanded=True) as status:
            dispatch_output = call_nvidia(f"You are the Dispatcher. Based on this plan: {logistics_output}, write a Public Red Alert and a Mayor's Briefing.")
            time.sleep(1)
            status.update(label="📢 Alerts Transmitted", state="complete")

        st.divider()
        st.success("✅ MISSION RECOVERY PLAN GENERATED")
        st.markdown(f"### 📢 Public & Govt Communications\n{dispatch_output}")
