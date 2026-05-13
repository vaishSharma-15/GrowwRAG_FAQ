"""
Phase 6: User Interface - Streamlit Frontend
Mutual Fund FAQ Assistant UI
"""

import os
import sys
import json
import requests
from datetime import datetime

import streamlit as st

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Mutual Fund FAQ Assistant",
    page_icon="💰",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme styling
st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #10b981;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Status indicator */
    .status-indicator {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .disclaimer-box {
        background-color: #1e293b;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        text-align: center;
        font-weight: 500;
        color: #fbbf24;
    }
    .example-btn {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
        color: #f1f5f9;
    }
    .example-btn:hover {
        background-color: #334155;
        border-color: #10b981;
    }
    .response-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 1rem;
        color: #f1f5f9;
    }
    .source-link {
        color: #10b981;
        text-decoration: none;
        font-size: 0.9rem;
    }
    .source-link:hover {
        text-decoration: underline;
    }
    .refusal-box {
        background-color: #1e293b;
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 1rem;
        color: #fca5a5;
    }
    .footer {
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #334155;
    }
    .stButton>button {
        width: 100%;
        background-color: #10b981;
        color: #0f172a;
        font-weight: 600;
        border: none;
    }
    .stButton>button:hover {
        background-color: #059669;
    }
    /* Text input styling */
    .stTextInput>div>div>input {
        background-color: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        color: #f1f5f9;
    }
    
    /* Captions */
    .stCaption {
        color: #64748b;
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
    # Header
    st.markdown('<div class="main-header">💰 Axis Mutual Fund FAQ Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Get factual answers about Axis Mutual Fund schemes</div>', unsafe_allow_html=True)
    
    # Status indicator
    api_healthy = check_api_health()
    status_color = "#10b981" if api_healthy else "#ef4444"
    status_text = "API Connected" if api_healthy else "API Disconnected"
    st.markdown(
        f'<div class="status-indicator">'
        f'<div class="status-dot" style="background-color: {status_color};"></div>'
        f'<span>{status_text}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Disclaimer
    st.markdown(
        '<div class="disclaimer-box">⚠️ <strong>Facts-only information.</strong> '
        'This system does not provide investment advice.</div>',
        unsafe_allow_html=True
    )
    
    if not api_healthy:
        st.error("⚠️ Backend API is not running. Please start it with: `python3 -m uvicorn src.api:app --reload`")
        st.info("The frontend will still work for demonstration, but queries won't be processed.")
    
    # Example questions as chips
    st.markdown("### Try an example question:")
    
    example_questions = [
        "What is the expense ratio of Axis Flexi Cap Fund?",
        "What is the NAV of Axis Small Cap Fund?",
        "What is the exit load of Axis Gold Fund?",
        "What is the AUM of Axis Silver FoF?",
        "What is the minimum SIP amount?",
        "How to download statements?"
    ]
    
    # Display example questions as clickable chips
    cols = st.columns(3)
    for i, question in enumerate(example_questions):
        with cols[i % 3]:
            if st.button(question, key=f"example_{i}", use_container_width=True):
                st.session_state.query = question
                st.session_state.query_input = question
                st.session_state.submit_clicked = True
    
    # Query input
    st.markdown("---")
    st.markdown("### Or ask your own question:")
    
    # Initialize session state
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "submit_clicked" not in st.session_state:
        st.session_state.submit_clicked = False
    if "response" not in st.session_state:
        st.session_state.response = None
    
    # Input field
    query = st.text_input(
        "Your question:",
        value=st.session_state.query,
        placeholder="e.g., What is the NAV of Axis Gold Fund?",
        key="query_input"
    )
    
    # Update session state
    st.session_state.query = query
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit = st.button("🔍 Get Answer", use_container_width=True, type="primary")
    
    # Process query
    if submit or st.session_state.submit_clicked:
        if query.strip():
            with st.spinner("🔍 Finding answer..."):
                if api_healthy:
                    response = submit_query(query)
                    st.session_state.response = response
                else:
                    # Demo mode when API is not available
                    st.session_state.response = {
                        "answer": "(Demo Mode - API not connected) This is where the RAG-generated answer would appear.",
                        "source_url": None,
                        "has_answer": True,
                        "query_timestamp": datetime.now().isoformat()
                    }
            
            st.session_state.submit_clicked = False
        else:
            st.warning("Please enter a question.")
    
    # Display response
    if st.session_state.response:
        response = st.session_state.response
        
        st.markdown("---")
        
        if response.get("has_answer"):
            # Success response
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown(f"**Answer:**\n\n{response['answer']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Source information
            if response.get("source_url"):
                st.markdown(f"📄 **Source:** [{response['source_url']}]({response['source_url']})")
            
            if response.get("scheme_name"):
                st.markdown(f"🏦 **Scheme:** {response['scheme_name']}")
            
            if response.get("last_updated"):
                st.markdown(f"📅 **Last Updated:** {response['last_updated']}")
        else:
            # Refusal response
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
            
            st.markdown(f'<div class="refusal-box">{message}</div>', unsafe_allow_html=True)
        
        # Timestamp
        if response.get("query_timestamp"):
            st.caption(f"⏱️ Query time: {response['query_timestamp'][:19]}")
    
    # Available schemes section
    with st.expander("📋 Available Schemes"):
        schemes = get_schemes() if api_healthy else []
        
        if schemes:
            for scheme in schemes:
                st.markdown(f"- **{scheme['name']}** ({scheme['category']} - {scheme['sub_category']})")
        else:
            st.info("The following 5 Axis Mutual Fund schemes are available:")
            demo_schemes = [
                "Axis Silver FoF Direct Growth",
                "Axis Small Cap Fund Direct Growth", 
                "Axis Flexi Cap Fund Direct Growth",
                "Axis Gold Fund Direct Growth",
                "Axis Nifty India Defence Index Fund Direct Growth"
            ]
            for scheme in demo_schemes:
                st.markdown(f"- {scheme}")
    
    # Footer
    st.markdown(
        '<div class="footer">'
        '🤖 Powered by RAG + Groq LLM | '
        '📊 Data source: Groww'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
