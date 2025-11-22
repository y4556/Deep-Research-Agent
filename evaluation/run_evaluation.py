"""
Evaluation Runner for Deep Research Agent

This script runs the research agent on all test personas and evaluates performance.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from core.graph import ResearchWorkflow
from timothy_overturf import (
    TIMOTHY_OVERFURT_EVALUATION_PROFILE,
    evaluate_timothy_overturf_research
)
from maria_rodriguez import (
    MARIA_RODRIGUEZ_EVALUATION_PROFILE,
    evaluate_maria_rodriguez_research
)
from blackstone_capital import (
    BLACKSTONE_CAPITAL_EVALUATION_PROFILE,
    evaluate_blackstone_capital_research
)


class EvaluationRunner:
    """Runs evaluations on test personas"""
    
    def __init__(self):
        self.workflow = ResearchWorkflow()
        self.results = []
        
        self.test_personas = [
            {
                "profile": TIMOTHY_OVERFURT_EVALUATION_PROFILE,
                "evaluator": evaluate_timothy_overturf_research
            },
            {
                "profile": MARIA_RODRIGUEZ_EVALUATION_PROFILE,
                "evaluator": evaluate_maria_rodriguez_research
            },
            {
                "profile": BLACKSTONE_CAPITAL_EVALUATION_PROFILE,
                "evaluator": evaluate_blackstone_capital_research
            }
        ]
    
    async def run_single_evaluation(self, persona_config: Dict) -> Dict[str, Any]:
        """Run evaluation on a single persona"""
        profile = persona_config["profile"]
        evaluator = persona_config["evaluator"]
        
        print(f"\n{'='*80}")
        print(f"🔍 Evaluating: {profile['name']} (Difficulty: {profile['difficulty']})")
        print(f"{'='*80}\n")
        
        try:
            # Run research
            print(f"⏳ Starting research on {profile['name']}...")
            start_time = datetime.now()
            
            research_result = await self.workflow.conduct_research(
                target_entity=profile["name"],
                max_depth=profile.get("evaluation_criteria", {}).get("research_depth", 3)
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"✅ Research completed in {duration:.1f} seconds")
            
            # Extract report
            report = research_result.get("final_report", {})
            
            if not report:
                print("⚠️  Warning: No final report generated, using state data")
                report = {
                    "key_findings": research_result.get("verified_facts", []),
                    "risk_assessment": {
                        "critical_risks": [r for r in research_result.get("risks_flagged", []) 
                                         if r.get("severity") == "critical"],
                        "high_risks": [r for r in research_result.get("risks_flagged", []) 
                                      if r.get("severity") == "high"],
                        "medium_risks": [r for r in research_result.get("risks_flagged", []) 
                                        if r.get("severity") == "medium"],
                        "low_risks": [r for r in research_result.get("risks_flagged", []) 
                                     if r.get("severity") == "low"]
                    },
                    "connection_network": research_result.get("connections", [])
                }
            
            # Evaluate
            print(f"📊 Evaluating results...")
            evaluation_result = evaluator(report)
            
            # Add metadata
            evaluation_result.update({
                "profile_name": profile["name"],
                "profile_difficulty": profile["difficulty"],
                "research_duration_seconds": duration,
                "research_depth_achieved": research_result.get("research_depth", 0),
                "queries_executed": len(research_result.get("search_queries", [])),
                "evaluation_timestamp": datetime.now().isoformat()
            })
            
            # Display results
            self._display_evaluation_result(evaluation_result)
            
            return evaluation_result
            
        except Exception as e:
            print(f"❌ Error evaluating {profile['name']}: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "profile_name": profile["name"],
                "error": str(e),
                "overall_score": 0.0
            }
    
    def _display_evaluation_result(self, result: Dict[str, Any]):
        """Display evaluation results in a formatted way"""
        print(f"\n{'─'*80}")
        print(f"📈 EVALUATION RESULTS")
        print(f"{'─'*80}")
        
        print(f"\n🎯 Overall Score: {result['overall_score']:.2%}")
        
        if "detailed_scores" in result:
            print(f"\n📊 Detailed Scores:")
            for metric, score in result["detailed_scores"].items():
                bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
                print(f"  {metric.replace('_', ' ').title():.<30} {bar} {score:.2%}")
        
        print(f"\n📝 Findings:")
        print(f"  Facts Found: {result.get('facts_found', 0)}")
        print(f"  Risks Identified: {result.get('risks_identified', 0)}")
        
        if "critical_facts_discovered" in result:
            print(f"  Critical Facts: {', '.join(result['critical_facts_discovered']) if result['critical_facts_discovered'] else 'None'}")
        
        print(f"\n⏱️  Performance:")
        print(f"  Duration: {result.get('research_duration_seconds', 0):.1f}s")
        print(f"  Depth Achieved: {result.get('research_depth_achieved', 0)}")
        print(f"  Queries Executed: {result.get('queries_executed', 0)}")
    
    async def run_all_evaluations(self):
        """Run all evaluations"""
        print("\n" + "="*80)
        print("🚀 DEEP RESEARCH AGENT - EVALUATION SUITE")
        print("="*80)
        print(f"\nStarting evaluation at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test Personas: {len(self.test_personas)}")
        
        self.results = []
        
        for persona_config in self.test_personas:
            result = await self.run_single_evaluation(persona_config)
            self.results.append(result)
            
            # Small delay between evaluations
            await asyncio.sleep(2)
        
        # Display summary
        self._display_summary()
        
        # Save results
        self._save_results()
    
    def _display_summary(self):
        """Display overall summary"""
        print(f"\n\n{'='*80}")
        print(f"📋 EVALUATION SUMMARY")
        print(f"{'='*80}\n")
        
        # Create summary table
        summary_data = []
        for result in self.results:
            if "error" not in result:
                summary_data.append({
                    "Persona": result["profile_name"],
                    "Difficulty": result["profile_difficulty"].title(),
                    "Overall Score": f"{result['overall_score']:.2%}",
                    "Facts Found": result.get("facts_found", 0),
                    "Risks Identified": result.get("risks_identified", 0),
                    "Duration (s)": f"{result.get('research_duration_seconds', 0):.1f}"
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            print(df.to_string(index=False))
            
            # Calculate averages
            avg_score = sum(r["overall_score"] for r in self.results if "error" not in r) / len([r for r in self.results if "error" not in r])
            print(f"\n🎯 Average Performance: {avg_score:.2%}")
            
            # Performance by difficulty
            print(f"\n📊 Performance by Difficulty:")
            by_difficulty = {}
            for result in self.results:
                if "error" not in result:
                    diff = result["profile_difficulty"]
                    if diff not in by_difficulty:
                        by_difficulty[diff] = []
                    by_difficulty[diff].append(result["overall_score"])
            
            for diff, scores in sorted(by_difficulty.items()):
                avg = sum(scores) / len(scores)
                print(f"  {diff.title():.<20} {avg:.2%}")
        
        # Display errors if any
        errors = [r for r in self.results if "error" in r]
        if errors:
            print(f"\n⚠️  Errors:")
            for error in errors:
                print(f"  - {error['profile_name']}: {error['error']}")
    
    def _save_results(self):
        """Save evaluation results to file"""
        output_dir = Path(__file__).parent / "results"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"evaluation_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump({
                "evaluation_run": {
                    "timestamp": datetime.now().isoformat(),
                    "total_personas": len(self.test_personas),
                    "successful_evaluations": len([r for r in self.results if "error" not in r])
                },
                "results": self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_file}")


async def main():
    """Main entry point"""
    try:
        runner = EvaluationRunner()
        await runner.run_all_evaluations()
        
        print(f"\n✅ Evaluation complete!")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Evaluation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Evaluation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           DEEP RESEARCH AGENT - EVALUATION RUNNER            ║
    ║                                                               ║
    ║  This script will evaluate the research agent on test        ║
    ║  personas and generate performance metrics.                  ║
    ║                                                               ║
    ║  ⚠️  Note: This requires valid API keys and may take         ║
    ║  significant time and incur API costs.                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Confirmation prompt
    response = input("\nProceed with evaluation? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        asyncio.run(main())
    else:
        print("\n❌ Evaluation cancelled")
        sys.exit(0)

