import streamlit as st
import time
from datetime import datetime

def research_input_component(api_client, max_depth, research_focus):
    st.header("🎯 Launch Deep Research Investigation")
    
    # Target entity input
    target_entity = st.text_input(
        "Target Entity",
        value=st.session_state.get('target_entity', ''),
        placeholder="Enter name of person or organization to research...",
        help="Full name of the person or organization you want to investigate"
    )
    
    # Additional context
    with st.expander("🔧 Advanced Research Options"):
        additional_context = st.text_area(
            "Additional Context",
            placeholder="Any specific areas of interest, known associations, or particular risks to focus on...",
            help="Provide any additional context that might help the research"
        )
        
        enable_deep_dive = st.checkbox("Enable Deep Dive Mode", value=True,
                                      help="Allow the agent to conduct additional research iterations for complex cases")
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Start Deep Research", type="primary", use_container_width=True):
            if target_entity:
                start_research(api_client, target_entity, max_depth, research_focus, additional_context)
            else:
                st.error("❌ Please enter a target entity to research")
    
    with col2:
        if st.button("🔄 Quick Scan", use_container_width=True):
            if target_entity:
                start_research(api_client, target_entity, 1, research_focus, additional_context, quick_scan=True)
            else:
                st.error("❌ Please enter a target entity to research")
    
    with col3:
        if st.button("🗑️ Clear Form", use_container_width=True):
            st.session_state.pop('target_entity', None)
            st.rerun()
    
    # Research tips
    with st.expander("💡 Research Tips"):
        st.markdown("""
        **For best results:**
        - Use full names with correct spelling
        - Include relevant context (industry, location, known associations)
        - Be specific about the type of information you're seeking
        - For organizations, include the legal entity name if known
        
        **Example targets:**
        - Timothy Overturf (business executive with complex background)
        - John Doe - Tech Executive at ABC Corporation
        - Acme Corp (manufacturing company with international operations)
        """)

def start_research(api_client, target_entity, max_depth, research_focus, additional_context, quick_scan=False):
    """Start a new research session"""
    try:
        with st.spinner("🚀 Starting deep research investigation..."):
            # Prepare request
            request_data = {
                "target_entity": target_entity,
                "max_depth": 1 if quick_scan else max_depth,
                "research_focus": research_focus
            }
            
            if additional_context:
                request_data["additional_context"] = {
                    "user_context": additional_context,
                    "quick_scan": quick_scan
                }
            
            # Start research session
            response = api_client.start_research(request_data)
            
            if response and "session_id" in response:
                session_id = response["session_id"]
                st.session_state.current_session_id = session_id
                st.session_state.research_start_time = datetime.now()
                
                if quick_scan:
                    st.success(f"✅ Quick scan started! Session ID: {session_id}")
                else:
                    st.success(f"✅ Deep research started! Session ID: {session_id}")
                
                # Show progress
                progress_container = st.container()
                status_text = st.empty()
                
                # Poll for progress
                for i in range(50):  # Max 50 checks
                    status = api_client.get_session_status(session_id)
                    
                    if status:
                        progress = status.get("progress", 0)
                        
                        # Update progress bar
                        progress_container.progress(progress / 100)
                        status_text.text(f"Status: {status['status']} - {progress}% complete")
                        
                        if status['status'] == 'completed':
                            st.session_state.research_report = api_client.get_report(session_id)
                            st.rerun()
                            break
                        elif status['status'] == 'error':
                            st.error(f"❌ Research failed: {status.get('error', 'Unknown error')}")
                            break
                    
                    time.sleep(3)  # Check every 3 seconds
                
            else:
                st.error("❌ Failed to start research session")
                
    except Exception as e:
        st.error(f"❌ Error starting research: {str(e)}")