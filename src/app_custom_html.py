"""
Phase 6: User Interface - Streamlit Frontend (Exact Dark Theme)
Axis Mutual Fund FAQ Assistant - Exact UI matching design
"""

import os
import sys
import json
import requests
from datetime import datetime
import streamlit.components.v1 as components

import streamlit as st

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration - remove default padding
st.set_page_config(
    page_title="Axis Mutual Fund FAQ Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Remove default padding
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 900px;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for exact dark theme styling
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Container */
    .custom-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem 1rem;
    }
    
    /* Header */
    .header-section {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #10b981;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    
    /* Status indicator */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: #1e293b;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #94a3b8;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Disclaimer */
    .disclaimer-box {
        background-color: #1e293b;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 500;
        color: #fbbf24;
        font-size: 0.95rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 1rem;
    }
    
    /* Example question chips */
    .example-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 2rem;
    }
    
    .example-chip {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
        color: #f1f5f9;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-chip:hover {
        background-color: #334155;
        border-color: #10b981;
    }
    
    /* Input section */
    .input-section {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .input-label {
        font-size: 0.95rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.75rem;
    }
    
    .custom-input {
        width: 100%;
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        color: #f1f5f9;
        font-size: 1rem;
        outline: none;
    }
    
    .custom-input:focus {
        border-color: #10b981;
    }
    
    .submit-btn {
        width: 100%;
        background-color: #10b981;
        color: #0f172a;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.8rem;
        margin-top: 1rem;
        cursor: pointer;
        font-size: 1rem;
        transition: background-color 0.2s;
    }
    
    .submit-btn:hover {
        background-color: #059669;
    }
    
    /* Response box */
    .response-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1.5rem;
        color: #f1f5f9;
    }
    
    .response-answer {
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .response-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #334155;
    }
    
    .response-meta a {
        color: #10b981;
        text-decoration: none;
    }
    
    .response-meta a:hover {
        text-decoration: underline;
    }
    
    /* Refusal box */
    .refusal-box {
        background-color: #1e293b;
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        color: #fca5a5;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #334155;
    }
    
    /* Hide Streamlit default elements */
    .stTextInput, .stButton {
        display: none;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_schemes():
    """Fetch available schemes from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/schemes", timeout=5)
        if response.status_code == 200:
            return response.json().get("schemes", [])
        return []
    except:
        return []


def submit_query(query: str) -> dict:
    """Submit query to backend API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"query": query},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "answer": f"Error: {response.status_code} - {response.text}",
                "has_answer": False,
                "refusal_reason": "api_error"
            }
    except requests.exceptions.ConnectionError:
        return {
            "answer": "Unable to connect to backend. Please ensure the API server is running.",
            "has_answer": False,
            "refusal_reason": "connection_error"
        }
    except Exception as e:
        return {
            "answer": f"An error occurred: {str(e)}",
            "has_answer": False,
            "refusal_reason": "error"
        }


def main():
    # Initialize session state
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "response" not in st.session_state:
        st.session_state.response = None
    
    # Check API health
    api_healthy = check_api_health()
    status_color = "#10b981" if api_healthy else "#ef4444"
    status_text = "API Connected" if api_healthy else "API Disconnected"
    
    # Handle query submission from custom HTML
    query_input = st.text_input("query_input", "", key="hidden_input", label_visibility="collapsed")
    
    if st.button("Submit Query", key="submit_hidden"):
        if query_input.strip():
            if api_healthy:
                response = submit_query(query_input)
                st.session_state.response = response
            else:
                st.session_state.response = {
                    "answer": "(Demo Mode - API not connected) This is where the RAG-generated answer would appear.",
                    "source_url": None,
                    "has_answer": True,
                    "query_timestamp": datetime.now().isoformat()
                }
    
    # Handle example question clicks
    example_clicked = st.text_input("example_clicked", "", key="example_hidden", label_visibility="collapsed")
    if example_clicked:
        st.session_state.query = example_clicked
    
    # Render custom HTML UI
    html_template = f"""
    <div class="custom-container">
        <!-- Header -->
        <div class="header-section">
            <div class="main-header">💰 Axis Mutual Fund FAQ Assistant</div>
            <div class="sub-header">Get factual answers about Axis Mutual Fund schemes</div>
            <div class="status-indicator">
                <div class="status-dot" style="background-color: {status_color};"></div>
                <span>{status_text}</span>
            </div>
        </div>
        
        <!-- Disclaimer -->
        <div class="disclaimer-box">
            ⚠️ <strong>Facts-only information.</strong> This system does not provide investment advice.
        </div>
        
        <!-- Example Questions -->
        <div class="section-header">Try an example question:</div>
        <div class="example-chips">
            <div class="example-chip" onclick="setExample('What is the expense ratio of Axis Flexi Cap Fund?')">What is the expense ratio of Axis Flexi Cap Fund?</div>
            <div class="example-chip" onclick="setExample('What is the NAV of Axis Small Cap Fund?')">What is the NAV of Axis Small Cap Fund?</div>
            <div class="example-chip" onclick="setExample('What is the exit load of Axis Gold Fund?')">What is the exit load of Axis Gold Fund?</div>
            <div class="example-chip" onclick="setExample('What is the AUM of Axis Silver FoF?')">What is the AUM of Axis Silver FoF?</div>
            <div class="example-chip" onclick="setExample('What is the minimum SIP amount?')">What is the minimum SIP amount?</div>
            <div class="example-chip" onclick="setExample('How to download statements?')">How to download statements?</div>
        </div>
        
        <!-- Input Section -->
        <div class="input-section">
            <div class="input-label">Your question:</div>
            <input type="text" class="custom-input" id="queryInput" placeholder="e.g., What is the NAV of Axis Gold Fund?" value="{st.session_state.query}">
            <button class="submit-btn" onclick="submitQuery()">🔍 Get Answer</button>
        </div>
        
        <!-- Response Section -->
    """
    
    if st.session_state.response:
        response = st.session_state.response
        if response.get("has_answer"):
            html_template += f"""
        <div class="response-box">
            <div class="response-answer">{response['answer']}</div>
            <div class="response-meta">
                {'📄 Source: <a href="' + response.get('source_url', '#') + '" target="_blank">' + response.get('source_url', '') + '</a>' if response.get('source_url') else ''}
                {'🏦 Scheme: ' + response.get('scheme_name', '') if response.get('scheme_name') else ''}
                {'📅 Last Updated: ' + response.get('last_updated', '') if response.get('last_updated') else ''}
            </div>
        </div>
            """
        else:
            refusal_reason = response.get("refusal_reason", "")
            if refusal_reason == "advisory":
                message = "❌ I cannot provide investment advice. Please consult a SEBI-registered investment advisor."
            elif refusal_reason == "pii":
                message = "❌ I cannot access personal information. Please check your portfolio on the official AMC website."
            elif refusal_reason == "out_of_scope":
                message = "❌ I can only answer questions about Axis Mutual Fund schemes in my knowledge base."
            elif refusal_reason == "unknown_scheme":
                message = f"❌ {response.get('answer', 'This scheme is not available in my knowledge base.')}"
            elif refusal_reason == "no_context":
                message = "❌ I don't have sufficient information to answer this question accurately."
            else:
                message = response.get("answer", "Unable to process your request.")
            
            html_template += f"""
        <div class="refusal-box">
            {message}
        </div>
            """
    
    html_template += """
        <!-- Available Schemes -->
        <div class="section-header" style="margin-top: 2rem;">📋 Available Schemes</div>
        <div style="background-color: #1e293b; border-radius: 8px; padding: 1rem; color: #f1f5f9;">
            <div>• Axis Flexi Cap Fund Direct Growth (Equity - Flexi-cap)</div>
            <div>• Axis Small Cap Fund Direct Growth (Equity - Small-cap)</div>
            <div>• Axis Silver FoF Direct Growth (Fund of Funds - Commodities)</div>
            <div>• Axis Gold Fund Direct Growth (Commodity - Gold)</div>
            <div>• Axis Nifty India Defence Index Fund Direct Growth (Index - Thematic Defence)</div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            🤖 Powered by RAG + Groq LLM | 📊 Data source: Groww
        </div>
    </div>
    
    <script>
        function setExample(question) {
            document.getElementById('queryInput').value = question;
            document.getElementById('queryInput').focus();
        }
        
        function submitQuery() {
            const query = document.getElementById('queryInput').value;
            if (query.trim()) {
                // Trigger Streamlit rerun with the query
                window.location.href = window.location.pathname + '?query=' + encodeURIComponent(query);
            }
        }
    </script>
    """
    
    components.html(html_template, height=800)


if __name__ == "__main__":
    main()
