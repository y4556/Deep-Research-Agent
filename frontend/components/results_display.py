import streamlit as st
import time
from datetime import datetime
import json

def results_display_component(api_client, session_id: str):
    """
    Component for displaying live research results
    """
    st.header("📊 Live Research Results")
    
    # Create auto-refresh
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    auto_refresh = st.checkbox("Auto-refresh (every 5 seconds)", value=True)
    
    if auto_refresh and (time.time() - st.session_state.last_refresh > 5):
        st.session_state.last_refresh = time.time()
        st.rerun()
    
    try:
        # Fetch session status
        status = api_client.get_session_status(session_id)
        
        if not status:
            st.warning("Could not retrieve research status. Please check your backend connection.")
            return
        
        # Display status header
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_emoji = {
                "initializing": "🔄",
                "researching": "🔍",
                "completed": "✅",
                "error": "❌",
                "cancelled": "⏹️"
            }.get(status.get("status", "unknown"), "❓")
            
            st.metric(
                "Status",
                f"{status_emoji} {status.get('status', 'Unknown').title()}"
            )
        
        with col2:
            progress = status.get("progress", 0)
            st.metric("Progress", f"{progress:.0f}%")
        
        with col3:
            findings_count = status.get("findings_count", 0)
            st.metric("Facts Found", findings_count, delta=None)
        
        with col4:
            risks_count = status.get("risks_identified", 0)
            risk_delta_color = "off" if risks_count == 0 else "normal"
            st.metric("Risks Identified", risks_count, delta_color=risk_delta_color)
        
        # Progress bar
        if status.get("status") in ["initializing", "researching"]:
            st.progress(progress / 100 if progress > 0 else 0.1)
        
        # Current step
        if status.get("current_step"):
            st.info(f"Current Step: **{status['current_step'].replace('_', ' ').title()}**")
        
        st.markdown("---")
        
        # Fetch full report if completed
        if status.get("status") == "completed":
            try:
                report = api_client.get_research_report(session_id)
                display_complete_report(report)
            except Exception as e:
                st.error(f"Error loading complete report: {str(e)}")
                # Show what we have from status
                display_partial_results(status)
        
        elif status.get("status") in ["researching", "initializing"]:
            # Show partial/live results
            st.subheader("🔄 Research in Progress...")
            display_partial_results(status)
            
            # Show spinning indicator
            with st.spinner("Researching..."):
                time.sleep(1)
        
        elif status.get("status") == "error":
            st.error("❌ Research encountered an error")
            if status.get("error"):
                st.exception(status["error"])
        
        elif status.get("status") == "cancelled":
            st.warning("⏹️ Research was cancelled")
    
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.exception(e)


def display_complete_report(report: dict):
    """Display complete research report"""
    st.success("✅ Research Complete!")
    
    # Executive Summary
    st.subheader("📋 Executive Summary")
    if report.get("executive_summary"):
        st.markdown(report["executive_summary"])
    else:
        st.info("Executive summary not available")
    
    st.markdown("---")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Key Findings",
        "⚠️ Risk Assessment",
        "🕸️ Connections",
        "📊 Metadata"
    ])
    
    with tab1:
        display_key_findings(report)
    
    with tab2:
        display_risk_assessment(report)
    
    with tab3:
        display_connections(report)
    
    with tab4:
        display_metadata(report)
    
    # Export options
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("📥 Download JSON", use_container_width=True):
            st.download_button(
                label="Download Report (JSON)",
                data=json.dumps(report, indent=2),
                file_name=f"research_report_{report.get('session_id', 'unknown')[:8]}.json",
                mime="application/json"
            )
    
    with col_export2:
        if st.button("📄 Generate PDF", use_container_width=True):
            st.info("PDF generation coming soon")
    
    with col_export3:
        if st.button("📧 Email Report", use_container_width=True):
            st.info("Email functionality coming soon")


def display_key_findings(report: dict):
    """Display key findings section"""
    key_findings = report.get("key_findings", [])
    
    if not key_findings:
        st.info("No key findings available yet")
        return
    
    # Group by category
    findings_by_category = {}
    for finding in key_findings:
        category = finding.get("category", "General")
        if category not in findings_by_category:
            findings_by_category[category] = []
        findings_by_category[category].append(finding)
    
    # Display by category
    for category, findings in findings_by_category.items():
        with st.expander(f"📂 {category.title()} ({len(findings)} facts)", expanded=True):
            for finding in findings[:10]:  # Limit to 10 per category
                confidence = finding.get("confidence", 0)
                verified = finding.get("verified", False)
                
                # Color code by confidence
                if confidence >= 0.8:
                    confidence_color = "🟢"
                elif confidence >= 0.6:
                    confidence_color = "🟡"
                else:
                    confidence_color = "🔴"
                
                verified_badge = "✓ Verified" if verified else "⚠ Unverified"
                
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <p style="margin: 0;"><strong>{finding.get('content', 'N/A')}</strong></p>
                    <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #666;">
                        {confidence_color} Confidence: {confidence:.2%} | {verified_badge}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show sources
                if finding.get("sources"):
                    with st.expander("Sources"):
                        for source in finding["sources"][:3]:
                            st.caption(f"🔗 {source}")


def display_risk_assessment(report: dict):
    """Display risk assessment section"""
    risk_assessment = report.get("risk_assessment", {})
    
    if not risk_assessment:
        st.info("No risk assessment available yet")
        return
    
    # Overall risk level
    overall_risk = risk_assessment.get("overall_risk_level", "unknown")
    risk_colors = {
        "critical": ("🔴", "#ff4444"),
        "high": ("🟠", "#ff8800"),
        "medium": ("🟡", "#ffcc00"),
        "low": ("🟢", "#00cc00"),
        "unknown": ("⚪", "#999999")
    }
    
    risk_emoji, risk_color = risk_colors.get(overall_risk, risk_colors["unknown"])
    
    st.markdown(f"""
    <div style="background-color: {risk_color}22; padding: 20px; border-radius: 10px; border-left: 5px solid {risk_color};">
        <h3>Overall Risk Level: {risk_emoji} {overall_risk.upper()}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display risks by severity
    for severity in ["critical_risks", "high_risks", "medium_risks", "low_risks"]:
        risks = risk_assessment.get(severity, [])
        
        if risks:
            severity_name = severity.replace("_risks", "").title()
            severity_emoji = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢"
            }.get(severity_name, "⚪")
            
            with st.expander(f"{severity_emoji} {severity_name} Risks ({len(risks)})", 
                           expanded=(severity in ["critical_risks", "high_risks"])):
                for risk in risks:
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 10px; border-left: 3px solid {risk_colors.get(risk.get('severity', 'low'), risk_colors['low'])[1]};">
                        <h4 style="margin: 0 0 10px 0;">{risk.get('type', 'Unknown').replace('_', ' ').title()}</h4>
                        <p style="margin: 0 0 10px 0;">{risk.get('description', 'No description available')}</p>
                        <p style="margin: 0; font-size: 0.85em; color: #666;">
                            Confidence: {risk.get('confidence', 0):.0%} | Impact: {risk.get('impact', 'Unknown')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show evidence
                    if risk.get("evidence"):
                        with st.expander("Evidence"):
                            for evidence in risk["evidence"][:5]:
                                st.caption(f"• {evidence}")


def display_connections(report: dict):
    """Display connection network"""
    connections = report.get("connection_network", [])
    
    if not connections:
        st.info("No connections mapped yet")
        return
    
    st.markdown(f"**Total Connections Mapped:** {len(connections)}")
    
    # Group by relationship type
    by_relationship = {}
    for conn in connections:
        rel_type = conn.get("relationship", "unknown")
        if rel_type not in by_relationship:
            by_relationship[rel_type] = []
        by_relationship[rel_type].append(conn)
    
    # Display by relationship type
    for rel_type, conns in by_relationship.items():
        with st.expander(f"🔗 {rel_type.title()} Connections ({len(conns)})", expanded=True):
            for conn in conns[:15]:  # Limit display
                strength = conn.get("strength", 0)
                strength_bar = "█" * int(strength * 10) + "░" * (10 - int(strength * 10))
                
                st.markdown(f"""
                **{conn.get('source', 'Unknown')}** → **{conn.get('target', 'Unknown')}**
                
                Strength: {strength_bar} ({strength:.0%})
                """)
                
                if conn.get("evidence"):
                    with st.expander("Evidence"):
                        for evidence in conn["evidence"][:3]:
                            st.caption(f"• {evidence}")
                
                st.markdown("---")


def display_metadata(report: dict):
    """Display research metadata"""
    metadata = report.get("research_metadata", {})
    
    if not metadata:
        st.info("No metadata available")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Research Statistics")
        st.metric("Research Depth", metadata.get("research_depth", "N/A"))
        st.metric("Total Queries", metadata.get("total_queries_executed", "N/A"))
        st.metric("Facts Discovered", metadata.get("total_facts_discovered", "N/A"))
        st.metric("Verified Facts", metadata.get("total_verified_facts", "N/A"))
    
    with col2:
        st.subheader("Quality Metrics")
        st.metric("Connections Mapped", metadata.get("total_connections", "N/A"))
        st.metric("Risks Identified", metadata.get("total_risks", "N/A"))
        avg_conf = metadata.get("average_confidence")
        if avg_conf:
            st.metric("Average Confidence", f"{avg_conf:.0%}")
        high_conf = metadata.get("high_confidence_facts")
        if high_conf:
            st.metric("High Confidence Facts", high_conf)
    
    # Timing information
    st.subheader("Timing")
    col_time1, col_time2 = st.columns(2)
    
    with col_time1:
        if metadata.get("start_time"):
            st.text(f"Started: {metadata['start_time']}")
    
    with col_time2:
        if metadata.get("completion_time"):
            st.text(f"Completed: {metadata['completion_time']}")
    
    # Confidence assessment
    if report.get("confidence_assessment"):
        st.subheader("Confidence Assessment")
        conf = report["confidence_assessment"]
        
        col_conf1, col_conf2, col_conf3 = st.columns(3)
        
        with col_conf1:
            st.metric("Average Confidence", f"{conf.get('average_confidence', 0):.0%}")
        
        with col_conf2:
            st.metric("Verified Ratio", f"{conf.get('verified_ratio', 0):.0%}")
        
        with col_conf3:
            st.metric("High Confidence Ratio", f"{conf.get('high_confidence_ratio', 0):.0%}")


def display_partial_results(status: dict):
    """Display partial results while research is ongoing"""
    st.info("Research is still in progress. Partial results will be shown here.")
    
    # Show any available preliminary data
    if status.get("findings_count", 0) > 0:
        st.markdown(f"**Preliminary findings:** {status['findings_count']} facts discovered so far")
    
    if status.get("risks_identified", 0) > 0:
        st.markdown(f"**Preliminary risks:** {status['risks_identified']} potential risks identified")
    
    # Show progress indicator
    st.markdown("""
    **Research Process:**
    1. ✅ Planning research strategy
    2. 🔄 Generating search queries
    3. ⏳ Executing deep searches
    4. ⏳ Extracting facts
    5. ⏳ Validating sources
    6. ⏳ Mapping connections
    7. ⏳ Assessing risks
    8. ⏳ Synthesizing report
    """)

