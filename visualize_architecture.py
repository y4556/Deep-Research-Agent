"""
Architecture Visualization Tool
Generates supplementary architecture diagrams

NOTE: For the actual LangGraph workflow, use visualize_langgraph.py instead!
This file creates additional diagrams for system architecture, model mapping, etc.
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches
from pathlib import Path

# Create output directory
output_dir = Path("architecture_diagrams")
output_dir.mkdir(exist_ok=True)


def create_langgraph_workflow():
    """Create the LangGraph workflow visualization"""
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    nodes = {
        "Start": {"color": "#90EE90", "shape": "circle"},
        "Planner": {"color": "#87CEEB", "shape": "box"},
        "QueryGen": {"color": "#87CEEB", "shape": "box"},
        "SearchExec": {"color": "#DDA0DD", "shape": "box"},
        "FactExtract": {"color": "#F0E68C", "shape": "box"},
        "SourceVal": {"color": "#F0E68C", "shape": "box"},
        "ConnMap": {"color": "#F0E68C", "shape": "box"},
        "RiskAssess": {"color": "#FFA07A", "shape": "box"},
        "Decision": {"color": "#FF6347", "shape": "diamond"},
        "Reflector": {"color": "#98FB98", "shape": "box"},
        "Synthesizer": {"color": "#FFD700", "shape": "box"},
        "End": {"color": "#FFB6C1", "shape": "circle"}
    }
    
    for node, attrs in nodes.items():
        G.add_node(node, **attrs)
    
    # Add edges
    edges = [
        ("Start", "Planner"),
        ("Planner", "QueryGen"),
        ("QueryGen", "SearchExec"),
        ("SearchExec", "FactExtract"),
        ("FactExtract", "SourceVal"),
        ("SourceVal", "ConnMap"),
        ("ConnMap", "RiskAssess"),
        ("RiskAssess", "Decision"),
        ("Decision", "Reflector"),
        ("Decision", "Synthesizer"),
        ("Reflector", "QueryGen"),
        ("Synthesizer", "End")
    ]
    
    G.add_edges_from(edges)
    
    # Create layout
    pos = {
        "Start": (0, 10),
        "Planner": (0, 8.5),
        "QueryGen": (0, 7),
        "SearchExec": (0, 5.5),
        "FactExtract": (0, 4),
        "SourceVal": (0, 2.5),
        "ConnMap": (0, 1),
        "RiskAssess": (0, -0.5),
        "Decision": (0, -2),
        "Reflector": (2.5, -3.5),
        "Synthesizer": (-2.5, -3.5),
        "End": (0, -5)
    }
    
    # Draw
    plt.figure(figsize=(14, 16))
    
    # Draw nodes
    for node, (x, y) in pos.items():
        color = G.nodes[node]["color"]
        shape = G.nodes[node]["shape"]
        
        if shape == "circle":
            circle = plt.Circle((x, y), 0.4, color=color, ec='black', linewidth=2, zorder=2)
            plt.gca().add_patch(circle)
        elif shape == "diamond":
            diamond = mpatches.FancyBboxPatch(
                (x-0.5, y-0.3), 1, 0.6,
                boxstyle="round,pad=0.1",
                facecolor=color, edgecolor='black', linewidth=2, zorder=2
            )
            plt.gca().add_patch(diamond)
        else:  # box
            rect = FancyBboxPatch(
                (x-0.6, y-0.3), 1.2, 0.6,
                boxstyle="round,pad=0.05",
                facecolor=color, edgecolor='black', linewidth=2, zorder=2
            )
            plt.gca().add_patch(rect)
    
    # Draw edges
    for (u, v) in G.edges():
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        
        # Adjust for node sizes
        if v == "QueryGen" and u == "Reflector":
            # Loop back edge
            arrow = FancyArrowPatch(
                (x1-0.6, y1+0.2), (x2+0.6, y2-0.2),
                arrowstyle='->', mutation_scale=20, linewidth=2,
                color='#666', connectionstyle="arc3,rad=.5"
            )
        else:
            # Regular edge
            dy = y2 - y1
            if abs(dy) > 0.6:
                y1_adj = y1 - 0.3 if dy < 0 else y1 + 0.3
                y2_adj = y2 + 0.3 if dy < 0 else y2 - 0.3
            else:
                y1_adj, y2_adj = y1, y2
            
            arrow = FancyArrowPatch(
                (x1, y1_adj), (x2, y2_adj),
                arrowstyle='->', mutation_scale=20, linewidth=2,
                color='#666'
            )
        
        plt.gca().add_patch(arrow)
    
    # Add labels
    labels = {
        "Start": "Start",
        "Planner": "Research\nPlanner",
        "QueryGen": "Query\nGenerator",
        "SearchExec": "Search\nExecutor",
        "FactExtract": "Fact\nExtractor",
        "SourceVal": "Source\nValidator",
        "ConnMap": "Connection\nMapper",
        "RiskAssess": "Risk\nAssessor",
        "Decision": "Continue?",
        "Reflector": "Research\nReflector",
        "Synthesizer": "Report\nSynthesizer",
        "End": "End"
    }
    
    for node, label in labels.items():
        x, y = pos[node]
        plt.text(x, y, label, ha='center', va='center', fontsize=10, fontweight='bold', zorder=3)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='#87CEEB', label='Planning & Query'),
        mpatches.Patch(color='#DDA0DD', label='Search'),
        mpatches.Patch(color='#F0E68C', label='Extraction & Validation'),
        mpatches.Patch(color='#FFA07A', label='Risk Assessment'),
        mpatches.Patch(color='#98FB98', label='Reflection'),
        mpatches.Patch(color='#FFD700', label='Synthesis'),
        mpatches.Patch(color='#FF6347', label='Decision Point'),
    ]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.xlim(-4, 5)
    plt.ylim(-6, 11)
    plt.axis('off')
    plt.title('LangGraph Research Workflow', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(output_dir / 'langgraph_workflow.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'langgraph_workflow.png'}")
    plt.close()


def create_system_architecture():
    """Create overall system architecture diagram"""
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Define components
    components = {
        # Frontend
        "Frontend\n(Streamlit)": (2, 8, 3, 1.5, '#87CEEB'),
        
        # Backend components
        "FastAPI\nREST API": (8, 9, 2.5, 1, '#90EE90'),
        "LangGraph\nWorkflow": (8, 7, 2.5, 1, '#FFD700'),
        "State\nManagement": (8, 5, 2.5, 1, '#F0E68C'),
        
        # Services
        "Multi-Model\nCoordinator": (13, 9, 2.5, 1, '#DDA0DD'),
        "Search\nEngine": (13, 7, 2.5, 1, '#98FB98'),
        "Validation\nService": (13, 5, 2.5, 1, '#FFA07A'),
        "LangSmith\nClient": (13, 3, 2.5, 1, '#FFB6C1'),
        
        # External
        "OpenAI\nGPT-4": (18, 9.5, 2, 0.8, '#E0E0E0'),
        "Anthropic\nClaude": (18, 8.5, 2, 0.8, '#E0E0E0'),
        "Google\nGemini": (18, 7.5, 2, 0.8, '#E0E0E0'),
        "Tavily\nSearch": (18, 6.5, 2, 0.8, '#E0E0E0'),
        "DuckDuckGo": (18, 5.5, 2, 0.8, '#E0E0E0'),
        "LangSmith\nPlatform": (18, 3, 2, 0.8, '#E0E0E0'),
    }
    
    # Draw components
    for name, (x, y, w, h, color) in components.items():
        rect = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor='black', linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, name, ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    # Draw connections
    connections = [
        # Frontend to Backend
        ((5, 8.75), (8, 9.5), "HTTP/REST"),
        
        # Backend internal
        ((10.5, 9.5), (8, 7.5), "Triggers"),
        ((10.5, 7.5), (8, 5.5), "Updates"),
        
        # Backend to Services
        ((10.5, 7.5), (13, 9.5), "Uses"),
        ((10.5, 7.5), (13, 7.5), "Calls"),
        ((10.5, 7.5), (13, 5.5), "Validates"),
        ((10.5, 7.5), (13, 3.5), "Traces"),
        
        # Services to External
        ((15.5, 9.5), (18, 9.9), "API"),
        ((15.5, 9.3), (18, 8.9), "API"),
        ((15.5, 9.1), (18, 7.9), "API"),
        ((15.5, 7.5), (18, 6.9), "API"),
        ((15.5, 7.3), (18, 5.9), "API"),
        ((15.5, 3.5), (18, 3.4), "API"),
    ]
    
    for (x1, y1), (x2, y2), label in connections:
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='->', mutation_scale=15, linewidth=1.5,
            color='#555', alpha=0.7
        )
        ax.add_patch(arrow)
    
    # Add section labels
    ax.text(3.5, 10.5, "FRONTEND", fontsize=14, fontweight='bold', 
            bbox=dict(boxstyle='round', facecolor='#87CEEB', alpha=0.5))
    ax.text(9.25, 11, "BACKEND CORE", fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#90EE90', alpha=0.5))
    ax.text(14.25, 11, "SERVICES", fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#DDA0DD', alpha=0.5))
    ax.text(19, 11, "EXTERNAL", fontsize=14, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#E0E0E0', alpha=0.5))
    
    ax.set_xlim(0, 21)
    ax.set_ylim(2, 12)
    ax.axis('off')
    ax.set_title('Deep Research Agent - System Architecture', 
                 fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'system_architecture.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'system_architecture.png'}")
    plt.close()


def create_node_model_mapping():
    """Create diagram showing which AI model each node uses"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Nodes and their assigned models
    node_model_map = {
        "Research Planner": ("Claude Opus", "#FF6B6B"),
        "Query Generator": ("GPT-4", "#4ECDC4"),
        "Search Executor": ("No AI", "#95E1D3"),
        "Fact Extractor": ("Claude Sonnet", "#F38181"),
        "Source Validator": ("Service Only", "#95E1D3"),
        "Connection Mapper": ("GPT-4", "#4ECDC4"),
        "Risk Assessor": ("Claude Opus", "#FF6B6B"),
        "Research Reflector": ("Gemini Pro", "#FFE66D"),
        "Report Synthesizer": ("Claude Opus", "#FF6B6B"),
    }
    
    y_pos = 9
    for node, (model, color) in node_model_map.items():
        # Node box
        node_rect = FancyBboxPatch(
            (2, y_pos), 4, 0.7,
            boxstyle="round,pad=0.05",
            facecolor='#E8E8E8', edgecolor='black', linewidth=2
        )
        ax.add_patch(node_rect)
        ax.text(4, y_pos + 0.35, node, ha='center', va='center', 
                fontsize=10, fontweight='bold')
        
        # Arrow
        arrow = FancyArrowPatch(
            (6.2, y_pos + 0.35), (8, y_pos + 0.35),
            arrowstyle='->', mutation_scale=20, linewidth=2, color='#666'
        )
        ax.add_patch(arrow)
        
        # Model box
        model_rect = FancyBboxPatch(
            (8.2, y_pos), 3.5, 0.7,
            boxstyle="round,pad=0.05",
            facecolor=color, edgecolor='black', linewidth=2
        )
        ax.add_patch(model_rect)
        ax.text(9.95, y_pos + 0.35, model, ha='center', va='center',
                fontsize=10, fontweight='bold')
        
        y_pos -= 1
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color='#FF6B6B', label='Claude Opus (Best reasoning)'),
        mpatches.Patch(color='#4ECDC4', label='GPT-4 (Reliable, structured)'),
        mpatches.Patch(color='#F38181', label='Claude Sonnet (Cost-effective)'),
        mpatches.Patch(color='#FFE66D', label='Gemini Pro (Diverse perspective)'),
        mpatches.Patch(color='#95E1D3', label='No AI Model (Service/Tool)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    ax.set_xlim(0, 13)
    ax.set_ylim(-1, 11)
    ax.axis('off')
    ax.set_title('Node → AI Model Assignment Strategy', 
                 fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'node_model_mapping.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'node_model_mapping.png'}")
    plt.close()


def create_data_flow():
    """Create data flow diagram"""
    
    fig, ax = plt.subplots(figsize=(12, 14))
    
    stages = [
        ("USER INPUT", "John Doe - CEO", '#90EE90'),
        ("INITIALIZATION", "ResearchState created", '#87CEEB'),
        ("PLANNING", "Research plan generated", '#FFD700'),
        ("QUERY GEN", "Specific queries created", '#98FB98'),
        ("SEARCH", "Results retrieved", '#DDA0DD'),
        ("EXTRACTION", "Facts extracted", '#F0E68C'),
        ("VALIDATION", "Facts verified", '#FFA07A'),
        ("CONNECTION", "Relationships mapped", '#FFB6C1'),
        ("RISK ASSESS", "Risks identified", '#FF6B6B'),
        ("DECISION", "Continue or finalize?", '#FF6347'),
        ("REFLECTION", "Gaps identified", '#B4E197'),
        ("SYNTHESIS", "Final report", '#FFD700'),
        ("DISPLAY", "Results shown to user", '#90EE90'),
    ]
    
    y_pos = 13
    for stage, desc, color in stages:
        # Stage box
        rect = FancyBboxPatch(
            (2, y_pos), 8, 0.8,
            boxstyle="round,pad=0.1",
            facecolor=color, edgecolor='black', linewidth=2
        )
        ax.add_patch(rect)
        
        # Text
        ax.text(3, y_pos + 0.4, stage, ha='left', va='center',
                fontsize=11, fontweight='bold')
        ax.text(8, y_pos + 0.4, desc, ha='right', va='center',
                fontsize=9, style='italic')
        
        # Arrow to next stage (except last)
        if y_pos > 0.5:
            arrow = FancyArrowPatch(
                (6, y_pos), (6, y_pos - 0.2),
                arrowstyle='->', mutation_scale=20, linewidth=2.5, color='#333'
            )
            ax.add_patch(arrow)
        
        # Loop back arrow for reflection
        if stage == "REFLECTION":
            loop_arrow = FancyArrowPatch(
                (10, y_pos + 0.4), (10, 10.5),
                arrowstyle='->', mutation_scale=15, linewidth=2,
                color='#FF6347', linestyle='--',
                connectionstyle="arc3,rad=.3"
            )
            ax.add_patch(loop_arrow)
            ax.text(11, 7, "Loop back\nif needed", ha='center', va='center',
                   fontsize=8, color='#FF6347', fontweight='bold')
        
        y_pos -= 1
    
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.5, 14.5)
    ax.axis('off')
    ax.set_title('Research Data Flow', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'data_flow.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_dir / 'data_flow.png'}")
    plt.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎨 Deep Research Agent - Architecture Visualizer")
    print("="*60 + "\n")
    
    print("ℹ️  Note: For the ACTUAL LangGraph workflow, use:")
    print("   python visualize_langgraph.py\n")
    
    print("Generating supplementary diagrams...\n")
    
    create_langgraph_workflow()  # Conceptual diagram
    create_system_architecture()
    create_node_model_mapping()
    create_data_flow()
    
    print(f"\n✅ All diagrams generated successfully!")
    print(f"📁 Location: {output_dir.absolute()}\n")
    print("Generated files:")
    print("  1. langgraph_workflow.png    - LangGraph workflow (conceptual)")
    print("  2. system_architecture.png   - Overall system architecture")
    print("  3. node_model_mapping.png    - Which AI model each node uses")
    print("  4. data_flow.png             - Data flow through the system")
    print("\n💡 For the actual compiled graph structure:")
    print("   python visualize_langgraph.py")
    print("\n" + "="*60 + "\n")

