"""
Streamlit App for Axis Mutual Fund FAQ Assistant
Combines backend RAG pipeline with frontend chat interface
"""

import streamlit as st
import sys
import os

# Page configuration
st.set_page_config(
    page_title="Axis Mutual Fund FAQ",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for exact local frontend styling
st.markdown("""
<style>
    /* Import Hanken Grotesk font */
    @import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background-color: #0A0A0A;
        font-family: 'Hanken Grotesk', sans-serif;
    }
    
    /* Sidebar styling */
    .stSidebar {
        background-color: #131313;
        border-right: 1px solid #494455;
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #7c4dff;
        color: white;
        border: none;
        border-radius: 16px;
        padding: 8px 16px;
        font-family: 'Hanken Grotesk', sans-serif;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.2s;
        box-shadow: 0 0 15px rgba(124, 77, 255, 0.3);
    }
    
    .stButton>button:hover {
        background-color: #6833ea;
        opacity: 0.9;
    }
    
    /* Input styling */
    .stChatInput {
        background-color: #131313;
        border: 1px solid #494455;
        border-radius: 12px;
        padding: 12px 16px;
        color: #e5e2e1;
        font-family: 'Hanken Grotesk', sans-serif;
    }
    
    .stChatInput:focus {
        border-color: #7c4dff;
        outline: none;
        box-shadow: 0 0 0 2px rgba(124, 77, 255, 0.3);
    }
    
    /* Title styling */
    h1 {
        color: #cdbdff;
        font-family: 'Hanken Grotesk', sans-serif;
        font-weight: 600;
    }
    
    /* Text styling */
    p, .stMarkdown {
        color: #e5e2e1;
        font-family: 'Hanken Grotesk', sans-serif;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #131313;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #494455;
        border-radius: 10px;
    }
</style>

<script>
    // Auto-scroll to bottom when new messages are added
    function scrollToBottom() {
        const chatContainer = document.querySelector('.stChatMessageContainer');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }
    
    // Scroll to bottom on page load
    window.onload = scrollToBottom;
    
    // Scroll to bottom after each render
    setTimeout(scrollToBottom, 100);
</script>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
        <div style="width: 40px; height: 40px; background-color: #7c4dff; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 24px;">🏦</span>
        </div>
        <div>
            <h2 style="margin: 0; color: #7c4dff; font-size: 16px;">Axis Mutual Fund FAQ</h2>
            <p style="margin: 0; color: #e5e2e1; font-size: 12px; opacity: 0.7;">Verified Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Schemes")
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
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("Powered by RAG + Groq LLM", unsafe_allow_html=True)

# Main chat interface
st.title("Axis Mutual Fund FAQ Assistant")
st.markdown("Ask me anything about Axis mutual fund schemes including expense ratios, NAV, exit loads, and more.")

# Try to initialize RAG pipeline first
rag_available = False
rag_error = None
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Create log directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), 'logs', 'phase4')
    os.makedirs(log_dir, exist_ok=True)
    
    # Check if vector database exists
    vector_db_path = os.path.join(os.path.dirname(__file__), 'data', 'vector_db', 'chroma_db')
    if not os.path.exists(vector_db_path):
        rag_error = "Vector database not found. Please ensure data/vector_db/chroma_db exists."
        st.warning(rag_error)
        st.info("The app is running in demo mode. Vector database is required for RAG functionality.")
    else:
        from rag_pipeline import RAGPipeline
        from groq_client import GroqClient
        
        if "rag_pipeline" not in st.session_state:
            with st.spinner("Initializing RAG Pipeline..."):
                st.session_state.rag_pipeline = RAGPipeline()
        rag_available = True
        
except ImportError as e:
    rag_error = f"Missing dependency: {str(e)}"
    st.warning(rag_error)
    st.info("The app is running in demo mode. Please ensure all RAG dependencies are installed.")
except Exception as e:
    rag_error = f"RAG Pipeline error: {str(e)}"
    st.warning(rag_error)
    st.info("The app is running in demo mode. Full RAG functionality requires additional dependencies.")

# Function to generate response (used by both example prompts and chat input)
def generate_response(prompt):
    """Generate response for a given prompt"""
    if rag_available:
        try:
            response = st.session_state.rag_pipeline.query(prompt)
            
            if response.has_answer:
                answer = response.answer
                if response.source_url:
                    answer += f"\n\n📄 Source: {response.source_url}"
                if response.scheme_name:
                    answer += f"\n🏦 Scheme: {response.scheme_name}"
                if response.last_updated:
                    answer += f"\n📅 Last Updated: {response.last_updated}"
            else:
                answer = response.answer
            
            return answer
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            return error_msg
    else:
        # Demo mode response
        return "⚠️ **RAG Pipeline Not Available**\n\nThe full RAG functionality requires additional dependencies (sentence-transformers, chromadb, groq). Please add these to the requirements file and redeploy the app."

# Example prompts (like local frontend)
example_prompts = [
    "What is the expense ratio of Axis Flexi Cap Fund?",
    "What is the NAV of Axis Small Cap Fund?",
    "What is the exit load of Axis Gold Fund?",
    "What is the AUM of Axis Silver FoF?"
]

# Display example prompts (always visible at bottom like local version)
st.markdown("### Quick Questions")
cols = st.columns(2)
for i, prompt in enumerate(example_prompts):
    col_idx = i % 2
    with cols[col_idx]:
        if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Generate and add assistant response
            response = generate_response(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            st.rerun()

# Display chat messages with custom HTML to match local frontend exactly
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
            <div style="background-color: #2a2a2a; border-radius: 16px; border-top-right-radius: 0; padding: 16px; max-width: 600px; color: #e5e2e1;">
                <p style="margin: 0; font-family: 'Hanken Grotesk', sans-serif; font-size: 16px; line-height: 24px;">{message['content']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background-color: #7c4dff; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 18px;">🏦</span>
                </div>
                <span style="font-family: 'Hanken Grotesk', sans-serif; font-size: 14px; font-weight: 500; color: #e5e2e1;">Axis Mutual Fund FAQ Assistant</span>
            </div>
            <div style="background: rgba(30, 30, 30, 0.7); backdrop-filter: blur(20px); border: 1px solid rgba(46, 46, 46, 1); border-left: 4px solid #40e56c; border-radius: 16px; border-top-left-radius: 0; padding: 16px; max-width: 800px; color: #e5e2e1;">
                <p style="margin: 0 0 16px 0; font-family: 'Hanken Grotesk', sans-serif; font-size: 16px; line-height: 24px;">{message['content']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask about Axis Mutual Fund schemes..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Generate response
    response = generate_response(prompt)
    
    # Add assistant message to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()
