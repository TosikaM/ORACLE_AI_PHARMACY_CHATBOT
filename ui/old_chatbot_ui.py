"""
CRITICAL: Import settings FIRST to load environment variables
before any other modules try to use them
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings FIRST - this loads the .env file
import config.settings

# Now import everything else
import streamlit as st
from chatbot.rag_engine import rag_engine
from chatbot.smart_client import smart_client

st.set_page_config(
    page_title="Pharmacy AI Chatbot",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Pharmacy AI Chatbot")
st.markdown("Your intelligent pharmacy assistant powered by Oracle Cloud + Google Gemini")

with st.sidebar:
    st.header("📊 SmartClient Status")
    
    status = smart_client.get_current_status()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Active Key",
            value=f"#{status['current_key']}",
            help="Which API key is currently being used"
        )
    with col2:
        st.metric(
            label="Total Keys",
            value=status['total_keys'],
            help="Total number of API keys configured"
        )
    
    st.metric(
        label="Current Model",
        value=status['current_model'],
        help="AI model currently in use for generating responses"
    )
    
    st.divider()
    
    st.subheader("Usage Statistics")
    
    st.metric(
        label="Total Requests",
        value=status['total_requests'],
        help="Total number of API requests made"
    )
    
    st.metric(
        label="Success Rate",
        value=f"{status['success_rate']:.1f}%",
        help="Percentage of successful requests"
    )
    
    st.metric(
        label="Failover Count",
        value=status['failover_count'],
        help="How many times SmartClient switched between keys/models"
    )
    
    working = status['working_combinations']
    total = status['total_combinations']
    quota = status['quota_exceeded_combinations']
    
    st.progress(
        working / total if total > 0 else 0,
        text=f"Working: {working}/{total} combinations"
    )
    
    if quota > 0:
        st.warning(f"⚠️ {quota} combinations at quota limit")
    elif working == total:
        st.success("✅ All combinations working!")
    
    if st.button("🔄 Reset SmartClient"):
        smart_client.reset()
        st.success("SmartClient reset to initial state!")
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your pharmacy AI assistant. I can answer questions about medicines, dosages, drug interactions, side effects, storage instructions, and general pharmacy guidance. What would you like to know today?"
    }]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about medicines..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking and searching database..."):
            try:
                response = rag_engine.generate_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                st.rerun()
                
            except Exception as e:
                error_msg = (
                    f"I apologize, but I encountered an error while processing "
                    f"your question. This might be due to API quota limits or "
                    f"connectivity issues.\n\n"
                    f"Error details: {str(e)}\n\n"
                    f"Please try again in a moment, or check the SmartClient "
                    f"status in the sidebar to see if all API keys are exhausted."
                )
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

st.divider()
st.caption(
    "Pharmacy AI Chatbot | "
    "Powered by Oracle Autonomous Database + Google Gemini + SmartClient Failover"
)
