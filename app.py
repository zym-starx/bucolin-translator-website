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

def get_theme_colors(theme='dark'):
    """Get color variables for the selected theme"""
    if theme == 'dark':
        return """
        /* Background Colors */
        --bg-primary: #0c1220;
        --bg-secondary: #151b2d;
        --bg-tertiary: #1f2937;
        --bg-elevated: #1a2030;
        --bg-surface: #11171f;
        
        /* Accent Colors */
        --accent-primary: #5eb3d1;
        --accent-secondary: #4a9ab8;
        --accent-tertiary: #7bc4de;
        --accent-muted: #3d8aa8;
        --accent-medium: #4a9ab8;
        --accent-hover: #5eb3d1;
        
        /* Text Colors */
        --text-primary: #ecfeff;
        --text-secondary: #cffafe;
        --text-muted: #a5f3fc;
        --text-accent: #7dd3fc;
        --text-bright: #ffffff;
        --text-subtle: #e0f2fe;
        
        /* Border Colors */
        --border-primary: #2c3e50;
        --border-secondary: #1f2d3d;
        --border-accent: #22d3ee;
        
        /* Status Colors */
        --status-success: #6ee7b7;
        --status-error: #fca5a5;
        --status-warning: #fcd34d;
        --status-info: #7dd3fc;
        
        /* Interactive Colors */
        --interactive-primary: #22d3ee;
        --interactive-primary-hover: #06b6d4;
        --interactive-primary-active: #0891b2;
        --interactive-secondary: #7dd3fc;
        --interactive-secondary-hover: #38bdf8;
        --interactive-secondary-active: #0ea5e9;
        
        /* Shadow Effects */
        --shadow-sm: rgba(0, 0, 0, 0.3);
        --shadow-md: rgba(0, 0, 0, 0.4);
        --shadow-lg: rgba(0, 0, 0, 0.5);
        --shadow-xl: rgba(0, 0, 0, 0.6);
        
        /* Overlay Effects */
        --overlay-primary-xs: rgba(125, 211, 252, 0.05);
        --overlay-primary-sm: rgba(125, 211, 252, 0.08);
        --overlay-primary-md: rgba(125, 211, 252, 0.12);
        --overlay-primary-lg: rgba(125, 211, 252, 0.25);
        --overlay-primary-xl: rgba(125, 211, 252, 0.35);
        --overlay-primary-2xl: rgba(125, 211, 252, 0.45);
        --overlay-secondary-sm: rgba(56, 189, 248, 0.08);
        --overlay-secondary-lg: rgba(56, 189, 248, 0.3);
        --overlay-secondary-xl: rgba(56, 189, 248, 0.4);
        --overlay-tertiary-sm: rgba(165, 243, 252, 0.08);
        --overlay-tertiary-md: rgba(165, 243, 252, 0.12);
        --overlay-tertiary-lg: rgba(165, 243, 252, 0.2);
        --overlay-tertiary-xl: rgba(165, 243, 252, 0.3);
        --overlay-tertiary-2xl: rgba(165, 243, 252, 0.35);
        --overlay-tertiary-3xl: rgba(165, 243, 252, 0.45);
        --overlay-highlight-md: rgba(125, 211, 252, 0.4);
        --overlay-highlight-lg: rgba(165, 243, 252, 0.5);
        --overlay-white-sm: rgba(255, 255, 255, 0.08);
        --overlay-white-md: rgba(255, 255, 255, 0.15);
        """
    else:  # light theme
        return """
        /* Background Colors */
        --bg-primary: #ffffff;
        --bg-secondary: #ecfeff;
        --bg-tertiary: #cffafe;
        --bg-elevated: #ffffff;
        --bg-surface: #a5f3fc;
        
        /* Accent Colors */
        --accent-primary: #0891b2;
        --accent-secondary: #0e7490;
        --accent-tertiary: #06b6d4;
        --accent-muted: #22d3ee;
        --accent-medium: #0891b2;
        --accent-hover: #0e7490;
        
        /* Text Colors */
        --text-primary: #083344;
        --text-secondary: #155e75;
        --text-muted: #0e7490;
        --text-accent: #0891b2;
        --text-bright: #042f2e;
        --text-subtle: #0c4a6e;
        
        /* Border Colors */
        --border-primary: #a5f3fc;
        --border-secondary: #cffafe;
        --border-accent: #22d3ee;
        
        /* Status Colors */
        --status-success: #10b981;
        --status-error: #ef4444;
        --status-warning: #f59e0b;
        --status-info: #06b6d4;
        
        /* Interactive Colors */
        --interactive-primary: #0891b2;
        --interactive-primary-hover: #0e7490;
        --interactive-primary-active: #155e75;
        --interactive-secondary: #06b6d4;
        --interactive-secondary-hover: #0891b2;
        --interactive-secondary-active: #0e7490;
        
        /* Shadow Effects */
        --shadow-sm: rgba(8, 51, 68, 0.1);
        --shadow-md: rgba(8, 51, 68, 0.15);
        --shadow-lg: rgba(8, 51, 68, 0.2);
        --shadow-xl: rgba(8, 51, 68, 0.25);
        
        /* Overlay Effects */
        --overlay-primary-xs: rgba(8, 145, 178, 0.04);
        --overlay-primary-sm: rgba(8, 145, 178, 0.06);
        --overlay-primary-md: rgba(8, 145, 178, 0.10);
        --overlay-primary-lg: rgba(8, 145, 178, 0.15);
        --overlay-primary-xl: rgba(8, 145, 178, 0.20);
        --overlay-primary-2xl: rgba(8, 145, 178, 0.25);
        --overlay-secondary-sm: rgba(6, 182, 212, 0.08);
        --overlay-secondary-lg: rgba(6, 182, 212, 0.20);
        --overlay-secondary-xl: rgba(6, 182, 212, 0.25);
        --overlay-tertiary-sm: rgba(34, 211, 238, 0.08);
        --overlay-tertiary-md: rgba(34, 211, 238, 0.12);
        --overlay-tertiary-lg: rgba(34, 211, 238, 0.16);
        --overlay-tertiary-xl: rgba(34, 211, 238, 0.20);
        --overlay-tertiary-2xl: rgba(34, 211, 238, 0.25);
        --overlay-tertiary-3xl: rgba(34, 211, 238, 0.30);
        --overlay-highlight-md: rgba(8, 145, 178, 0.20);
        --overlay-highlight-lg: rgba(6, 182, 212, 0.30);
        --overlay-white-sm: rgba(255, 255, 255, 0.6);
        --overlay-white-md: rgba(255, 255, 255, 0.9);
        """
    
def apply_custom_styles():
    """Apply beautiful, modern custom CSS styles to the application"""
    # Get theme from session state (default to dark)
    theme = st.session_state.get('theme', 'dark')
    theme_colors = get_theme_colors(theme)
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
    
    :root {{
        {theme_colors}
    }}
    
    .stApp {{
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: background 0.3s ease, color 0.3s ease;
    }}
    
    /* Add subtle pattern overlay */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 1px 1px, var(--overlay-primary-xs) 1px, transparent 0);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: -1;
    }}
    
    .nav-container {{
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        backdrop-filter: blur(30px);
        padding: 1rem 2rem;
        border-radius: 30px;
        margin-bottom: 2rem;
        border: 2px solid var(--overlay-primary-lg);
        box-shadow: 0 8px 32px var(--shadow-lg), inset 0 1px 0 var(--overlay-white-sm);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}

    .nav-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), var(--accent-tertiary), var(--accent-secondary), transparent);
    }}

    .nav-container::after {{
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, var(--overlay-primary-md) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(50%, -50%);
        pointer-events: none;
    }}
    
    .bucolin-brand {{
        color: var(--accent-primary);
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
    }}

    .bucolin-brand::after {{
        content: '';
        position: absolute;
        bottom: -8px;
        left: 50%;
        transform: translateX(-50%);
        width: 60px;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
    }}
    
    .main-header {{
        text-align: center;
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: var(--text-primary);
        margin-bottom: 3rem;
        box-shadow: 
            0 16px 40px var(--shadow-md),
            inset 0 1px 0 var(--overlay-white-sm);
        border: 1px solid var(--border-primary);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            135deg,
            var(--overlay-primary-sm) 0%,
            var(--overlay-secondary-sm) 50%,
            var(--overlay-tertiary-sm) 100%
        );
        pointer-events: none;
    }}
    
    .main-header h1 {{
        position: relative;
        z-index: 1;
        font-family: 'Crimson Text', serif !important;
        font-weight: 700;
        font-size: 2.8rem;
        margin: 0;
        background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 4px 8px var(--shadow-sm);
    }}
    
    .translation-container {{
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-primary);
        box-shadow: 0 12px 32px var(--shadow-md);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    .translation-container:hover {{
        transform: translateY(-2px);
        box-shadow: 0 16px 40px var(--shadow-md);
    }}
    
    .translation-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
    }}
    
    .section-header {{
        color: var(--accent-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid var(--accent-secondary);
        text-transform: uppercase;
        letter-spacing: 3px;
        font-family: 'Inter', sans-serif;
        position: relative;
    }}
    
    .section-header::after {{
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: var(--accent-primary);
    }}
    
    .stats-grid {{
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
        backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 3rem 0;
        border: 1px solid var(--border-primary);
        box-shadow: 0 16px 40px var(--shadow-md);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    .stats-grid::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-tertiary), var(--accent-secondary));
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        padding: 2rem 1.5rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--border-primary);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px var(--shadow-sm);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, var(--overlay-primary-md), transparent);
        transition: left 0.5s ease;
    }}
    
    .metric-card:hover::before {{
        left: 100%;
    }}
    
    .metric-card:hover {{
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 40px var(--overlay-primary-lg);
        border-color: var(--accent-primary);
    }}
    
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--accent-primary);
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 2px 8px var(--overlay-primary-xl);
    }}
    
    .metric-label {{
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.9;
    }}
    
    .stTextArea > div > div > textarea {{
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 12px !important;
        font-size: 1.05rem !important;
        line-height: 1.7 !important;
        font-family: 'Crimson Text', serif !important;
        padding: 1.2rem !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(10px) !important;
    }}
    
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px var(--overlay-primary-lg), 0 8px 25px var(--shadow-sm) !important;
        transform: translateY(-1px) !important;
    }}
    
    .stTextArea > div > div > textarea::placeholder {{
        color: var(--text-muted) !important;
        font-style: italic !important;
    }}
    
    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-primary) 100%) !important;
        color: var(--text-primary) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px var(--overlay-tertiary-3xl) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    .stButton > button::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, var(--overlay-white-md), transparent) !important;
        transition: left 0.5s ease !important;
    }}
    
    .stButton > button:hover::before {{
        left: 100% !important;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-tertiary) 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px var(--overlay-primary-2xl) !important;
    }}
    
    .success-message {{
        background: linear-gradient(135deg, var(--overlay-tertiary-lg), var(--overlay-tertiary-md));
        color: var(--status-success);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        border: 1px solid var(--overlay-tertiary-xl);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px var(--overlay-tertiary-lg);
    }}
    
    .error-message {{
        background: linear-gradient(135deg, var(--overlay-secondary-lg), var(--overlay-secondary-sm));
        color: var(--status-error);
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        border: 1px solid var(--overlay-secondary-lg);
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px var(--overlay-secondary-xl);
    }}
    
    .details-section {{
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border-primary);
        margin-top: 1.5rem;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }}
    
    /* Translate button special styling */
    .stButton[data-testid="baseButton-primary"] > button {{
        background: linear-gradient(135deg, var(--interactive-primary) 0%, var(--interactive-primary-hover) 50%, var(--interactive-primary-active) 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 8px 25px var(--overlay-highlight-md) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    .stButton[data-testid="baseButton-primary"] > button:hover {{
        background: linear-gradient(135deg, var(--interactive-secondary) 0%, var(--interactive-secondary-hover) 50%, var(--interactive-secondary-active) 100%) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px var(--overlay-highlight-lg) !important;
    }}
    
    /* Secondary button styling for navigation */
    .stButton[data-testid="baseButton-secondary"] > button {{
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-elevated) 100%) !important;
        color: var(--text-secondary) !important;
        border: 1px solid var(--border-primary) !important;
        border-radius: 12px !important;
        padding: 1rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 12px var(--shadow-sm) !important;
        font-family: 'Inter', sans-serif !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    
    .stButton[data-testid="baseButton-secondary"] > button::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, var(--overlay-primary-sm), transparent) !important;
        transition: left 0.5s ease !important;
    }}
    
    .stButton[data-testid="baseButton-secondary"] > button:hover::before {{
        left: 100% !important;
    }}
    
    .stButton[data-testid="baseButton-secondary"] > button:hover {{
        background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-tertiary) 100%) !important;
        color: var(--text-primary) !important;
        border-color: var(--accent-primary) !important;
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 20px var(--shadow-md) !important;
    }}
    
    /* Character counter styling */
    .stCaption {{
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        margin-top: 0.5rem !important;
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-primary) !important;
        transition: all 0.3s ease !important;
    }}
    
    /* Link button styling */
    .stLinkButton > a {{
        background: linear-gradient(135deg, var(--accent-tertiary) 0%, var(--accent-primary) 100%) !important;
        color: var(--text-primary) !important;
        text-decoration: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }}
    
    .stLinkButton > a:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px var(--overlay-secondary-xl) !important;
    }}
    
    /* Animation for loading */
    @keyframes shimmer {{
        0% {{ background-position: -1000px 0; }}
        100% {{ background-position: 1000px 0; }}
    }}
    
    .loading-shimmer {{
        background: linear-gradient(90deg, transparent, var(--overlay-primary-md), transparent);
        background-size: 1000px 100%;
        animation: shimmer 2s infinite;
    }}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-tertiary));
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(135deg, var(--accent-tertiary), var(--accent-secondary));
    }}

    /* Responsive Navigation for Small Screens */
    @media (max-width: 1200px) {{
        .stButton > button,
        .stButton[data-testid="baseButton-secondary"] > button,
        .stButton[data-testid="baseButton-primary"] > button {{
            font-size: 0.9rem !important;
            letter-spacing: 1px !important;
            padding: 0.8rem 1.5rem !important;
        }}
    }}

    @media (max-width: 992px) {{
        .stButton > button,
        .stButton[data-testid="baseButton-secondary"] > button,
        .stButton[data-testid="baseButton-primary"] > button {{
            font-size: 0.85rem !important;
            letter-spacing: 0.5px !important;
            padding: 0.7rem 1rem !important;
        }}
        
        .bucolin-brand {{
            font-size: 1.2rem !important;
            letter-spacing: 3px !important;
        }}
    }}

    @media (max-width: 768px) {{
        .stButton > button,
        .stButton[data-testid="baseButton-secondary"] > button,
        .stButton[data-testid="baseButton-primary"] > button {{
            font-size: 0.75rem !important;
            letter-spacing: 0px !important;
            padding: 0.6rem 0.8rem !important;
            text-transform: none !important;
        }}
        
        .bucolin-brand {{
            font-size: 1rem !important;
            letter-spacing: 2px !important;
            margin-bottom: 0.5rem !important;
        }}
        
        .nav-container {{
            padding: 0.8rem 1rem !important;
        }}
    }}

    @media (max-width: 576px) {{
        /* Hide decorative icon on very small screens */
        [data-testid="column"]:first-child {{
            display: none !important;
        }}
        
        .stButton > button,
        .stButton[data-testid="baseButton-secondary"] > button,
        .stButton[data-testid="baseButton-primary"] > button {{
            font-size: 0.7rem !important;
            padding: 0.5rem 0.6rem !important;
        }}
        
        .stLinkButton > a {{
            font-size: 0.7rem !important;
            padding: 0.5rem 0.6rem !important;
        }}
    }}

    </style>
    """, unsafe_allow_html=True)

def theme_toggle():
    """Render theme toggle button"""
    current_theme = st.session_state.get('theme', 'dark')
    
    # Create columns for the theme toggle in the navigation
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col3:
        if current_theme == 'dark':
            if st.button("☀️ Light", key="theme_btn", use_container_width=True):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙 Dark", key="theme_btn", use_container_width=True):
                st.session_state.theme = 'dark'
                st.rerun()

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
    
    # Navigation buttons with small decorative icon and theme toggle on the ends
    col_left, col1, col2, col3, col4, col5, col_right = st.columns([0.6, 1, 1, 1, 1, 1, 0.6])
    
    # Small decorative element on the left (not a button)
    with col_left:
        st.markdown(
            '<div style="display: flex; align-items: center; justify-content: center; height: 38px; font-size: 1.2rem; opacity: 0.4;">📚</div>',
            unsafe_allow_html=True
        )
    
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
    
    # Small theme toggle button on the right
    with col_right:
        current_theme = st.session_state.get('theme', 'dark')
        if current_theme == 'dark':
            if st.button("☀️", use_container_width=True, key="theme_btn", help="Switch to Light Mode"):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙", use_container_width=True, key="theme_btn", help="Switch to Dark Mode"):
                st.session_state.theme = 'dark'
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return current_page

def main_app():
    """Main translation application interface"""
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <div style="position: relative; z-index: 1;">
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700; font-family: 'Crimson Text', serif; 
                       background: linear-gradient(135deg, var(--text-primary), var(--accent-primary));
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                HISTORICAL TURKISH TRANSLATOR
            </h1>
            <div style="display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 1rem;">
                <span style="color: var(--accent-tertiary); font-weight: 600; font-size: 1rem; font-family: 'Inter', sans-serif;">
                    {PublicConfig.DEFAULT_LANGUAGE_PAIR[0].replace('_', ' ').title()}
                </span>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 8px; height: 1px; background: var(--accent-primary);"></div>
                    <span style="color: var(--accent-primary); font-size: 1.2rem; font-weight: 700;">⟷</span>
                    <div style="width: 8px; height: 1px; background: var(--accent-primary);"></div>
                </div>
                <span style="color: var(--accent-tertiary); font-weight: 600; font-size: 1rem; font-family: 'Inter', sans-serif;">
                    {PublicConfig.DEFAULT_LANGUAGE_PAIR[1].replace('_', ' ').title()}
                </span>
            </div>
            <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; margin-top: 1.5rem; font-size: 0.85rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--accent-secondary);">🚀</span>
                    <span style="color: var(--text-muted); font-weight: 500;">v{PublicConfig.APP_VERSION}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="color: var(--accent-primary);">🎓</span>
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
                <div style="display: inline-block; width: 60px; height: 60px; border: 3px solid var(--border-primary); 
                            border-radius: 50%; border-top: 3px solid var(--accent-primary); 
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
            <h3 style="color: var(--accent-primary); margin-bottom: 2.5rem; text-align: center; 
                       font-family: 'Crimson Text', serif; text-transform: uppercase; 
                       letter-spacing: 3px; font-size: 1.6rem; font-weight: 700;
                       background: linear-gradient(135deg, var(--accent-primary), var(--accent-tertiary));
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
                    confidence_color = "var(--accent-secondary)"
                    confidence_label = "Excellent"
                elif confidence > 0.6:
                    confidence_emoji = "🟡"  
                    confidence_color = "var(--accent-primary)"
                    confidence_label = "Good"
                else:
                    confidence_emoji = "🔴"
                    confidence_color = "var(--accent-tertiary)"
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
                service_color = "var(--accent-tertiary)" if "Mock" in service_used else "var(--accent-secondary)"
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
        <h1 style="color: var(--accent-primary); font-family: 'Crimson Text', serif; font-size: 3rem; font-weight: 700; margin-bottom: 1rem;">Historical Turkish Translation</h1>
        <p style="color: var(--text-secondary); font-size: 1.3rem; font-weight: 400; max-width: 600px; margin: 0 auto;">Bridging centuries of Turkish linguistic evolution with cutting-edge AI technology</p>
        <div style="width: 80px; height: 3px; background: linear-gradient(90deg, var(--accent-primary), var(--accent-tertiary)); margin: 2rem auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-primary); 
                    box-shadow: 0 12px 32px var(--shadow-md); margin-bottom: 2rem;">
            <h2 style="color: var(--accent-primary); font-size: 1.8rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">🌟 Project Overview</h2>
            <p style="color: var(--text-secondary); line-height: 1.8; font-size: 1.1rem; margin-bottom: 1.5rem;">
                This translation system represents a breakthrough in computational linguistics for historical Turkish texts. 
                Developed by the BUCOLIN lab at Boğaziçi University, it enables seamless translation between Ottoman Turkish 
                and Modern Turkish, making centuries of historical documents accessible to contemporary readers and researchers.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%); 
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-primary); 
                    box-shadow: 0 12px 32px var(--shadow-md);">
            <h3 style="color: var(--accent-tertiary); font-size: 1.5rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">🚀 Key Features</h3>
            <div style="display: grid; gap: 1rem;">
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-primary);">
                    <span style="color: var(--accent-primary); font-size: 1.2rem; margin-right: 1rem;">🎯</span>
                    <div>
                        <strong style="color: var(--text-primary);">Historical Accuracy:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Trained on authentic texts from 15th-20th centuries</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-tertiary);">
                    <span style="color: var(--accent-tertiary); font-size: 1.2rem; margin-right: 1rem;">🔬</span>
                    <div>
                        <strong style="color: var(--text-primary);">Linguistic Precision:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Preserves semantic meaning across temporal variations</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-secondary);">
                    <span style="color: var(--accent-secondary); font-size: 1.2rem; margin-right: 1rem;">🎓</span>
                    <div>
                        <strong style="color: var(--text-primary);">Academic Grade:</strong>
                        <span style="color: var(--text-secondary); margin-left: 0.5rem;">Suitable for scholarly research and educational purposes</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 0.8rem; background: var(--bg-primary); border-radius: 8px; border-left: 3px solid var(--accent-primary);">
                    <span style="color: var(--accent-primary); font-size: 1.2rem; margin-right: 1rem;">⚡</span>
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
        <div style="background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-primary) 100%); 
                    padding: 2.5rem; border-radius: 16px; color: var(--text-primary); 
                    box-shadow: 0 16px 40px var(--overlay-tertiary-2xl); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; 
                        background: radial-gradient(circle, var(--overlay-white-sm) 0%, transparent 70%); 
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
    <h2 style="text-align: center; color: var(--accent-primary); font-family: 'Crimson Text', serif; 
               font-size: 2.2rem; margin: 3rem 0 2rem 0;">✨ Core Capabilities</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 2rem; 
                    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
                    border-radius: 16px; border: 1px solid var(--border-primary);
                    box-shadow: 0 12px 32px var(--shadow-md); 
                    transition: all 0.4s ease; position: relative; overflow: hidden;"
             onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 40px var(--overlay-primary-xl)';"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 12px 32px var(--shadow-md)';">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem; 
                        background: linear-gradient(135deg, var(--accent-primary), var(--accent-tertiary));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">📜</div>
            <h3 style="color: var(--accent-primary); margin-bottom: 1rem; font-family: 'Crimson Text', serif; font-size: 1.3rem;">Historical Texts</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">Process manuscripts, documents, and literature from the Ottoman period with unprecedented accuracy and cultural sensitivity.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 2rem; 
                    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
                    border-radius: 16px; border: 1px solid var(--border-primary);
                    box-shadow: 0 12px 32px var(--shadow-md); 
                    transition: all 0.4s ease; position: relative; overflow: hidden;"
             onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 40px var(--overlay-secondary-xl)';"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 12px 32px var(--shadow-md)';">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem; 
                        background: linear-gradient(135deg, var(--accent-tertiary), var(--accent-primary));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">🧠</div>
            <h3 style="color: var(--accent-tertiary); margin-bottom: 1rem; font-family: 'Crimson Text', serif; font-size: 1.3rem;">AI-Powered</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">Advanced neural networks specifically trained and fine-tuned for the nuances of historical Turkish language variations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 2.5rem 2rem; 
                    background: linear-gradient(135deg, var(--bg-tertiary) 0%, var(--bg-secondary) 100%);
                    border-radius: 16px; border: 1px solid var(--border-primary);
                    box-shadow: 0 12px 32px var(--shadow-md); 
                    transition: all 0.4s ease; position: relative; overflow: hidden;"
             onmouseover="this.style.transform='translateY(-8px) scale(1.02)'; this.style.boxShadow='0 20px 40px var(--overlay-tertiary-2xl)';"
             onmouseout="this.style.transform='translateY(0) scale(1)'; this.style.boxShadow='0 12px 32px var(--shadow-md)';">
            <div style="font-size: 3.5rem; margin-bottom: 1.5rem; 
                        background: linear-gradient(135deg, var(--accent-secondary), var(--accent-primary));
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                        background-clip: text;">🎓</div>
            <h3 style="color: var(--accent-secondary); margin-bottom: 1rem; font-family: 'Crimson Text', serif; font-size: 1.3rem;">Academic Research</h3>
            <p style="color: var(--text-secondary); line-height: 1.6;">Developed by computational linguistics experts at Boğaziçi University with rigorous academic standards and peer review.</p>
        </div>
        """, unsafe_allow_html=True)

def research_page():
    """Research page with academic information"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 4rem;">
        <h1 style="color: var(--accent-primary); font-family: 'Crimson Text', serif; font-size: 3rem; font-weight: 700; margin-bottom: 1rem;">Research & Publications</h1>
        <p style="color: var(--text-secondary); font-size: 1.3rem; font-weight: 400; max-width: 600px; margin: 0 auto;">Academic foundations and cutting-edge research in historical Turkish NLP</p>
        <div style="width: 80px; height: 3px; background: linear-gradient(90deg, var(--accent-primary), var(--accent-tertiary)); margin: 2rem auto; border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        with st.container():
            st.markdown("""
            <div style="background: var(--bg-elevated); padding: 1.5rem; border-radius: 8px; border-left: 4px solid var(--accent-medium); margin: 1rem 0;">
                <h3 style="color: var(--text-bright); margin-top: 0;">Translation Model Main Publication</h3>
                <p style="color: var(--text-accent); margin: 0.5rem 0;"><strong>Authors:</strong> BUCOLIN Research Team</p>
                <p style="color: var(--text-accent); margin: 0.5rem 0;"><strong>Institution:</strong> Boğaziçi University</p>
                <p style="color: var(--text-accent); margin: 0.5rem 0;"><strong>Status:</strong> <span style="color: var(--accent-hover);">Work in Progress</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("📄 Paper Coming Soon", disabled=True):
                st.info("Paper will be available upon publication")
        
        with st.container():
            st.markdown("""
            <div style="background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-muted) 100%); 
                        padding: 2rem; border-radius: 12px; border-left: 4px solid var(--accent-primary); 
                        margin: 1rem 0; box-shadow: 0 8px 24px var(--overlay-tertiary-2xl);">
                <h3 style="color: var(--text-primary); margin-top: 0; font-size: 1.4rem; font-family: 'Crimson Text', serif; line-height: 1.3;">
                    Building Foundations for Natural Language Processing of Historical Turkish: Resources and Models
                </h3>
                <div style="margin: 1.5rem 0;">
                    <p style="color: var(--text-secondary); margin: 0.5rem 0;"><strong>Authors:</strong> Şaziye Betül Özateş, Tarık Emre Tıraş, Ece Elif Adak, Berat Doğan, Fatih Burak Karagöz, Efe Eren Genç, Esma F. Bilgin Taşdemir</p>
                    <p style="color: var(--text-secondary); margin: 0.5rem 0;"><strong>Institution:</strong> Boğaziçi University</p>
                    <p style="color: var(--text-secondary); margin: 0.5rem 0;"><strong>Published:</strong> <span style="color: var(--accent-primary);">January 8, 2025</span></p>
                    <p style="color: var(--text-secondary); margin: 0.5rem 0;"><strong>arXiv ID:</strong> <span style="color: var(--accent-tertiary);">2501.04828</span></p>
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
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-primary); 
                    box-shadow: 0 12px 32px var(--shadow-md); margin-top: 2rem;">
            <h3 style="color: var(--accent-tertiary); font-size: 1.5rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">📋 Abstract</h3>
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
                    padding: 2.5rem; border-radius: 16px; border: 1px solid var(--border-primary); 
                    box-shadow: 0 12px 32px var(--shadow-md); margin-top: 2rem; opacity: 0.8;
                    border: 2px dashed var(--accent-primary);">
            <h3 style="color: var(--accent-primary); font-size: 1.5rem; margin-bottom: 1.5rem; font-family: 'Crimson Text', serif;">🚀 Upcoming Publication</h3>
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
        <div style="background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-primary) 100%); 
                    padding: 2.5rem; border-radius: 16px; color: var(--text-primary); 
                    box-shadow: 0 16px 40px var(--overlay-tertiary-2xl); position: relative; overflow: hidden; margin-bottom: 2rem;">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; 
                        background: radial-gradient(circle, var(--overlay-white-sm) 0%, transparent 70%); 
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
        <div style="background: linear-gradient(135deg, var(--accent-tertiary) 0%, var(--accent-primary) 100%); 
                    padding: 2.5rem; border-radius: 16px; color: var(--text-primary); 
                    box-shadow: 0 16px 40px var(--overlay-secondary-xl); position: relative; overflow: hidden;">
            <div style="position: absolute; top: -50%; right: -50%; width: 100%; height: 100%; 
                        background: radial-gradient(circle, var(--overlay-white-sm) 0%, transparent 70%); 
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
        <h1 style="color: var(--accent-hover); font-family: Georgia, serif; font-size: 2.5rem;">Research Team</h1>
        <p style="color: var(--text-accent); font-size: 1.2rem;">BUCOLIN - Boğaziçi University Computational Linguistics Lab</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("## 🏛️ Laboratory")
    
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <p style="color: var(--text-bright); font-size: 1.1rem;">
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
    <div style="background: var(--accent-medium); padding: 2.5rem; border-radius: 8px; margin-bottom: 2rem; color: var(--text-bright); box-shadow: 0 6px 20px var(--overlay-tertiary-3xl); border: 2px solid var(--accent-secondary);">
        <h1 style="color: var(--text-bright); font-weight: bold; margin: 0;">🔧 System Administration</h1>
        <p style="color: var(--text-bright); margin: 0.5rem 0 0 0;">{PublicConfig.APP_NAME} - Control Panel</p>
        <p style="color: var(--text-subtle); margin: 0.3rem 0 0 0; font-size: 0.9rem;">Environment: {'Development' if SecureConfig.is_development() else 'Production'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # System Status Overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        service_type = "Mock Service" if SecureConfig.use_mock_service() else "Production API"
        environment = "Development" if SecureConfig.is_development() else "Production"
        st.markdown(f"""
        <div style="background: var(--bg-surface); padding: 1.5rem; border-radius: 8px; border: 2px solid var(--border-secondary); text-align: center; color: var(--text-bright);">
            <h3 style="color: var(--accent-hover); margin: 0.5rem 0;">Service Mode</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;">{service_type}</p>
            <p style="font-size: 0.9rem; color: var(--text-accent); margin: 0;">{environment}</p>
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
        <div style="background: var(--bg-surface); padding: 1.5rem; border-radius: 8px; border: 2px solid var(--border-secondary); text-align: center; color: var(--text-bright);">
            <h3 style="color: var(--accent-hover); margin: 0.5rem 0;">API Status</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;">{status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        endpoint_display = SecureConfig.get_api_endpoint().split('/')[-2] if not SecureConfig.use_mock_service() else "localhost"
        st.markdown(f"""
        <div style="background: var(--bg-surface); padding: 1.5rem; border-radius: 8px; border: 2px solid var(--border-secondary); text-align: center; color: var(--text-bright);">
            <h3 style="color: var(--accent-hover); margin: 0.5rem 0;">Endpoint</h3>
            <p style="font-size: 1.1rem; margin: 0.5rem 0;">{endpoint_display}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System Configuration
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: var(--bg-surface); padding: 2rem; border-radius: 8px; border: 2px solid var(--border-secondary);">
            <h3 style="color: var(--accent-hover);">🔧 System Information</h3>
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
        <div style="background: var(--bg-surface); padding: 2rem; border-radius: 8px; border: 2px solid var(--border-secondary);">
            <h3 style="color: var(--accent-hover);">🧪 Service Testing</h3>
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
    <div style="background: var(--bg-tertiary); padding: 2rem; border-radius: 12px; border-top: 3px solid var(--accent-primary); margin-top: 3rem; text-align: center; border: 1px solid var(--border-primary);">
        <h3 style="color: var(--accent-primary); font-size: 1.5rem; margin: 0 0 1rem 0;">BUCOLIN</h3>
        <p style="color: var(--text-secondary); margin: 0 0 1rem 0;">Boğaziçi University Computational Linguistics Lab</p>
        <div style="width: 80px; height: 2px; background: var(--accent-primary); margin: 1rem auto;"></div>
        <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">
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
    
    # Initialize theme in session state if not present
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    
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