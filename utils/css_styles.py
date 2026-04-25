CSS_GLOBAL = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {
        background: #0a0a0f !important;
        color-scheme: dark !important;
    }

    #MainMenu { display: none !important; }
    footer { display: none !important; }
    .stAppDeployButton { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    [data-testid="stStatusWidget"] { display: none !important; }
    button[title="View fullscreen"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    button[kind="header"] { display: none !important; }

    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }

    .main .block-container {
        max-width: 600px;
        margin: 0 auto;
        padding-top: 0.5rem !important;
        padding-bottom: 5rem !important;
        animation: pageIn 0.4s ease-out both;
    }

    @keyframes pageIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
        .main .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    .main h1, .main h2, .main h3,
    .main p, .main label, .main input,
    .main [data-testid="stMarkdownContainer"] p,
    .main [data-testid="stMarkdownContainer"] span,
    .main [data-testid="stWidgetLabel"] *,
    .main .stButton > button,
    .main .stDownloadButton > button,
    [data-testid="stForm"] * {
        font-family: 'Poppins', sans-serif !important;
    }

    .main h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #f5f5f5 !important; }
    .main h2 { font-size: 1.15rem !important; font-weight: 600 !important; color: #e0e0e0 !important; }
    .main h3 { font-size: 1rem !important; font-weight: 600 !important; color: #c0c0c0 !important; }
    .main p, .main [data-testid="stMarkdownContainer"] p {
        font-size: 0.88rem !important; color: #a0a0b0 !important; line-height: 1.6 !important;
    }
    .main strong { color: #f5f5f5 !important; font-weight: 600 !important; }

    .main .stTextInput label, .main .stNumberInput label,
    .main .stSelectbox label, .main .stCheckbox label {
        font-size: 0.78rem !important; font-weight: 500 !important; color: #8a8a9a !important;
    }
    .main .stTextInput input, .main .stNumberInput input {
        font-size: 0.9rem !important; color: #f5f5f5 !important;
        background: #13131a !important; border: 1.5px solid #2a2a3a !important;
        border-radius: 10px !important; padding: 10px 14px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .main .stTextInput input:focus, .main .stNumberInput input:focus {
        border-color: #c4a35a !important; box-shadow: 0 0 0 3px rgba(196,163,90,0.15) !important;
    }

    .main [data-baseweb="select"] { background: #13131a !important; border-radius: 10px !important; }

    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #13131a 0%, #1a1a25 100%) !important;
        border: 1px solid #2a2a3a !important; border-radius: 14px !important;
        padding: 16px 18px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        animation: metricIn 0.4s ease-out both;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 24px rgba(196,163,90,0.08) !important;
    }
    @keyframes metricIn {
        from { opacity: 0; transform: scale(0.95) translateY(6px); }
        to   { opacity: 1; transform: scale(1) translateY(0); }
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.68rem !important; font-weight: 500 !important;
        text-transform: uppercase !important; letter-spacing: 0.05em !important; color: #8a8a9a !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.35rem !important; font-weight: 700 !important; color: #f5f5f5 !important;
    }

    .main .stButton > button {
        font-size: 0.82rem !important; font-weight: 600 !important;
        border-radius: 10px !important; color: #f5f5f5 !important;
        border: 1.5px solid #2a2a3a !important; background: #13131a !important;
        transition: all 0.2s ease !important;
    }
    .main .stButton > button:hover {
        background: #1e1e2a !important; border-color: #c4a35a !important;
        box-shadow: 0 4px 12px rgba(196,163,90,0.12) !important;
        transform: translateY(-1px) !important;
    }
    .main .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #c4a35a, #a08030) !important;
        border: none !important; color: #0a0a0f !important; font-weight: 700 !important;
    }
    .main .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #d4b36a, #b09040) !important;
        box-shadow: 0 6px 20px rgba(196,163,90,0.25) !important;
    }

    [data-testid="stForm"] {
        background: #13131a !important; border: 1px solid #2a2a3a !important;
        border-radius: 14px !important; padding: 20px !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #2a2a3a !important; border-radius: 12px !important;
        background: #13131a !important; margin-bottom: 6px !important;
    }

    [data-testid="stDataFrame"] { border-radius: 12px !important; border: 1px solid #2a2a3a !important; }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important; background: #13131a !important;
        border-radius: 12px !important; padding: 4px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important; font-family: 'Poppins', sans-serif !important;
        font-size: 0.78rem !important; font-weight: 600 !important;
        color: #8a8a9a !important; padding: 8px 16px !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #c4a35a, #a08030) !important;
        color: #0a0a0f !important;
    }

    .main hr { border: none !important; border-top: 1px solid #1e1e2a !important; }

    .main [data-testid="stToggle"] label span {
        color: #8a8a9a !important; font-size: 0.82rem !important;
    }
</style>
"""

CSS_OPENING = """
<style>
    .opening-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        text-align: center;
        padding: 20px;
        overflow: hidden;
        position: fixed;
        inset: 0;
        background: #0a0a0f;
        z-index: 9998;
    }

    /* block container full viewport saat opening */
    .main .block-container {
        max-width: 100% !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }

    .coin-container {
        position: relative;
        width: 120px;
        height: 120px;
        margin-bottom: 28px;
        animation: coinEntry 1s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        opacity: 0;
    }

    .coin {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, #c4a35a, #e8d48b, #a08030, #c4a35a);
        background-size: 300% 300%;
        animation: coinSpin 3s ease-in-out infinite, coinShine 4s linear infinite;
        box-shadow: 0 0 30px rgba(196,163,90,0.3), inset 0 0 20px rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 10px auto;
        position: relative;
    }

    .coin::after {
        content: '💰';
        font-size: 2.5rem;
        animation: coinPulse 2s ease-in-out infinite;
    }

    .coin-ring {
        position: absolute;
        width: 115px;
        height: 115px;
        border: 2px solid rgba(196,163,90,0.3);
        border-radius: 50%;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        animation: ringPulse 2.5s ease-in-out infinite;
    }

    @keyframes coinEntry {
        0%   { opacity: 0; transform: scale(0.2) translateY(40px) rotate(-20deg); }
        60%  { opacity: 1; transform: scale(1.1) translateY(-5px) rotate(5deg); }
        100% { opacity: 1; transform: scale(1) translateY(0) rotate(0deg); }
    }
    @keyframes coinSpin {
        0%, 100% { transform: rotateY(0deg); }
        50%      { transform: rotateY(15deg); }
    }
    @keyframes coinShine {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes coinPulse {
        0%, 100% { transform: scale(1); }
        50%      { transform: scale(1.1); }
    }
    @keyframes ringPulse {
        0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
        50%      { transform: translate(-50%, -50%) scale(1.15); opacity: 0.6; }
    }

    .sparkle {
        position: absolute;
        width: 6px;
        height: 6px;
        background: #c4a35a;
        border-radius: 50%;
        animation: sparkleFloat 3s ease-in-out infinite;
    }
    .sparkle:nth-child(1) { top: -5px; left: 20px; animation-delay: 0s; }
    .sparkle:nth-child(2) { top: 10px; right: -5px; animation-delay: 0.5s; }
    .sparkle:nth-child(3) { bottom: 0px; left: 5px; animation-delay: 1s; }
    .sparkle:nth-child(4) { top: 30px; left: -8px; animation-delay: 1.5s; }

    @keyframes sparkleFloat {
        0%, 100% { opacity: 0; transform: translateY(0) scale(0.5); }
        50%      { opacity: 1; transform: translateY(-12px) scale(1); }
    }

    .opening-name {
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #f5f5f5;
        margin: 0 0 6px 0;
        animation: textUp 0.7s ease-out 0.4s forwards;
        opacity: 0;
    }

    .opening-tagline {
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
        font-weight: 400;
        color: #c4a35a;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 0 0 20px 0;
        animation: textUp 0.7s ease-out 0.6s forwards;
        opacity: 0;
    }

    .opening-line {
        width: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #c4a35a, transparent);
        margin: 0 auto 20px auto;
        animation: lineGrow 0.8s ease-out 0.8s forwards;
        opacity: 0;
    }

    .opening-subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 0.75rem;
        font-weight: 400;
        color: #5a5a6a;
        margin: 0;
        animation: textUp 0.7s ease-out 1.0s forwards, subtitlePulse 2s ease-in-out 2s infinite;
        opacity: 0;
    }

    @keyframes textUp {
        from { opacity: 0; transform: translateY(18px); filter: blur(4px); }
        to   { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

    @keyframes lineGrow {
        from { opacity: 0; width: 0; }
        to   { opacity: 1; width: 120px; }
    }

    @keyframes subtitlePulse {
        0%, 100% { opacity: 0.6; }
        50%      { opacity: 1; color: #c4a35a; }
    }

    /* tombol fixed agar selalu terlihat */
    div[data-testid="stButton"] {
        position: fixed !important;
        left: 50% !important;
        bottom: 7vh !important;
        transform: translateX(-50%) !important;
        width: min(320px, calc(100vw - 2rem)) !important;
        z-index: 10000 !important;
        margin: 0 !important;
    }

    div[data-testid="stButton"] > button {
        width: 100% !important;
        background: transparent !important;
        border: 2px solid #c4a35a !important;
        color: #c4a35a !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        padding: 12px 40px !important;
        border-radius: 50px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        animation: btnFadeIn 0.8s ease-out 1.2s forwards !important;
        opacity: 0;
    }

    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #c4a35a, #a08030) !important;
        color: #0a0a0f !important;
        box-shadow: 0 0 25px rgba(196,163,90,0.3) !important;
        transform: scale(1.02) !important;
    }

    @keyframes btnFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
        div[data-testid="stButton"] {
            width: min(300px, calc(100vw - 1.5rem)) !important;
            bottom: 6vh !important;
        }
    }
</style>
"""

def inject_css():
    import streamlit as st
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)

def inject_opening_css():
    import streamlit as st
    st.markdown(CSS_OPENING, unsafe_allow_html=True)

def render_top_nav(active="kas"):
    import streamlit as st

    nav_items = [
        {"icon": "💰", "label": "Keuangan", "page": "pages/1_💰_Kas.py", "key": "kas"},
        {"icon": "📊", "label": "Rekap", "page": "app.py", "key": "home"},
        {"icon": "⚙️", "label": "Setting", "page": "pages/2_⚙️_Pengaturan.py", "key": "setting"},
    ]

    cols = st.columns(len(nav_items))
    for i, item in enumerate(nav_items):
        with cols[i]:
            btn_type = "primary" if item["key"] == active else "secondary"
            if st.button(
                f"{item['icon']} {item['label']}",
                key=f"nav_{item['key']}",
                type=btn_type,
                use_container_width=True
            ):
                st.switch_page(item["page"])
