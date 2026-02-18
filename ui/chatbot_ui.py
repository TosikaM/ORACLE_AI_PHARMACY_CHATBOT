"""
ui/chatbot_ui.py - Enhanced with detailed model and quota tracking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.settings

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
    
    # Current Active Configuration
    st.subheader("🎯 Currently Active")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Key", f"#{status['current_key']}")
    with col2:
        st.metric("Total Keys", status['total_keys'])
    
    st.info(f"**Model:** {status['current_model']}")
    
    st.divider()
    
    # Overall Statistics
    st.subheader("📈 Overall Statistics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Requests", status['total_requests'])
        st.metric("Successful", status['successful_requests'], 
                 delta=None if status['total_requests'] == 0 else f"{status['success_rate']:.0f}%")
    with col2:
        st.metric("Failed", status['failed_requests'])
        st.metric("Failovers", status['failover_count'])
    
    # Progress bar showing working combinations
    working = status['working_combinations']
    total = status['total_combinations']
    quota_exceeded = status['quota_exceeded_combinations']
    
    st.progress(working / total if total > 0 else 0)
    st.caption(f"Working: {working}/{total} combinations")
    
    st.divider()
    
    # Detailed Model Status
    st.subheader("🔍 Detailed Model Status")
    
    # Get detailed status from smart_client
    combo_status = smart_client.combination_status
    
    # Group by API key
    for key_idx in range(status['total_keys']):
        key_num = key_idx + 1
        
        with st.expander(f"🔑 API Key #{key_num}", expanded=(key_num == status['current_key'])):
            
            for model in smart_client.models:
                combo_key = f"key_{key_num}_{model}"
                combo_data = combo_status[combo_key]
                
                model_status = combo_data['status']
                success_count = combo_data['success_count']
                failure_count = combo_data['failure_count']
                
                # Show model name
                model_short = model.replace('models/', '')
                
                # Status indicator
                if model_status == 'working':
                    status_icon = "✅"
                    status_text = "WORKING"
                    status_color = "green"
                elif model_status == 'quota_exceeded':
                    status_icon = "🚫"
                    status_text = "QUOTA LIMIT"
                    status_color = "red"
                elif model_status == 'untested':
                    status_icon = "❓"
                    status_text = "NOT TESTED YET"
                    status_color = "gray"
                else:
                    status_icon = "⚠️"
                    status_text = "ERROR"
                    status_color = "orange"
                
                # Display model info
                if key_num == status['current_key'] and model == status['current_model']:
                    st.markdown(f"**{status_icon} {model_short}** 🎯 **(ACTIVE NOW)**")
                else:
                    st.markdown(f"{status_icon} **{model_short}**")
                
                # Status badge
                if status_color == "green":
                    st.success(f"Status: {status_text}")
                elif status_color == "red":
                    st.error(f"Status: {status_text}")
                elif status_color == "orange":
                    st.warning(f"Status: {status_text}")
                else:
                    st.info(f"Status: {status_text}")
                
                # Usage stats
                if success_count > 0 or failure_count > 0:
                    st.caption(f"✅ Successful: {success_count} | ❌ Failed: {failure_count}")
                
                # Last activity
                if combo_data['last_success']:
                    st.caption(f"Last success: {combo_data['last_success'].strftime('%H:%M:%S')}")
                if combo_data['last_failure']:
                    st.caption(f"Last failure: {combo_data['last_failure'].strftime('%H:%M:%S')}")
                
                st.markdown("---")
    
    st.divider()
    
    # Quota Warning
    if quota_exceeded > 0:
        st.warning(f"⚠️ {quota_exceeded} combination(s) at quota limit")
        st.caption("Quota resets daily. SmartClient will automatically rotate to working combinations.")
    elif working == total:
        st.success("✅ All combinations working!")
    
    # Reset button
    if st.button("🔄 Reset SmartClient", use_container_width=True):
        smart_client.reset()
        st.success("SmartClient reset!")
        st.rerun()
    
    st.divider()
    
    # Information
    with st.expander("ℹ️ About Quota Limits"):
        st.markdown("""
        **How Quotas Work:**
        - Each API key has daily request limits
        - Free tier: ~15 requests/minute per key
        - When quota exceeded, SmartClient automatically switches to next key
        - Quotas reset at midnight Pacific Time
        
        **What You're Seeing:**
        - ✅ **WORKING**: Model is available and responding
        - 🚫 **QUOTA LIMIT**: This combination hit its daily limit
        - ❓ **NOT TESTED**: Haven't tried this combination yet
        - ⚠️ **ERROR**: Some other error occurred
        
        **Note:** Google doesn't provide exact quota numbers, only errors when limit is reached.
        """)

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your pharmacy AI assistant. I can answer questions about medicines, dosages, drug interactions, side effects, and general pharmacy guidance. What would you like to know?"
    }]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about medicines..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and searching database..."):
            try:
                response = rag_engine.generate_response(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
                
            except Exception as e:
                error_msg = f"I apologize, but I encountered an error: {str(e)}\n\nThis might be due to API quota limits. Check the sidebar for status details."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.caption("Pharmacy AI Chatbot | Powered by Oracle Autonomous Database + Google Gemini + SmartClient Failover")
