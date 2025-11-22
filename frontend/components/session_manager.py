import streamlit as st
from typing import List, Dict
import pandas as pd

def session_manager_component(api_client):
    """
    Component for managing research sessions
    """
    try:
        # Fetch all sessions
        sessions = api_client.list_sessions()
        
        if not sessions:
            st.info("No active sessions")
            return
        
        # Display session count
        st.metric("Total Sessions", len(sessions))
        
        # Create DataFrame for display
        session_data = []
        for session in sessions:
            session_data.append({
                "ID": session.get("session_id", "")[:8] + "...",
                "Target": session.get("target_entity", "Unknown"),
                "Status": session.get("status", "unknown").title(),
                "Progress": f"{session.get('progress', 0):.0f}%"
            })
        
        df = pd.DataFrame(session_data)
        
        # Display sessions as table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Session actions
        if sessions:
            selected_session_display = st.selectbox(
                "Select Session",
                options=[f"{s.get('target_entity', 'Unknown')} ({s.get('session_id', '')[:8]}...)" 
                        for s in sessions]
            )
            
            # Extract session ID
            if selected_session_display:
                session_idx = [f"{s.get('target_entity', 'Unknown')} ({s.get('session_id', '')[:8]}...)" 
                              for s in sessions].index(selected_session_display)
                selected_session_id = sessions[session_idx].get("session_id")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("View", use_container_width=True):
                        st.session_state.current_session_id = selected_session_id
                        st.success("Session loaded! Check Live Results tab")
                
                with col2:
                    if st.button("Cancel", use_container_width=True):
                        try:
                            api_client.cancel_research(selected_session_id)
                            st.success("Session cancelled")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error cancelling: {e}")
                
                with col3:
                    if st.button("Delete", use_container_width=True):
                        st.warning("Delete functionality coming soon")
    
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

