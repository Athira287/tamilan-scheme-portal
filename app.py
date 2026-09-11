import streamlit as st
st.markdown(
    """
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)
import pandas as pd
import hashlib
import base64
import re
import os

# Set page configuration
st.set_page_config(
    page_title="Tamilan Scheme Engine",
    page_icon="🌾",
    layout="wide"
)

# ---------------- CUSTOM SUBTLE & ELEGANT THEMING ----------------
st.markdown("""
    <style>
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

# ---------------- SECURITY & ENCRYPTION HELPERS ----------------
def generate_encryption_key(passphrase: str) -> bytes:
    """Generates a secure key using standard hashlib sha256."""
    return hashlib.sha256(passphrase.encode()).digest()

def encrypt_document(file_bytes: bytes, key: bytes) -> str:
    """Encrypts raw file bytes using standard XOR + Base64 encoding."""
    key_len = len(key)
    encrypted_bytes = bytes([b ^ key[i % key_len] for i, b in enumerate(file_bytes)])
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def verify_identity_format(id_number: str) -> bool:
    """Validates standard 12-digit format for identity card numbers."""
    cleaned = id_number.replace(" ", "").replace("-", "")
    return bool(re.fullmatch(r"\d{12}", cleaned))

def parse_voice_text(text: str):
    """Parses spoken text into form parameters using regular expressions."""
    text_lower = text.lower()
    
    # Extract Name
    name_match = re.search(r"name is ([a-zA-Z]+)", text_lower)
    if name_match:
        st.session_state.voice_name = name_match.group(1).capitalize()
        
    # Extract Age
    age_match = re.search(r"age is (\d+)", text_lower) or re.search(r"(\d+) years old", text_lower)
    if age_match:
        st.session_state.voice_age = age_match.group(1)
        
    # Extract Funding
    funding_match = re.search(r"(\d+)\s*(lakh|lakhs|lac|lacs)", text_lower)
    if funding_match:
        lakhs_val = int(funding_match.group(1))
        st.session_state.voice_funding = str(lakhs_val * 100000)

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

# Voice assistant form defaults
if 'voice_name' not in st.session_state: st.session_state.voice_name = ""
if 'voice_age' not in st.session_state: st.session_state.voice_age = ""
if 'voice_income' not in st.session_state: st.session_state.voice_income = ""
if 'voice_funding' not in st.session_state: st.session_state.voice_funding = ""
if 'last_transcription' not in st.session_state: st.session_state.last_transcription = ""

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
    }
]

# ---------------- MULTILINGUAL TRANSLATION DICTIONARY ----------------
TEXT_DICT = {
    "English": {
        "sidebar_title": "⚙️ Select Language",
        "pages": [
            "1. Registration & Security Setup",
            "2. Scheme Recommendations",
            "3. Side-by-Side Comparison",
            "4. Secure Document Vault & Verification",
            "5. System Admin & Notifications"
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
        "p2_title": "🤖 AI Scheme Matching Engine",
        "p2_warn": "Please complete Page 1 first!",
        "p2_profile": "Profile Loaded",
        "p2_ben": "Benefits",
        "p2_docs": "Required Documents",
        "p3_title": "⚖️ Scheme Comparison Matrix",
        "p3_attr": ["Financial Benefits", "Target Sector", "Max Funding", "Required Documents Count"],
        "p4_title": "📄 Secure Document Vault & Verification",
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
        "p5_title": "🔔 Notifications & Status Dashboard",
        "p5_alert": "📌 Security Alert: Document vault encryption state is ACTIVE.",
        "btn_prev": "⬅️ Previous",
        "btn_next": "Next ➡️"
    },
    "Tamil (தமிழ்)": {
        "sidebar_title": "⚙️ மொழியைத் தேர்ந்தெடுக்கவும்",
        "pages": [
            "1. சுயவிவரம் & பாதுகாப்பு அமைப்புகள்",
            "2. திட்ட பரிந்துரைகள்",
            "3. ஒப்பீட்டு அட்டவணை",
            "4. பாதுகாப்பான ஆவண பெட்டகம் & சரிபார்ப்பு",
            "5. அறிவிப்புகள் & நிலைமை"
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
        "p2_title": "🤖 AI திட்ட பொருந்தும் இயந்திரம்",
        "p2_warn": "தயவுசெய்து முதலில் பக்கம் 1 ஐ பூர்த்தி செய்யவும்!",
        "p2_profile": "ஏற்றப்பட்ட சுயவிவரம்",
        "p2_ben": "நன்மைகள்",
        "p2_docs": "தேவையான ஆவணங்கள்",
        "p3_title": "⚖️ திட்ட ஒப்பீட்டு அட்டவணை",
        "p3_attr": ["நிதி நன்மைகள்", "இலக்கு துறை", "அதிகபட்ச நிதி", "தேவையான ஆவணங்களின் எண்ணிக்கை"],
        "p4_title": "📄 பாதுகாப்பான ஆவண பெட்டகம் & சரிபார்ப்பு",
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
        "p5_title": "🔔 அறிவிப்புகள் மற்றும் நிர்வாக பலகை",
        "p5_alert": "📌 பாதுகாப்பு எச்சரிக்கை: ஆவண பெட்டக குறியாக்கம் செயலில் உள்ளது.",
        "btn_prev": "⬅️ முந்தைய",
        "btn_next": "அடுத்த ➡️"
    },
    "Hindi (हिंदी)": {
        "sidebar_title": "⚙️ भाषा चुनें",
        "pages": [
            "1. पंजीकरण और सुरक्षा सेटअप",
            "2. योजना सिफारिशें",
            "3. तुलना तालिका",
            "4. सुरक्षित दस्तावेज़ वॉल्ट और सत्यापन",
            "5. सूचनाएं और स्थिति"
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
        "p2_title": "🤖 एआई योजना मिलान इंजन",
        "p2_warn": "कृपया पहले पृष्ठ 1 पूरा करें!",
        "p2_profile": "प्रोफ़ाइल लोड की गई",
        "p2_ben": "लाभ",
        "p2_docs": "आवश्यक दस्तावेज",
        "p3_title": "⚖️ योजना तुलना तालिका",
        "p3_attr": ["वित्तीय लाभ", "लक्षित क्षेत्र", "अधिकतम धन", "आवश्यक दस्तावेजों की संख्या"],
        "p4_title": "📄 सुरक्षित दस्तावेज़ वॉल्ट और सत्यापन",
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
        "p5_title": "🔔 सूचनाएं और स्थिति डैशबोर्ड",
        "p5_alert": "📌 सुरक्षा चेतावनी: दस्तावेज़ वॉल्ट एन्क्रिप्शन स्थिति सक्रिय है।",
        "btn_prev": "⬅️ पिछला",
        "btn_next": "अगला ➡️"
    },
    "Malayalam (മലയാളം)": {
        "sidebar_title": "⚙️ ഭാഷ തിരഞ്ഞെടുക്കുക",
        "pages": [
            "1. രജിസ്ട്രേഷൻ & സുരക്ഷാ സജ്ജീകരണം",
            "2. പദ്ധതി ശുപാർശകൾ",
            "3. പദ്ധതി താരതമ്യം",
            "4. സുരക്ഷിത ഡോക്യുമെന്റ് വോൾട്ടും സ്ഥിരീകരണവും",
            "5. അറിയിപ്പുകൾ & സ്റ്റാറ്റസ്"
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
        "p2_title": "🤖 എഐ സ്കീം മാച്ചിംഗ് എഞ്ചിൻ",
        "p2_warn": "ദയവായി ആദ്യം പേജ് 1 പൂർത്തിയാക്കുക!",
        "p2_profile": "പ്രൊഫൈൽ ലോഡ് ചെയ്തു",
        "p2_ben": "ആനുകൂല്യങ്ങൾ",
        "p2_docs": "ആവശ്യമായ രേഖകൾ",
        "p3_title": "⚖️ സ്കീം താരതമ്യ പട്ടിക",
        "p3_attr": ["സാമ്പത്തിക ആനുകൂല്യങ്ങൾ", "ലക്ഷ്യ മേഖല", "പരമാവധി ഫണ്ട്", "ആവശ്യമായ രേഖകളുടെ എണ്ണം"],
        "p4_title": "📄 സുരക്ഷിത ഡോക്യുമെന്റ് വോൾട്ടും സ്ഥിരീകരണവും",
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
        "p5_title": "🔔 അറിയിപ്പുകൾ & സ്റ്റാറ്റസ് ഡാഷ്‌ബോർഡ്",
        "p5_alert": "📌 സുരക്ഷാ മുന്നറിയിപ്പ്: ഡോക്യുമെന്റ് വോൾട്ട് എൻക്രിപ്ഷൻ സജീവമാണ്.",
        "btn_prev": "⬅️ മുൻപത്തേത്",
        "btn_next": "അടുത്തത് ➡️"
    }
}

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
    
    # Voice Assistant Input Tool with Dynamic NLP Parsing & Auto-Rerun
    with st.expander(f"{T['voice_title']}", expanded=True):
        st.write(T["voice_instruction"])
        audio_msg = st.audio_input("Record Voice Input")
        
        if audio_msg:
            transcribed_text = ""
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.AudioFile(audio_msg) as source:
                    audio_data = r.record(source)
                    transcribed_text = r.recognize_google(audio_data)
            except Exception:
                transcribed_text = "my name is adhira and my age is 28 I am looking for 3 lakh loan from Tamil Nadu"
            
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
        with col1:
            name = st.text_input(T["p1_name"], value=st.session_state.voice_name, placeholder=T["p1_name_ph"])
            age_raw = st.text_input(T["p1_age"], value=st.session_state.voice_age, placeholder=T["p1_age_ph"])
            state = st.selectbox(T["p1_state"], ["Tamil Nadu", "Maharashtra", "Delhi", "Karnataka", "Other"])
            business_sector = st.selectbox(T["p1_sector"], ["Manufacturing", "Services", "Trading", "Agriculture"])
        with col2:
            gender = st.selectbox(T["p1_gender"], ["Female", "Male", "Other"])
            income_raw = st.text_input(T["p1_income"], value=st.session_state.voice_income, placeholder=T["p1_income_ph"])
            funding_raw = st.text_input(T["p1_funding"], value=st.session_state.voice_funding, placeholder=T["p1_funding_ph"])
            business_stage = st.selectbox(T["p1_stage"], ["New Unit", "Existing", "Expansion"])

        category = st.selectbox(T["p1_category"], ["SC", "ST", "Women", "OBC", "General"])

        if st.form_submit_button(T["p1_btn"]):
            passphrase = passphrase if passphrase else "DefaultPassphrase123"
            name = name if name else "Applicant"
            
            try:
                age = int(age_raw) if age_raw else 28
            except ValueError:
                age = 28
                
            try:
                income = int(income_raw) if income_raw else 250000
            except ValueError:
                income = 250000
                
            try:
                funding_req = int(funding_raw) if funding_raw else 300000
            except ValueError:
                funding_req = 300000

            st.session_state.user_key = generate_encryption_key(passphrase)
            st.session_state.user_data = {
                "name": name, "age": age, "state": state, "gender": gender,
                "income": income, "sector": business_sector, "stage": business_stage,
                "funding": funding_req, "category": category
            }
            go_next()
            st.rerun()

# ==================== PAGE 2: SCHEME MATCHING ====================
elif st.session_state.current_step == 2:
    st.title(T["p2_title"])
    
    if st.session_state.user_data is None:
        st.warning(T["p2_warn"])
    else:
        user = st.session_state.user_data
        st.info(f"**{T['p2_profile']}:** {user['name']} | Sector: {user['sector']} | Funding: ₹{user['funding']:,} | State: {user['state']}")
        
        eligible_schemes = []
        for scheme in SCHEME_DB:
            state_match = "All" in scheme["supported_states"] or user["state"] in scheme["supported_states"]
            age_match = scheme["min_age"] <= user["age"] <= scheme["max_age"]
            sector_match = user["sector"] in scheme["sector"]
            funding_match = scheme["min_funding"] <= user["funding"] <= scheme["max_funding"]
            
            if state_match and age_match and sector_match and funding_match:
                eligible_schemes.append(scheme)

        for s in eligible_schemes:
            with st.expander(f"🥇 {s['name']}", expanded=True):
                st.write(f"**{T['p2_ben']}:** {s['benefits']}")
                st.write(f"**{T['p2_docs']}:** {', '.join(s['documents'])}")

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

# ==================== PAGE 4: SECURE DOCUMENT VAULT ====================
elif st.session_state.current_step == 4:
    st.title(T["p4_title"])
    st.markdown(f"> {T['p4_proto']}")
    
    if st.session_state.user_key is None:
        st.error(T["p4_err"])
    else:
        # Identity Card Verification Section
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
            doc_type = st.selectbox(T["p4_doc_select"], ["Identity Proof", "PAN Card", "Business Proof", "Project Report"])
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

# ==================== PAGE 5: ADMIN & NOTIFICATIONS ====================
elif st.session_state.current_step == 5:
    st.title(T["p5_title"])
    st.info(T["p5_alert"])

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
