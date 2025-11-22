import streamlit as st
from typing import Optional

def research_input_component(api_client, max_depth: int, research_focus: str):
    """
    Component for research input form
    """
    st.header("🚀 Launch New Research")
    st.markdown("Enter the target entity for comprehensive due diligence research.")
    
    # Initialize session state
    if 'target_entity' not in st.session_state:
        st.session_state.target_entity = ""
    if 'research_running' not in st.session_state:
        st.session_state.research_running = False
    
    # Create form
    with st.form("research_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            target_entity = st.text_input(
                "Target Entity (Person or Organization)",
                value=st.session_state.get("target_entity", ""),
                placeholder="e.g., John Smith - Tech Executive, Acme Corporation",
                help="Enter the full name of the person or organization to research"
            )
        
        with col2:
            st.markdown("**Quick Examples**")
            if st.form_submit_button("Timothy Overturf", use_container_width=True):
                st.session_state.target_entity = "Timothy Overturf"
                st.rerun()
        
        # Additional context (optional)
        additional_context = st.text_area(
            "Additional Context (Optional)",
            placeholder="e.g., Former CEO of TechCorp, Based in California, Involved in 2020 merger...",
            help="Provide any additional context that might help focus the research",
            height=100
        )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            col_a1, col_a2 = st.columns(2)
            
            with col_a1:
                custom_depth = st.number_input(
                    "Research Depth",
                    min_value=1,
                    max_value=5,
                    value=max_depth,
                    help="Number of research iterations (higher = more comprehensive but slower)"
                )
            
            with col_a2:
                focus_areas = st.multiselect(
                    "Focus Areas",
                    options=["Financial", "Legal", "Professional", "Personal", "Reputation", "Connections"],
                    default=["Financial", "Legal", "Professional"],
                    help="Select specific areas to focus the research"
                )
            
            include_timeline = st.checkbox("Include Timeline Analysis", value=True)
            include_network_map = st.checkbox("Include Connection Network Map", value=True)
        
        # Submit button
        col_submit1, col_submit2, col_submit3 = st.columns([2, 1, 1])
        
        with col_submit1:
            submit_button = st.form_submit_button(
                "🔍 Start Research",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.research_running
            )
        
        with col_submit2:
            if st.session_state.research_running:
                if st.form_submit_button("⏸️ Pause", use_container_width=True):
                    # Implement pause functionality
                    st.info("Pause functionality coming soon")
        
        with col_submit3:
            if st.session_state.research_running:
                if st.form_submit_button("⏹️ Stop", use_container_width=True):
                    st.session_state.research_running = False
                    st.success("Research stopped")
                    st.rerun()
    
    # Handle form submission
    if submit_button and target_entity:
        if len(target_entity.strip()) < 3:
            st.error("Please enter a valid target entity (at least 3 characters)")
            return
        
        st.session_state.research_running = True
        st.session_state.target_entity = target_entity
        
        # Show loading state
        with st.spinner(f"🔍 Initiating research for: {target_entity}..."):
            try:
                # Prepare request data
                request_data = {
                    "target_entity": target_entity,
                    "max_depth": custom_depth,
                    "research_focus": research_focus.lower() if research_focus != "Comprehensive" else None,
                    "additional_context": {
                        "user_provided_context": additional_context if additional_context else None,
                        "focus_areas": focus_areas if focus_areas else None,
                        "include_timeline": include_timeline,
                        "include_network_map": include_network_map
                    }
                }
                
                # Start research via API
                response = api_client.start_research(request_data)
                
                if response and response.get("session_id"):
                    st.session_state.current_session_id = response["session_id"]
                    st.success(f"✅ Research started! Session ID: {response['session_id'][:8]}...")
                    st.info("Switch to the **Live Results** tab to monitor progress.")
                    
                    # Auto-switch to results tab (if possible)
                    st.balloons()
                else:
                    st.error("Failed to start research. Please try again.")
                    st.session_state.research_running = False
                
            except Exception as e:
                st.error(f"Error starting research: {str(e)}")
                st.session_state.research_running = False
                st.exception(e)
    
    elif submit_button and not target_entity:
        st.warning("⚠️ Please enter a target entity to research")
    
    # Show current status
    if st.session_state.research_running:
        st.info("🔄 Research in progress... Check the **Live Results** tab for updates.")
    
    # Quick tips section
    with st.expander("💡 Research Tips"):
        st.markdown("""
        **For best results:**
        
        1. **Be Specific**: Include full names and context (e.g., "John Smith - CEO of TechCorp" rather than just "John Smith")
        
        2. **Provide Context**: Additional information helps focus the research and improves accuracy
        
        3. **Choose Appropriate Depth**:
           - Depth 1-2: Quick overview (5-10 mins)
           - Depth 3: Standard comprehensive research (15-20 mins)
           - Depth 4-5: Deep investigation (30+ mins)
        
        4. **Focus Areas**: Select specific areas if you have particular concerns (saves time and cost)
        
        5. **Review Carefully**: Always verify critical findings with primary sources
        
        **Note**: Research time and cost increase with depth. Start with depth 2-3 for most use cases.
        """)
    
    # Cost estimate
    with st.expander("💰 Estimated Cost"):
        estimated_queries = custom_depth * 5
        estimated_api_calls = custom_depth * 8
        estimated_cost = estimated_api_calls * 0.02  # Rough estimate
        
        st.markdown(f"""
        **Estimated Research Resources:**
        - Search Queries: ~{estimated_queries}
        - AI Model Calls: ~{estimated_api_calls}
        - Estimated Cost: ${estimated_cost:.2f} - ${estimated_cost * 2:.2f}
        - Estimated Time: {custom_depth * 5}-{custom_depth * 7} minutes
        
        *Actual costs may vary based on result complexity and API pricing*
        """)

