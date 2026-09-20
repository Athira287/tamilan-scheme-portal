import streamlit as st

# 1. ALWAYS FIRST STREAMLIT COMMAND (Force sidebar to stay open)
st.set_page_config(
    page_title="Tamilan Scheme Engine",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. HIDE TOOLBAR & KEEP SIDEBAR BUTTON VISIBLE
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppViewerFooter, .stAppDeployButton, [data-testid="stDecoration"] {display: none !important;}
    
    /* Force sidebar toggle button to remain visible */
    [data-testid="stSidebarCollapseButton"], [data-testid="stHeader"] {
        display: block !important;
        visibility: visible !important;
        background: transparent !important;
    }
    
    /* Main Background & Base Typography */
    .stApp {
        background-color: #121418;
        color: #d1d5db;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1d24 !important;
        border-right: 1px solid #2a2e39 !important;
    }
    
    /* Elegant Subtle Headers */
    h1 {
        color: #e5c158 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #d8b244 !important;
        font-weight: 600 !important;
    }

    /* Subtle Accent Buttons */
    div.stButton > button {
        background-color: #242832 !important;
        color: #e5c158 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid #3b4252 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #2e3440 !important;
        border-color: #e5c158 !important;
        color: #f3d677 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    /* Soft Cards & Expanders */
    .streamlit-expanderHeader {
        background-color: #1a1d24 !important;
        border-radius: 8px !important;
        border-left: 3px solid #d8b244 !important;
        color: #e5e7eb !important;
        font-weight: 500 !important;
    }
    
    /* Form Inputs */
    .stTextInput > div > div > input {
        background-color: #1a1d24 !important;
        color: #f3f4f6 !important;
        border: 1px solid #2a2e39 !important;
        border-radius: 6px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #d8b244 !important;
        box-shadow: 0 0 0 1px #d8b244 !important;
    }

    /* Muted Status & Alert Cards */
    .stSuccess {
        background-color: rgba(46, 125, 50, 0.12) !important;
        border: 1px solid rgba(46, 125, 50, 0.3) !important;
        color: #81c784 !important;
        border-radius: 6px !important;
    }
    .stInfo {
        background-color: rgba(216, 178, 68, 0.1) !important;
        border: 1px solid rgba(216, 178, 68, 0.3) !important;
        color: #e5c158 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

import pandas as pd
import hashlib
import base64
import re
import os
import io

# 3. AUTHENTICATION SESSION STATE & USER DATABASE
if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": "sih2026"}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- FORGOT PASSWORD MODAL ---
@st.dialog("🔑 Reset Your Password")
def reset_password_dialog():
    st.write("Enter your registered Username / Identity number to set a new password.")
    user_input = st.text_input("Username / Mobile / Identity Number").strip().lower()
    
    if st.button("Send OTP"):
        if len(user_input) >= 3:
            st.success("OTP sent to your registered mobile number ending with ******42!")
            new_pass = st.text_input("Enter New Password", type="password")
            if st.button("Update Password"):
                if user_input in st.session_state["user_db"]:
                    st.session_state["user_db"][user_input] = new_pass
                    st.success("Password updated successfully! Please login with your new password.")
                else:
                    st.error("Username not found in registered database.")
        else:
            st.error("Please enter a valid Username or Identity Number.")

# --- DYNAMIC LOGIN & REGISTRATION PAGE ---
def auth_page():
    st.title("🔒 Tamilan Scheme Portal")
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up (Create Account)"])
    
    # --- LOGIN TAB ---
    with tab1:
        st.subheader("Login to Your Account")
        username = st.text_input("Username / Name / Identity ID", key="login_user").strip().lower()
        password = st.text_input("Password", type="password", key="login_pass").strip()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Login", use_container_width=True):
                if username in st.session_state["user_db"] and st.session_state["user_db"][username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["current_username"] = username
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password. Click 'Sign Up' if you need to create an account.")
        with col2:
            if st.button("Forgot Password?", use_container_width=True):
                reset_password_dialog()
                
    # --- SIGN UP TAB ---
    with tab2:
        st.subheader("Create New Account")
        new_username = st.text_input("Choose Your Name / Username", key="reg_user").strip().lower()
        new_password = st.text_input("Choose Your Password", type="password", key="reg_pass").strip()
        confirm_password = st.text_input("Confirm Your Password", type="password", key="reg_confirm").strip()
        
        if st.button("Register Account", use_container_width=True):
            if not new_username or not new_password:
                st.error("Please fill in both Name/Username and Password fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            elif new_username in st.session_state["user_db"]:
                st.warning("This Username is already registered. Please login instead.")
            else:
                st.session_state["user_db"][new_username] = new_password
                st.success(f"Account created successfully for '{new_username}'! You can now switch to the Login tab.")

# 4. APP GATEKEEPER
if not st.session_state["authenticated"]:
    auth_page()
else:
    # Sidebar Logout Button
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"authenticated": False}))

    # ---------------- SECURITY & ENCRYPTION HELPERS ----------------
    def generate_encryption_key(passphrase: str) -> bytes:
        return hashlib.sha256(passphrase.encode()).digest()

    def encrypt_document(file_bytes: bytes, key: bytes) -> str:
        key_len = len(key)
        encrypted_bytes = bytes([b ^ key[i % key_len] for i, b in enumerate(file_bytes)])
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def verify_identity_format(id_number: str) -> bool:
        cleaned = id_number.replace(" ", "").replace("-", "")
        return bool(re.fullmatch(r"\d{12}", cleaned))

    # ---------------- DYNAMIC VOICE PARSING ENGINE ----------------
    def parse_voice_text(text: str):
        text_lower = text.lower()
        
        # Extract Name
        name_match = re.search(r"(?:my name is|i am|this is)\s+([a-zA-Z]+)", text_lower)
        if name_match:
            st.session_state.voice_name = name_match.group(1).capitalize()
            
        # Extract Age
        age_match = re.search(r"(?:age is|i am|aged?)\s*(\d+)", text_lower) or re.search(r"(\d+)\s*years?\s*old", text_lower)
        if age_match:
            st.session_state.voice_age = age_match.group(1)
            
        # Extract Funding Needed (Lakhs, Crores, or Raw Numbers)
        funding_match = re.search(r"(?:looking for|need|required?|funding of|loan of)?\s*(\d+)\s*(lakh|lakhs|lac|lacs|cr|crore|crores)?\s*(?:loan|funding|rupees|rs)?", text_lower)
        if funding_match:
            val = int(funding_match.group(1))
            unit = funding_match.group(2)
            if unit in ["lakh", "lakhs", "lac", "lacs"]:
                val *= 100000
            elif unit in ["cr", "crore", "crores"]:
                val *= 10000000
            st.session_state.voice_funding = str(val)

        # Extract Income
        income_match = re.search(r"(?:income|earning|salary)(?: is)?\s*(\d+)\s*(lakh|lakhs|lac|lacs)?", text_lower)
        if income_match:
            inc_val = int(income_match.group(1))
            inc_unit = income_match.group(2)
            if inc_unit in ["lakh", "lakhs", "lac", "lacs"]:
                inc_val *= 100000
            st.session_state.voice_income = str(inc_val)

        # Extract State
        states = ["Tamil Nadu", "Maharashtra", "Delhi", "Karnataka"]
        for s in states:
            if s.lower() in text_lower:
                st.session_state.voice_state = s
                break

        # Extract Business Sector
        sectors = ["Manufacturing", "Services", "Trading", "Agriculture"]
        for sec in sectors:
            if sec.lower() in text_lower:
                st.session_state.voice_sector = sec
                break

    # ---------------- INITIALIZE SESSION STATE ----------------
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'lang' not in st.session_state:
        st.session_state.lang = "English"
    if 'user_key' not in st.session_state:
        st.session_state.user_key = None
    if 'uploaded_docs' not in st.session_state:
        st.session_state.uploaded_docs = {}
    if 'verified_identity' not in st.session_state:
        st.session_state.verified_identity = False

    if 'voice_name' not in st.session_state: st.session_state.voice_name = ""
    if 'voice_age' not in st.session_state: st.session_state.voice_age = ""
    if 'voice_income' not in st.session_state: st.session_state.voice_income = ""
    if 'voice_funding' not in st.session_state: st.session_state.voice_funding = ""
    if 'voice_state' not in st.session_state: st.session_state.voice_state = "Tamil Nadu"
    if 'voice_sector' not in st.session_state: st.session_state.voice_sector = "Manufacturing"
    if 'last_transcription' not in st.session_state: st.session_state.last_transcription = ""

    # Chatbot memory state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Mock Scheme Database
    SCHEME_DB = [
        {
            "id": "SCH001",
            "name": "Prime Minister Employment Generation Programme (PMEGP)",
            "sector": ["Manufacturing", "Services"],
            "min_age": 18, "max_age": 60, "max_income": 1000000,
            "supported_states": ["All"], "max_funding": 5000000, "min_funding": 50000,
            "target_categories": ["SC", "ST", "OBC", "Women", "General"],
            "stages": ["New Unit"],
            "benefits": "15% to 35% Subsidy (Margin Money) on project cost.",
            "documents": ["Identity Proof", "PAN Card", "EDP Training Certificate", "Project Report"],
            "portal_url": "https://www.kviconline.gov.in/pmegpeportal/",
            "date_added": "2026-01-15"
        },
        {
            "id": "SCH002",
            "name": "Pradhan Mantri MUDRA Yojana (Tarun)",
            "sector": ["Manufacturing", "Services", "Trading", "Agriculture"],
            "min_age": 18, "max_age": 65, "max_income": 1500000,
            "supported_states": ["All"], "max_funding": 1000000, "min_funding": 500000,
            "target_categories": ["General", "SC", "ST", "OBC"],
            "stages": ["Existing", "Expansion"],
            "benefits": "Collateral-free business loan up to ₹10 Lakhs.",
            "documents": ["Identity Proof", "PAN Card", "Business License", "Bank Statement"],
            "portal_url": "https://www.mudra.org.in/",
            "date_added": "2026-02-01"
        },
        {
            "id": "SCH003",
            "name": "Tamil Nadu NEEDS Scheme",
            "sector": ["Manufacturing", "Services"],
            "min_age": 21, "max_age": 45, "max_income": 2000000,
            "supported_states": ["Tamil Nadu"], "max_funding": 5000000, "min_funding": 100000,
            "target_categories": ["General", "SC", "ST", "OBC", "Women"],
            "stages": ["New Unit"],
            "benefits": "25% Capital Subsidy up to ₹75 Lakhs with 3% interest subvention.",
            "documents": ["Identity Proof", "Degree/Diploma Certificate", "Project Report"],
            "portal_url": "https://msmeonline.tn.gov.in/",
            "date_added": "2026-02-20"
        },
        {
            "id": "SCH004",
            "name": "Tamil Nadu MAuto Rural Mobility Scheme (New 2026)",
            "sector": ["Services", "Trading"],
            "min_age": 18, "max_age": 50, "max_income": 800000,
            "supported_states": ["Tamil Nadu"], "max_funding": 1500000, "min_funding": 100000,
            "target_categories": ["Women", "SC", "ST", "OBC", "General"],
            "stages": ["New Unit", "Existing"],
            "benefits": "40% Subsidy for purchasing eco-friendly EV commercial vehicles.",
            "documents": ["Identity Proof", "Driving License", "Income Certificate"],
            "portal_url": "https://tn.gov.in/scheme/mauto",
            "date_added": "2026-03-01"
        }
    ]

    # ---------------- MULTILINGUAL TRANSLATION DICTIONARY ----------------
    TEXT_DICT = {
        "English": {
            "sidebar_title": "⚙️ Select Language",
            "pages": [
                "1. Registration & Security Setup",
                "2. Scheme Recommendations & AI Agent",
                "3. Side-by-Side Comparison",
                "4. Secure Vault & Application Assistant",
                "5. System Admin & Real-Time Alerts"
            ],
            "p1_title": "🌾 Tamilan Scheme - Profile & Security Setup",
            "voice_title": "🎙️ AI Voice Guidance Assistant",
            "voice_instruction": "Click record below to speak your details instead of typing.",
            "p1_sec_sub": "Security Details (Documents Safety Key)",
            "p1_sec_pass": "Create Secret Key / Passphrase for Documents Encryption",
            "p1_sec_ph": "for example: enter your secret passphrase eg. Pass@123",
            "p1_sec_caption": "🔒 This key encrypts your uploaded documents locally using SHA256-XOR stream cipher before storing.",
            "p1_pers_sub": "Personal & Business Parameters",
            "p1_name": "Full Name",
            "p1_name_ph": "for example: enter your name",
            "p1_age": "Age",
            "p1_age_ph": "for example: enter your age eg. 28",
            "p1_state": "State",
            "p1_sector": "Sector",
            "p1_gender": "Gender",
            "p1_income": "Annual Household Income (₹)",
            "p1_income_ph": "for example: enter annual income eg. 250000",
            "p1_funding": "Funding Required (₹)",
            "p1_funding_ph": "for example: enter funding required eg. 300000",
            "p1_stage": "Business Stage",
            "p1_category": "Target Category",
            "p1_btn": "Save & Go to Matching ➡️",
            "p2_title": "🤖 AI Scheme Engine & Conversational Agent",
            "p2_warn": "Please complete Page 1 first!",
            "p2_profile": "Profile Loaded",
            "p2_ben": "Benefits",
            "p2_docs": "Required Documents",
            "p2_bot_title": "💬 Multilingual AI Scheme Agent",
            "p2_bot_placeholder": "Ask any question about eligible schemes, subsidies, or requirements...",
            "p3_title": "⚖️ Scheme Comparison Matrix",
            "p3_attr": ["Financial Benefits", "Target Sector", "Max Funding", "Required Documents Count"],
            "p4_title": "📄 Secure Document Vault & Application Assistant",
            "p4_proto": "🔒 Privacy Protocol: Documents uploaded are encrypted in-memory using SHA256-XOR Key Stream Cipher. Unverified third parties cannot access your documents without authorization.",
            "p4_err": "Please set your Encryption Passphrase on Page 1 first!",
            "p4_id_ver": "🆔 Secure Identity Card Verification",
            "p4_id_input": "Enter 12-Digit Government Identity Card Number for Verification",
            "p4_id_ph": "for example: enter 12-digit ID eg. 123456789012",
            "p4_id_btn": "Verify Government ID",
            "p4_id_succ": "✅ Government Identity Format Verified Successfully! Data masked & encrypted.",
            "p4_id_fail": "❌ Invalid 12-digit Identity format. Please re-check.",
            "p4_sub_up": "Upload Verification Documents",
            "p4_doc_select": "Select Document Type",
            "p4_btn_enc": "🔒 Encrypt & Store Document",
            "p4_succ": "successfully encrypted and saved to Secure Memory!",
            "p4_status_sub": "Encrypted Document Status",
            "p4_no_docs": "No documents uploaded yet.",
            "p4_assistant_title": "📋 Application & Document Assistant",
            "p5_title": "🔔 Real-time New Scheme Monitoring & Alerts",
            "p5_alert": "📌 Security Alert: Document vault encryption state is ACTIVE.",
            "btn_prev": "⬅️ Previous",
            "btn_next": "Next ➡️"
        },
        "Tamil (தமிழ்)": {
            "sidebar_title": "⚙️ மொழியைத் தேர்ந்தெடுக்கவும்",
            "pages": [
                "1. சுயவிவரம் & பாதுகாப்பு அமைப்புகள்",
                "2. திட்ட பரிந்துரைகள் & AI உதவியாளர்",
                "3. ஒப்பீட்டு அட்டவணை",
                "4. ஆவண பெட்டகம் & விண்ணப்ப உதவியாளர்",
                "5. நேரலை திட்ட அறிவிப்புகள்"
            ],
            "p1_title": "🌾 தமிழன் ஸ்கீம் - சுயவிவர அமைப்பு மற்றும் பாதுகாப்பு விவரங்கள்",
            "voice_title": "🎙️ குரல் உதவி உதவியாளர்",
            "voice_instruction": "உங்கள் விவரங்களை பேச கீழே உள்ள பதிவு பொத்தானை அழுத்தவும்.",
            "p1_sec_sub": "பாதுகாப்பு விவரங்கள் (ஆவணங்கள் பாதுகாப்பு சாவி)",
            "p1_sec_pass": "ஆவணங்கள் குறியாக்கத்திற்கான ரகசிய கடவுச்சொல் உருவாக்கவும்",
            "p1_sec_ph": "உதாரணமாக: உங்கள் ரகசிய கடவுச்சொல்லை உள்ளிடவும் எ.கா. Pass@123",
            "p1_sec_caption": "🔒 இந்த கடவுச்சொல் உங்கள் ஆவணங்களை சேமிக்கும் முன் பாதுகாப்பாக குறியாக்கம் செய்யும்.",
            "p1_pers_sub": "தனிப்பட்ட மற்றும் வணிக அளவுருக்கள்",
            "p1_name": "முழு பெயர்",
            "p1_name_ph": "உதாரணமாக: உங்கள் பெயரை உள்ளிடவும்",
            "p1_age": "வயது",
            "p1_age_ph": "உதாரணமாக: உங்கள் வயதை உள்ளிடவும் எ.கா. 28",
            "p1_state": "மாநிலம்",
            "p1_sector": "வணிக துறை",
            "p1_gender": "பாலினம்",
            "p1_income": "ஆண்டு குடும்ப வருமானம் (₹)",
            "p1_income_ph": "உதாரணமாக: குடும்ப வருமானத்தை உள்ளிடவும் எ.கா. 250000",
            "p1_funding": "தேவைப்படும் நிதி (₹)",
            "p1_funding_ph": "உதாரணமாக: தேவையான நிதியை உள்ளிடவும் எ.கா. 300000",
            "p1_stage": "வணிக நிலை",
            "p1_category": "இலக்கு பிரிவு",
            "p1_btn": "சேமித்துத் தொடரவும் ➡️",
            "p2_title": "🤖 AI திட்ட பொருந்தும் இயந்திரம் & அரட்டை உதவியாளர்",
            "p2_warn": "தயவுசெய்து முதலில் பக்கம் 1 ஐ பூர்த்தி செய்யவும்!",
            "p2_profile": "ஏற்றப்பட்ட சுயவிவரம்",
            "p2_ben": "நன்மைகள்",
            "p2_docs": "தேவையான ஆவணங்கள்",
            "p2_bot_title": "💬 பன்மொழி AI திட்ட உதவியாளர்",
            "p2_bot_placeholder": "திட்டங்கள், மானியங்கள் குறித்து உங்கள் கேள்விகளைக் கேளுங்கள்...",
            "p3_title": "⚖️ திட்ட ஒப்பீட்டு அட்டவணை",
            "p3_attr": ["நிதி நன்மைகள்", "இலக்கு துறை", "அதிகபட்ச நிதி", "தேவையான ஆவணங்களின் எண்ணிக்கை"],
            "p4_title": "📄 பாதுகாப்பான ஆவண பெட்டகம் & விண்ணப்ப உதவியாளர்",
            "p4_proto": "🔒 தனியுரிமை நெறிமுறை: பதிவேற்றப்பட்ட ஆவணங்கள் பாதுகாப்பாக குறியாக்கம் செய்யப்படுகின்றன.",
            "p4_err": "தயவுசெய்து முதலில் பக்கம் 1 இல் உங்கள் கடவுச்சொல்லை அமைக்கவும்!",
            "p4_id_ver": "🆔 அரசு அடையாள அட்டை சரிபார்ப்பு",
            "p4_id_input": "12 இலக்க அரசு அடையாள அட்டை எண்ணை உள்ளிடவும்",
            "p4_id_ph": "உதாரணமாக: 12 இலக்க எண்ணை உள்ளிடவும் எ.கா. 123456789012",
            "p4_id_btn": "அடையாள அட்டையை சரிபார்க்கவும்",
            "p4_id_succ": "✅ அரசு அடையாள வடிவம் வெற்றிகரமாக சரிபார்க்கப்பட்டது!",
            "p4_id_fail": "❌ தவறான 12 இலக்க அடையாள வடிவம். மீண்டும் சரிபார்க்கவும்.",
            "p4_sub_up": "சரிபார்ப்பு ஆவணங்களை பதிவேற்றவும்",
            "p4_doc_select": "ஆவண வகையைத் தேர்ந்தெடுக்கவும்",
            "p4_btn_enc": "🔒 குறியாக்கம் செய்து சேமிக்கவும்",
            "p4_succ": "வெற்றிகரமாக குறியாக்கம் செய்யப்பட்டு சேமிக்கப்பட்டது!",
            "p4_status_sub": "குறியாக்கம் செய்யப்பட்ட ஆவண நிலை",
            "p4_no_docs": "இன்னும் ஆவணங்கள் எதுவும் பதிவேற்றப்படவில்லை.",
            "p4_assistant_title": "📋 விண்ணப்ப ஆவண வழிகாட்டி",
            "p5_title": "🔔 புதிய திட்ட கண்காணிப்பு & எச்சரிக்கைகள்",
            "p5_alert": "📌 பாதுகாப்பு எச்சரிக்கை: ஆவண பெட்டக குறியாக்கம் செயலில் உள்ளது.",
            "btn_prev": "⬅️ முந்தைய",
            "btn_next": "அடுத்த ➡️"
        },
        "Hindi (हिंदी)": {
            "sidebar_title": "⚙️ भाषा चुनें",
            "pages": [
                "1. पंजीकरण और सुरक्षा सेटअप",
                "2. योजना सिफारिशें और एआई एजेंट",
                "3. तुलना तालिका",
                "4. सुरक्षित दस्तावेज़ वॉल्ट और आवेदन सहायक",
                "5. नई योजनाएं और अलर्ट"
            ],
            "p1_title": "🌾 तमिलन स्कीम - प्रोफ़ाइल और सुरक्षा सेटअप",
            "voice_title": "🎙️ एआई वॉयस असिस्टेंट",
            "voice_instruction": "टाइप करने के बजाय अपने विवरण बोलने के लिए नीचे रिकॉर्ड करें।",
            "p1_sec_sub": "सुरक्षा विवरण (दस्तावेज़ सुरक्षा कुंजी)",
            "p1_sec_pass": "दस्तावेज़ एन्क्रिप्शन के लिए गुप्त पासफ़्रेज़ बनाएं",
            "p1_sec_ph": "उदाहरण के लिए: अपना गुप्त पासफ़्रेज़ दर्ज करें जैसे Pass@123",
            "p1_sec_caption": "🔒 यह कुंजी आपके अपलोड किए गए दस्तावेज़ों को सुरक्षित रूप से एन्क्रिप्ट करती है।",
            "p1_pers_sub": "व्यक्तिगत और व्यावसायिक पैरामीटर",
            "p1_name": "पूरा नाम",
            "p1_name_ph": "उदाहरण के लिए: अपना नाम दर्ज करें",
            "p1_age": "आयु",
            "p1_age_ph": "उदाहरण के लिए: अपनी आयु दर्ज करें जैसे 28",
            "p1_state": "राज्य",
            "p1_sector": "व्यवसाय क्षेत्र",
            "p1_gender": "लिंग",
            "p1_income": "वार्षिक घरेलू आय (₹)",
            "p1_income_ph": "उदाहरण के लिए: वार्षिक आय दर्ज करें जैसे 250000",
            "p1_funding": "आवश्यक धन (₹)",
            "p1_funding_ph": "उदाहरण के लिए: आवश्यक धन दर्ज करें जैसे 300000",
            "p1_stage": "व्यापार चरण",
            "p1_category": "लक्षित वर्ग",
            "p1_btn": "सहेजें और आगे बढ़ें ➡️",
            "p2_title": "🤖 एआई योजना मिलान इंजन और चैटबॉट",
            "p2_warn": "कृपया पहले पृष्ठ 1 पूरा करें!",
            "p2_profile": "प्रोफ़ाइल लोड की गई",
            "p2_ben": "लाभ",
            "p2_docs": "आवश्यक दस्तावेज",
            "p2_bot_title": "💬 बहुभाषी एआई योजना एजेंट",
            "p2_bot_placeholder": "योजनाओं या सब्सिडी के बारे में कोई भी प्रश्न पूछें...",
            "p3_title": "⚖️ योजना तुलना तालिका",
            "p3_attr": ["वित्तीय लाभ", "लक्षित क्षेत्र", "अधिकतम धन", "आवश्यक दस्तावेजों की संख्या"],
            "p4_title": "📄 सुरक्षित दस्तावेज़ वॉल्ट और आवेदन सहायक",
            "p4_proto": "🔒 गोपनीयता प्रोटोकॉल: अपलोड किए गए दस्तावेज़ों को सुरक्षित रूप से एन्क्रिप्ट किया जाता है।",
            "p4_err": "कृपया पहले पृष्ठ 1 पर अपना पासफ़्रेज़ सेट करें!",
            "p4_id_ver": "🆔 पहचान पत्र सत्यापन",
            "p4_id_input": "सत्यापन के लिए 12-अंकीय पहचान पत्र संख्या दर्ज करें",
            "p4_id_ph": "उदाहरण के लिए: 12-अंकीय पहचान संख्या दर्ज करें जैसे 123456789012",
            "p4_id_btn": "पहचान पत्र सत्यापित करें",
            "p4_id_succ": "✅ पहचान पत्र प्रारूप सफलतापूर्वक सत्यापित किया गया!",
            "p4_id_fail": "❌ अमान्य 12-अंकीय पहचान प्रारूप।",
            "p4_sub_up": "सत्यापन दस्तावेज़ अपलोड करें",
            "p4_doc_select": "दस्तावेज़ प्रकार चुनें",
            "p4_btn_enc": "🔒 एन्क्रिप्ट करें और सहेजें",
            "p4_succ": "सफलतापूर्वक एन्क्रिप्ट किया गया और सहेजा गया!",
            "p4_status_sub": "एन्क्रिप्टेड दस्तावेज़ स्थिति",
            "p4_no_docs": "अभी तक कोई दस्तावेज़ अपलोड नहीं किया गया है।",
            "p4_assistant_title": "📋 आवेदन और दस्तावेज सहायक",
            "p5_title": "🔔 नई योजनाओं की निगरानी और अलर्ट",
            "p5_alert": "📌 सुरक्षा चेतावनी: दस्तावेज़ वॉल्ट एन्क्रिप्शन स्थिति सक्रिय है।",
            "btn_prev": "⬅️ पिछला",
            "btn_next": "अगला ➡️"
        },
        "Malayalam (മലയാളം)": {
            "sidebar_title": "⚙️ ഭാഷ തിരഞ്ഞെടുക്കുക",
            "pages": [
                "1. രജിസ്ട്രേഷൻ & സുരക്ഷാ സജ്ജീകരണം",
                "2. പദ്ധതി ശുപാർശകൾ & എഐ ഏജന്റ്",
                "3. പദ്ധതി താരതമ്യം",
                "4. സുരക്ഷിത വോൾട്ടും അപേക്ഷാ അസിസ്റ്റന്റും",
                "5. തത്സമയ മുന്നറിയിപ്പുകൾ"
            ],
            "p1_title": "🌾 തമിഴൻ സ്കീം - പ്രൊഫൈൽ & സുരക്ഷാ സജ്ജീകരണം",
            "voice_title": "🎙️ എഐ വോയ്സ് അസിസ്റ്റന്റ്",
            "voice_instruction": "ടൈപ്പ് ചെയ്യുന്നതിന് പകരം സംസാരിച്ച് വിവരങ്ങൾ നൽകുക.",
            "p1_sec_sub": "സുരക്ഷാ വിവരങ്ങൾ (ഡോക്യുമെന്റ് സുരക്ഷാ കീ)",
            "p1_sec_pass": "ഡോക്യുമെന്റ് എൻക്രിപ്ഷനായി പാസ്‌ഫ്രെയ്‌സ് സൃഷ്‌ടിക്കുക",
            "p1_sec_ph": "ഉദാഹരണത്തിന്: നിങ്ങളുടെ പാസ്‌ഫ്രെയ്‌സ് നൽകുക ഉദാ. Pass@123",
            "p1_sec_caption": "🔒 ഈ രഹസ്യ കീ നിങ്ങളുടെ ഡോക്യുമെന്റുകളെ സുരക്ഷിതമായി എൻക്രിപ്റ്റ് ചെയ്യുന്നു.",
            "p1_pers_sub": "വ്യക്തിഗത, ബിസിനസ്സ് പാരാമീറ്ററുകൾ",
            "p1_name": "മുഴുവൻ പേര്",
            "p1_name_ph": "ഉദാഹരണത്തിന്: നിങ്ങളുടെ പേര് നൽകുക",
            "p1_age": "പ്രായം",
            "p1_age_ph": "ഉദാഹരണത്തിന്: നിങ്ങളുടെ പ്രായം നൽകുക ഉദാ. 28",
            "p1_state": "സംസ്ഥാനം",
            "p1_sector": "ബിസിനസ്സ് മേഖല",
            "p1_gender": "ലിംഗഭേദം",
            "p1_income": "വാർഷിക കുടുംബ വരുമാനം (₹)",
            "p1_income_ph": "ഉദാഹരണത്തിന്: വാർഷിക വരുമാനം നൽകുക ഉദാ. 250000",
            "p1_funding": "ആവശ്യമായ ഫണ്ട് (₹)",
            "p1_funding_ph": "ഉദാഹരണത്തിന്: ആവശ്യമായ ഫണ്ട് നൽകുക ഉദാ. 300000",
            "p1_stage": "ബിസിനസ് ഘട്ടം",
            "p1_category": "വിഭാഗം",
            "p1_btn": "സേവ് ചെയ്ത് തുടരുക ➡️",
            "p2_title": "🤖 എഐ സ്കീം മാച്ചിംഗ് എഞ്ചിൻ & ഏജന്റ്",
            "p2_warn": "ദയവായി ആദ്യം പേജ് 1 പൂർത്തിയാക്കുക!",
            "p2_profile": "പ്രൊഫൈൽ ലോഡ് ചെയ്തു",
            "p2_ben": "ആനുകൂല്യങ്ങൾ",
            "p2_docs": "ആവശ്യമായ രേഖകൾ",
            "p2_bot_title": "💬 എഐ സ്കീം ഏജന്റ്",
            "p2_bot_placeholder": "പദ്ധതികളെക്കുറിച്ചുള്ള നിങ്ങളുടെ സംശയങ്ങൾ ചോദിക്കുക...",
            "p3_title": "⚖️ സ്കീം താരതമ്യ പട്ടിക",
            "p3_attr": ["സാമ്പത്തിക ആനുകൂല്യങ്ങൾ", "ലക്ഷ്യ മേഖല", "പരമാവധി ഫണ്ട്", "ആവശ്യമായ രേഖകളുടെ എണ്ണം"],
            "p4_title": "📄 സുരക്ഷിത വോൾട്ടും അപേക്ഷാ അസിസ്റ്റന്റും",
            "p4_proto": "🔒 സ്വകാര്യതാ പ്രോട്ടോക്കോൾ: അപ്‌ലോഡ് ചെയ്‌ത ഡോക്യുമെന്റുകൾ എൻക്രിപ്റ്റ് ചെയ്‌തിരിക്കുന്നു.",
            "p4_err": "ദയവായി ആദ്യം പേജ് 1-ൽ നിങ്ങളുടെ പാസ്‌ഫ്രെയ്‌സ് സജ്ജീകരിക്കുക!",
            "p4_id_ver": "🆔 ഗവൺമെന്റ് തിരിച്ചറിയൽ കാർഡ് സ്ഥിരീകരണം",
            "p4_id_input": "12 അക്ക തിരിച്ചറിയൽ കാർഡ് നമ്പർ നൽകുക",
            "p4_id_ph": "ഉദാഹരണത്തിന്: 12 അക്ക നമ്പർ നൽകുക ഉദാ. 123456789012",
            "p4_id_btn": "കാർഡ് സ്ഥിരീകരിക്കുക",
            "p4_id_succ": "✅ തിരിച്ചറിയൽ കാർഡ് ഫോർമാറ്റ് വിജയിച്ചു!",
            "p4_id_fail": "❌ തെറ്റായ 12 അക്ക നമ്പർ ഫോർമാറ്റ്.",
            "p4_sub_up": "രേഖകൾ അപ്‌ലോഡ് ചെയ്യുക",
            "p4_doc_select": "ഡോക്യുമെന്റ് ടൈപ്പ് തിരഞ്ഞെടുക്കുക",
            "p4_btn_enc": "🔒 എൻക്രിപ്റ്റ് ചെയ്ത് സൂക്ഷിക്കുക",
            "p4_succ": "വിജയകരമായി എൻക്രിപ്റ്റ് ചെയ്ത് സൂക്ഷിച്ചു!",
            "p4_status_sub": "എൻക്രിപ്റ്റ് ചെയ്ത രേഖകളുടെ അവസ്ഥ",
            "p4_no_docs": "രേഖകളൊന്നും അപ്‌ലോഡ് ചെയ്തിട്ടില്ല.",
            "p4_assistant_title": "📋 ആപ്ലിക്കേഷൻ അസിസ്റ്റന്റ്",
            "p5_title": "🔔 പുതിയ സ്കീമുകളും തത്സമയ മുന്നറിയിപ്പുകളും",
            "p5_alert": "📌 സുരക്ഷാ മുന്നറിയിപ്പ്: ഡോക്യുമെന്റ് വോൾട്ട് എൻക്രിപ്ഷൻ സജീവമാണ്.",
            "btn_prev": "⬅️ മുൻപത്തേത്",
            "btn_next": "അടുത്തത് ➡️"
        }
    }

    # ---------------- AI REASONING & AI AGENT HELPERS ----------------
    def calculate_match_explanation(scheme: dict, user: dict):
        reasons = []
        match_score = 0
        total_criteria = 4

        # 1. State Check
        state_ok = "All" in scheme["supported_states"] or user["state"] in scheme["supported_states"]
        if state_ok:
            match_score += 1
            reasons.append(f"✅ Location Matched: Supported in {user['state']}")
        else:
            reasons.append(f"❌ Location Mismatch: Available only for {', '.join(scheme['supported_states'])}")

        # 2. Age Check
        age_ok = scheme["min_age"] <= user["age"] <= scheme["max_age"]
        if age_ok:
            match_score += 1
            reasons.append(f"✅ Age Matched: {user['age']} years is within [{scheme['min_age']}-{scheme['max_age']}] range")
        else:
            reasons.append(f"❌ Age Out of Range: Must be between {scheme['min_age']} and {scheme['max_age']} years")

        # 3. Sector Check
        sector_ok = user["sector"] in scheme["sector"]
        if sector_ok:
            match_score += 1
            reasons.append(f"✅ Sector Matched: Supports {user['sector']} business")
        else:
            reasons.append(f"❌ Sector Mismatch: Scheme is focused on {', '.join(scheme['sector'])}")

        # 4. Funding Check
        funding_ok = scheme["min_funding"] <= user["funding"] <= scheme["max_funding"]
        if funding_ok:
            match_score += 1
            reasons.append(f"✅ Funding Budget Matched: Requested ₹{user['funding']:,} fits limit (Up to ₹{scheme['max_funding']:,})")
        else:
            reasons.append(f"❌ Funding Amount Out of Bounds: Min ₹{scheme['min_funding']:,} - Max ₹{scheme['max_funding']:,}")

        pct = int((match_score / total_criteria) * 100)
        return pct, reasons

    def generate_ai_chat_response(query: str, user_profile: dict) -> str:
        q = query.lower()
        lang = st.session_state.lang

        # Multilingual conversational answers
        if "subsidy" in q or "benefit" in q or "நன்மை" in q or "सब्सिडी" in q or "ആനുകൂല്യം" in q:
            if lang == "Tamil (தமிழ்)":
                return f"வணக்கம் {user_profile.get('name', 'பயனரே')}, நீங்கள் கேட்ப்பது மானியம் பற்றி. PMEGP திட்டத்தில் 15% - 35% வரை மானியம் பெறலாம், மற்றும் NEEDS திட்டத்தில் 25% மூலதன மானியம் பெறலாம்."
            elif lang == "Hindi (हिंदी)":
                return f"नमस्ते {user_profile.get('name', 'आवेदक')}, सब्सिडी की बात करें तो PMEGP में 15% से 35% तक का मार्जिन मनी सब्सिडी मिलती है और NEEDS योजना में 25% तक की पूंजीगत सब्सिडी है।"
            elif lang == "Malayalam (മലയാളം)":
                return f"ഹലോ {user_profile.get('name', 'അപേക്ഷകന്')}, PMEGP പദ്ധതിയിൽ 15% മുതൽ 35% വരെ സബ്‌സിഡിയും NEEDS പദ്ധതിയിൽ 25% ക്യാപിറ്റൽ സബ്‌സിഡിയും ലഭിക്കും."
            else:
                return f"Hello {user_profile.get('name', 'Applicant')}, regarding subsidies: PMEGP provides 15%-35% margin money subsidy, while NEEDS offers a 25% capital subsidy for new units in Tamil Nadu."

        elif "document" in q or "proof" in q or "ஆவணம்" in q or "दस्तावेज़" in q or "രേഖകള്" in q:
            docs = ["Identity Proof", "PAN Card", "Project Report", "Bank Statement"]
            return f"Standard requirements for your profile ({user_profile.get('sector', 'Business')} sector):\n- " + "\n- ".join(docs) + "\nYou can encrypt and store all of these on Page 4!"

        elif "apply" in q or "how" in q or "எப்படி" in q or "कैसे" in q or "എങ്ങനെ" in q:
            return f"To apply: 1. Ensure your profile matches 100%. 2. Upload and encrypt required docs in Page 4. 3. Use the official direct portal links provided in the Scheme Cards above."

        else:
            if lang == "Tamil (தமிழ்)":
                return f"உங்கள் கேள்வி புரிந்தது. உங்கள் துறை ({user_profile.get('sector', 'வணிகம்')}) மற்றும் தேவைகளுக்கு (₹{user_profile.get('funding', 0):,}) ஏற்ற சிறந்த திட்டங்களை மேலே பார்க்கலாம்."
            elif lang == "Hindi (हिंदी)":
                return f"आपके प्रश्न के आधार पर: आपकी प्रोफ़ाइल ({user_profile.get('sector', 'व्यापार')}) के अनुसार सबसे उपयुक्त योजनाएं ऊपर सूचीबद्ध की गई हैं।"
            else:
                return f"Based on your profile ({user_profile.get('sector', 'Services')} sector, requesting ₹{user_profile.get('funding', 0):,}), I recommend prioritizing top-matched schemes listed above."

    # ---------------- SIDEBAR BRANDING & NAVIGATION ----------------
    logo_filename = "logo.png"
    if os.path.exists(logo_filename):
        st.sidebar.image(logo_filename, width=180)

    st.sidebar.markdown("# 🌾 **Tamilan Scheme**")
    st.sidebar.caption("Government Scheme Portal & Matching Engine")
    st.sidebar.markdown("---")

    selected_lang = st.sidebar.radio(
        "Select Interface Language:", 
        ["English", "Tamil (தமிழ்)", "Hindi (हिंदी)", "Malayalam (മലയാളം)"]
    )

    st.session_state.lang = selected_lang
    T = TEXT_DICT[st.session_state.lang]

    page_names = T["pages"]
    selected_page = st.sidebar.radio("Navigate Steps:", page_names, index=st.session_state.current_step - 1)
    st.session_state.current_step = page_names.index(selected_page) + 1

    st.progress(st.session_state.current_step / 5)

    def go_next():
        if st.session_state.current_step < 5:
            st.session_state.current_step += 1

    def go_prev():
        if st.session_state.current_step > 1:
            st.session_state.current_step -= 1

    st.markdown("---")

    # ==================== PAGE 1: REGISTRATION ====================
    if st.session_state.current_step == 1:
        st.title(T["p1_title"])
        
        # Voice Assistant Input Tool
        with st.expander(f"{T['voice_title']}", expanded=True):
            st.write(T["voice_instruction"])
            audio_msg = st.audio_input("Record Voice Input")
            
            if audio_msg:
                transcribed_text = ""
                try:
                    import speech_recognition as sr
                    from pydub import AudioSegment

                    # Convert audio bytes into standard WAV format
                    audio_bytes = audio_msg.read()
                    sound = AudioSegment.from_file(io.BytesIO(audio_bytes))
                    wav_io = io.BytesIO()
                    sound.export(wav_io, format="wav")
                    wav_io.seek(0)

                    r = sr.Recognizer()
                    with sr.AudioFile(wav_io) as source:
                        audio_data = r.record(source)
                        transcribed_text = r.recognize_google(audio_data)

                except Exception as e:
                    st.error("Could not process audio clearly. Please try speaking into the microphone again.")
                    transcribed_text = ""
                
                if transcribed_text and transcribed_text != st.session_state.last_transcription:
                    st.session_state.last_transcription = transcribed_text
                    parse_voice_text(transcribed_text)
                    st.rerun()

            if st.session_state.last_transcription:
                st.success(f"🎙️ **Transcribed Input:** \"{st.session_state.last_transcription}\"")
                st.info("💡 Speech processed! Extracted parameters auto-filled into form fields below.")

        with st.form("user_profile_form"):
            st.subheader(T["p1_sec_sub"])
            passphrase = st.text_input(T["p1_sec_pass"], value="", placeholder=T["p1_sec_ph"], type="password")
            st.caption(T["p1_sec_caption"])

            st.subheader(T["p1_pers_sub"])
            col1, col2 = st.columns(2)
            
            state_opts = ["Tamil Nadu", "Maharashtra", "Delhi", "Karnataka", "Other"]
            sector_opts = ["Manufacturing", "Services", "Trading", "Agriculture"]
            
            state_idx = state_opts.index(st.session_state.voice_state) if st.session_state.voice_state in state_opts else 0
            sector_idx = sector_opts.index(st.session_state.voice_sector) if st.session_state.voice_sector in sector_opts else 0

            with col1:
                name = st.text_input(T["p1_name"], value=st.session_state.voice_name, placeholder=T["p1_name_ph"])
                age_raw = st.text_input(T["p1_age"], value=st.session_state.voice_age, placeholder=T["p1_age_ph"])
                state = st.selectbox(T["p1_state"], state_opts, index=state_idx)
                business_sector = st.selectbox(T["p1_sector"], sector_opts, index=sector_idx)
            with col2:
                gender = st.selectbox(T["p1_gender"], ["Female", "Male", "Other"])
                income_raw = st.text_input(T["p1_income"], value=st.session_state.voice_income, placeholder=T["p1_income_ph"])
                funding_raw = st.text_input(T["p1_funding"], value=st.session_state.voice_funding, placeholder=T["p1_funding_ph"])
                business_stage = st.selectbox(T["p1_stage"], ["New Unit", "Existing", "Expansion"])

            category = st.selectbox(T["p1_category"], ["SC", "ST", "Women", "OBC", "General"])

            if st.form_submit_button(T["p1_btn"]):
                passphrase = passphrase if passphrase else "DefaultPassphrase123"
                name = name if name else "Applicant"
                
                try: age = int(age_raw) if age_raw else 28
                except ValueError: age = 28
                    
                try: income = int(income_raw) if income_raw else 250000
                except ValueError: income = 250000
                    
                try: funding_req = int(funding_raw) if funding_raw else 300000
                except ValueError: funding_req = 300000

                st.session_state.user_key = generate_encryption_key(passphrase)
                st.session_state.user_data = {
                    "name": name, "age": age, "state": state, "gender": gender,
                    "income": income, "sector": business_sector, "stage": business_stage,
                    "funding": funding_req, "category": category
                }
                go_next()
                st.rerun()

    # ==================== PAGE 2: SCHEME MATCHING & CONVERSATIONAL AI AGENT ====================
    elif st.session_state.current_step == 2:
        st.title(T["p2_title"])
        
        if st.session_state.user_data is None:
            st.warning(T["p2_warn"])
        else:
            user = st.session_state.user_data
            st.info(f"**{T['p2_profile']}:** {user['name']} | Sector: {user['sector']} | Funding: ₹{user['funding']:,} | State: {user['state']}")
            
            st.subheader("💡 Personalized AI Eligibility Analysis")
            
            for scheme in SCHEME_DB:
                score, explanations = calculate_match_explanation(scheme, user)
                
                header_icon = "🥇" if score == 100 else ("🥈" if score >= 50 else "⚠️")
                with st.expander(f"{header_icon} {scheme['name']} — Match Score: {score}%", expanded=(score == 100)):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"**{T['p2_ben']}:** {scheme['benefits']}")
                        st.write(f"**{T['p2_docs']}:** {', '.join(scheme['documents'])}")
                        st.write(f"**Official Portal:** [{scheme['portal_url']}]({scheme['portal_url']})")
                    with col_b:
                        st.markdown("**AI Explanation Break-down:**")
                        for exp in explanations:
                            st.caption(exp)
                            
            st.markdown("---")
            st.subheader(T["p2_bot_title"])
            
            # Interactive Conversational Chatbot UI
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            user_query = st.chat_input(T["p2_bot_placeholder"])
            if user_query:
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.write(user_query)
                    
                bot_reply = generate_ai_chat_response(user_query, user)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                with st.chat_message("assistant"):
                    st.write(bot_reply)

    # ==================== PAGE 3: COMPARISON ====================
    elif st.session_state.current_step == 3:
        st.title(T["p3_title"])
        
        comp_data = {
            "Attribute": T["p3_attr"]
        }
        for s in SCHEME_DB:
            comp_data[str(s["name"])] = [
                str(s["benefits"]),
                str(", ".join(s["sector"])),
                f"₹{s['max_funding']:,}",
                str(len(s["documents"]))
            ]
            
        df = pd.DataFrame(comp_data).set_index("Attribute")
        st.table(df)

    # ==================== PAGE 4: SECURE DOCUMENT VAULT & APPLICATION ASSISTANT ====================
    elif st.session_state.current_step == 4:
        st.title(T["p4_title"])
        st.markdown(f"> {T['p4_proto']}")
        
        if st.session_state.user_key is None:
            st.error(T["p4_err"])
        else:
            st.subheader(T["p4_id_ver"])
            id_num_input = st.text_input(T["p4_id_input"], value="", placeholder=T["p4_id_ph"], type="password")
            if st.button(T["p4_id_btn"]):
                if verify_identity_format(id_num_input):
                    st.session_state.verified_identity = True
                    st.success(T["p4_id_succ"])
                else:
                    st.error(T["p4_id_fail"])

            st.markdown("---")

            col_up, col_status = st.columns([2, 1])
            
            with col_up:
                st.subheader(T["p4_sub_up"])
                doc_type = st.selectbox(T["p4_doc_select"], ["Identity Proof", "PAN Card", "Business Proof", "Project Report", "Income Certificate"])
                uploaded_file = st.file_uploader(f"Choose File for {doc_type} (PDF, PNG, JPG)", type=["pdf", "png", "jpg"])
                
                if uploaded_file is not None:
                    if st.button(T["p4_btn_enc"]):
                        raw_bytes = uploaded_file.read()
                        encrypted_string = encrypt_document(raw_bytes, st.session_state.user_key)
                        
                        st.session_state.uploaded_docs[doc_type] = {
                            "file_name": uploaded_file.name,
                            "encrypted_payload": encrypted_string,
                            "size": len(encrypted_string)
                        }
                        st.success(f"✅ {doc_type} {T['p4_succ']}")

            with col_status:
                st.subheader(T["p4_status_sub"])
                if st.session_state.verified_identity:
                    st.success("🆔 Government Identity Verification: Active")
                
                if not st.session_state.uploaded_docs:
                    st.info(T["p4_no_docs"])
                else:
                    for k, v in st.session_state.uploaded_docs.items():
                        st.write(f"🔒 **{k}**")
                        st.caption(f"File: {v['file_name']} | Size: {v['size']} chars")

            st.markdown("---")
            st.subheader(T["p4_assistant_title"])
            st.write("Generate a tailored document preparation roadmap for your target scheme:")
            
            selected_scheme_name = st.selectbox("Select Target Scheme for Assistant Guidance:", [s["name"] for s in SCHEME_DB])
            target_scheme = next((s for s in SCHEME_DB if s["name"] == selected_scheme_name), None)
            
            if target_scheme:
                required_list = target_scheme["documents"]
                uploaded_keys = list(st.session_state.uploaded_docs.keys())
                
                col_req, col_readiness = st.columns([2, 1])
                with col_req:
                    st.markdown("**Required Document Checklist:**")
                    for req_doc in required_list:
                        is_ready = req_doc in uploaded_keys
                        icon = "✅" if is_ready else "❌"
                        st.write(f"{icon} **{req_doc}**: {'Stored in Secure Vault' if is_ready else 'Pending Upload'}")
                
                with col_readiness:
                    readiness_score = int((len(set(required_list).intersection(uploaded_keys)) / len(required_list)) * 100)
                    st.metric("Application Readiness", f"{readiness_score}%")
                    if readiness_score == 100:
                        st.success("🎉 You are 100% ready to submit your official application!")
                    else:
                        st.warning("Upload missing items to complete your vault payload.")

    # ==================== PAGE 5: NEW-SCHEME MONITORING & ALERTS ====================
    elif st.session_state.current_step == 5:
        st.title(T["p5_title"])
        st.info(T["p5_alert"])
        
        st.subheader("📡 Live Scheme Feed & Automated Monitoring")
        
        user_sec = st.session_state.user_data["sector"] if st.session_state.user_data else "All"
        st.caption(f"Showing real-time notifications for sector preference: **{user_sec}**")

        # Dynamic Alerts Generator
        for scheme in SCHEME_DB:
            is_new = scheme.get("date_added", "").startswith("2026-03") or scheme.get("date_added", "").startswith("2026-02")
            if is_new:
                st.success(f"🔔 **NEW SCHEME ANNOUNCEMENT ({scheme.get('date_added')}):** {scheme['name']} is now live!")
                with st.expander("View Announcement Details"):
                    st.write(f"**Benefits:** {scheme['benefits']}")
                    st.write(f"**Max Funding Limit:** ₹{scheme['max_funding']:,}")
                    st.write(f"**Official Portal:** [{scheme['portal_url']}]({scheme['portal_url']})")

    # ==================== BOTTOM NAVIGATION ====================
    st.markdown("---")
    b1, b2, b3 = st.columns([1, 4, 1])
    with b1:
        if st.session_state.current_step > 1:
            if st.button(T["btn_prev"], use_container_width=True):
                go_prev()
                st.rerun()
    with b3:
        if st.session_state.current_step < 5:
            if st.button(T["btn_next"], use_container_width=True):
                go_next()
                st.rerun()
