import streamlit as st
import os
import time
import random
from datetime import datetime
from io import BytesIO
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas as pdf_canvas

st.set_page_config(
    page_title="AEGIS-NET | Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&family=Orbitron:wght@400;700;900&display=swap');

/* ─── Root & Global ─── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #060d1a !important;
    color: #c8d8e8 !important;
    font-family: 'Rajdhani', sans-serif !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f20 0%, #040a15 100%) !important;
    border-right: 1px solid #0f3460 !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.block-container { padding-top: 1rem !important; }

/* ─── Header Banner ─── */
.aegis-header {
    background: linear-gradient(135deg, #060d1a 0%, #0a1628 40%, #060d1a 100%);
    border: 1px solid #0f3460;
    border-top: 3px solid #00d4ff;
    border-radius: 8px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.08), inset 0 0 60px rgba(0, 212, 255, 0.03);
}
.aegis-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff, #ff3366, #00d4ff, transparent);
    animation: scanline 4s linear infinite;
}
@keyframes scanline {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}
.aegis-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2.4rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, #00d4ff, #7b61ff, #00d4ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: shimmer 3s linear infinite;
    letter-spacing: 4px;
    margin: 0;
}
@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}
.aegis-subtitle {
    font-family: 'Share Tech Mono', monospace;
    color: #4a7fa5;
    font-size: 0.75rem;
    letter-spacing: 3px;
    margin-top: 0.3rem;
    text-transform: uppercase;
}
.status-row {
    display: flex;
    gap: 1.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.status-chip {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    padding: 3px 10px;
    border-radius: 2px;
    letter-spacing: 2px;
}
.chip-online { background: rgba(0,255,136,0.1); border: 1px solid #00ff88; color: #00ff88; }
.chip-alert  { background: rgba(255,51,102,0.1); border: 1px solid #ff3366; color: #ff3366; animation: pulse-red 1.5s ease-in-out infinite; }
.chip-info   { background: rgba(0,212,255,0.1); border: 1px solid #00d4ff; color: #00d4ff; }
@keyframes pulse-red {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255,51,102,0.4); }
    50%       { box-shadow: 0 0 8px 3px rgba(255,51,102,0.2); }
}

/* ─── Section Headings ─── */
.section-heading {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 3px;
    color: #4a7fa5;
    text-transform: uppercase;
    border-bottom: 1px solid #0f3460;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}

/* ─── Input Area ─── */
[data-testid="stTextArea"] textarea {
    background: #080f20 !important;
    border: 1px solid #0f3460 !important;
    color: #a8c8e8 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 4px !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #00d4ff !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
}

/* ─── Launch Button ─── */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #1a0520, #300a10) !important;
    border: 2px solid #ff3366 !important;
    color: #ff3366 !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 3px !important;
    padding: 1rem 3rem !important;
    border-radius: 4px !important;
    width: 100% !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(255,51,102,0.3), inset 0 0 20px rgba(255,51,102,0.05) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #300a10, #500a18) !important;
    box-shadow: 0 0 40px rgba(255,51,102,0.5), inset 0 0 30px rgba(255,51,102,0.1) !important;
    transform: translateY(-1px) !important;
}

/* ─── Agent Cards ─── */
.agent-card {
    background: linear-gradient(135deg, #080f20 0%, #0a1428 100%);
    border: 1px solid #0f3460;
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    position: relative;
    box-shadow: 0 0 20px rgba(0,0,0,0.4), inset 0 0 30px rgba(0,0,0,0.2);
}
.agent-card::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 80px; height: 80px;
    background: radial-gradient(circle at top right, rgba(255,255,255,0.02), transparent);
    border-radius: 0 6px 0 0;
}
.agent-card-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.8rem;
}
.agent-icon {
    font-size: 1.6rem;
    filter: drop-shadow(0 0 8px var(--accent));
}
.agent-name {
    font-family: 'Orbitron', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
}
.agent-role {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #4a7fa5;
    letter-spacing: 1px;
}
.agent-output {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.95rem;
    color: #c8d8e8;
    line-height: 1.6;
    white-space: pre-wrap;
    border-top: 1px solid #0f3460;
    padding-top: 0.8rem;
    margin-top: 0.4rem;
}
.badge {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    padding: 2px 8px;
    border-radius: 2px;
    letter-spacing: 1px;
    margin-left: auto;
}
.badge-scout      { background: rgba(123,97,255,0.15); border: 1px solid #7b61ff; color: #7b61ff; }
.badge-logistics  { background: rgba(0,212,255,0.15); border: 1px solid #00d4ff; color: #00d4ff; }
.badge-dispatcher { background: rgba(255,51,102,0.15); border: 1px solid #ff3366; color: #ff3366; }

/* ─── st.status override ─── */
[data-testid="stStatusWidget"] {
    background: #080f20 !important;
    border: 1px solid #0f3460 !important;
    border-radius: 6px !important;
}

/* ─── Sidebar ─── */
.sidebar-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    color: #2a5f8f;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.health-metric {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid #0a1e35;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
}
.health-label { color: #4a7fa5; }
.health-value { color: #00ff88; font-weight: bold; }
.health-warn  { color: #ffaa00; font-weight: bold; }
.health-crit  { color: #ff3366; font-weight: bold; animation: pulse-red 1.5s infinite; }

[data-testid="stSelectbox"] > div > div {
    background: #080f20 !important;
    border: 1px solid #0f3460 !important;
    color: #a8c8e8 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}
[data-testid="stTextInput"] input {
    background: #080f20 !important;
    border: 1px solid #0f3460 !important;
    color: #a8c8e8 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ─── Divider ─── */
hr {
    border: none !important;
    border-top: 1px solid #0f3460 !important;
    margin: 1.5rem 0 !important;
}

/* ─── Metric numbers ─── */
[data-testid="stMetric"] {
    background: #080f20;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 0.5rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.6rem !important;
    color: #4a7fa5 !important;
    letter-spacing: 2px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    color: #00d4ff !important;
    font-size: 1.3rem !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #060d1a; }
::-webkit-scrollbar-thumb { background: #0f3460; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
</style>
"""

SCENARIOS = {
    "High-Speed Rail Derailment": {
        "description": "Multiple passenger cars have derailed at 280 km/h near an urban corridor. Reports of casualties, fuel leaks, and compromised bridge supports at the incident site.",
        "emoji": "🚄",
        "threat": "CRITICAL"
    },
    "Bridge Structural Failure": {
        "description": "Sensor arrays on the Northgate suspension bridge are registering critical tension anomalies in main cables. Traffic load at 94%. Seismic micro-activity detected in foundations.",
        "emoji": "🌉",
        "threat": "CRITICAL"
    },
    "Chemical Plant Explosion": {
        "description": "Explosions at the Meridian Chemical Complex, Unit-7. HAZMAT sensors detecting chlorine and ammonia compounds at 3x safe thresholds. Wind patterns directing plume toward residential zones.",
        "emoji": "🏭",
        "threat": "EXTREME"
    },
    "Coastal Flood Emergency": {
        "description": "Category 4 storm surge exceeding 5.2m breaching coastal defenses. Inundation spreading inland at 2km/hr. Power grid substations at risk. Evacuation routes partially compromised.",
        "emoji": "🌊",
        "threat": "SEVERE"
    },
    "Power Grid Cascade Failure": {
        "description": "Cascading failure detected across NE grid sector. 3 major substations offline. Load imbalance risk at 87%. Critical infrastructure — hospitals, water treatment, emergency comms — on backup power.",
        "emoji": "⚡",
        "threat": "CRITICAL"
    },
    "Urban Earthquake Response": {
        "description": "Magnitude 6.8 earthquake. Structural collapse reported in 4 districts. Gas main ruptures at 12 locations. Underground transit tunnels status unknown. Hospital infrastructure status: degraded.",
        "emoji": "🏙️",
        "threat": "EXTREME"
    },
    "[Custom Input]": {
        "description": "",
        "emoji": "🛠️",
        "threat": "UNKNOWN"
    }
}

SCOUT_SYSTEM = """You are SCOUT-1, an elite AI hazard analysis agent embedded in the AEGIS-NET emergency response system.
Your mission: Analyze raw sensor data and field reports to produce a precise tactical threat assessment.
Structure your analysis as:
1. HAZARD IDENTIFICATION — List all detected hazards with severity codes (CRITICAL/HIGH/MODERATE/LOW)
2. CASUALTY RISK ASSESSMENT — Estimated affected population, injury probability zones
3. INFRASTRUCTURE IMPACT — Affected systems (transport, power, comms, water, medical)
4. ENVIRONMENTAL FACTORS — Weather, terrain, secondary risk amplifiers
5. SCOUT VERDICT — Overall threat level and top 3 priority actions for the logistics team
Be precise, technical, and use emergency management terminology. No fluff."""

LOGISTICS_SYSTEM = """You are LOGISTICS-ALPHA, a strategic AI resource deployment planner in the AEGIS-NET system.
You receive a threat assessment from SCOUT-1 and must create a tactical deployment plan.
Structure your response as:
1. RESOURCE DEPLOYMENT MATRIX — What assets (personnel, equipment, vehicles) to deploy, where, and how many
2. TRANSIT CORRIDOR REROUTING — Road/rail/air corridors to close, redirect, or prioritize
3. STAGING AREA DESIGNATION — Forward operating bases, triage points, supply depot locations
4. INTER-AGENCY COORDINATION — Which agencies to activate (FEMA, Coast Guard, National Guard, etc.)
5. TIMELINE — 0-1hr / 1-6hr / 6-24hr / 24-72hr action phases
6. LOGISTICS VERDICT — Critical path bottleneck and single most important action right now
Be decisive, tactical, and resource-specific."""

DISPATCHER_SYSTEM = """You are DISPATCH-OMEGA, the AI emergency communications director of the AEGIS-NET system.
You receive the full tactical situation and logistics plan. Your mission: generate public communications and government briefs.
Structure your output as:
--- PUBLIC EMERGENCY ALERT ---
[Short, clear public alert in plain language for broadcast — max 120 words]

--- EVACUATION INSTRUCTIONS ---
[Specific numbered steps for civilians to follow]

--- TECHNICAL GOVERNMENT BRIEF ---
[Classified-style brief for emergency management officials: situation summary, resources deployed, projected outcomes, resource gaps, recommended policy actions]

--- MEDIA STATEMENT ---
[Official press release opening paragraph for news briefing]

Use appropriate urgency and authoritative language. The public alert must be clear and panic-free."""


def get_client(api_key: str) -> OpenAI:
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )


def stream_agent(client: OpenAI, system_prompt: str, user_content: str, placeholder) -> str:
    full_text = ""
    try:
        stream = client.chat.completions.create(
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.65,
            max_tokens=1200,
            stream=True,
            top_p=0.9
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_text += delta
                placeholder.markdown(
                    f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.82rem;'
                    f'color:#8ab8d8;white-space:pre-wrap;line-height:1.6;">{full_text}▌</div>',
                    unsafe_allow_html=True
                )
    except Exception as e:
        full_text = f"[AGENT ERROR]: {str(e)}"
        placeholder.error(full_text)
    return full_text


def render_agent_card(icon: str, name: str, role: str, badge_class: str, output: str, accent: str):
    st.markdown(
        f"""
        <div class="agent-card" style="--accent:{accent}">
            <div class="agent-card-header">
                <span class="agent-icon">{icon}</span>
                <div>
                    <div class="agent-name">{name}</div>
                    <div class="agent-role">{role}</div>
                </div>
                <span class="badge {badge_class}">COMPLETED</span>
            </div>
            <div class="agent-output">{output}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_health_row(label: str, value: str, css_class: str = "health-value"):
    st.markdown(
        f'<div class="health-metric"><span class="health-label">{label}</span>'
        f'<span class="{css_class}">{value}</span></div>',
        unsafe_allow_html=True
    )


def generate_pdf(
    scenario: str,
    threat: str,
    sensor_data: str,
    scout: str,
    logistics: str,
    dispatcher: str,
    timestamp: str,
) -> bytes:
    buf = BytesIO()

    # ── Colour palette ───────────────────────────────────────────────────────
    C_BG        = colors.HexColor("#060d1a")
    C_HEADER_BG = colors.HexColor("#080f20")
    C_BORDER    = colors.HexColor("#0f3460")
    C_CYAN      = colors.HexColor("#00d4ff")
    C_PURPLE    = colors.HexColor("#7b61ff")
    C_RED       = colors.HexColor("#ff3366")
    C_GREEN     = colors.HexColor("#00ff88")
    C_AMBER     = colors.HexColor("#ffaa00")
    C_TEXT      = colors.HexColor("#c8d8e8")
    C_MUTED     = colors.HexColor("#4a7fa5")
    C_WHITE     = colors.white

    threat_color = C_RED if threat in ("CRITICAL", "EXTREME") else (C_AMBER if threat == "SEVERE" else C_CYAN)

    W, H = A4

    # ── Page template with header/footer ────────────────────────────────────
    def draw_page_chrome(c, doc):
        c.saveState()
        # Full dark background
        c.setFillColor(C_BG)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        # Top cyan accent bar
        c.setFillColor(C_CYAN)
        c.rect(0, H - 6, W, 6, fill=1, stroke=0)

        # Header band
        c.setFillColor(C_HEADER_BG)
        c.rect(0, H - 36, W, 30, fill=1, stroke=0)

        c.setFont("Courier-Bold", 9)
        c.setFillColor(C_CYAN)
        c.drawString(20, H - 26, "AEGIS-NET  |  INCIDENT RECOVERY REPORT")
        c.setFont("Courier", 7)
        c.setFillColor(C_MUTED)
        c.drawRightString(W - 20, H - 26, f"GENERATED: {timestamp}  |  CLASSIFICATION: FOR OFFICIAL USE ONLY")

        # Bottom accent bar
        c.setFillColor(C_BORDER)
        c.rect(0, 0, W, 18, fill=1, stroke=0)
        c.setFillColor(C_RED)
        c.rect(0, 0, W, 3, fill=1, stroke=0)

        c.setFont("Courier", 6.5)
        c.setFillColor(C_MUTED)
        c.drawCentredString(W / 2, 6, f"AEGIS-NET AUTONOMOUS RECOVERY SYSTEM  •  PAGE {doc.page}  •  CONFIDENTIAL")
        c.restoreState()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=46,
        bottomMargin=26,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"AEGIS-NET Incident Report — {scenario}",
    )

    # ── Styles ───────────────────────────────────────────────────────────────
    def style(name, **kw):
        return ParagraphStyle(
            name,
            fontName=kw.get("fontName", "Courier"),
            fontSize=kw.get("fontSize", 9),
            textColor=kw.get("textColor", C_TEXT),
            alignment=kw.get("alignment", TA_LEFT),
            leading=kw.get("leading", 14),
            spaceAfter=kw.get("spaceAfter", 2),
            spaceBefore=kw.get("spaceBefore", 0),
            backColor=kw.get("backColor", None),
            leftIndent=kw.get("leftIndent", 0),
            rightIndent=kw.get("rightIndent", 0),
        )

    s_title    = style("title",    fontName="Courier-Bold", fontSize=22, textColor=C_CYAN,   alignment=TA_CENTER, leading=28, spaceAfter=4)
    s_subtitle = style("subtitle", fontName="Courier",      fontSize=8,  textColor=C_MUTED,  alignment=TA_CENTER, leading=12, spaceAfter=14)
    s_agent    = style("agent",    fontName="Courier-Bold", fontSize=11, textColor=C_CYAN,   leading=16, spaceAfter=4, spaceBefore=10)
    s_role     = style("role",     fontName="Courier",      fontSize=7,  textColor=C_MUTED,  leading=10, spaceAfter=6)
    s_body     = style("body",     fontName="Courier",      fontSize=8,  textColor=C_TEXT,   leading=12, spaceAfter=2)
    s_sensor   = style("sensor",   fontName="Courier",      fontSize=7.5,textColor=C_MUTED,  leading=11, spaceAfter=2, leftIndent=6)
    s_label    = style("label",    fontName="Courier-Bold", fontSize=7,  textColor=C_MUTED,  leading=10)
    s_value    = style("value",    fontName="Courier-Bold", fontSize=7,  textColor=C_WHITE,  leading=10)

    story = []

    # ── Cover block ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(Paragraph("AEGIS-NET", s_title))
    story.append(Paragraph("MULTI-AGENT AUTONOMOUS INFRASTRUCTURE RECOVERY REPORT", s_subtitle))

    # Metadata table
    meta_data = [
        ["INCIDENT TYPE", scenario.upper(), "THREAT LEVEL", threat],
        ["TIMESTAMP (UTC)", timestamp,       "AI MODEL",     "meta/llama-3.1-70b-instruct"],
        ["AGENTS DEPLOYED", "3 (SCOUT-1 / LOGISTICS-ALPHA / DISPATCH-OMEGA)", "STATUS", "COMPLETE"],
    ]
    meta_col_widths = [38*mm, 62*mm, 38*mm, 42*mm]
    meta_tbl = Table(meta_data, colWidths=meta_col_widths)
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), C_HEADER_BG),
        ("GRID",        (0, 0), (-1, -1), 0.5, C_BORDER),
        ("FONTNAME",    (0, 0), (0, -1),  "Courier-Bold"),
        ("FONTNAME",    (2, 0), (2, -1),  "Courier-Bold"),
        ("FONTNAME",    (1, 0), (1, -1),  "Courier"),
        ("FONTNAME",    (3, 0), (3, -1),  "Courier"),
        ("FONTSIZE",    (0, 0), (-1, -1), 7),
        ("TEXTCOLOR",   (0, 0), (0, -1),  C_MUTED),
        ("TEXTCOLOR",   (2, 0), (2, -1),  C_MUTED),
        ("TEXTCOLOR",   (1, 0), (1, -1),  C_WHITE),
        ("TEXTCOLOR",   (3, 0), (3, -1),  threat_color),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",(0, 0), (-1, -1), 6),
        ("LINEABOVE",   (0, 0), (-1, 0),  2, C_CYAN),
    ]))
    story.append(meta_tbl)
    story.append(Spacer(1, 8))

    # Sensor data box
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BORDER))
    story.append(Spacer(1, 4))
    story.append(Paragraph("◈  RAW SENSOR / FIELD REPORT", s_label))
    story.append(Spacer(1, 3))
    sensor_tbl = Table([[Paragraph(sensor_data.strip(), s_sensor)]], colWidths=[170*mm])
    sensor_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_HEADER_BG),
        ("BOX",          (0,0), (-1,-1), 0.5, C_BORDER),
        ("LEFTLINEBEFORE",(0,0),(-1,-1), 2, C_PURPLE),
        ("TOPPADDING",   (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(sensor_tbl)
    story.append(Spacer(1, 10))

    # ── Agent output sections ────────────────────────────────────────────────
    agents = [
        ("SCOUT-1",          "Hazard Identification & Threat Assessment Agent",    C_PURPLE, scout),
        ("LOGISTICS-ALPHA",  "Resource Deployment & Transit Rerouting Strategist", C_CYAN,   logistics),
        ("DISPATCH-OMEGA",   "Emergency Communications & Government Briefing Director", C_RED, dispatcher),
    ]

    for ag_name, ag_role, ag_color, ag_text in agents:
        # Section header bar
        header_tbl = Table(
            [[Paragraph(f"▶  {ag_name}", ParagraphStyle("ah", fontName="Courier-Bold", fontSize=11, textColor=ag_color, leading=16)),
              Paragraph("COMPLETED", ParagraphStyle("ab", fontName="Courier-Bold", fontSize=7, textColor=ag_color, leading=16, alignment=TA_RIGHT))]],
            colWidths=[140*mm, 30*mm]
        )
        header_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), C_HEADER_BG),
            ("LINEBELOW",     (0,0),(-1,-1), 1.5, ag_color),
            ("LINEABOVE",     (0,0),(-1,-1), 0.3, C_BORDER),
            ("LEFTPADDING",   (0,0),(-1,-1), 8),
            ("RIGHTPADDING",  (0,0),(-1,-1), 8),
            ("TOPPADDING",    (0,0),(-1,-1), 5),
            ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ]))
        story.append(KeepTogether([
            header_tbl,
            Spacer(1, 2),
            Paragraph(ag_role, ParagraphStyle("ar", fontName="Courier", fontSize=6.5, textColor=C_MUTED, leading=10, spaceAfter=6)),
        ]))

        # Body text
        for line in ag_text.strip().split("\n"):
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 3))
            elif stripped.startswith("---") or stripped.isupper() and len(stripped) < 60:
                story.append(Paragraph(
                    stripped,
                    ParagraphStyle("sec", fontName="Courier-Bold", fontSize=8, textColor=ag_color, leading=13, spaceBefore=6, spaceAfter=2)
                ))
            else:
                story.append(Paragraph(stripped, s_body))

        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.4, color=C_BORDER))
        story.append(Spacer(1, 4))

    doc.build(story, onFirstPage=draw_page_chrome, onLaterPages=draw_page_chrome)
    return buf.getvalue()


def simulate_health():
    return {
        "CPU Load": (f"{random.randint(34, 58)}%", "health-value"),
        "Memory": (f"{random.randint(61, 74)}%", "health-warn"),
        "Network Uplink": ("NOMINAL", "health-value"),
        "Agent Pool": ("3 / 3 READY", "health-value"),
        "NVIDIA API": ("CONNECTED", "health-value"),
        "Threat DB": ("LIVE SYNC", "health-value"),
        "Response Latency": (f"{random.randint(42, 89)}ms", "health-value"),
        "Uptime": ("99.97%", "health-value"),
    }


# ─── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Orbitron\',monospace;font-size:1rem;font-weight:700;'
        'color:#00d4ff;letter-spacing:3px;padding:0.5rem 0 1rem;text-align:center;'
        'border-bottom:1px solid #0f3460;margin-bottom:1rem;">🛡️ AEGIS-NET<br>'
        '<span style="font-size:0.55rem;color:#2a5f8f;letter-spacing:4px;font-weight:400;">'
        'COMMAND INTERFACE v2.4</span></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="section-heading">⬡ SYSTEM HEALTH</div>', unsafe_allow_html=True)
    health = simulate_health()
    for label, (val, css_cls) in health.items():
        render_health_row(label, val, css_cls)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-heading">⬡ CONFIGURATION</div>', unsafe_allow_html=True)

    api_key_env = os.environ.get("NVIDIA_API_KEY", "")
    if api_key_env:
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            'color:#00ff88;padding:6px 10px;background:rgba(0,255,136,0.05);'
            'border:1px solid #00ff88;border-radius:3px;letter-spacing:1px;">'
            '✓ NVIDIA_API_KEY LOADED FROM ENV</div>',
            unsafe_allow_html=True
        )
        api_key = api_key_env
    else:
        api_key = st.text_input(
            "NVIDIA API KEY",
            type="password",
            placeholder="nvapi-••••••••••••••••••",
            help="Get your key at build.nvidia.com"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-heading">⬡ CRISIS SCENARIO</div>', unsafe_allow_html=True)
    selected_scenario = st.selectbox(
        "Select Incident Type",
        options=list(SCENARIOS.keys()),
        label_visibility="collapsed"
    )

    scenario_data = SCENARIOS[selected_scenario]
    if scenario_data["threat"] in ("CRITICAL", "EXTREME"):
        threat_color = "#ff3366"
    elif scenario_data["threat"] == "SEVERE":
        threat_color = "#ffaa00"
    else:
        threat_color = "#00d4ff"

    if selected_scenario != "[Custom Input]":
        st.markdown(
            f'<div style="margin-top:0.8rem;padding:10px 12px;'
            f'background:rgba(255,51,102,0.05);border:1px solid #1a2744;'
            f'border-left:3px solid {threat_color};border-radius:3px;">'
            f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.58rem;'
            f'color:{threat_color};letter-spacing:2px;margin-bottom:4px;">'
            f'{scenario_data["emoji"]} THREAT: {scenario_data["threat"]}</div>'
            f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:0.78rem;'
            f'color:#6a8faf;line-height:1.4;">{scenario_data["description"]}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    col_ts = st.columns(1)[0]
    col_ts.markdown(
        f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
        f'color:#1a3a5c;text-align:center;">ZULU TIME: {datetime.utcnow().strftime("%Y-%m-%d %H:%MZ")}</div>',
        unsafe_allow_html=True
    )


# ─── Main Content ────────────────────────────────────────────────────────────
st.markdown(DARK_CSS, unsafe_allow_html=True)

st.markdown(
    '<div class="aegis-header">'
    '<div class="aegis-title">AEGIS-NET</div>'
    '<div class="aegis-subtitle">Multi-Agent Autonomous Infrastructure Recovery System</div>'
    '<div class="status-row">'
    '<span class="status-chip chip-online">● SYSTEM ONLINE</span>'
    '<span class="status-chip chip-alert">⚠ STANDBY MODE</span>'
    '<span class="status-chip chip-info">NVIDIA LLaMA-3.1-70B</span>'
    '<span class="status-chip chip-info">3-AGENT PIPELINE</span>'
    '<span class="status-chip chip-online">● ALL AGENTS READY</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

col_left, col_right = st.columns([3, 1])

with col_left:
    st.markdown('<div class="section-heading">⬡ SENSOR DATA INPUT</div>', unsafe_allow_html=True)

    if selected_scenario != "[Custom Input]":
        default_input = scenario_data["description"]
    else:
        default_input = ""

    sensor_data = st.text_area(
        "Raw Sensor / Field Report",
        value=default_input,
        height=140,
        placeholder="Paste raw sensor telemetry, field reports, or incident data here...",
        label_visibility="collapsed"
    )

with col_right:
    st.markdown('<div class="section-heading">⬡ PIPELINE STATUS</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("AGENTS", "3")
    m2.metric("MODEL", "70B")
    m3.metric("MODE", "LIVE")

st.markdown("<br>", unsafe_allow_html=True)

launch_clicked = st.button(
    "🚨  INITIALIZE RECOVERY PROTOCOL",
    type="primary",
    use_container_width=True
)

st.markdown("<hr>", unsafe_allow_html=True)

if launch_clicked:
    if not api_key:
        st.error("⚠️  No API key detected. Enter your NVIDIA API key in the sidebar to proceed.")
        st.stop()
    if not sensor_data.strip():
        st.error("⚠️  No sensor data provided. Input incident data or select a scenario.")
        st.stop()

    client = get_client(api_key)

    st.markdown(
        '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;'
        'color:#ff3366;letter-spacing:3px;text-align:center;padding:0.5rem 0;">'
        '⚠ PROTOCOL INITIATED — MULTI-AGENT CHAIN ACTIVATING ⚠</div>',
        unsafe_allow_html=True
    )

    scout_result = ""
    logistics_result = ""
    dispatcher_result = ""

    # ── AGENT 1: Scout ───────────────────────────────────────────────────────
    with st.status("🔍  SCOUT-1 — Analyzing Hazards & Threat Assessment...", expanded=True) as scout_status:
        st.markdown(
            '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            'color:#7b61ff;letter-spacing:2px;margin-bottom:0.6rem;">'
            '[ SCOUT-1 ACTIVE ] Processing sensor telemetry...</div>',
            unsafe_allow_html=True
        )
        scout_placeholder = st.empty()
        scout_result = stream_agent(
            client,
            SCOUT_SYSTEM,
            f"INCOMING SENSOR DATA / FIELD REPORT:\n\n{sensor_data}",
            scout_placeholder
        )
        if "[AGENT ERROR]" not in scout_result:
            scout_status.update(label="✅  SCOUT-1 — Threat Assessment Complete", state="complete", expanded=False)
        else:
            scout_status.update(label="❌  SCOUT-1 — Analysis Failed", state="error", expanded=True)

    if "[AGENT ERROR]" not in scout_result:
        render_agent_card(
            icon="🔍",
            name="SCOUT-1",
            role="Hazard Identification & Threat Assessment Agent",
            badge_class="badge-scout",
            output=scout_result,
            accent="#7b61ff"
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── AGENT 2: Logistics Strategist ────────────────────────────────────────
    if "[AGENT ERROR]" not in scout_result:
        with st.status("📦  LOGISTICS-ALPHA — Planning Resource Deployment...", expanded=True) as log_status:
            st.markdown(
                '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'color:#00d4ff;letter-spacing:2px;margin-bottom:0.6rem;">'
                '[ LOGISTICS-ALPHA ACTIVE ] Formulating tactical deployment plan...</div>',
                unsafe_allow_html=True
            )
            log_placeholder = st.empty()
            logistics_input = (
                f"SCOUT-1 THREAT ASSESSMENT REPORT:\n{scout_result}\n\n"
                f"ORIGINAL INCIDENT DATA:\n{sensor_data}"
            )
            logistics_result = stream_agent(
                client, LOGISTICS_SYSTEM, logistics_input, log_placeholder
            )
            if "[AGENT ERROR]" not in logistics_result:
                log_status.update(label="✅  LOGISTICS-ALPHA — Deployment Plan Ready", state="complete", expanded=False)
            else:
                log_status.update(label="❌  LOGISTICS-ALPHA — Planning Failed", state="error", expanded=True)

        if "[AGENT ERROR]" not in logistics_result:
            render_agent_card(
                icon="📦",
                name="LOGISTICS-ALPHA",
                role="Resource Deployment & Transit Rerouting Strategist",
                badge_class="badge-logistics",
                output=logistics_result,
                accent="#00d4ff"
            )

        st.markdown("<hr>", unsafe_allow_html=True)

    # ── AGENT 3: Emergency Dispatcher ────────────────────────────────────────
    if "[AGENT ERROR]" not in scout_result and "[AGENT ERROR]" not in logistics_result:
        with st.status("📡  DISPATCH-OMEGA — Generating Alerts & Government Briefs...", expanded=True) as disp_status:
            st.markdown(
                '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
                'color:#ff3366;letter-spacing:2px;margin-bottom:0.6rem;">'
                '[ DISPATCH-OMEGA ACTIVE ] Composing emergency communications...</div>',
                unsafe_allow_html=True
            )
            disp_placeholder = st.empty()
            dispatch_input = (
                f"INCIDENT DATA:\n{sensor_data}\n\n"
                f"SCOUT-1 ASSESSMENT:\n{scout_result}\n\n"
                f"LOGISTICS-ALPHA PLAN:\n{logistics_result}"
            )
            dispatcher_result = stream_agent(
                client, DISPATCHER_SYSTEM, dispatch_input, disp_placeholder
            )
            if "[AGENT ERROR]" not in dispatcher_result:
                disp_status.update(label="✅  DISPATCH-OMEGA — Communications Ready", state="complete", expanded=False)
            else:
                disp_status.update(label="❌  DISPATCH-OMEGA — Dispatch Failed", state="error", expanded=True)

        if "[AGENT ERROR]" not in dispatcher_result:
            render_agent_card(
                icon="📡",
                name="DISPATCH-OMEGA",
                role="Emergency Communications & Government Briefing Director",
                badge_class="badge-dispatcher",
                output=dispatcher_result,
                accent="#ff3366"
            )

    # ── Pipeline Complete Banner ──────────────────────────────────────────────
    if all("[AGENT ERROR]" not in r for r in [scout_result, logistics_result, dispatcher_result]):
        st.markdown(
            '<div style="text-align:center;padding:1.5rem;margin-top:1rem;'
            'background:linear-gradient(135deg,rgba(0,255,136,0.05),rgba(0,212,255,0.05));'
            'border:1px solid #0f3460;border-top:2px solid #00ff88;border-radius:6px;">'
            '<div style="font-family:\'Orbitron\',monospace;font-size:1.1rem;font-weight:700;'
            'color:#00ff88;letter-spacing:4px;">✓ RECOVERY PROTOCOL COMPLETE</div>'
            '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
            'color:#2a5f8f;letter-spacing:2px;margin-top:0.4rem;">'
            'ALL 3 AGENTS EXECUTED SUCCESSFULLY — OUTPUTS READY FOR ACTION</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # ── PDF Export ────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-heading">⬡ EXPORT INCIDENT REPORT</div>', unsafe_allow_html=True)

        report_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        safe_name = selected_scenario.replace(" ", "_").replace("[", "").replace("]", "")
        file_name = f"AEGIS-NET_Report_{safe_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"

        col_exp1, col_exp2, col_exp3 = st.columns([1, 2, 1])
        with col_exp2:
            with st.spinner("Compiling report..."):
                pdf_bytes = generate_pdf(
                    scenario=selected_scenario,
                    threat=scenario_data["threat"],
                    sensor_data=sensor_data,
                    scout=scout_result,
                    logistics=logistics_result,
                    dispatcher=dispatcher_result,
                    timestamp=report_ts,
                )
            st.download_button(
                label="📄  DOWNLOAD FULL INCIDENT REPORT  (PDF)",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                use_container_width=True,
            )
            st.markdown(
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.6rem;'
                f'color:#1a3a5c;text-align:center;margin-top:0.4rem;letter-spacing:1px;">'
                f'INCLUDES: THREAT ASSESSMENT · DEPLOYMENT PLAN · PUBLIC ALERT · GOVT BRIEF<br>'
                f'CLASSIFICATION: FOR OFFICIAL USE ONLY  •  {report_ts}</div>',
                unsafe_allow_html=True
            )

else:
    # ── Idle State ────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;padding:3rem 2rem;'
        'background:linear-gradient(135deg,#060d1a,#080f20);'
        'border:1px solid #0f3460;border-radius:6px;">'
        '<div style="font-family:\'Orbitron\',monospace;font-size:2rem;'
        'color:#0f3460;letter-spacing:6px;margin-bottom:1rem;">AWAITING</div>'
        '<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.7rem;'
        'color:#1a3a5c;letter-spacing:3px;line-height:2;">'
        'SELECT A CRISIS SCENARIO<br>'
        'INPUT SENSOR / FIELD DATA<br>'
        'PROVIDE NVIDIA API KEY<br>'
        'PRESS INITIALIZE RECOVERY PROTOCOL</div>'
        '<div style="margin-top:2rem;font-size:3rem;opacity:0.15;">🛡️</div>'
        '</div>',
        unsafe_allow_html=True
    )
