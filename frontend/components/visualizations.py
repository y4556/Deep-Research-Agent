import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from typing import List, Dict
import pandas as pd

def create_network_graph(connections: List[Dict] = None) -> go.Figure:
    """
    Create an interactive network graph visualization of connections
    """
    if not connections:
        # Create a placeholder graph
        fig = go.Figure()
        fig.add_annotation(
            text="No connection data available yet.<br>Connections will appear here once research is complete.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Connection Network Map",
            height=500,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Create NetworkX graph
    G = nx.Graph()
    
    # Add nodes and edges
    for conn in connections:
        source = conn.get("source", "Unknown")
        target = conn.get("target", "Unknown")
        strength = conn.get("strength", 0.5)
        relationship = conn.get("relationship", "unknown")
        
        G.add_node(source)
        G.add_node(target)
        G.add_edge(source, target, weight=strength, relationship=relationship)
    
    # Calculate layout
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Create edge traces
    edge_traces = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = edge[2].get('weight', 0.5)
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=weight*5, color='#888'),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        # Calculate node size based on degree (number of connections)
        degree = G.degree(node)
        node_size.append(20 + degree * 5)
        
        # Create hover text
        connections_list = [f"{neighbor} ({G[node][neighbor].get('relationship', 'unknown')})" 
                           for neighbor in G.neighbors(node)]
        hover_text = f"<b>{node}</b><br>Connections: {degree}<br>" + "<br>".join(connections_list[:5])
        node_text.append(hover_text)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[node[:15] + "..." if len(node) > 15 else node for node in G.nodes()],
        hovertext=node_text,
        textposition="top center",
        marker=dict(
            size=node_size,
            color='#1f77b4',
            line=dict(width=2, color='white')
        ),
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    fig.update_layout(
        title="Connection Network Map",
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0,l=0,r=0,t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    
    return fig


def create_risk_chart(risks: List[Dict] = None) -> go.Figure:
    """
    Create a risk distribution chart
    """
    if not risks:
        # Create placeholder
        fig = go.Figure()
        fig.add_annotation(
            text="No risk data available yet.<br>Risk assessment will appear here once complete.",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            title="Risk Assessment Distribution",
            height=400
        )
        return fig
    
    # Count risks by severity
    severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    
    for risk in risks:
        severity = risk.get("severity", "").title()
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    # Create bar chart
    colors = {
        "Critical": "#ff4444",
        "High": "#ff8800",
        "Medium": "#ffcc00",
        "Low": "#00cc00"
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(severity_counts.keys()),
            y=list(severity_counts.values()),
            marker_color=[colors[sev] for sev in severity_counts.keys()],
            text=list(severity_counts.values()),
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Risk Distribution by Severity",
        xaxis_title="Severity Level",
        yaxis_title="Number of Risks",
        height=400,
        showlegend=False
    )
    
    return fig


def create_confidence_distribution(facts: List[Dict] = None) -> go.Figure:
    """
    Create a confidence score distribution chart
    """
    if not facts:
        # Placeholder
        return px.bar(
            x=["High (>80%)", "Medium (60-80%)", "Low (<60%)"],
            y=[0, 0, 0],
            title="Fact Confidence Distribution",
            labels={"x": "Confidence Level", "y": "Number of Facts"}
        )
    
    # Categorize facts by confidence
    high_conf = sum(1 for f in facts if f.get("confidence", 0) >= 0.8)
    medium_conf = sum(1 for f in facts if 0.6 <= f.get("confidence", 0) < 0.8)
    low_conf = sum(1 for f in facts if f.get("confidence", 0) < 0.6)
    
    fig = go.Figure(data=[
        go.Bar(
            x=["High (≥80%)", "Medium (60-80%)", "Low (<60%)"],
            y=[high_conf, medium_conf, low_conf],
            marker_color=["#00cc00", "#ffcc00", "#ff4444"],
            text=[high_conf, medium_conf, low_conf],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Fact Confidence Distribution",
        xaxis_title="Confidence Level",
        yaxis_title="Number of Facts",
        height=400,
        showlegend=False
    )
    
    return fig


def create_timeline_visualization(facts: List[Dict] = None) -> go.Figure:
    """
    Create a timeline of events/facts
    """
    if not facts:
        fig = go.Figure()
        fig.add_annotation(
            text="No timeline data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        fig.update_layout(title="Research Timeline", height=300)
        return fig
    
    # Extract dates/years from facts
    timeline_data = []
    for fact in facts:
        # Simple year extraction (you can enhance this)
        content = fact.get("content", "")
        import re
        years = re.findall(r'\b(19|20)\d{2}\b', content)
        
        if years:
            timeline_data.append({
                "year": int(years[0]),
                "content": content[:100] + "..." if len(content) > 100 else content,
                "category": fact.get("category", "general")
            })
    
    if not timeline_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No dated events found",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        fig.update_layout(title="Event Timeline", height=300)
        return fig
    
    # Sort by year
    timeline_data.sort(key=lambda x: x["year"])
    
    # Create scatter plot
    df = pd.DataFrame(timeline_data)
    
    fig = px.scatter(
        df,
        x="year",
        y=[1] * len(df),  # Same y-value for all points
        hover_data=["content"],
        color="category",
        title="Event Timeline",
        labels={"year": "Year"}
    )
    
    fig.update_traces(marker=dict(size=15))
    fig.update_layout(
        height=300,
        yaxis=dict(visible=False),
        showlegend=True
    )
    
    return fig


def create_category_breakdown(facts: List[Dict] = None) -> go.Figure:
    """
    Create a pie chart showing facts by category
    """
    if not facts:
        return px.pie(
            values=[1],
            names=["No data"],
            title="Facts by Category"
        )
    
    # Count facts by category
    category_counts = {}
    for fact in facts:
        category = fact.get("category", "general").title()
        category_counts[category] = category_counts.get(category, 0) + 1
    
    fig = px.pie(
        values=list(category_counts.values()),
        names=list(category_counts.keys()),
        title="Facts by Category"
    )
    
    fig.update_layout(height=400)
    
    return fig


def create_source_credibility_chart(facts: List[Dict] = None) -> go.Figure:
    """
    Create a chart showing source credibility distribution
    """
    if not facts:
        return px.bar(
            x=["High", "Medium", "Low"],
            y=[0, 0, 0],
            title="Source Credibility Distribution"
        )
    
    # Count facts with verified sources
    verified = sum(1 for f in facts if f.get("verified", False))
    unverified = len(facts) - verified
    
    fig = go.Figure(data=[
        go.Bar(
            x=["Verified", "Unverified"],
            y=[verified, unverified],
            marker_color=["#00cc00", "#ff8800"],
            text=[verified, unverified],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Source Verification Status",
        xaxis_title="Status",
        yaxis_title="Number of Facts",
        height=400,
        showlegend=False
    )
    
    return fig

