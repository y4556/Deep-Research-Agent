import streamlit as st
import requests
import time
import json
import logging
from datetime import datetime
from utils.api_client import ResearchAPIClient
from utils.pdf_generator import generate_pdf_report

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Deep Research AI Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .log-container {
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        height: 400px;
        overflow-y: auto;
        margin: 20px 0;
    }
    .log-line {
        margin: 5px 0;
        line-height: 1.4;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .status-researching {
        background-color: #ffa50066;
        color: #ff8800;
    }
    .status-completed {
        background-color: #00cc0066;
        color: #00cc00;
    }
    .status-error {
        background-color: #ff444466;
        color: #ff4444;
    }
    .report-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize API client
    api_client = ResearchAPIClient()
    
    # Initialize session state
    if 'target_entity' not in st.session_state:
        st.session_state.target_entity = ""
    if 'current_session_id' not in st.session_state:
        st.session_state.current_session_id = None
    if 'research_status' not in st.session_state:
        st.session_state.research_status = None
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    
    # Session recovery in sidebar
    with st.sidebar:
        st.markdown("### 🔄 Resume Session")
        session_id_input = st.text_input("Enter Session ID", placeholder="e.g., abc123...")
        if st.button("Load Session", use_container_width=True):
            if session_id_input:
                st.session_state.current_session_id = session_id_input
                st.rerun()
    
    # Header
    st.markdown('<div class="main-header">🔍 Deep Research AI Agent</div>', unsafe_allow_html=True)
    st.markdown("**Comprehensive Due Diligence Research powered by AI**")
    st.markdown("---")
    
    # === INPUT SECTION ===
    col_input1, col_input2 = st.columns([3, 1])
    
    with col_input1:
        target_entity = st.text_input(
            "Target Entity (Person or Organization)",
            value=st.session_state.target_entity,
            placeholder="e.g., Timothy Overturf, John Smith - CEO of TechCorp",
            disabled=st.session_state.current_session_id is not None
        )
    
    with col_input2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Start Research", type="primary", use_container_width=True, 
                     disabled=st.session_state.current_session_id is not None):
            if target_entity and len(target_entity.strip()) >= 3:
                with st.spinner("Initiating research..."):
                    try:
                        request_data = {
                            "target_entity": target_entity,
                            "max_depth": 3,
                            "research_focus": None,
                            "additional_context": {}
                        }
                        response = api_client.start_research(request_data)
                        
                        if response and response.get("session_id"):
                            st.session_state.current_session_id = response["session_id"]
                            st.session_state.target_entity = target_entity
                            st.session_state.logs = [f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Research initiated for: {target_entity}"]
                            st.success(f"✅ Research started! Session: {response['session_id'][:8]}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to start research")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a valid target entity (at least 3 characters)")
    
    # === LIVE RESULTS SECTION ===
    if st.session_state.current_session_id:
        st.markdown("---")
        
        # Auto-refresh toggle
        col_toggle1, col_toggle2, col_toggle3 = st.columns([2, 1, 1])
        with col_toggle1:
            st.session_state.auto_refresh = st.checkbox("🔄 Auto-refresh (every 3 seconds)", value=st.session_state.auto_refresh)
        
        with col_toggle2:
            if st.button("🔄 Refresh Now", use_container_width=True):
                st.rerun()
        
        with col_toggle3:
            if st.button("⏹️ New Research", use_container_width=True):
                st.session_state.current_session_id = None
                st.session_state.research_status = None
                st.session_state.logs = []
                st.session_state.target_entity = ""
                st.rerun()
        
        # Fetch current status
        try:
            status = api_client.get_session_status(st.session_state.current_session_id)
            
            if status:
                st.session_state.research_status = status
                
                # Status header
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    status_text = status.get('status', 'unknown').upper()
                    status_class = f"status-{status.get('status', 'unknown')}"
                    st.markdown(f'<span class="status-badge {status_class}">{status_text}</span>', unsafe_allow_html=True)
                
                with col_s2:
                    st.metric("Progress", f"{status.get('progress', 0):.0f}%")
                
                with col_s3:
                    st.metric("Facts Found", status.get('findings_count', 0))
                
                with col_s4:
                    st.metric("Risks Identified", status.get('risks_identified', 0))
                
                # Progress bar
                if status.get('status') in ['researching', 'initializing']:
                    progress = status.get('progress', 0) / 100
                    st.progress(progress if progress > 0 else 0.1)
                
                # Current step
                if status.get('current_step'):
                    step_name = status['current_step'].replace('_', ' ').title()
                    st.info(f"**Current Step:** {step_name}")
                
                # === LIVE LOGS SECTION ===
                st.subheader("📋 Live Backend Logs")
                
                # Fetch REAL backend logs
                try:
                    logs_response = api_client.get_session_logs(st.session_state.current_session_id, last_n=50)
                    
                    if logs_response and logs_response.get('logs'):
                        backend_logs = logs_response['logs']
                        
                        # Display logs
                        log_html = '<div class="log-container">'
                        for log in backend_logs:
                            log_html += f'<div class="log-line">{log}</div>'
                        log_html += '</div>'
                        st.markdown(log_html, unsafe_allow_html=True)
                    else:
                        # Fallback to simple messages if logs not available
                        current_step = status.get('current_step', '')
                        st.info(f"Backend is working on: {current_step.replace('_', ' ').title()}" if current_step else "Initializing...")
                
                except Exception as log_error:
                    # Fallback display
                    logger.warning(f"Could not fetch logs: {log_error}")
                    st.info(f"Backend Status: {status.get('status', 'unknown').upper()} - {status.get('current_step', 'processing').replace('_', ' ').title()}")
                
                # === RESULTS DISPLAY ===
                if status.get('status') == 'completed':
                    st.success("✅ **Research Complete!**")
                    
                    try:
                        report = api_client.get_research_report(st.session_state.current_session_id)
                        
                        if report:
                            # Display quick summary
                            st.markdown("---")
                            st.subheader("📊 Research Summary")
                            
                            col_sum1, col_sum2, col_sum3 = st.columns(3)
                            
                            with col_sum1:
                                total_facts = len(report.get('key_findings', []))
                                st.metric("Total Facts", total_facts)
                            
                            with col_sum2:
                                risk_level = report.get('risk_assessment', {}).get('overall_risk_level', 'unknown').upper()
                                st.metric("Risk Level", risk_level)
                            
                            with col_sum3:
                                connections = len(report.get('connection_network', []))
                                st.metric("Connections Mapped", connections)
                            
                            # Executive Summary
                            st.markdown("---")
                            st.subheader("📋 Executive Summary")
                            st.markdown(report.get('executive_summary', 'No summary available'))
                            
                            # Download button
                            st.markdown("---")
                            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
                            
                            with col_dl2:
                                if st.button("📥 Download Full Report (PDF)", type="primary", use_container_width=True):
                                    with st.spinner("Generating PDF report..."):
                                        try:
                                            pdf_bytes = generate_pdf_report(report)
                                            
                                            st.download_button(
                                                label="📄 Download Report",
                                                data=pdf_bytes,
                                                file_name=f"research_report_{st.session_state.target_entity.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                                mime="application/pdf",
                                                use_container_width=True
                                            )
                                            st.success("✅ PDF generated successfully!")
                                        except Exception as e:
                                            st.error(f"Error generating PDF: {str(e)}")
                    
                    except Exception as e:
                        st.error(f"Error loading report: {str(e)}")
                
                elif status.get('status') == 'error':
                    st.error("❌ **Research encountered an error**")
                    if status.get('error'):
                        st.exception(status['error'])
                
                # Auto-refresh
                if st.session_state.auto_refresh and status.get('status') in ['researching', 'initializing']:
                    time.sleep(3)
                    st.rerun()
        
        except Exception as e:
            st.error(f"Error fetching status: {str(e)}")
    
    else:
        # Show welcome message
        st.info("👆 Enter a target entity above and click 'Start Research' to begin")
        
        st.markdown("---")
        st.subheader("📊 What You'll Get")
        
        col_feature1, col_feature2, col_feature3 = st.columns(3)
        
        with col_feature1:
            st.markdown("""
            **🔍 Biographical & Professional Details**
            
            Verified personal details, career trajectory, and professional history.
            """)
        
        with col_feature2:
            st.markdown("""
            **🕸️ Connection Mapping**
            
            Structured map of relationships, organizations, and entities.
            """)
        
        with col_feature3:
            st.markdown("""
            **⚠️ Risk Assessment**
            
            Identification of red flags, inconsistencies, and potential risks.
            """)

if __name__ == "__main__":
    main()

