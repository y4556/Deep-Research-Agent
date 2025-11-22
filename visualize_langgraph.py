"""
LangGraph Visualization Tool
Uses the actual compiled graph to generate visualizations
"""

import sys
from pathlib import Path
import asyncio

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from core.graph import ResearchWorkflow

# Create output directory
output_dir = Path("architecture_diagrams")
output_dir.mkdir(exist_ok=True)


def visualize_graph():
    """Visualize the actual LangGraph workflow"""
    
    print("\n" + "="*60)
    print("🔍 LangGraph Workflow Visualizer")
    print("="*60 + "\n")
    
    # Initialize the workflow
    print("⏳ Building workflow...")
    workflow = ResearchWorkflow()
    
    # Get the compiled graph
    compiled_graph = workflow.graph
    
    print("✅ Workflow compiled successfully!\n")
    
    # 1. ASCII Visualization
    print("📊 Generating ASCII visualization...\n")
    try:
        ascii_diagram = compiled_graph.get_graph().draw_ascii()
        
        # Save to file
        ascii_file = output_dir / "langgraph_ascii.txt"
        with open(ascii_file, 'w', encoding='utf-8') as f:
            f.write(ascii_diagram)
        
        print("ASCII Diagram:")
        print("-" * 60)
        print(ascii_diagram)
        print("-" * 60)
        print(f"✅ Saved to: {ascii_file}\n")
    except Exception as e:
        print(f"⚠️  ASCII generation failed: {e}\n")
    
    # 2. Mermaid Diagram
    print("📊 Generating Mermaid diagram...")
    try:
        mermaid_diagram = compiled_graph.get_graph().draw_mermaid()
        
        # Save to file
        mermaid_file = output_dir / "langgraph_mermaid.md"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write("# LangGraph Research Workflow\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_diagram)
            f.write("\n```\n\n")
            f.write("View this at: https://mermaid.live\n")
        
        print(f"✅ Saved to: {mermaid_file}")
        print("   You can view this at: https://mermaid.live\n")
    except Exception as e:
        print(f"⚠️  Mermaid generation failed: {e}\n")
    
    # 3. PNG Visualization (requires graphviz)
    print("📊 Generating PNG visualization...")
    try:
        png_data = compiled_graph.get_graph().draw_mermaid_png()
        
        # Save to file
        png_file = output_dir / "langgraph_workflow.png"
        with open(png_file, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ Saved to: {png_file}\n")
    except ImportError:
        print("⚠️  PNG generation requires 'pygraphviz' package")
        print("   Install with: pip install pygraphviz")
        print("   Or on Windows: conda install -c conda-forge pygraphviz\n")
    except Exception as e:
        print(f"⚠️  PNG generation failed: {e}")
        print("   This is optional - ASCII and Mermaid diagrams work fine!\n")
    
    # 4. Graph Information
    print("📋 Graph Information:")
    print("-" * 60)
    graph_info = compiled_graph.get_graph()
    
    print(f"Nodes: {len(graph_info.nodes)}")
    for node_id in sorted(graph_info.nodes.keys()):
        print(f"  • {node_id}")
    
    print(f"\nEdges: {len(graph_info.edges)}")
    for edge in graph_info.edges:
        print(f"  • {edge.source} → {edge.target}")
    
    print("-" * 60)
    
    # Summary
    print("\n" + "="*60)
    print("✅ Visualization Complete!")
    print("="*60)
    print(f"\n📁 Output directory: {output_dir.absolute()}\n")
    print("Generated files:")
    print("  1. langgraph_ascii.txt     - ASCII art diagram (always works)")
    print("  2. langgraph_mermaid.md    - Mermaid diagram (view at mermaid.live)")
    print("  3. langgraph_workflow.png  - PNG image (if graphviz installed)")
    print("\n💡 Tip: The ASCII diagram shows the actual graph structure!")
    print("   All conditional edges and loops are accurately represented.\n")


if __name__ == "__main__":
    try:
        visualize_graph()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

