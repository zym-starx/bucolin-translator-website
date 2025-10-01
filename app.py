import streamlit as st
import requests
import json
import time
from typing import Dict, Any
from urllib.parse import parse_qs

# Import secure configuration and admin system
from config import PublicConfig, SecureConfig
from admin import admin_required

class MockTranslationService:
    """Mock translation service for development/demo purposes"""
    
    def translate(self, text: str) -> Dict[str, Any]:
        time.sleep(PublicConfig.MOCK_PROCESSING_TIME)
        
        mock_translations = {
            "merhaba": "hello",
            "selam": "greetings", 
            "kitap": "book",
            "ev": "house",
            "su": "water",
            "yemek": "food",
            "güzel": "beautiful",
            "büyük": "big",
            "küçük": "small"
        }
        
        words = text.lower().split()
        translated_words = []
        confidence_scores = []
        
        for word in words:
            if word in mock_translations:
                translated_words.append(mock_translations[word])
                confidence_scores.append(PublicConfig.MOCK_CONFIDENCE_THRESHOLD + 0.2)
            else:
                translated_words.append(f"[{word}]")
                confidence_scores.append(0.3)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        translation = " ".join(translated_words)
        
        return {
            "success": True,
            "original_text": text,
            "translated_text": translation,
            "confidence": avg_confidence,
            "processing_time": PublicConfig.MOCK_PROCESSING_TIME,
            "word_count": len(words),
            "recognized_words": len([w for w in words if w in mock_translations])
        }

class APITranslationService:
    """Production API translation service"""
    
    def __init__(self):
        self.api_endpoint = SecureConfig.get_api_endpoint()
        self.timeout = 30
        self.max_retries = 3
    
    def translate(self, text: str) -> Dict[str, Any]:
        payload = {"text": text}
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    result["processing_time"] = time.time() - start_time
                    return result
                else:
                    return {
                        "success": False,
                        "error": "Translation service is currently unavailable",
                        "processing_time": time.time() - start_time
                    }
                    
            except requests.exceptions.RequestException:
                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": "Cannot connect to translation service",
                        "processing_time": time.time() - start_time
                    }
                time.sleep(2 ** attempt)

class TurkishTranslator:
    """Main translator class that handles service selection"""
    
    def __init__(self):
        if SecureConfig.use_mock_service():
            self.service = MockTranslationService()
            self.service_name = "Mock Service (Development)"
        else:
            self.service = APITranslationService()
            self.service_name = "AI Model (Production)"
    
    def translate_text(self, text: str) -> Dict[str, Any]:
        if not text.strip():
            return {"success": False, "error": "Please enter some text to translate"}
        
        if len(text) > PublicConfig.MAX_TEXT_LENGTH:
            return {"success": False, "error": f"Text too long. Maximum {PublicConfig.MAX_TEXT_LENGTH} characters allowed."}
        
        result = self.service.translate(text)
        result["service_used"] = self.service_name
        return result

def apply_custom_styles():
    """Apply beautiful, modern custom CSS styles to the application"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
    
    :root {
        --bg-primary: #0f1419;
        --bg-secondary: #1a1f2e;
        --bg-tertiary: #252b3a;
        --accent-gold: #d4af37;
        --accent-emerald: #2d5a3a;
        --accent-copper: #b87333;
        --text-primary: #f7f3e9;
        --text-secondary: #d1c7b8;
        --text-muted: #a08d78;
        --border-subtle: #3a4553;
        --shadow-soft: rgba(0, 0, 0, 0.3);
        --shadow-medium: rgba(0, 0, 0, 0.5);
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Add subtle pattern overlay */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 1px 1px, rgba(212, 175, 55, 0.05) 1px, transparent 0);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: -1;
    }
    
    .nav-container {
        background: linear-gradient(135deg, rgba(37, 43, 58, 0.6) 0%, rgba(26, 31, 46, 0.8) 100%);
        backdrop-filter: blur(30px);
        padding: 1rem 2rem;
        border-radius: 30px;
        margin-bottom: 2rem;
        border: 2px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .nav-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), var(--accent-copper), var(--accent-emerald), transparent);
    }

    .nav-container::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(50%, -50%);
        pointer-events: none;
    }
    
    .bucolin-brand {
        color: var(--accent-gold);
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Crimson Text', serif;
        letter-spacing: 4px;
        text-transform: uppercase;
        position: relative;
        display: inline-block;
        width: 100%;
    }

    .bucolin-brand::after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: var(--text-primary);
        margin-bottom: 3rem;
        box-shadow: 
            0 16px 40px var(--shadow-medium),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        border: 1px solid var(--border-subtle);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            135deg,
            rgba(212, 175, 55, 0.08) 0%,
            rgba(184, 115, 51, 0.08) 50%,
            rgba(45, 90, 58, 0.08) 100%
        );
        pointer-events: none;
    }
    
    .main-header h1 {
        position: relative;
        z-index: 1;
        font-family: 'Crimson Text', serif !important;
        font-weight: 700;
        font-size: 2.8rem;
        margin: 0;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-gold));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 4px 8px var(--shadow-soft);
    }
    
    .translation-container {
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 12px 32px var(--shadow-medium);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .translation-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 40px var(--shadow-medium);
    }
    
    .translation-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
    }
    
    .section-header {
        color: var(--accent-gold);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid var(--accent-emerald);
        text-transform: uppercase;
        letter-spacing: 3px;
        font-family: 'Inter', sans-serif;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: var(--accent-gold);
    }
    
    .stats-grid {
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 3rem 0;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 16px 40px var(--shadow-medium);
        position: relative;
        overflow: hidden;
    }
    
    .stats-grid::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-gold), var(--accent-copper), var(--accent-emerald));
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        padding: 2rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--border-subtle);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .metric-card:hover::before {
        left: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 40px rgba(212, 175, 55, 0.2);
        border-color: var(--accent-gold);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--accent-gold);
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 2px 8px rgba(212, 175, 55, 0.3);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.9;
    }
    
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
        font-family: 'Crimson Text', serif !important;
        padding: 1.2rem !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.2), 0 8px 25px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted) !important;
        font-style: italic !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-emerald) 0%, var(--accent-gold) 100%) !important;
        color: var(--text-primary) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px rgba(45, 90, 58, 0.4) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent) !important;
        transition: left 0.5s ease !important;
    }
    
    .stButton > button:hover::before {
        left: 100% !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-copper) 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(212, 175, 55, 0.4) !important;
    }
    
    .success-message {
        background: linear-gradient(135deg, rgba(45, 90, 58, 0.2), rgba(45, 90, 58, 0.1));
        color: #a8e6a3;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        border: 1px solid rgba(45, 90, 58, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(45, 90, 58, 0.2);
    }
    
    .error-message {
        background: linear-gradient(135deg, rgba(184, 115, 51, 0.2), rgba(184, 115, 51, 0.1));
        color: #ffb3b3;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        border: 1px solid rgba(184, 115, 51, 0.3);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(184, 115, 51, 0.2);
    }
    
    .details-section {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border-subtle);
        margin-top: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    /* Translate button special styling */
    .stButton[data-testid="baseButton-primary"] > button {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 50%, #a93226 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px rgba(231, 76, 60, 0.4) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton[data-testid="baseButton-primary"] > button:hover {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 50%, #d35400 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(243, 156, 18, 0.5) !important;
    }
    
    /* Character counter styling */
    .stCaption {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        margin-top: 0.5rem !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-subtle) !important;
    }
    
    /* Link button styling */
    .stLinkButton > a {
        background: linear-gradient(135deg, var(--accent-copper) 0%, var(--accent-gold) 100%) !important;
        color: var(--text-primary) !important;
        text-decoration: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }
    
    .stLinkButton > a:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(184, 115, 51, 0.3) !important;
    }
    
    /* Animation for loading */
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .loading-shimmer {
        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--accent-gold), var(--accent-copper));
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--accent-copper), var(--accent-emerald));
    }
    </style>
    """, unsafe_allow_html=True)

def navigation_menu():
    """Render navigation menu and handle routing"""
    apply_custom_styles()
    
    # Get current page from query params
    query_params = st.query_params
    current_page = query_params.get("page", "demo")
    
    st.markdown('''
    <div class="nav-container">
        <div class="bucolin-brand">BUCOLIN</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("Demo", use_container_width=True, type="primary" if current_page == "demo" else "secondary"):
            st.query_params.page = "demo"
            st.rerun()
    
    with col2:
        if st.button("About", use_container_width=True, type="primary" if current_page == "about" else "secondary"):
            st.query_params.page = "about"
            st.rerun()
    
    with col3:
        if st.button("Research", use_container_width=True, type="primary" if current_page == "research" else "secondary"):
            st.query_params.page = "research"
            st.rerun()
    
    with col4:
        if st.button("Team", use_container_width=True, type="primary" if current_page == "team" else "secondary"):
            st.query_params.page = "team"
            st.rerun()
    
    with col5:
        st.link_button("🤗 HuggingFace", PublicConfig.HUGGINGFACE_URL, use_container_width=True)
    
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return current_page

def main_app():
    """Main translation application interface"""
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700; font-family: 'Crimson Text', serif; 
                       background: linear-gradient(135deg, var(--text-primary), var(--accent-gold));
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                HISTORICAL TURKISH TRANSLATOR
            </h1>
            <div style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem;">
                <span style="color: var(--accent-copper); font-weight: 600; font-size: 1rem; font-family: 'Inter', sans-serif;">
                    {PublicConfig.DEFAULT_LANGUAGE_PAIR[0].replace('_', ' ').title()}
                </span>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 8px; height: 1px; background: var(--accent-gold);"></div>
                    <span style="color: var(--accent-gold); font-size: 1.2rem; font-weight: 700;">⟷</span>
                    <div style="width: 8px; height: 1px; background: var(--accent-gold);"></div>
                </div>
                <span style="color: var(--accent-copper); font-weight: 600; font-size: 1rem; font-family: 'Inter', sans-serif;">
                    {PublicConfig.DEFAULT_LANGUAGE_PAIR[1].replace('_', ' ').title()}
                </span>
            </div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; margin-top: 1.5rem; font-size: 0.85rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--accent-emerald);">🚀</span>
                    <span style="color: var(--text-muted); font-weight: 500;">v{PublicConfig.APP_VERSION}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--accent-gold);">🎓</span>
                    <span style="color: var(--text-muted); font-weight: 500;">Research Preview</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    translator = TurkishTranslator()
    
    # Main translation interface
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div class="translation-container">
            <div class="section-header">Source Text</div>
        </div>
        """, unsafe_allow_html=True)
        
        input_text = st.text_area(
            "Enter your historical Turkish text here...",
            height=200,
            placeholder=f"Type or paste your Old Turkish text here... (max {PublicConfig.MAX_TEXT_LENGTH} characters)",
            label_visibility="collapsed",
            key="input_text",
            max_chars=PublicConfig.MAX_TEXT_LENGTH
        )
        
        # Character count
        char_count = len(input_text) if input_text else 0
        st.caption(f"Characters: {char_count}/{PublicConfig.MAX_TEXT_LENGTH}")
        
        # Translate button
        translate_clicked = st.button(
            "TRANSLATE", 
            use_container_width=True,
            help="Process translation using AI",
            disabled=(char_count == 0 or char_count > PublicConfig.MAX_TEXT_LENGTH)
        )
        
        if translate_clicked and input_text.strip():
            # Create a beautiful loading animation
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="display: inline-block; width: 60px; height: 60px; border: 3px solid var(--border-subtle); 
                            border-radius: 50%; border-top: 3px solid var(--accent-gold); 
                            animation: spin 1s linear infinite; margin-bottom: 1rem;"></div>
                <p style="color: var(--text-secondary); font-family: 'Inter', sans-serif; font-weight: 500;">
                    🧠 Processing translation with AI...
                </p>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
            </div>
            """, unsafe_allow_html=True)
            
            # Process translation
            result = translator.translate_text(input_text)
            st.session_state.translation_result = result
            st.session_state.has_translation = True
            
            # Clear loading animation
            loading_placeholder.empty()
        elif translate_clicked:
            st.warning("⚠️ Please enter text to translate")
    
    with col2:
        st.markdown("""
        <div class="translation-container">
            <div class="section-header">Modern Translation</div>
        </div>
        """, unsafe_allow_html=True)
        
        if hasattr(st.session_state, 'has_translation') and st.session_state.has_translation:
            result = st.session_state.translation_result
            
            if result.get("success"):
                # Translation output
                translation_text = result.get("translated_text", "")
                st.text_area(
                    "Translation result:",
                    value=translation_text,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
                
                # Success indicator
                st.markdown('<div class="success-message">✅ Translation completed successfully</div>', unsafe_allow_html=True)
                
            else:
                st.text_area(
                    "Translation result:",
                    value="Translation failed - please try again",
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
                st.markdown(f'<div class="error-message">❌ {result.get("error", "Translation failed")}</div>', unsafe_allow_html=True)
        else:
            st.text_area(
                "Translation will appear here...",
                value="",
                height=200,
                disabled=True,
                label_visibility="collapsed",
                placeholder="Your modern Turkish translation will appear here"
            )
    
    # Statistics section
    if hasattr(st.session_state, 'has_translation') and st.session_state.has_translation:
        result = st.session_state.translation_result
        
        if result.get("success"):
            st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
            st.markdown("""
            <h3 style="color: var(--accent-gold); margin-bottom: 2.5rem; text-align: center; 
                       font-family: 'Crimson Text', serif; text-transform: uppercase; 
                       letter-spacing: 3px; font-size: 1.6rem; font-weight: 700;
                       background: linear-gradient(135deg, var(--accent-gold), var(--accent-copper));
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                       background-clip: text;">
                ✨ Translation Analysis ✨
            </h3>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                confidence = result.get('confidence', 0)
                if confidence > 0.8:
                    confidence_emoji = "🟢"
                    confidence_color = "var(--accent-emerald)"
                    confidence_label = "Excellent"
                elif confidence > 0.6:
                    confidence_emoji = "🟡"  
                    confidence_color = "var(--accent-gold)"
                    confidence_label = "Good"
                else:
                    confidence_emoji = "🔴"
                    confidence_color = "var(--accent-copper)"
                    confidence_label = "Fair"
                    
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Confidence {confidence_emoji}</div>
                    <div class="metric-value" style="color: {confidence_color};">{confidence:.1%}</div>
                    <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem; 
                               text-transform: uppercase; letter-spacing: 1px;">{confidence_label}</div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                processing_time = result.get('processing_time', 0)
                time_emoji = "⚡" if processing_time < 1 else "🐌" if processing_time > 3 else "⏱️"
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Processing Time {time_emoji}</div>
                    <div class="metric-value">{processing_time:.2f}s</div>
                    <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem; 
                               text-transform: uppercase; letter-spacing: 1px;">
                        {"Lightning Fast" if processing_time < 1 else "Standard" if processing_time < 3 else "Processing"}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                word_count = result.get('word_count', 0)
                word_emoji = "📊" if word_count < 50 else "📈" if word_count < 200 else "📋"
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Words Processed {word_emoji}</div>
                    <div class="metric-value">{word_count}</div>
                    <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem; 
                               text-transform: uppercase; letter-spacing: 1px;">
                        {"Short Text" if word_count < 50 else "Medium Text" if word_count < 200 else "Long Text"}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                service_used = result.get('service_used', 'Unknown')
                service_display = service_used.split(' (')[0]  # Remove environment info for display
                service_emoji = "🔧" if "Mock" in service_used else "🚀"
                service_color = "var(--accent-copper)" if "Mock" in service_used else "var(--accent-emerald)"
                st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Engine Used {service_emoji}</div>
                    <div class="metric-value" style="font-size: 1.2rem; color: {service_color};">{service_display}</div>
                    <div style="color: var(--text-muted); font-size: 0.75rem; margin-top: 0.5rem; 
                               text-transform: uppercase; letter-spacing: 1px;">
                        {"Development" if "Mock" in service_used else "Production"}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed analysis
            with st.expander("Detailed Analysis"):
                st.markdown('<div class="details-section">', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Source Language:** Old Turkish (Ottoman)")
                    st.write("**Target Language:** Modern Turkish")
                    if "recognized_words" in result:
                        recognition_rate = result["recognized_words"] / result["word_count"] if result["word_count"] > 0 else 0
                        st.write(f"**Recognition Rate:** {recognition_rate:.1%}")
                
                with col2:
                    st.write(f"**Source Length:** {len(result.get('original_text', ''))} characters")
                    st.write(f"**Translation Length:** {len(result.get('translated_text', ''))} characters")
                    st.write(f"**Service:** {result.get('service_used', 'Unknown')}")
                
                st.markdown('</div>', unsafe_allow_html=True)

def about_page():
    """About page with project information"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 4rem;">
        <h1 style="color: var(--accent-gold); font-family: 'Crimson Text', serif; font-size: 3rem; font-weight: 700; margin-bottom: 1rem;">Historical Turkish Translation</h1>
        <p style="color: var(--text-secondary); font-size: 1.3rem; font-weight: 400; max-width: 600px; margin: 0 auto;">Bridging centuries of Turkish linguistic evolution with cutting-edge AI technology</p>
        <div style="width: 80px; height: 3px; background: linear-gradient(90deg, var(--accent-gold), var(--accent-copper)); margin: 2rem auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); 
                    box-shadow: 0 12px 32px var(--shadow-medium); margin-bottom: 2rem;">
            <h2 style="color: var(--accent-gold); font-size: 1.8rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">🌟 Project Overview</h2>
            <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.1rem; margin-bottom: 1.5rem;">
                This translation system represents a breakthrough in computational linguistics for historical Turkish texts. 
                Developed by the BUCOLIN lab at Boğaziçi University, it enables seamless translation between Ottoman Turkish 
                and Modern Turkish, making centuries of historical documents accessible to contemporary readers and researchers.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); 
                    box-shadow: 0 12px 32px var(--shadow-medium);">
            <h3 style="color: var(--accent-copper); font-size: 1.5rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">🚀 Key Features</h3>
            <div style="display: grid; gap: 1rem;">
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-gold);">
                    <span style="color: var(--accent-gold); font-size: 1.2rem; margin-right: 1rem;">🎯</span>
                    <div>
                        <strong style="color: var(--text-primary);">Historical Accuracy:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Trained on authentic texts from 15th-20th centuries</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-copper);">
                    <span style="color: var(--accent-copper); font-size: 1.2rem; margin-right: 1rem;">🔬</span>
                    <div>
                        <strong style="color: var(--text-primary);">Linguistic Precision:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Preserves semantic meaning across temporal variations</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-emerald);">
                    <span style="color: var(--accent-emerald); font-size: 1.2rem; margin-right: 1rem;">🎓</span>
                    <div>
                        <strong style="color: var(--text-primary);">Academic Grade:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Suitable for scholarly research and educational purposes</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-gold);">
                    <span style="color: var(--accent-gold); font-size: 1.2rem; margin-right: 1rem;">⚡</span>
                    <div>
                        <strong style="color: var(--text-primary);">Real-time Processing:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Instant translation with confidence metrics</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, var(--accent-emerald) 0%, var(--accent-gold) 100%); 
                    padding: 2.5rem; border-radius: 16px; color: var(--text-primary); 
                    box-shadow: 0 16px 40px rgba(45, 90, 58, 0.3); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        border-radius: 50%;"></div>
            <h3 style="color: var(--text-primary); font-size: 1.4rem; margin-bottom: 1.5rem; 
                       font-family: 'Crimson Text', serif; position: relative; z-index: 1;">⚙️ Technical Specifications</h3>
            <div style="position: relative; z-index: 1;">
                <div style="margin-bottom: 1rem;">
                    <strong>Model Type:</strong><br>
                    <span style="opacity: 0.9;">Transformer-based</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Training Data:</strong><br>
                    <span style="opacity: 0.9;">Ottoman Text Corpus</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Coverage:</strong><br>
                    <span style="opacity: 0.9;">15th-20th centuries</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Languages:</strong><br>
                    <span style="opacity: 0.9;">{PublicConfig.DEFAULT_LANGUAGE_PAIR[0].replace('_', ' ').title()} ↔ {PublicConfig.DEFAULT_LANGUAGE_PAIR[1].replace('_', ' ').title()}</span>
                </div>
                <div style="margin-bottom: 1rem;">
                    <strong>Version:</strong><br>
                    <span style="opacity: 0.9;">{PublicConfig.APP_VERSION}</span>
                </div>
                <div style="margin-bottom: 0;">
                    <strong>Max Text Length:</strong><br>
                    <span style="opacity: 0.9;">{PublicConfig.MAX_TEXT_LENGTH:,} characters</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Feature cards
    st.markdown("---")
    st.markdown("""
    <h2 style="text-align: center; color: var(--accent-gold); font-family: 'Crimson Text', serif; 
               font-size: 2.2rem; margin: 3rem 0 2rem 0;">✨ Core Capabilities</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 2rem; 
                    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
                    border-radius: 16px; border: 1px solid var(--border-subtle);
                    box-shadow: 0 12px 32px var(--shadow-medium); 
                    transition: all 0.4s ease; position: relative; overflow: hidden;"
             onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 40px rgba(212, 175, 55, 0.3)';"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 12px 32px var(--shadow-medium)';">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem; 
                        background: linear-gradient(135deg, var(--accent-gold), var(--accent-copper));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">📜</div>
            <h3 style="color: var(--accent-gold); margin-bottom: 1rem; font-family: 'Crimson Text', serif; font-size: 1.3rem;">Historical Texts</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">Process manuscripts, documents, and literature from the Ottoman period with unprecedented accuracy and cultural sensitivity.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 2rem; 
                    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
                    border-radius: 16px; border: 1px solid var(--border-subtle);
                    box-shadow: 0 12px 32px var(--shadow-medium); 
                    transition: all 0.4s ease; position: relative; overflow: hidden;"
             onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 40px rgba(184, 115, 51, 0.3)';"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 12px 32px var(--shadow-medium)';">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem; 
                        background: linear-gradient(135deg, var(--accent-copper), var(--accent-gold));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">🧠</div>
            <h3 style="color: var(--accent-copper); margin-bottom: 1rem; font-family: 'Crimson Text', serif; font-size: 1.3rem;">AI-Powered</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">Advanced neural networks specifically trained and fine-tuned for the nuances of historical Turkish language variations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 2rem; 
                    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
                    border-radius: 16px; border: 1px solid var(--border-subtle);
                    box-shadow: 0 12px 32px var(--shadow-medium); 
                    transition: all 0.4s ease; position: relative; overflow: hidden;"
             onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 40px rgba(45, 90, 58, 0.3)';"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 12px 32px var(--shadow-medium)';">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem; 
                        background: linear-gradient(135deg, var(--accent-emerald), var(--accent-gold));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">🎓</div>
            <h3 style="color: var(--accent-emerald); margin-bottom: 1rem; font-family: 'Crimson Text', serif; font-size: 1.3rem;">Academic Research</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">Developed by computational linguistics experts at Boğaziçi University with rigorous academic standards and peer review.</p>
        </div>
        """, unsafe_allow_html=True)

def research_page():
    """Research page with academic information"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 4rem;">
        <h1 style="color: var(--accent-gold); font-family: 'Crimson Text', serif; font-size: 3rem; font-weight: 700; margin-bottom: 1rem;">Research & Publications</h1>
        <p style="color: var(--text-secondary); font-size: 1.3rem; font-weight: 400; max-width: 600px; margin: 0 auto;">Academic foundations and cutting-edge research in historical Turkish NLP</p>
        <div style="width: 80px; height: 3px; background: linear-gradient(90deg, var(--accent-gold), var(--accent-copper)); margin: 2rem auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        with st.container():
            st.markdown("""
            <div style="background: #2d2419; padding: 1.5rem; border-radius: 8px; border-left: 4px solid #3d6b4a; margin: 1rem 0;">
                <h3 style="color: #e8e2d5; margin-top: 0;">Translation Model Main Publication</h3>
                <p style="color: #a0b5a8; margin: 0.5rem 0;"><strong>Authors:</strong> BUCOLIN Research Team</p>
                <p style="color: #a0b5a8; margin: 0.5rem 0;"><strong>Institution:</strong> Boğaziçi University</p>
                <p style="color: #a0b5a8; margin: 0.5rem 0;"><strong>Status:</strong> <span style="color: #4a7a5a;">Work in Progress</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📄 Paper Coming Soon", disabled=True):
                st.info("Paper will be available upon publication")
        
        with st.container():
            st.markdown("""
            <div style="background: linear-gradient(135deg, #2d5a3a 0%, #1a4228 100%); 
                        padding: 2rem; border-radius: 12px; border-left: 4px solid #d4af37; 
                        margin: 1rem 0; box-shadow: 0 8px 24px rgba(45, 90, 58, 0.3);">
                <h3 style="color: #f7f3e9; margin-top: 0; font-size: 1.4rem; font-family: 'Crimson Text', serif; line-height: 1.3;">
                    Building Foundations for Natural Language Processing of Historical Turkish: Resources and Models
                </h3>
                <div style="margin: 1.5rem 0;">
                    <p style="color: #d1c7b8; margin: 0.5rem 0;"><strong>Authors:</strong> Şaziye Betül Özateş, Tarık Emre Tıraş, Ece Elif Adak, Berat Doğan, Fatih Burak Karagöz, Efe Eren Genç, Esma F. Bilgin Taşdemir</p>
                    <p style="color: #d1c7b8; margin: 0.5rem 0;"><strong>Institution:</strong> Boğaziçi University</p>
                    <p style="color: #d1c7b8; margin: 0.5rem 0;"><strong>Published:</strong> <span style="color: #d4af37;">January 8, 2025</span></p>
                    <p style="color: #d1c7b8; margin: 0.5rem 0;"><strong>arXiv ID:</strong> <span style="color: #b87333;">2501.04828</span></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                st.link_button("📄 Read Paper", "https://arxiv.org/abs/2501.04828", use_container_width=True)
            with col_btn2:
                st.link_button("🤗 HuggingFace Resources", "https://huggingface.co/BUCOLIN", use_container_width=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); 
                    box-shadow: 0 12px 32px var(--shadow-medium); margin-top: 2rem;">
            <h3 style="color: var(--accent-copper); font-size: 1.5rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">📋 Abstract</h3>
            <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.05rem;">
                This paper introduces foundational resources and models for natural language processing of historical Turkish, 
                a domain that has remained underexplored in computational linguistics. We present the first named entity recognition (NER) dataset, 
                <strong>HisTR</strong> and the first Universal Dependencies treebank, <strong>OTA-BOUN</strong> for a historical form of the Turkish language 
                along with transformer-based models trained using these datasets for named entity recognition, dependency parsing, and part-of-speech tagging tasks.
            </p>
            <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.05rem; margin-top: 1rem;">
                Additionally, we introduce <strong>Ottoman Text Corpus (OTC)</strong>, a clean corpus of transliterated historical Turkish texts 
                that spans a wide range of historical periods. Our experimental results show significant improvements in the computational analysis 
                of historical Turkish, achieving promising results in tasks that require understanding of historical linguistic structures.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Placeholder for upcoming model paper
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-subtle); 
                    box-shadow: 0 12px 32px var(--shadow-medium); margin-top: 2rem; opacity: 0.8;
                    border: 2px dashed var(--accent-gold);">
            <h3 style="color: var(--accent-gold); font-size: 1.5rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">🚀 Upcoming Publication</h3>
            <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.05rem;">
                <strong>Translation Model Paper</strong> - Additional research paper focusing on the translation models will be available soon.
                This will provide detailed insights into the translation methodology and performance evaluation.
            </p>
            <p style="color: var(--text-muted); font-style: italic; margin-top: 1rem;">
                Stay tuned for updates...
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--accent-emerald) 0%, var(--accent-gold) 100%); 
                    padding: 2.5rem; border-radius: 16px; color: var(--text-primary); 
                    box-shadow: 0 16px 40px rgba(45, 90, 58, 0.3); position: relative; overflow: hidden; margin-bottom: 2rem;">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        border-radius: 50%;"></div>
            <h3 style="color: var(--text-primary); font-size: 1.4rem; margin-bottom: 1.5rem; 
                       font-family: 'Crimson Text', serif; position: relative; z-index: 1;">🔬 Research Areas</h3>
            <div style="position: relative; z-index: 1;">
                <ul style="list-style: none; padding: 0; margin: 0;">
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: center;">
                        <span style="color: var(--text-primary); margin-right: 0.5rem;">📚</span>
                        <span>Historical Text Processing</span>
                    </li>
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: center;">
                        <span style="color: var(--text-primary); margin-right: 0.5rem;">🔄</span>
                        <span>Neural Machine Translation</span>
                    </li>
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: center;">
                        <span style="color: var(--text-primary); margin-right: 0.5rem;">🏷️</span>
                        <span>Named Entity Recognition</span>
                    </li>
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: center;">
                        <span style="color: var(--text-primary); margin-right: 0.5rem;">🌳</span>
                        <span>Dependency Parsing</span>
                    </li>
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: center;">
                        <span style="color: var(--text-primary); margin-right: 0.5rem;">📖</span>
                        <span>Corpus Linguistics</span>
                    </li>
                    <li style="margin-bottom: 0; display: flex; align-items: center;">
                        <span style="color: var(--text-primary); margin-right: 0.5rem;">🎯</span>
                        <span>POS Tagging</span>
                    </li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--accent-copper) 0%, var(--accent-gold) 100%); 
                    padding: 2.5rem; border-radius: 16px; color: var(--text-primary); 
                    box-shadow: 0 16px 40px rgba(184, 115, 51, 0.3); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; 
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); 
                        border-radius: 50%;"></div>
            <h3 style="color: var(--text-primary); font-size: 1.4rem; margin-bottom: 1.5rem; 
                       font-family: 'Crimson Text', serif; position: relative; z-index: 1;">📊 Datasets & Resources</h3>
            <div style="position: relative; z-index: 1;">
                <div style="margin-bottom: 1.2rem;">
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1.1rem;">HisTR</h4>
                    <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">First NER dataset for historical Turkish (812 sentences, 17th-19th centuries)</p>
                </div>
                <div style="margin-bottom: 1.2rem;">
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1.1rem;">OTA-BOUN</h4>
                    <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">First UD treebank for historical Turkish (514 sentences)</p>
                </div>
                <div style="margin-bottom: 0;">
                    <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1.1rem;">OTC</h4>
                    <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Ottoman Text Corpus (15th-20th centuries)</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    

def team_page():
    """Team page with lab information"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1 style="color: #4a7a5a; font-family: Georgia, serif; font-size: 2.5rem;">Research Team</h1>
        <p style="color: #a0b5a8; font-size: 1.2rem;">BUCOLIN - Boğaziçi University Computational Linguistics Lab</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🏛️ Laboratory")
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <p style="color: #e8e2d5; font-size: 1.1rem;">
            <strong>Boğaziçi University Computational Linguistics Lab (BUCOLIN)</strong><br>
            Department of Computer Engineering<br>
            Boğaziçi University, İstanbul, Turkey
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button("🏫 Boğaziçi University", PublicConfig.UNIVERSITY_URL, use_container_width=True)
    
    with col2:
        st.link_button("🤗 BUCOLIN on HuggingFace", PublicConfig.HUGGINGFACE_URL, use_container_width=True)
    
    st.markdown("### Research Focus")
    st.markdown("""
    Our lab specializes in developing computational methods for processing historical and contemporary Turkish texts. 
    We work on machine translation, named entity recognition, dependency parsing, and corpus development 
    to advance the field of Turkish computational linguistics.
    """)

def admin_panel():
    """Secure admin panel - requires authentication"""
    # Apply security check
    admin_required()
    
    st.markdown(f"""
    <div style="background: #3d6b4a; padding: 2.5rem; border-radius: 8px; margin-bottom: 2rem; color: #e8e2d5; box-shadow: 0 6px 20px rgba(61, 107, 74, 0.4); border: 2px solid #2d5a3a;">
        <h1 style="color: #e8e2d5; font-weight: bold; margin: 0;">🔧 System Administration</h1>
        <p style="color: #e8e2d5; margin: 0.5rem 0 0 0;">{PublicConfig.APP_NAME} - Control Panel</p>
        <p style="color: #c5d8ca; margin: 0.3rem 0 0 0; font-size: 0.9rem;">Environment: {'Development' if SecureConfig.is_development() else 'Production'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        service_type = "Mock Service" if SecureConfig.use_mock_service() else "Production API"
        environment = "Development" if SecureConfig.is_development() else "Production"
        st.markdown(f"""
        <div style="background: #242420; padding: 1.5rem; border-radius: 8px; border: 2px solid #3d3d36; text-align: center; color: #e8e2d5;">
            <h3 style="color: #4a7a5a; margin: 0.5rem 0;">Service Mode</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;">{service_type}</p>
            <p style="font-size: 0.9rem; color: #a0b5a8; margin: 0;">{environment}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Test API connectivity
        if not SecureConfig.use_mock_service():
            try:
                test_url = SecureConfig.get_api_endpoint().replace('/translate', '/health')
                response = requests.get(test_url, timeout=3)
                status = "🟢 Online" if response.status_code == 200 else "🔴 Error"
            except:
                status = "🔴 Offline"
        else:
            status = "🟢 Active (Mock)"
        
        st.markdown(f"""
        <div style="background: #242420; padding: 1.5rem; border-radius: 8px; border: 2px solid #3d3d36; text-align: center; color: #e8e2d5;">
            <h3 style="color: #4a7a5a; margin: 0.5rem 0;">API Status</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;">{status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        endpoint_display = SecureConfig.get_api_endpoint().split('/')[-2] if not SecureConfig.use_mock_service() else "localhost"
        st.markdown(f"""
        <div style="background: #242420; padding: 1.5rem; border-radius: 8px; border: 2px solid #3d3d36; text-align: center; color: #e8e2d5;">
            <h3 style="color: #4a7a5a; margin: 0.5rem 0;">Endpoint</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;">{endpoint_display}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Configuration
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: #242420; padding: 2rem; border-radius: 8px; border: 2px solid #3d3d36;">
            <h3 style="color: #4a7a5a;">🔧 System Information</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Application Version:** {PublicConfig.APP_VERSION}")
        st.write(f"**Service Mode:** {'Mock (Development)' if SecureConfig.use_mock_service() else 'Production API'}")
        st.write(f"**Environment:** {'Development' if SecureConfig.is_development() else 'Production'}")
        st.write(f"**API Endpoint:** {SecureConfig.get_api_endpoint()}")
        st.write(f"**Max Text Length:** {PublicConfig.MAX_TEXT_LENGTH:,} characters")
        st.write(f"**Mock Processing Time:** {PublicConfig.MOCK_PROCESSING_TIME}s")
    
    with col2:
        st.markdown("""
        <div style="background: #242420; padding: 2rem; border-radius: 8px; border: 2px solid #3d3d36;">
            <h3 style="color: #4a7a5a;">🧪 Service Testing</h3>
        </div>
        """, unsafe_allow_html=True)
        
        test_text = st.text_input("Test Input", placeholder="Enter test text...")
        
        if st.button("🚀 Run Test", use_container_width=True):
            if test_text:
                translator = TurkishTranslator()
                with st.spinner("Testing service..."):
                    result = translator.translate_text(test_text)
                
                if result["success"]:
                    st.success(f"✅ Service operational")
                    st.code(f"Translation: {result.get('translated_text', 'N/A')}")
                    st.caption(f"Response time: {result.get('processing_time', 0):.2f}s | Service: {result.get('service_used', 'Unknown')}")
                else:
                    st.error(f"❌ Service error: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please enter test text")
    
    # Admin Actions
    st.markdown("### 🛠️ Admin Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Clear Session", use_container_width=True):
            # Clear translation results from session
            if 'translation_result' in st.session_state:
                del st.session_state.translation_result
            if 'has_translation' in st.session_state:
                del st.session_state.has_translation
            st.success("Session cleared successfully")
    
    with col2:
        if st.button("📊 System Info", use_container_width=True):
            st.info("System information displayed above")
    
    with col3:
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

def footer():
    """Simple, working footer"""
    st.markdown(f"""
    <div style="background: #252b3a; padding: 2rem; border-radius: 12px; border-top: 3px solid #d4af37; margin-top: 3rem; text-align: center; border: 1px solid #3a4553;">
        <h3 style="color: #d4af37; font-size: 1.5rem; margin: 0 0 1rem 0;">BUCOLIN</h3>
        <p style="color: #d1c7b8; margin: 0 0 1rem 0;">Boğaziçi University Computational Linguistics Lab</p>
        <div style="width: 80px; height: 2px; background: #d4af37; margin: 1rem auto;"></div>
        <p style="color: #d1c7b8; font-size: 0.9rem; margin: 0;">
            {PublicConfig.APP_NAME} v{PublicConfig.APP_VERSION} • © 2025 BUCOLIN Lab
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title=PublicConfig.APP_NAME,
        page_icon="📜",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Check URL parameters for admin access
    query_params = st.query_params
    
    # Admin panel routing (secure)
    if "admin" in query_params:
        admin_panel()
        return
    
    # Regular page routing
    current_page = navigation_menu()
    
    if current_page == "about":
        about_page()
    elif current_page == "research":
        research_page()
    elif current_page == "team":
        team_page()
    else:  # default to demo
        main_app()
    
    # Footer on all pages except admin
    footer()

if __name__ == "__main__":
    main()