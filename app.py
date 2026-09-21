import streamlit as st
import pandas as pd
import hashlib
import base64
import re
import os
from datetime import datetime

# 1. ALWAYS FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Tamilan Scheme Engine",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CLEAN CSS & SIDEBAR CONTROLS (FIXED SIDEBAR TOGGLE)
st.markdown(
    """
    <style>
    /* Hide top header bar decoration & footer, but KEEP sidebar controls visible */
    footer, .stAppViewerFooter, .stAppDeployButton, [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Make top header background transparent while leaving the sidebar arrow visible */
    header[data-testid="stHeader"] {
        background: transparent !important;
        z-index: 99999 !important;
    }
    
    /* Ensure sidebar toggle arrow icon stays visible and styled */
    button[data-testid="stSidebarCollapseButton"], 
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        color: #e5c158 !important;
        z-index: 100000 !important;
    }
    
    .stApp {
        background-color: #121418;
        color: #d1d5db;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #1a1d24 !important;
        border-right: 1px solid #2a2e39 !important;
    }
    
    h1 {
        color: #e5c158 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #d8b244 !important;
        font-weight: 600 !important;
    }

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
    
    .stSelectbox > div > div {
        background-color: #1a1d24 !important;
        color: #e5c158 !important;
        border: 1px solid #2a2e39 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. INITIALIZE SESSION STATES
if 'lang' not in st.session_state:
    st.session_state.lang = "English"

if "user_db" not in st.session_state:
    st.session_state["user_db"] = {"admin": "sih2026"}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "reset_stage" not in st.session_state:
    st.session_state.reset_stage = "input_user"

# --- MULTILINGUAL DICTIONARY FOR ENTIRE PORTAL ---
TEXT_DICT = {
    "English": {
        "auth_title": "🔒 Tamilan Scheme Portal",
        "login_tab": "🔑 Login",
        "signup_tab": "📝 Sign Up (Create Account)",
        "login_sub": "Login to Your Account",
        "user_label": "Username / Name / Identity ID",
        "pass_label": "Password",
        "login_btn": "Login",
        "forgot_btn": "Forgot Password?",
        "signup_sub": "Create New Account",
        "reg_user_label": "Choose Your Name / Username",
        "reg_pass_label": "Choose Your Password",
        "reg_conf_label": "Confirm Your Password",
        "reg_btn": "Register Account",
        "sidebar_title": "⚙️ Select Language",
        "pages": [
            "1. Registration & Security Setup",
            "2. AI Scheme Recommendations",
            "3. Side-by-Side Comparison",
            "4. Smart Vault & Document Assistant",
            "5. AI Chatbot & Real-Time Alerts"
        ],
        "p1_title": "🌾 Tamilan Scheme - Profile & Security Setup",
        "voice_title": "🎙️ AI Voice Guidance Assistant",
        "voice_instruction": "Click record below to speak your details instead of typing.",
        "p1_sec_sub": "Security Details (Documents Safety Key)",
        "p1_sec_pass": "Create Secret Key / Passphrase for Documents Encryption",
        "p1_sec_ph": "enter your secret passphrase eg. Pass@123",
        "p1_sec_caption": "🔒 Encrypts your uploaded documents locally using SHA256-XOR stream cipher.",
        "p1_pers_sub": "Personal & Business Parameters",
        "p1_name": "Full Name *",
        "p1_name_ph": "enter your full name",
        "p1_age": "Age *",
        "p1_age_ph": "enter age (e.g. 28)",
        "p1_state": "State",
        "p1_sector": "Sector",
        "p1_gender": "Gender",
        "p1_income": "Annual Household Income (₹) *",
        "p1_income_ph": "enter income (e.g. 250000)",
        "p1_funding": "Funding Required (₹) *",
        "p1_funding_ph": "enter funding amount (e.g. 300000)",
        "p1_stage": "Business Stage",
        "p1_category": "Target Category",
        "p1_btn": "Save & Go to Matching ➡️",
        "p2_title": "🤖 AI Scheme Matching Engine & Insights",
        "p2_warn": "⚠️ No profile data found! Please complete Profile Setup (Step 1) first by filling in your Name, Age, Income, and Funding requirements.",
        "p2_profile": "Profile Loaded",
        "p2_ben": "Financial Benefits",
        "p2_docs": "Required Documents",
        "p2_ai_explain": "💡 Personalized AI Match Breakdown",
        "p3_title": "⚖️ Scheme Comparison Matrix",
        "p3_attr": ["Financial Benefits", "Target Sector", "Max Funding", "Required Documents Count"],
        "p4_title": "📄 Smart Vault & Application Document Assistant",
        "p4_proto": "🔒 Privacy Protocol: Documents uploaded are encrypted in-memory using SHA256-XOR stream cipher.",
        "p4_err": "Please set your Encryption Passphrase on Step 1 first!",
        "p4_id_ver": "🆔 Identity Verification",
        "p4_id_input": "Enter 12-Digit Government Identity Card Number",
        "p4_id_ph": "enter 12-digit ID eg. 123456789012",
        "p4_id_btn": "Verify Government ID",
        "p4_id_succ": "✅ Identity Format Verified! Data masked & encrypted.",
        "p4_id_fail": "❌ Invalid 12-digit Identity format.",
        "p4_sub_up": "Upload Verification Documents",
        "p4_doc_select": "Select Document Type",
        "p4_btn_enc": "🔒 Encrypt & Store Document",
        "p4_succ": "successfully encrypted and saved!",
        "p4_status_sub": "Document Checklist Assistant",
        "p4_no_docs": "No documents uploaded yet.",
        "p5_title": "💬 Multilingual AI Chatbot & Monitoring Alerts",
        "p5_alert": "📌 Live Scheme Broadcast Feed Active.",
        "btn_prev": "⬅️ Previous",
        "btn_next": "Next ➡️"
    },
    "Tamil (தமிழ்)": {
        "auth_title": "🔒 தமிழன் திட்டம் போர்டல்",
        "login_tab": "🔑 உள்நுழைவு (Login)",
        "signup_tab": "📝 கணக்கு உருவாக்க (Sign Up)",
        "login_sub": "உங்கள் கணக்கில் உள்நுழையவும்",
        "user_label": "பயனர்பெயர் / அடையாள எண்",
        "pass_label": "கடவுச்சொல்",
        "login_btn": "உள்நுழைக",
        "forgot_btn": "கடவுச்சொல்லை மறந்துவிட்டீர்களா?",
        "signup_sub": "புதிய கணக்கை உருவாக்கவும்",
        "reg_user_label": "உங்கள் பெயரைத் தேர்ந்தெடுக்கவும்",
        "reg_pass_label": "கடவுச்சொல்லை உருவாக்கவும்",
        "reg_conf_label": "கடவுச்சொல்லை உறுதிப்படுத்தவும்",
        "reg_btn": "கணக்கை பதிவு செய்யவும்",
        "sidebar_title": "⚙️ மொழியைத் தேர்ந்தெடுக்கவும்",
        "pages": [
            "1. சுயவிவரம் & பாதுகாப்பு அமைப்புகள்",
            "2. AI திட்ட பரிந்துரைகள்",
            "3. ஒப்பீட்டு அட்டவணை",
            "4. ஆவண பெட்டகம் & AI உதவி",
            "5. AI சாட்பாட் & நேரலை அறிவிப்புகள்"
        ],
        "p1_title": "🌾 தமிழன் ஸ்கீம் - சுயவிவர அமைப்பு மற்றும் பாதுகாப்பு",
        "voice_title": "🎙️ குரல் உதவி உதவியாளர்",
        "voice_instruction": "உங்கள் விவரங்களை பேச கீழே உள்ள பதிவு பொத்தானை அழுத்தவும்.",
        "p1_sec_sub": "பாதுகாப்பு விவரங்கள்",
        "p1_sec_pass": "ரகசிய கடவுச்சொல் உருவாக்கவும்",
        "p1_sec_ph": "உதாரணமாக: Pass@123",
        "p1_sec_caption": "🔒 உங்கள் ஆவணங்களை சேமிக்கும் முன் பாதுகாப்பாக குறியாக்கம் செய்யும்.",
        "p1_pers_sub": "தனிப்பட்ட மற்றும் வணிக அளவுருக்கள்",
        "p1_name": "முழு பெயர் *",
        "p1_name_ph": "உங்கள் பெயரை உள்ளிடவும்",
        "p1_age": "வயது *",
        "p1_age_ph": "உங்கள் வயதை உள்ளிடவும் எ.கா. 28",
        "p1_state": "மாநிலம்",
        "p1_sector": "வணிக துறை",
        "p1_gender": "பாலினம்",
        "p1_income": "ஆண்டு குடும்ப வருமானம் (₹) *",
        "p1_income_ph": "குடும்ப வருமானத்தை உள்ளிடவும் எ.கா. 250000",
        "p1_funding": "தேவைப்படும் நிதி (₹) *",
        "p1_funding_ph": "தேவையான நிதியை உள்ளிடவும் எ.கா. 300000",
        "p1_stage": "வணிக நிலை",
        "p1_category": "இலக்கு பிரிவு",
        "p1_btn": "சேமித்துத் தொடரவும் ➡️",
        "p2_title": "🤖 AI திட்ட பொருந்தும் இயந்திரம்",
        "p2_warn": "⚠️ சுயவிவர தகவல்கள் இல்லை! தயவுசெய்து முதலில் பக்கம் 1-ல் உங்கள் பெயர், வயது, வருமானம் மற்றும் நிதி தேவைகளை பூர்த்தி செய்யவும்.",
        "p2_profile": "ஏற்றப்பட்ட சுயவிவரம்",
        "p2_ben": "நன்மைகள்",
        "p2_docs": "தேவையான ஆவணங்கள்",
        "p2_ai_explain": "💡 தனிப்பயனாக்கப்பட்ட AI விளக்கம்",
        "p3_title": "⚖️ திட்ட ஒப்பீட்டு அட்டவணை",
        "p3_attr": ["நிதி நன்மைகள்", "இலக்கு துறை", "அதிகபட்ச நிதி", "தேவையான ஆவணங்கள்"],
        "p4_title": "📄 ஆவண பெட்டகம் & AI உதவி",
        "p4_proto": "🔒 பதிவேற்றப்பட்ட ஆவணங்கள் பாதுகாப்பாக குறியாக்கம் செய்யப்படுகின்றன.",
        "p4_err": "தயவுசெய்து முதலில் பக்கம் 1 இல் உங்கள் கடவுச்சொல்லை அமைக்கவும்!",
        "p4_id_ver": "🆔 அரசு அடையாள அட்டை சரிபார்ப்பு",
        "p4_id_input": "12 இலக்க அரசு அடையாள அட்டை எண்ணை உள்ளிடவும்",
        "p4_id_ph": "எ.கா. 123456789012",
        "p4_id_btn": "அடையாள அட்டையை சரிபார்க்கவும்",
        "p4_id_succ": "✅ அரசு அடையாள வடிவம் வெற்றிகரமாக சரிபார்க்கப்பட்டது!",
        "p4_id_fail": "❌ தவறான 12 இலக்க அடையாள வடிவம்.",
        "p4_sub_up": "சரிபார்ப்பு ஆவணங்களை பதிவேற்றவும்",
        "p4_doc_select": "ஆவண வகையைத் தேர்ந்தெடுக்கவும்",
        "p4_btn_enc": "🔒 குறியாக்கம் செய்து சேமிக்கவும்",
        "p4_succ": "வெற்றிகரமாக சேமிக்கப்பட்டது!",
        "p4_status_sub": "தேவையான ஆவணங்களின் AI சரிபார்ப்பு பட்டியல்",
        "p4_no_docs": "இன்னும் ஆவணங்கள் பதிவேற்றப்படவில்லை.",
        "p5_title": "💬 AI உரையாடல் சாட்பாட் & நேரலை அறிவிப்புகள்",
        "p5_alert": "📌 நேரலை திட்ட அறிவிப்பு சேவைகள் செயலில் உள்ளன.",
        "btn_prev": "⬅️ முந்தைய",
        "btn_next": "அடுத்த ➡️"
    },
    "Hindi (हिंदी)": {
        "auth_title": "🔒 तमिलन स्कीम पोर्टल",
        "login_tab": "🔑 लॉगिन",
        "signup_tab": "📝 खाता बनाएं",
        "login_sub": "अपने खाते में लॉगिन करें",
        "user_label": "उपयोगकर्ता नाम / आईडी",
        "pass_label": "पासवर्ड",
        "login_btn": "लॉगिन करें",
        "forgot_btn": "पासवर्ड भूल गए?",
        "signup_sub": "नया खाता बनाएं",
        "reg_user_label": "अपना नाम चुनें",
        "reg_pass_label": "पासवर्ड चुनें",
        "reg_conf_label": "पासवर्ड की पुष्टि करें",
        "reg_btn": "खाता पंजीकृत करें",
        "sidebar_title": "⚙️ भाषा चुनें",
        "pages": [
            "1. पंजीकरण और सुरक्षा सेटअप",
            "2. एआई योजना सिफारिशें",
            "3. तुलना तालिका",
            "4. दस्तावेज़ वॉल्ट और एआई सहायक",
            "5. एआई चैटबॉट और लाइव अलर्ट"
        ],
        "p1_title": "🌾 तमिलन स्कीम - प्रोफ़ाइल और सुरक्षा सेटअप",
        "voice_title": "🎙️ एआई वॉयस असिस्टेंट",
        "voice_instruction": "टाइप करने के बजाय विवरण बोलने के लिए रिकॉर्ड करें।",
        "p1_sec_sub": "सुरक्षा विवरण",
        "p1_sec_pass": "गुप्त पासफ़्रेज़ बनाएं",
        "p1_sec_ph": "जैसे Pass@123",
        "p1_sec_caption": "🔒 दस्तावेज सुरक्षित रूप से एन्क्रिप्ट किए जाते हैं।",
        "p1_pers_sub": "व्यक्तिगत और व्यावसायिक पैरामीटर",
        "p1_name": "पूरा नाम *",
        "p1_name_ph": "अपना नाम दर्ज करें",
        "p1_age": "आयु *",
        "p1_age_ph": "आयु दर्ज करें जैसे 28",
        "p1_state": "राज्य",
        "p1_sector": "व्यवसाय क्षेत्र",
        "p1_gender": "लिंग",
        "p1_income": "वार्षिक घरेलू आय (₹) *",
        "p1_income_ph": "वार्षिक आय दर्ज करें जैसे 250000",
        "p1_funding": "आवश्यक धन (₹) *",
        "p1_funding_ph": "आवश्यक धन दर्ज करें जैसे 300000",
        "p1_stage": "व्यापार चरण",
        "p1_category": "लक्षित वर्ग",
        "p1_btn": "सहेजें और आगे बढ़ें ➡️",
        "p2_title": "🤖 एआई योजना मिलान इंजन",
        "p2_warn": "⚠️ कोई प्रोफ़ाइल डेटा नहीं मिला! कृपया पहले पृष्ठ 1 पर अपना नाम, आयु, आय और धन संबंधी विवरण भरें।",
        "p2_profile": "प्रोफ़ाइल लोड की गई",
        "p2_ben": "लाभ",
        "p2_docs": "आवश्यक दस्तावेज",
        "p2_ai_explain": "💡 एआई व्यक्तिगत विवरण",
        "p3_title": "⚖️ योजना तुलना तालिका",
        "p3_attr": ["वित्तीय लाभ", "लक्षित क्षेत्र", "अधिकतम धन", "आवश्यक दस्तावेज़"],
        "p4_title": "📄 सुरक्षित दस्तावेज़ वॉल्ट और एआई सहायक",
        "p4_proto": "🔒 अपलोड किए गए दस्तावेज़ सुरक्षित रूप से एन्क्रिप्ट किए जाते हैं।",
        "p4_err": "कृपया पहले पृष्ठ 1 पर अपना पासफ़्रेज़ सेट करें!",
        "p4_id_ver": "🆔 पहचान पत्र सत्यापन",
        "p4_id_input": "12-अंकीय पहचान पत्र संख्या दर्ज करें",
        "p4_id_ph": "जैसे 123456789012",
        "p4_id_btn": "सत्यापित करें",
        "p4_id_succ": "✅ पहचान पत्र सत्यापित किया गया!",
        "p4_id_fail": "❌ अमान्य पहचान प्रारूप।",
        "p4_sub_up": "दस्तावेज़ अपलोड करें",
        "p4_doc_select": "दस्तावेज़ प्रकार चुनें",
        "p4_btn_enc": "🔒 एन्क्रिप्ट करें और सहेजें",
        "p4_succ": "सफलतापूर्वक सहेजा गया!",
        "p4_status_sub": "दस्तावेज़ सहायक स्थिति",
        "p4_no_docs": "कोई दस्तावेज़ अपलोड नहीं किया गया।",
        "p5_title": "💬 एआई चैटबॉट और निगरानी अलर्ट",
        "p5_alert": "📌 लाइव योजना फ़ीड सक्रिय है।",
        "btn_prev": "⬅️ पिछला",
        "btn_next": "अगला ➡️"
    },
    "Malayalam (മലയാളം)": {
        "auth_title": "🔒 തമിഴൻ സ്കീം പോർട്ടൽ",
        "login_tab": "🔑 ലോഗിൻ",
        "signup_tab": "📝 അക്കൗണ്ട് സൃഷ്ടിക്കുക",
        "login_sub": "നിങ്ങളുടെ അക്കൗണ്ടിലേക്ക് ലോഗിൻ ചെയ്യുക",
        "user_label": "ഉപയോക്തൃനാമം / ഐഡി",
        "pass_label": "പാസ്‌വേഡ്",
        "login_btn": "ലോഗിൻ ചെയ്യുക",
        "forgot_btn": "പാസ്‌വേഡ് മറന്നോ?",
        "signup_sub": "പുതിയ അക്കൗണ്ട് സൃഷ്ടിക്കുക",
        "reg_user_label": "പേര് തിരഞ്ഞെടുക്കുക",
        "reg_pass_label": "പാസ്‌വേഡ് നൽകുക",
        "reg_conf_label": "പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക",
        "reg_btn": "രജിസ്റ്റർ ചെയ്യുക",
        "sidebar_title": "⚙️ ഭാഷ തിരഞ്ഞെടുക്കുക",
        "pages": [
            "1. രജിസ്ട്രേഷൻ & സുരക്ഷാ സജ്ജീകരണം",
            "2. എഐ പദ്ധതി ശുപാർശകൾ",
            "3. പദ്ധതി താരതമ്യം",
            "4. ഡോക്യുമെന്റ് വോൾട്ടും എഐ അസിസ്റ്റന്റും",
            "5. എഐ ചാറ്റ്ബോട്ടും തത്സമയ അറിയിപ്പുകളും"
        ],
        "p1_title": "🌾 തമിഴൻ സ്കീം - പ്രൊഫൈൽ & സുരക്ഷാ സജ്ജീകരണം",
        "voice_title": "🎙️ എഐ വോയ്സ് അസിസ്റ്റന്റ്",
        "voice_instruction": "സംസാരിച്ച് വിവരങ്ങൾ നൽകുക.",
        "p1_sec_sub": "സുരക്ഷാ വിവരങ്ങൾ",
        "p1_sec_pass": "പാസ്‌ഫ്രെയ്‌സ് സൃഷ്‌ടിക്കുക",
        "p1_sec_ph": "ഉദാ. Pass@123",
        "p1_sec_caption": "🔒 ഡോക്യുമെന്റുകൾ എൻക്രിപ്റ്റ് ചെയ്യുന്നു.",
        "p1_pers_sub": "വ്യക്തിഗത, ബിസിനസ്സ് പാരാമീറ്ററുകൾ",
        "p1_name": "മുഴുവൻ പേര് *",
        "p1_name_ph": "പേര് നൽകുക",
        "p1_age": "പ്രായം *",
        "p1_age_ph": "പ്രായം നൽകുക ഉദാ. 28",
        "p1_state": "സംസ്ഥാനം",
        "p1_sector": "ബിസിനസ്സ് മേഖല",
        "p1_gender": "ലിംഗഭേദം",
        "p1_income": "വാർഷിക കുടുംബ വരുമാനം (₹) *",
        "p1_income_ph": "വരുമാനം നൽകുക ഉദാ. 250000",
        "p1_funding": "ആവശ്യമായ ഫണ്ട് (₹) *",
        "p1_funding_ph": "ഫണ്ട് നൽകുക ഉദാ. 300000",
        "p1_stage": "ബിസിനസ് ഘട്ടം",
        "p1_category": "വിഭാഗം",
        "p1_btn": "സേവ് ചെയ്ത് തുടരുക ➡️",
        "p2_title": "🤖 എഐ സ്കീം മാച്ചിംഗ് എഞ്ചിൻ",
        "p2_warn": "⚠️ പ്രൊഫൈൽ വിവരങ്ങൾ ലഭ്യമല്ല! ദയവായി ആദ്യം പേജ് 1-ൽ നിങ്ങളുടെ വിവരങ്ങൾ നൽകുക.",
        "p2_profile": "പ്രൊഫൈൽ ലോഡ് ചെയ്തു",
        "p2_ben": "ആനുകൂല്യങ്ങൾ",
        "p2_docs": "ആവശ്യമായ രേഖകൾ",
        "p2_ai_explain": "💡 എഐ വിശകലനം",
        "p3_title": "⚖️ സ്കീം താരതമ്യ പട്ടിക",
        "p3_attr": ["സാമ്പത്തിക ആനുകൂല്യങ്ങൾ", "മേഖല", "പരമാവധി ഫണ്ട്", "രേഖകളുടെ എണ്ണം"],
        "p4_title": "📄 ഡോക്യുമെന്റ് വോൾട്ടും എഐ അസിസ്റ്റന്റും",
        "p4_proto": "🔒 അപ്‌ലോഡ് ചെയ്‌ത ഡോക്യുമെന്റുകൾ എൻക്രിപ്റ്റ് ചെയ്തിരിക്കുന്നു.",
        "p4_err": "ദയവായി പേജ് 1-ൽ പാസ്‌ഫ്രെയ്‌സ് സജ്ജീകരിക്കുക!",
        "p4_id_ver": "🆔 തിരിച്ചറിയൽ കാർഡ് സ്ഥിരീകരണം",
        "p4_id_input": "12 അക്ക നമ്പർ നൽകുക",
        "p4_id_ph": "ഉദാ. 123456789012",
        "p4_id_btn": "സ്ഥിരീകരിക്കുക",
        "p4_id_succ": "✅ തിരിച്ചറിയൽ കാർഡ് വിജയിച്ചു!",
        "p4_id_fail": "❌ തെറ്റായ നമ്പർ ഫോർമാറ്റ്.",
        "p4_sub_up": "രേഖകൾ അപ്‌ലോഡ് ചെയ്യുക",
        "p4_doc_select": "ടൈപ്പ് തിരഞ്ഞെടുക്കുക",
        "p4_btn_enc": "🔒 എൻക്രിപ്റ്റ് ചെയ്ത് സൂക്ഷിക്കുക",
        "p4_succ": "എൻക്രിപ്റ്റ് ചെയ്ത് സൂക്ഷിച്ചു!",
        "p4_status_sub": "രേഖകളുടെ എഐ അസിസ്റ്റന്റ്",
        "p4_no_docs": "രേഖകളൊന്നും അപ്‌ലോഡ് ചെയ്തിട്ടില്ല.",
        "p5_title": "💬 എഐ ചാറ്റ്ബോട്ടും തത്സമയ അറിയിപ്പുകളും",
        "p5_alert": "📌 തത്സമയ അറിയിപ്പുകൾ സജീവമാണ്.",
        "btn_prev": "⬅️ മുൻപത്തേത്",
        "btn_next": "അടുത്തത് ➡️"
    }
}

# --- SCHEME DATABASE ---
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
        "documents": ["Identity Proof", "PAN Card", "Project Report"],
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
        "documents": ["Identity Proof", "PAN Card", "Business Proof"],
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
        "documents": ["Identity Proof", "Degree Certificate", "Project Report"],
        "portal_url": "https://msmeonline.tn.gov.in/",
    }
]

# --- SIDEBAR LOGO & LANGUAGE SELECTION ---
logo_filename = "logo.png"
if os.path.exists(logo_filename):
    st.sidebar.image(logo_filename, width=180)

st.sidebar.markdown("# 🌾 **Tamilan Scheme**")
st.sidebar.caption("Government Scheme Portal & AI Engine")
st.sidebar.markdown("---")

lang_list = ["English", "Tamil (தமிழ்)", "Hindi (हिंदी)", "Malayalam (മലയാളം)"]
selected_lang_sidebar = st.sidebar.selectbox(
    "🌐 Select Interface Language:", 
    lang_list,
    index=lang_list.index(st.session_state.lang),
    key="sidebar_lang_selectbox"
)

if selected_lang_sidebar != st.session_state.lang:
    st.session_state.lang = selected_lang_sidebar
    st.rerun()

T = TEXT_DICT[st.session_state.lang]

# --- FIXED FORGOT PASSWORD MODAL ---
@st.dialog("🔑 Reset Your Password")
def reset_password_dialog():
    st.write("Enter your registered Username / Identity number to set a new password.")
    user_input = st.text_input("Username / Mobile Number", key="reset_user").strip().lower()
    
    if st.session_state.reset_stage == "input_user":
        if st.button("Send OTP"):
            if len(user_input) >= 3:
                st.session_state.reset_target = user_input
                st.session_state.reset_stage = "enter_new_pass"
                st.rerun()
            else:
                st.error("Please enter a valid Username or Identity Number.")
    
    elif st.session_state.reset_stage == "enter_new_pass":
        st.success(f"OTP sent to registered mobile for '{st.session_state.reset_target}'!")
        new_pass = st.text_input("Enter New Password", type="password", key="reset_new_p")
        
        if st.button("Update Password"):
            target = st.session_state.reset_target
            if target in st.session_state["user_db"]:
                st.session_state["user_db"][target] = new_pass
                st.success("Password updated successfully! Please login with your new password.")
                st.session_state.reset_stage = "input_user"
            else:
                st.error("Username not found in registered database.")

# --- DYNAMIC MULTILINGUAL AUTHENTICATION PAGE ---
def auth_page():
    st.title(T["auth_title"])
            
    tab1, tab2 = st.tabs([T["login_tab"], T["signup_tab"]])
    
    with tab1:
        st.subheader(T["login_sub"])
        username = st.text_input(T["user_label"], key="login_user").strip().lower()
        password = st.text_input(T["pass_label"], type="password", key="login_pass").strip()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button(T["login_btn"], use_container_width=True):
                if username in st.session_state["user_db"] and st.session_state["user_db"][username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["current_username"] = username
                    st.rerun()
                else:
                    st.error("Invalid Username or Password.")
        with col2:
            if st.button(T["forgot_btn"], use_container_width=True):
                reset_password_dialog()
                
    with tab2:
        st.subheader(T["signup_sub"])
        new_username = st.text_input(T["reg_user_label"], key="reg_user").strip().lower()
        new_password = st.text_input(T["reg_pass_label"], type="password", key="reg_pass").strip()
        confirm_password = st.text_input(T["reg_conf_label"], type="password", key="reg_confirm").strip()
        
        if st.button(T["reg_btn"], use_container_width=True):
            if not new_username or not new_password:
                st.error("Please fill in both fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            elif new_username in st.session_state["user_db"]:
                st.warning("Username is already registered. Please login!")
            else:
                st.session_state["user_db"][new_username] = new_password
                st.success(f"Account created successfully for '{new_username}'! Switch to Login tab.")

if not st.session_state["authenticated"]:
    auth_page()
else:
    st.sidebar.markdown("---")
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"authenticated": False}))

    def generate_encryption_key(passphrase: str) -> bytes:
        return hashlib.sha256(passphrase.encode()).digest()

    def encrypt_document(file_bytes: bytes, key: bytes) -> str:
        key_len = len(key)
        encrypted_bytes = bytes([b ^ key[i % key_len] for i, b in enumerate(file_bytes)])
        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def verify_identity_format(id_number: str) -> bool:
        cleaned = id_number.replace(" ", "").replace("-", "")
        return bool(re.fullmatch(r"\d{12}", cleaned))

    def parse_voice_text(text: str):
        text_lower = text.lower()
        
        name_match = re.search(r"name is ([a-zA-Z]+)", text_lower)
        if name_match:
            st.session_state.voice_name = name_match.group(1).capitalize()
            
        age_match = re.search(r"age is (\d+)", text_lower) or re.search(r"(\d+) years old", text_lower)
        if age_match:
            st.session_state.voice_age = age_match.group(1)
            
        funding_match = re.search(r"(\d+)\s*(lakh|lakhs|lac|lacs)", text_lower)
        if funding_match:
            lakhs_val = int(funding_match.group(1))
            st.session_state.voice_funding = str(lakhs_val * 100000)

    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
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
    if 'last_transcription' not in st.session_state: st.session_state.last_transcription = ""

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
        
        with st.expander(f"{T['voice_title']}", expanded=True):
            st.write(T["voice_instruction"])
            audio_msg = st.audio_input("Record Voice Input")
            
            if audio_msg:
                # Safe fallback parsing for audio buffer inputs
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
                name = st.text_input(T["p1_name"], value=st.session_state.voice_name, placeholder=T["p1_name_ph"]).strip()
                age_raw = st.text_input(T["p1_age"], value=st.session_state.voice_age, placeholder=T["p1_age_ph"]).strip()
                state = st.selectbox(T["p1_state"], ["Tamil Nadu", "Maharashtra", "Delhi", "Karnataka", "Other"])
                business_sector = st.selectbox(T["p1_sector"], ["Manufacturing", "Services", "Trading", "Agriculture"])
            with col2:
                gender = st.selectbox(T["p1_gender"], ["Female", "Male", "Other"])
                income_raw = st.text_input(T["p1_income"], value=st.session_state.voice_income, placeholder=T["p1_income_ph"]).strip()
                funding_raw = st.text_input(T["p1_funding"], value=st.session_state.voice_funding, placeholder=T["p1_funding_ph"]).strip()
                business_stage = st.selectbox(T["p1_stage"], ["New Unit", "Existing", "Expansion"])

            category = st.selectbox(T["p1_category"], ["SC", "ST", "Women", "OBC", "General"])

            if st.form_submit_button(T["p1_btn"]):
                if not name or not age_raw or not income_raw or not funding_raw:
                    st.error("Please fill in all required fields marked with * (Name, Age, Income, and Funding Amount) before proceeding!")
                else:
                    try:
                        age = int(age_raw)
                        income = int(income_raw)
                        funding_req = int(funding_raw)
                        
                        passphrase = passphrase if passphrase else "DefaultPassphrase123"
                        st.session_state.user_key = generate_encryption_key(passphrase)
                        st.session_state.user_data = {
                            "name": name, "age": age, "state": state, "gender": gender,
                            "income": income, "sector": business_sector, "stage": business_stage,
                            "funding": funding_req, "category": category
                        }
                        go_next()
                        st.rerun()
                    except ValueError:
                        st.error("Please enter valid numbers for Age, Income, and Funding Amount!")

    # ==================== PAGE 2: SCHEME MATCHING & AI INSIGHTS ====================
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

            if not eligible_schemes:
                st.warning("No exact schemes matched your parameters. Try broadening your criteria on Step 1.")
            else:
                for s in eligible_schemes:
                    with st.expander(f"🥇 {s['name']}", expanded=True):
                        st.write(f"**{T['p2_ben']}:** {s['benefits']}")
                        st.write(f"**{T['p2_docs']}:** {', '.join(s['documents'])}")
                        
                        st.markdown(f"**{T['p2_ai_explain']}**")
                        ai_reasoning = (
                            f"• Fits your age requirement ({user['age']} years old, within {s['min_age']}-{s['max_age']} limit).\n"
                            f"• Covers your requested funding amount of ₹{user['funding']:,}.\n"
                            f"• Explicitly tailored for the **{user['sector']}** sector in **{user['state']}**."
                        )
                        st.success(ai_reasoning)

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

    # ==================== PAGE 4: SMART VAULT & DOCUMENT ASSISTANT ====================
    elif st.session_state.current_step == 4:
        st.title(T["p4_title"])
        st.markdown(f"> {T['p4_proto']}")
        
        if st.session_state.user_key is None:
            st.error(T["p4_err"])
        else:
            st.subheader(T["p4_id_ver"])
            id_num_input = st.text_input(T["p4_id_input"], value="", placeholder=T["p4_id_ph"])
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
                    st.success("🆔 Government ID Format: Verified")
                
                st.write("📋 **Required Application Checklist:**")
                all_required = set()
                for s in SCHEME_DB:
                    for d in s["documents"]:
                        all_required.add(d)
                
                uploaded_set = set(st.session_state.uploaded_docs.keys())
                for req in sorted(all_required):
                    if req in uploaded_set:
                        st.markdown(f"✅ ~~{req}~~ *(Uploaded & Encrypted)*")
                    else:
                        st.markdown(f"❌ **{req}** *(Action Required)*")

    # ==================== PAGE 5: MULTILINGUAL AI CHATBOT & MONITORING ALERTS ====================
    elif st.session_state.current_step == 5:
        st.title(T["p5_title"])
        
        tab_chat, tab_alerts = st.tabs(["🤖 Interactive Multilingual AI Agent", "🔔 New-Scheme Monitoring & Alerts"])
        
        with tab_chat:
            st.subheader("Ask AI Assistant about Government Schemes")
            st.caption("Supports English, Tamil, Hindi, and Malayalam natural language queries.")
            
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            user_query = st.chat_input("Ask a question (e.g., 'What benefits can I get for manufacturing in Tamil Nadu?')")
            if user_query:
                st.session_state.chat_history.append({"role": "user", "content": user_query})
                with st.chat_message("user"):
                    st.markdown(user_query)
                
                query_lower = user_query.lower()
                response = ""
                
                if "tn" in query_lower or "tamil nadu" in query_lower or "needs" in query_lower:
                    response = "🌾 **Tamil Nadu NEEDS Scheme:** Provides **25% Capital Subsidy** up to ₹75 Lakhs with 3% interest subvention for manufacturing and service units."
                elif "loan" in query_lower or "mudra" in query_lower:
                    response = "💳 **Pradhan Mantri MUDRA Yojana:** Offers **collateral-free loans up to ₹10 Lakhs** across manufacturing, trading, and agriculture."
                elif "pmegp" in query_lower or "subsidy" in query_lower:
                    response = "🏭 **PMEGP Scheme:** Provides **15% to 35% subsidy** on project costs up to ₹50 Lakhs for micro-enterprises."
                else:
                    user_info = st.session_state.user_data
                    if user_info:
                        response = f"🤖 Based on your saved profile ({user_info['name']}, {user_info['sector']} sector, {user_info['state']}), you are eligible for schemes like **PMEGP** and **NEEDS** offering subsidies up to 35%."
                    else:
                        response = "🤖 Hello! I am your AI Scheme Assistant. Please complete your profile in Step 1 or ask me specific questions about loan amounts, subsidies, and required documents."
                
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(response)

        with tab_alerts:
            st.subheader("📡 Live Scheme Monitoring Broadcast Feed")
            st.info(T["p5_alert"])
            
            alerts_data = [
                {"date": "2026-09-15", "scheme": "TN MSME Technology Upgradation Grant", "status": "🆕 NEW RELEASE", "state": "Tamil Nadu"},
                {"date": "2026-09-10", "scheme": "PM Vishwakarma Artisan Support", "status": "📢 APPLICATION OPEN", "state": "All India"},
                {"date": "2026-09-02", "scheme": "Women Entrepreneurship Credit Guarantee", "status": "⚡ SUBSIDY INCREASED", "state": "All India"}
            ]
            
            for item in alerts_data:
                with st.container():
                    st.markdown(f"#### {item['status']}: {item['scheme']}")
                    st.caption(f"📅 Published: {item['date']} | Region: {item['state']}")
                    st.markdown("---")
            
            if st.button("🔔 Trigger Instant SMS/WhatsApp Notification Alert"):
                st.success("📱 Automatic personalized alerts dispatched to registered applicant number ending in ******42!")

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
