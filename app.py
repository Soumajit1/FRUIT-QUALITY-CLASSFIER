import os
import sqlite3
import hashlib
import hmac
import secrets
import json
import base64
import io
from datetime import datetime

import numpy as np
import requests
import streamlit as st
from PIL import Image, ImageOps

# Safely import TensorFlow for local fallback
try:
    import tensorflow as tf
    _tf_available = True
except ImportError:
    _tf_available = False

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(APP_DIR, "fruit_quality_model.keras")
DB_PATH = os.path.join(APP_DIR, "fruit_quality_users.db")
ASSETS_DIR = os.path.join(APP_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
ENV_PATH = os.path.join(APP_DIR, ".env")

# Load API key from environment or .env
DEFAULT_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not DEFAULT_API_KEY and os.path.exists(ENV_PATH):
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    DEFAULT_API_KEY = line.strip().split("=", 1)[1].strip()
    except Exception:
        pass

# Fallback default key if not in env
if not DEFAULT_API_KEY:
    DEFAULT_API_KEY = ""

# Page Configuration
page_icon = LOGO_PATH if os.path.exists(LOGO_PATH) else "🍎"
st.set_page_config(
    page_title="Fruit Quality Classifier",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Classic, Elegant Styling (Zero empty boxes, fluid scrolling) ----------
CLASSIC_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

    /* Guarantee scrolling on all devices */
    html, body {
        height: auto !important;
        min-height: 100% !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        background-color: #0d0e12;
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: #0d0e12 !important;
        height: auto !important;
        min-height: 100vh !important;
        overflow-y: auto !important;
    }

    [data-testid="stAppViewContainer"], .main {
        overflow-y: auto !important;
        height: auto !important;
    }

    /* Completely hide Streamlit upper navbar / header / toolbar */
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer,
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1240px;
    }

    /* Classic Typography */
    .classic-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2.3rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.01em;
        line-height: 1.2;
        margin: 0 0 0.4rem 0;
    }

    .classic-subtitle {
        font-size: 1rem;
        color: #9ca3af;
        line-height: 1.5;
        margin-bottom: 1.2rem;
    }

    .section-eyebrow {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #e50914;
        margin-bottom: 0.35rem;
    }

    /* Surface Card */
    .classic-card {
        background-color: #15171e;
        border: 1px solid #262936;
        border-radius: 8px;
        padding: 1.4rem;
        margin-bottom: 1.25rem;
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 0.4rem;
    }

    .card-desc {
        font-size: 0.88rem;
        color: #94a3b8;
        line-height: 1.5;
        margin-bottom: 0.8rem;
    }

    /* Stat Cards */
    .stat-card {
        background-color: #15171e;
        border: 1px solid #262936;
        border-radius: 8px;
        padding: 1.2rem 1.1rem;
        margin-bottom: 1rem;
    }
    .stat-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 0.35rem;
    }
    .stat-val {
        font-size: 1.85rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.1;
    }
    .stat-sub {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 0.35rem;
    }

    /* Status Badges */
    .badge-fresh {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.14);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.4);
        padding: 0.4rem 1.1rem;
        border-radius: 6px;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
    }

    .badge-rotten {
        display: inline-block;
        background-color: rgba(229, 9, 20, 0.16);
        color: #f87171;
        border: 1px solid rgba(229, 9, 20, 0.45);
        padding: 0.4rem 1.1rem;
        border-radius: 6px;
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-bottom: 0.5rem;
    }

    .fruit-pill {
        display: inline-block;
        background-color: #212430;
        color: #f1f5f9;
        border: 1px solid #363a4d;
        padding: 0.3rem 0.85rem;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        margin-top: 0.3rem;
        margin-bottom: 0.6rem;
    }

    .defect-tag {
        display: inline-block;
        background-color: rgba(229, 9, 20, 0.12);
        color: #fca5a5;
        border: 1px solid rgba(229, 9, 20, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .clean-tag {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.12);
        color: #86efac;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 500;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.02em;
        transition: all 0.15s ease;
    }

    .stButton>button[kind="primary"] {
        background-color: #e50914 !important;
        border-color: #e50914 !important;
        color: #ffffff !important;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #b80710 !important;
        border-color: #b80710 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111318 !important;
        border-right: 1px solid #20222a;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid #262936;
        gap: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.95rem;
        color: #94a3b8;
        padding: 0.75rem 0.2rem;
    }
    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        border-bottom-color: #e50914 !important;
    }

    /* Notice Box */
    .classic-notice {
        background-color: #15171e;
        border: 1px solid #262936;
        border-left: 3px solid #e50914;
        border-radius: 4px;
        padding: 0.85rem 1rem;
        font-size: 0.84rem;
        color: #94a3b8;
        margin-top: 1.5rem;
        line-height: 1.45;
    }

    .engine-badge {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
</style>
"""
st.markdown(CLASSIC_CSS, unsafe_allow_html=True)

# ---------- Database / Authentication ----------
def db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        salt BLOB NOT NULL,
        password_hash BLOB NOT NULL,
        created_at TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        prediction TEXT NOT NULL,
        confidence REAL NOT NULL,
        created_at TEXT NOT NULL,
        fruit_name TEXT DEFAULT 'Fruit',
        details TEXT DEFAULT '',
        ripeness TEXT DEFAULT '',
        shelf_life TEXT DEFAULT '',
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    # Migration checks for columns
    cols = [r[1] for r in con.execute("PRAGMA table_info(predictions)").fetchall()]
    for col in ["fruit_name", "details", "ripeness", "shelf_life"]:
        if col not in cols:
            try:
                con.execute(f"ALTER TABLE predictions ADD COLUMN {col} TEXT DEFAULT ''")
            except Exception:
                pass
    con.commit()
    return con

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260_000)
    return salt, digest

def register_user(username, email, password):
    username, email = username.strip(), email.strip().lower()
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    salt, digest = hash_password(password)
    con = db()
    try:
        con.execute("INSERT INTO users(username,email,salt,password_hash,created_at) VALUES(?,?,?,?,?)",
                    (username, email, salt, digest, datetime.now().isoformat(timespec="seconds")))
        con.commit()
        return True, "Account created successfully. You can now sign in."
    except sqlite3.IntegrityError:
        return False, "That username or email is already registered."
    finally:
        con.close()

def authenticate(username_or_email, password):
    con = db()
    row = con.execute("SELECT id, username, salt, password_hash FROM users WHERE lower(username)=lower(?) OR lower(email)=lower(?)",
                      (username_or_email.strip(), username_or_email.strip())).fetchone()
    con.close()
    if not row:
        return None
    salt, digest = row[2], row[3]
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 260_000)
    if hmac.compare_digest(candidate, digest):
        return {"id": row[0], "username": row[1]}
    return None

def get_history(user_id):
    con = db()
    rows = con.execute("SELECT filename, fruit_name, prediction, confidence, ripeness, shelf_life, created_at FROM predictions WHERE user_id=? ORDER BY id DESC",
                       (user_id,)).fetchall()
    con.close()
    return rows

def save_prediction(user_id, filename, prediction, confidence, fruit_name="Fruit", details="", ripeness="", shelf_life=""):
    con = db()
    con.execute("""INSERT INTO predictions(user_id, filename, prediction, confidence, created_at, fruit_name, details, ripeness, shelf_life)
                   VALUES(?,?,?,?,?,?,?,?,?)""",
                (user_id, filename, prediction, float(confidence), datetime.now().strftime("%Y-%m-%d %H:%M"), fruit_name, details, ripeness, shelf_life))
    con.commit()
    con.close()

# ---------- Gemini Vision AI Engine (State-of-the-Art Precision) ----------
def analyze_with_gemini_vision(image, api_key):
    """
    Direct multimodal LLM inference using Google Gemini Vision API.
    Provides precise fruit naming, freshness grading, mold/bruise detection,
    ripeness stage, and shelf life estimation.
    """
    if not api_key:
        return None, "No API key configured."

    # Convert image to base64
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=90)
    b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

    prompt = """You are an expert post-harvest agricultural specialist and food quality inspector.
Inspect this fruit photograph thoroughly.
Analyze:
1. Exact fruit name and specific variety (e.g. Honeycrisp Apple, Cavendish Banana, Valencia Orange, Alphonso Mango, Strawberry, etc.).
2. Freshness quality verdict: strictly either "Fresh" or "Rotten".
   - "Fresh": edible, firm, clean skin, normal coloration, safe to eat.
   - "Rotten": signs of mold, fungal growth, rotting patches, severe bruising, browning decay, or mushiness.
3. Confidence level (percentage between 75.0 and 99.9).
4. Physical condition assessment (skin firmness, coloration, mold, decay, softness, bruising).
5. Visible defects list (e.g. ["Mold growth", "Browning decay"] or ["None - Clean surface"]).
6. Ripeness stage (e.g. "Unripe", "Peak Ripeness", "Overripe", "Decayed").
7. Estimated remaining shelf life (e.g. "4-6 days (refrigerated)" or "0 days (Discard)").

Return strictly valid JSON with this exact structure:
{
  "fruit_name": "Fruit name and variety",
  "quality_verdict": "Fresh",
  "confidence": 96.5,
  "condition_details": "Clear 1-2 sentence description of physical condition, skin texture, color uniformity, and presence or absence of rot.",
  "defects_detected": ["None"],
  "ripeness_stage": "Ripe",
  "shelf_life": "4-6 days (refrigerated)"
}"""

    data = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_img}}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    # Candidate models in priority order
    candidate_models = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-3.1-flash-lite"]
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": api_key.strip()
    }

    for model_name in candidate_models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
            r = requests.post(url, headers=headers, json=data, timeout=25)
            if r.status_code == 200:
                res = r.json()
                raw_text = res["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(raw_text)
                return parsed, None
            elif r.status_code == 400:
                # Key error or format issue
                err = r.json().get("error", {}).get("message", "API request error")
                return None, f"API Error: {err}"
        except Exception:
            continue

    return None, "All Gemini Vision endpoints were busy. Falling back to local model."

# ---------- Local CNN Fallback Engine ----------
@st.cache_resource
def load_quality_model():
    if not _tf_available:
        return None
    if not os.path.exists(MODEL_PATH):
        return None
    return tf.keras.models.load_model(MODEL_PATH)

def center_crop_square(img):
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    return img.crop((left, top, left + min_dim, top + min_dim))

def predict_local_cnn(image):
    model = load_quality_model()
    if model is None:
        return "Unknown", 50.0, [0.5, 0.5]

    square_img = center_crop_square(image.convert("RGB"))
    v1 = square_img.resize((96, 96))
    v2 = ImageOps.mirror(v1)

    batch = np.array([
        np.asarray(v1, dtype=np.float32) / 255.0,
        np.asarray(v2, dtype=np.float32) / 255.0,
    ])

    probs = np.mean(model.predict(batch, verbose=0), axis=0)
    idx = int(np.argmax(probs))
    label = "Fresh" if idx == 0 else "Rotten"
    confidence = float(probs[idx]) * 100
    return label, confidence, probs

def logout():
    for key in ("user", "page", "last_result", "uploaded_image_bytes"):
        st.session_state.pop(key, None)
    st.rerun()

# ---------- Session State Initialization ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = DEFAULT_API_KEY
if "ai_engine" not in st.session_state:
    st.session_state.ai_engine = "Gemini Vision AI (Recommended)"

# =========================================================================
# LOGIN / SIGNUP SCREEN (Clean, Zero Empty Boxes, Classic Aesthetic, Logo)
# =========================================================================
if st.session_state.user is None:
    left_col, right_col = st.columns([1.1, 0.9], gap="large")

    with left_col:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=220)

        st.markdown("""
        <div class="section-eyebrow">QUALITY VERIFICATION SYSTEM</div>
        <h1 class="classic-title">Fruit Quality Classifier</h1>
        <p class="classic-subtitle">
            An advanced diagnostic platform powered by Multimodal Vision AI for automated fruit identification, freshness validation, decay detection, and shelf-life estimation.
        </p>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="classic-card">
            <div class="card-title">Multimodal Vision Intelligence</div>
            <div class="card-desc">
                High-precision dual analysis: automatically identifies fruit species and detects surface decay, fungal molds, or discoloration with post-harvest grade reporting.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Powered by Gemini Vision AI & Deep Neural Networks")

    with right_col:
        # Clean tabs rendered directly with zero empty wrapper divs
        login_tab, signup_tab = st.tabs(["Sign In", "Create Account"])

        with login_tab:
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("### Welcome Back")
            st.caption("Sign in with your registered credentials.")

            with st.form("login_form"):
                login_id = st.text_input("Username or Email", placeholder="e.g. inspector@quality.com")
                login_pw = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submitted:
                user = authenticate(login_id, login_pw)
                if user:
                    st.session_state.user = user
                    st.session_state.page = "Dashboard"
                    st.rerun()
                else:
                    st.error("Authentication failed. Please check your credentials.")

        with signup_tab:
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            st.markdown("### Create New Account")
            st.caption("Register a new inspector account.")

            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="Choose username")
                new_email = st.text_input("Email Address", placeholder="name@domain.com")
                new_pw = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
                confirm_pw = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                signup_submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if signup_submit:
                if new_pw != confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    ok, message = register_user(new_username, new_email, new_pw)
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)

    st.stop()

# =========================================================================
# AUTHENTICATED APP NAVIGATION & SIDEBAR
# =========================================================================
user = st.session_state.user
if not user:
    st.stop()

with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown("<h2 style='margin:0;color:#fff;'>Fruit Quality</h2>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
    st.divider()

    pages = ["Dashboard", "Inspect Fruit", "Inspection History", "Account Settings"]
    nav_mapping = {
        "Dashboard": "Dashboard",
        "Inspect Fruit": "Predict quality",
        "Inspection History": "History",
        "Account Settings": "Profile"
    }
    reverse_mapping = {v: k for k, v in nav_mapping.items()}
    current_label = reverse_mapping.get(st.session_state.page, "Dashboard")

    for page_label in pages:
        is_selected = (current_label == page_label)
        if st.button(page_label,
                     key="nav_" + page_label,
                     use_container_width=True,
                     type="primary" if is_selected else "secondary"):
            st.session_state.page = nav_mapping[page_label]
            st.rerun()

    st.divider()
    st.markdown("##### AI Vision Engine")
    engine_choice = st.radio(
        "Engine Selection",
        ["Gemini Vision AI (Recommended)", "Local CNN Model (Offline)"],
        index=0 if "Gemini" in st.session_state.ai_engine else 1,
        label_visibility="collapsed"
    )
    st.session_state.ai_engine = engine_choice

    if "Gemini" in engine_choice:
        st.caption("Active: Multimodal Vision AI")
        with st.expander("API Key Configuration", expanded=False):
            key_input = st.text_input("Gemini API Key", value=st.session_state.gemini_key, type="password")
            if key_input != st.session_state.gemini_key:
                st.session_state.gemini_key = key_input
    else:
        st.caption("Active: Local 96x96 CNN")

    st.divider()
    st.markdown(f"**Inspector:** {user.get('username', 'Inspector')}")
    st.caption("Status: Authenticated")
    if st.button("Sign Out", use_container_width=True):
        logout()

# Load user history
history = get_history(user["id"])

# =========================================================================
# DASHBOARD
# =========================================================================
if st.session_state.page == "Dashboard":
    header_col1, header_col2 = st.columns([0.85, 0.15])
    with header_col1:
        st.markdown(f"""
        <h1 class="classic-title">Welcome, {user['username']}</h1>
        <p class="classic-subtitle">Inspection metrics, quality throughput, and classification records.</p>
        """, unsafe_allow_html=True)
    with header_col2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=95)

    total = len(history)
    fresh_count = sum(1 for row in history if row[2] == "Fresh")
    rotten_count = sum(1 for row in history if row[2] == "Rotten")
    avg_conf = np.mean([row[3] for row in history]) if history else 0

    metrics = [
        ("TOTAL INSPECTIONS", total, "Recorded evaluations"),
        ("FRESH SPECIMENS", fresh_count, "Passed quality standard"),
        ("ROTTEN SPECIMENS", rotten_count, "Flagged degradation"),
        ("AVG. CONFIDENCE", f"{avg_conf:.1f}%" if history else "—", "Classification certainty"),
    ]

    cols = st.columns(4)
    for col, (label, value, caption) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-val">{value}</div>
                <div class="stat-sub">{caption}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("### Quick Operations")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("""
        <div class="classic-card">
            <div class="card-title">New Fruit Quality Inspection</div>
            <div class="card-desc">Upload a photograph to identify fruit variety, verify freshness, detect decay spots, and calculate shelf life.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Quality Inspection", type="primary", use_container_width=True):
            st.session_state.page = "Predict quality"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="classic-card">
            <div class="card-title">Inspection Log & Audit Trail</div>
            <div class="card-desc">Review previously analyzed fruit specimens, physical findings, timestamps, and export full records as CSV.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Inspection History", use_container_width=True):
            st.session_state.page = "History"
            st.rerun()

    st.markdown("""
    <div class="classic-notice">
        <strong>Active Intelligence:</strong> Powered by Google Gemini Vision AI for accurate fruit taxonomy identification and physical degradation analysis.
    </div>
    """, unsafe_allow_html=True)

# =========================================================================
# QUALITY INSPECTION (Accurate, Effective, Fruit Naming, Shelf Life)
# =========================================================================
elif st.session_state.page == "Predict quality":
    st.markdown('<h1 class="classic-title">Inspect Fruit Quality</h1>', unsafe_allow_html=True)
    st.markdown('<p class="classic-subtitle">Upload a photograph of a fruit specimen. The Vision AI identifies the fruit variety and conducts a detailed quality inspection.</p>', unsafe_allow_html=True)

    upload_col, result_col = st.columns([1, 1], gap="large")

    with upload_col:
        st.markdown("#### Specimen Photograph")
        st.caption("Supported formats: JPG, JPEG, PNG.")
        upload = st.file_uploader("Upload specimen photo", type=["jpg", "jpeg", "png"], key="fruit_upload", label_visibility="collapsed")

        if upload:
            try:
                image = Image.open(upload).convert("RGB")
                st.image(image, caption=f"Specimen: {upload.name}", use_container_width=True)

                engine_mode = "Gemini" if "Gemini" in st.session_state.ai_engine else "Local"
                btn_label = f"Analyze Specimen ({'Gemini Vision AI' if engine_mode == 'Gemini' else 'Local CNN'})"

                if st.button(btn_label, type="primary", use_container_width=True):
                    with st.spinner("Analyzing fruit with Multimodal Vision AI..."):
                        if engine_mode == "Gemini" and st.session_state.gemini_key:
                            ai_result, err = analyze_with_gemini_vision(image, st.session_state.gemini_key)
                            if ai_result:
                                fruit_name = ai_result.get("fruit_name", "Fruit Specimen")
                                quality_label = ai_result.get("quality_verdict", "Fresh")
                                confidence = float(ai_result.get("confidence", 95.0))
                                details = ai_result.get("condition_details", "")
                                defects = ai_result.get("defects_detected", [])
                                ripeness = ai_result.get("ripeness_stage", "Ripe")
                                shelf_life = ai_result.get("shelf_life", "3-5 days")
                                engine_used = "Gemini Vision AI"
                            else:
                                st.warning(f"Vision API: {err}. Using local fallback...")
                                quality_label, confidence, probs = predict_local_cnn(image)
                                fruit_name = "Fruit Specimen"
                                details = "Evaluated using local computer vision model."
                                defects = ["Potential decay"] if quality_label == "Rotten" else ["None observed"]
                                ripeness = "Standard"
                                shelf_life = "3-5 days" if quality_label == "Fresh" else "0 days"
                                engine_used = "Local Model"
                        else:
                            quality_label, confidence, probs = predict_local_cnn(image)
                            fruit_name = "Fruit Specimen"
                            details = "Evaluated using local computer vision model."
                            defects = ["Potential decay"] if quality_label == "Rotten" else ["None observed"]
                            ripeness = "Standard"
                            shelf_life = "3-5 days" if quality_label == "Fresh" else "0 days"
                            engine_used = "Local Model"

                    # Save record to database
                    save_prediction(
                        user["id"],
                        upload.name,
                        quality_label,
                        confidence,
                        fruit_name=fruit_name,
                        details=details,
                        ripeness=ripeness,
                        shelf_life=shelf_life
                    )

                    st.session_state.last_result = {
                        "filename": upload.name,
                        "fruit_name": fruit_name,
                        "prediction": quality_label,
                        "confidence": confidence,
                        "details": details,
                        "defects": defects,
                        "ripeness": ripeness,
                        "shelf_life": shelf_life,
                        "engine_used": engine_used,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.success("Inspection completed successfully.")
                    st.rerun()

            except Exception as e:
                st.error(f"Error processing image: {e}")

    with result_col:
        st.markdown("#### Diagnostic Results")
        st.caption("Post-harvest inspection findings and quality certainty.")

        if "last_result" in st.session_state:
            result = st.session_state.last_result
            is_fresh = result["prediction"].lower() == "fresh"

            badge_class = "badge-fresh" if is_fresh else "badge-rotten"
            verdict_text = "VERDICT: FRESH" if is_fresh else "VERDICT: ROTTEN / DEGRADED"
            fruit_display = result.get("fruit_name", "Fruit Specimen")

            st.markdown(f"""
            <div class="classic-card" style="border-left: 3px solid {'#22c55e' if is_fresh else '#e50914'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="section-eyebrow">INSPECTION REPORT · {result["time"]}</span>
                    <span class="engine-badge">{result.get("engine_used", "Gemini Vision")}</span>
                </div>
                <div style="font-size: 1.45rem; font-weight: 700; color: #ffffff; margin-top: 0.35rem; margin-bottom: 0.2rem;">
                    {fruit_display}
                </div>
                <div>
                    <span class="{badge_class}">{verdict_text}</span>
                </div>
                <div style="margin-top: 0.75rem; display: flex; justify-content: space-between; align-items: baseline;">
                    <span style="font-size: 0.9rem; color: #94a3b8;">Classification Confidence:</span>
                    <span style="font-size: 1.45rem; font-weight: 700; color: #ffffff;">{result["confidence"]:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.progress(min(max(result["confidence"] / 100, 0.0), 1.0))

            # Ripeness & Shelf Life cards
            st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
            rc1, rc2 = st.columns(2)
            with rc1:
                st.markdown(f"""
                <div class="stat-card" style="padding: 0.9rem 1rem;">
                    <div class="stat-label">Ripeness Stage</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">{result.get('ripeness', 'Ripe')}</div>
                </div>
                """, unsafe_allow_html=True)
            with rc2:
                st.markdown(f"""
                <div class="stat-card" style="padding: 0.9rem 1rem;">
                    <div class="stat-label">Estimated Shelf Life</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">{result.get('shelf_life', '3-5 days')}</div>
                </div>
                """, unsafe_allow_html=True)

            # Condition Details
            if result.get("details"):
                st.markdown("##### Visual Inspection Findings")
                st.markdown(f"""
                <div class="classic-card" style="padding: 1rem 1.1rem; font-size: 0.92rem; color: #cbd5e1; line-height: 1.55;">
                    {result['details']}
                </div>
                """, unsafe_allow_html=True)

            # Defects Tagging
            if result.get("defects"):
                st.markdown("##### Surface Defects & Observations")
                tags_html = ""
                for d in result["defects"]:
                    if d.lower() in ["none", "none - clean surface", "none observed"]:
                        tags_html += f'<span class="clean-tag">Clean: {d}</span>'
                    else:
                        tags_html += f'<span class="defect-tag">Defect: {d}</span>'
                st.markdown(tags_html, unsafe_allow_html=True)

        else:
            st.info("Upload an image on the left and click 'Analyze Specimen' to generate diagnostic output.")

# =========================================================================
# INSPECTION HISTORY
# =========================================================================
elif st.session_state.page == "History":
    st.markdown('<h1 class="classic-title">Inspection Records</h1>', unsafe_allow_html=True)
    st.markdown('<p class="classic-subtitle">Verified chronological record of fruit specimens analyzed under your account.</p>', unsafe_allow_html=True)

    if not history:
        st.markdown("""
        <div class="classic-card">
            <div class="card-title">No Previous Records</div>
            <div class="card-desc">Completed evaluations will be cataloged and preserved here.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Perform First Inspection", type="primary"):
            st.session_state.page = "Predict quality"
            st.rerun()
    else:
        import pandas as pd
        df = pd.DataFrame(history, columns=["Image File", "Fruit Variety", "Verdict", "Confidence (%)", "Ripeness", "Shelf Life", "Timestamp"])
        df["Confidence (%)"] = df["Confidence (%)"].map(lambda x: round(float(x), 1))

        st.dataframe(df, use_container_width=True, hide_index=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Records as CSV",
            data=csv_data,
            file_name=f"fruit_quality_audit_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# =========================================================================
# PROFILE / ACCOUNT SETTINGS
# =========================================================================
elif st.session_state.page == "Profile":
    st.markdown('<h1 class="classic-title">Account Settings</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div class="classic-card">
        <div class="card-title">Inspector Profile</div>
        <div class="card-desc">System configuration and authentication details.</div>
    """, unsafe_allow_html=True)

    st.write(f"**Inspector Username:** {user['username']}")
    st.write(f"**Storage Engine:** SQLite (`fruit_quality_users.db`)")
    st.write(f"**Primary Intelligence Engine:** Google Gemini Vision AI (`gemini-flash-lite-latest`)")
    st.write(f"**Offline Fallback Engine:** Keras / TensorFlow ({tf.__version__ if _tf_available else 'Disabled'})")

    st.markdown("""
    </div>
    <div class="classic-notice">
        Gemini Vision AI is active. All inspections provide high-precision fruit taxonomy classification, defect localization, and shelf-life prediction.
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Fruit Quality Classifier · Powered by Multimodal Vision AI")
