import streamlit as st
import requests
import time
import json
import plotly.graph_objects as go
import networkx as nx
import pandas as pd
from datetime import datetime

from components.research_input import research_input_component
from components.results_display import results_display_component
from components.visualizations import (
    create_network_graph, 
    create_risk_chart,
    create_confidence_distribution,
    create_category_breakdown,
    create_source_credibility_chart
)
from components.session_manager import session_manager_component
from utils.api_client import ResearchAPIClient

# Page configuration
st.set_page_config(
    page_title="Deep Research AI Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-bottom: 1rem;
    }
    .risk-high { 
        background-color: #ffcccc; 
        padding: 10px; 
        border-radius: 5px; 
        border-left: 5px solid #ff4444;
    }
    .risk-medium { 
        background-color: #fff4cc; 
        padding: 10px; 
        border-radius: 5px; 
        border-left: 5px solid #ffaa00;
    }
    .risk-low { 
        background-color: #ccffcc; 
        padding: 10px; 
        border-radius: 5px; 
        border-left: 5px solid #00cc00;
    }
    .fact-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 10px;
    }
    .connection-node {
        fill: #1f77b4;
        stroke: #fff;
        stroke-width: 2px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Initialize API client
    api_client = ResearchAPIClient()
    
    # Header
    st.markdown('<div class="main-header">Deep Research AI Agent</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Research settings
        max_depth = st.slider("Research Depth", 1, 5, 3, 
                             help="How deep the research should go (more depth = more comprehensive but slower)")
        
        research_focus = st.selectbox(
            "Research Focus",
            ["Comprehensive", "Financial", "Legal", "Professional", "Personal", "Reputation"],
            help="Focus area for the research"
        )
        
        st.markdown("---")
        st.header("Test Personas")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Timothy Overturf", use_container_width=True):
                st.session_state.target_entity = "Timothy Overturf"
                st.session_state.research_focus = "Comprehensive"
                st.rerun()
        
        with col2:
            if st.button("John Doe", use_container_width=True):
                st.session_state.target_entity = "John Doe - Tech Executive"
                st.session_state.research_focus = "Professional"
                st.rerun()
        
        st.markdown("---")
        st.header("📊 Session Management")
        session_manager_component(api_client)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Research Launch", "📈 Live Results", "🔍 Analysis", "📋 Session History"])
    
    with tab1:
        research_input_component(api_client, max_depth, research_focus)
    
    with tab2:
        if 'current_session_id' in st.session_state:
            results_display_component(api_client, st.session_state.current_session_id)
        else:
            st.info("Start a research session to see live results and progress")
            st.image("https://via.placeholder.com/600x300?text=Deep+Research+Analysis", use_column_width=True)
    
    with tab3:
        st.header("Advanced Analysis Tools")
        
        # Try to load current report data
        report_data = None
        if 'current_session_id' in st.session_state:
            try:
                status = api_client.get_session_status(st.session_state.current_session_id)
                if status and status.get("status") == "completed":
                    report_data = api_client.get_research_report(st.session_state.current_session_id)
            except:
                pass
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🕸️ Connection Network")
            connections = report_data.get("connection_network", []) if report_data else None
            network_fig = create_network_graph(connections)
            st.plotly_chart(network_fig, use_container_width=True)
            
            st.subheader("📊 Fact Confidence Distribution")
            facts = report_data.get("key_findings", []) if report_data else None
            conf_fig = create_confidence_distribution(facts)
            st.plotly_chart(conf_fig, use_container_width=True)
        
        with col2:
            st.subheader("⚠️ Risk Assessment")
            risks = []
            if report_data and report_data.get("risk_assessment"):
                risk_assessment = report_data["risk_assessment"]
                risks = (risk_assessment.get("critical_risks", []) +
                        risk_assessment.get("high_risks", []) +
                        risk_assessment.get("medium_risks", []) +
                        risk_assessment.get("low_risks", []))
            risk_fig = create_risk_chart(risks)
            st.plotly_chart(risk_fig, use_container_width=True)
            
            st.subheader("🔍 Source Verification")
            if facts:
                verified = sum(1 for f in facts if f.get("verified", False))
                st.metric("Verified Facts", verified, f"{len(facts) - verified} unverified")
            else:
                st.info("No data available yet")
        
        # Category breakdown
        st.markdown("---")
        st.subheader("📋 Facts by Category")
        if facts:
            cat_fig = create_category_breakdown(facts)
            st.plotly_chart(cat_fig, use_container_width=True)
        else:
            st.info("Complete a research session to see analysis")
    
    with tab4:
        st.header("Research Session History")
        
        try:
            sessions = api_client.list_sessions()
            if sessions:
                sessions_df = pd.DataFrame(sessions)
                st.dataframe(sessions_df, use_container_width=True)
                
                # Session details
                selected_session = st.selectbox(
                    "Select session for details",
                    [s["session_id"] for s in sessions]
                )
                
                if selected_session:
                    session_details = api_client.get_session_status(selected_session)
                    st.json(session_details)
            else:
                st.info("No research sessions yet. Start one in the Research Launch tab.")
                
        except Exception as e:
            st.error(f"Error loading sessions: {e}")

if __name__ == "__main__":
    main()