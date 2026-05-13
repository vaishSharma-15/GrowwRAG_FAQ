"""
Streamlit App for Axis Mutual Fund FAQ Assistant
Combines backend RAG pipeline with frontend chat interface
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag_pipeline import RAGPipeline
from groq_client import GroqClient

# Page configuration
st.set_page_config(
    page_title="Axis Mutual Fund FAQ",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        background-color: #1e1e1e;
    }
    .stChatMessage.user {
        background-color: #2a2a2a;
    }
    .stChatMessage.assistant {
        background-color: #1e1e1e;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_pipeline" not in st.session_state:
    with st.spinner("Initializing RAG Pipeline..."):
        st.session_state.rag_pipeline = RAGPipeline()

# Sidebar
with st.sidebar:
    st.title("🏦 Axis Mutual Fund FAQ")
    st.markdown("---")
    
    st.subheader("Supported Schemes")
    schemes = [
        "Axis Flexi Cap Fund",
        "Axis Small Cap Fund",
        "Axis Gold Fund",
        "Axis Silver FoF",
        "Axis Defence Index Fund"
    ]
    
    for scheme in schemes:
        st.markdown(f"• {scheme}")
    
    st.markdown("---")
    st.markdown("⚠️ **Facts-only information.**")
    st.markdown("This system does not provide investment advice.")
    
    st.markdown("---")
    st.markdown("### Quick Actions")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Powered by RAG + Groq LLM")

# Main chat interface
st.title("Axis Mutual Fund FAQ Assistant")
st.markdown("Ask me anything about Axis mutual fund schemes including expense ratios, NAV, exit loads, and more.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about Axis Mutual Fund schemes..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                response = st.session_state.rag_pipeline.query(prompt)
                
                if response.has_answer:
                    answer = response.answer
                    if response.source_url:
                        answer += f"\n\n📄 **Source:** {response.source_url}"
                    if response.scheme_name:
                        answer += f"\n🏦 **Scheme:** {response.scheme_name}"
                    if response.last_updated:
                        answer += f"\n📅 **Last Updated:** {response.last_updated}"
                else:
                    answer = response.answer
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
