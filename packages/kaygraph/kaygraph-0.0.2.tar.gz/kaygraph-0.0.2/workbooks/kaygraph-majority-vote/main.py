#!/usr/bin/env python3
"""
Majority Vote example using KayGraph.
Demonstrates LLM consensus through various voting strategies.
"""

import asyncio
import logging
import argparse
import json
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import AsyncGraph, AsyncParallelBatchNode, Node, MetricsNode
from consensus_nodes import (
    QueryRouterNode, ParallelLLMQueryNode, VoteAggregatorNode,
    ConfidenceCalculatorNode, ResultFormatterNode
)
from utils.llm_providers import query_llm_mock

logger = logging.getLogger(__name__)


class QueryComplexityAnalyzer(MetricsNode):
    """Analyze query complexity to determine routing strategy."""
    
    def __init__(self):
        super().__init__(node_id="query_analyzer", collect_metrics=True)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Analyze query complexity."""
        # Simple heuristics for complexity
        complexity_score = 0
        
        # Length-based
        if len(query) > 100:
            complexity_score += 2
        elif len(query) > 50:
            complexity_score += 1
        
        # Question type
        complex_indicators = [
            "explain", "analyze", "compare", "evaluate",
            "how", "why", "implications", "reasoning"
        ]
        simple_indicators = [
            "what is", "when", "where", "who",
            "define", "name", "list"
        ]
        
        query_lower = query.lower()
        
        for indicator in complex_indicators:
            if indicator in query_lower:
                complexity_score += 2
        
        for indicator in simple_indicators:
            if indicator in query_lower:
                complexity_score -= 1
        
        # Determine complexity level
        if complexity_score >= 3:
            complexity = "complex"
        elif complexity_score >= 1:
            complexity = "medium" 
        else:
            complexity = "simple"
        
        return {
            "query": query,
            "complexity": complexity,
            "score": complexity_score,
            "requires_consensus": complexity in ["complex", "medium"]
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, analysis: Dict[str, Any]) -> str:
        """Store analysis and route query."""
        shared["query_analysis"] = analysis
        
        logger.info(f"Query complexity: {analysis['complexity']} (score: {analysis['score']})")
        
        if analysis["requires_consensus"]:
            return "consensus"
        else:
            return "single"


class SingleLLMNode(Node):
    """Query a single LLM for simple queries."""
    
    def __init__(self, model: str = "gpt-3.5"):
        super().__init__(node_id="single_llm", max_retries=2)
        self.model = model
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare query."""
        return {
            "query": shared["query"],
            "model": self.model
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Query single LLM."""
        response = query_llm_mock(
            prep_res["query"],
            model=prep_res["model"]
        )
        
        return {
            "response": response["text"],
            "model": prep_res["model"],
            "confidence": response.get("confidence", 0.8)
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Store single response."""
        shared["llm_responses"] = [result]
        shared["consensus_method"] = "single"
        shared["final_response"] = result["response"]
        shared["confidence"] = result["confidence"]
        return None


class ConsensusOrchestrator(Node):
    """Orchestrate the consensus process."""
    
    def __init__(self, num_models: int = 3, strategy: str = "majority"):
        super().__init__(node_id="consensus_orchestrator")
        self.num_models = num_models
        self.strategy = strategy
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare consensus parameters."""
        # Select models based on query type
        analysis = shared.get("query_analysis", {})
        
        if analysis.get("complexity") == "complex":
            models = ["gpt-4", "claude-3", "gemini-pro", "gpt-3.5", "claude-2"][:self.num_models]
        else:
            models = ["gpt-3.5", "claude-2", "gemini-1.5"][:self.num_models]
        
        return {
            "query": shared["query"],
            "models": models,
            "strategy": self.strategy
        }
    
    def exec(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare model queries."""
        return [
            {
                "model": model,
                "query": params["query"],
                "request_id": f"{model}_{id(params)}"
            }
            for model in params["models"]
        ]
    
    def post(self, shared: Dict[str, Any], params: Dict[str, Any], queries: List[Dict[str, Any]]) -> None:
        """Store query batch."""
        shared["llm_queries"] = queries
        shared["consensus_strategy"] = params["strategy"]
        shared["models_used"] = params["models"]
        return None


def create_majority_vote_workflow(strategy: str = "majority", num_models: int = 3) -> AsyncGraph:
    """Create the majority vote workflow."""
    
    # Create nodes
    analyzer = QueryComplexityAnalyzer()
    single_llm = SingleLLMNode()
    orchestrator = ConsensusOrchestrator(num_models=num_models, strategy=strategy)
    parallel_query = ParallelLLMQueryNode()
    aggregator = VoteAggregatorNode(strategy=strategy)
    confidence_calc = ConfidenceCalculatorNode()
    formatter = ResultFormatterNode()
    
    # Build graph
    graph = AsyncGraph(start=analyzer)
    
    # Simple path
    analyzer - "single" >> single_llm
    single_llm >> formatter
    
    # Consensus path
    analyzer - "consensus" >> orchestrator
    orchestrator >> parallel_query
    parallel_query >> aggregator
    aggregator >> confidence_calc
    confidence_calc >> formatter
    
    return graph


async def run_majority_vote(args):
    """Run the majority vote example."""
    print("\n🗳️  KayGraph Majority Vote")
    print("=" * 60)
    print(f"Query: {args.query}")
    print(f"Strategy: {args.strategy}")
    print(f"Models: {args.models}")
    print("=" * 60)
    
    # Create workflow
    workflow = create_majority_vote_workflow(
        strategy=args.strategy,
        num_models=args.models
    )
    
    # Initialize shared context
    shared = {
        "query": args.query,
        "config": {
            "timeout": args.timeout,
            "min_confidence": args.min_confidence
        }
    }
    
    # Custom weights if provided
    if args.weights:
        weights = {}
        for w in args.weights.split(","):
            model, weight = w.split(":")
            weights[model] = float(weight)
        shared["model_weights"] = weights
    
    # Run workflow
    print("\n🔄 Processing query...")
    
    try:
        await workflow.run_async(shared)
        
        # Display results
        print("\n✅ Results")
        print("=" * 60)
        
        # Show individual responses if verbose
        if args.verbose and "llm_responses" in shared:
            print("\n📊 Individual Model Responses:")
            for i, resp in enumerate(shared["llm_responses"], 1):
                print(f"\n{i}. {resp['model']}:")
                print(f"   Response: {resp['response'][:100]}...")
                print(f"   Confidence: {resp.get('confidence', 'N/A')}")
        
        # Show consensus result
        print(f"\n🎯 Final Answer ({shared.get('consensus_method', 'unknown')} method):")
        print(shared.get("final_response", "No response generated"))
        
        print(f"\n📈 Confidence: {shared.get('confidence', 0):.2%}")
        
        # Show voting details if available
        if "voting_details" in shared:
            print("\n🗳️  Voting Details:")
            details = shared["voting_details"]
            if "votes" in details:
                for response, count in details["votes"].items():
                    print(f"   '{response[:50]}...': {count} votes")
            if "agreement_score" in details:
                print(f"   Agreement Score: {details['agreement_score']:.2%}")
        
        # Show metrics
        if args.show_metrics:
            print("\n📊 Performance Metrics:")
            print(f"   Total Time: {shared.get('total_time', 0):.2f}s")
            print(f"   Models Queried: {len(shared.get('models_used', []))}")
            if "query_analysis" in shared:
                print(f"   Query Complexity: {shared['query_analysis']['complexity']}")
        
    except Exception as e:
        logger.error(f"Error in majority vote: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="KayGraph Majority Vote Example")
    
    parser.add_argument("--query", required=True,
                       help="Query to process")
    parser.add_argument("--strategy", default="majority",
                       choices=["majority", "weighted", "confidence", "hierarchical"],
                       help="Voting strategy")
    parser.add_argument("--models", type=int, default=3,
                       help="Number of models to query")
    parser.add_argument("--weights", type=str,
                       help="Model weights (e.g., 'gpt4:0.4,claude:0.3,gemini:0.3')")
    parser.add_argument("--min-confidence", type=float, default=0.6,
                       help="Minimum confidence threshold")
    parser.add_argument("--timeout", type=int, default=30,
                       help="Query timeout in seconds")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed output")
    parser.add_argument("--show-metrics", action="store_true",
                       help="Show performance metrics")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run majority vote
    asyncio.run(run_majority_vote(args))


if __name__ == "__main__":
    main()