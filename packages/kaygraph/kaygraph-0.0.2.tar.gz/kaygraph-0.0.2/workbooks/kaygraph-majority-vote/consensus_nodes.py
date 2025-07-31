"""
Consensus and voting nodes for majority vote pattern.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter, defaultdict
import statistics

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from kaygraph import Node, AsyncNode, AsyncParallelBatchNode, ValidatedNode
from utils.llm_providers import query_llm_mock

logger = logging.getLogger(__name__)


class QueryRouterNode(Node):
    """Route queries based on complexity and requirements."""
    
    def __init__(self):
        super().__init__(node_id="query_router")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get query and analysis."""
        return {
            "query": shared.get("query"),
            "analysis": shared.get("query_analysis", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Determine routing strategy."""
        complexity = prep_res["analysis"].get("complexity", "simple")
        
        if complexity == "simple":
            return "single"
        elif complexity == "medium":
            return "consensus_simple"
        else:
            return "consensus_full"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], route: str) -> str:
        """Store routing decision and return action."""
        shared["routing_decision"] = route
        return route


class ParallelLLMQueryNode(AsyncParallelBatchNode):
    """Query multiple LLMs in parallel."""
    
    def __init__(self):
        super().__init__(node_id="parallel_llm_query", max_retries=1)
    
    async def prep_async(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get queries to execute."""
        return shared.get("llm_queries", [])
    
    async def exec_async(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Query a single LLM."""
        start_time = time.time()
        
        try:
            # Add some randomness to simulate different response times
            await asyncio.sleep(0.5 + (hash(query_info["model"]) % 10) * 0.1)
            
            response = query_llm_mock(
                query_info["query"],
                model=query_info["model"]
            )
            
            return {
                "model": query_info["model"],
                "response": response["text"],
                "confidence": response.get("confidence", 0.8),
                "latency": time.time() - start_time,
                "success": True,
                "request_id": query_info["request_id"]
            }
            
        except Exception as e:
            logger.error(f"Error querying {query_info['model']}: {e}")
            return {
                "model": query_info["model"],
                "response": None,
                "error": str(e),
                "latency": time.time() - start_time,
                "success": False,
                "request_id": query_info["request_id"]
            }
    
    async def post_async(self, shared: Dict[str, Any], queries: List[Dict], responses: List[Dict]) -> None:
        """Store all responses."""
        # Filter successful responses
        successful_responses = [r for r in responses if r["success"]]
        failed_responses = [r for r in responses if not r["success"]]
        
        shared["llm_responses"] = successful_responses
        shared["failed_queries"] = failed_responses
        
        logger.info(f"Queried {len(responses)} models: "
                   f"{len(successful_responses)} successful, "
                   f"{len(failed_responses)} failed")
        
        # Calculate average latency
        if successful_responses:
            avg_latency = statistics.mean(r["latency"] for r in successful_responses)
            shared["avg_query_latency"] = avg_latency


class VoteAggregatorNode(ValidatedNode):
    """Aggregate LLM responses using various voting strategies."""
    
    def __init__(self, strategy: str = "majority"):
        super().__init__(node_id="vote_aggregator")
        self.strategy = strategy
    
    def validate_input(self, responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate we have responses to aggregate."""
        if not responses:
            raise ValueError("No responses to aggregate")
        
        if len(responses) < 2 and self.strategy != "single":
            logger.warning(f"Only {len(responses)} responses for {self.strategy} voting")
        
        return responses
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get LLM responses."""
        return shared.get("llm_responses", [])
    
    def exec(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate responses based on strategy."""
        if self.strategy == "majority":
            return self._majority_vote(responses)
        elif self.strategy == "weighted":
            weights = self._get_weights()
            return self._weighted_vote(responses, weights)
        elif self.strategy == "confidence":
            return self._confidence_vote(responses)
        elif self.strategy == "hierarchical":
            return self._hierarchical_vote(responses)
        else:
            return self._majority_vote(responses)
    
    def _majority_vote(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple majority voting."""
        # Count exact matches (in practice, use semantic similarity)
        response_texts = [r["response"] for r in responses if r["response"]]
        
        if not response_texts:
            return {"winner": None, "votes": {}, "method": "majority"}
        
        # For demo, we'll use the first 50 chars as key
        vote_keys = [text[:50] for text in response_texts]
        vote_counter = Counter(vote_keys)
        
        winner_key, winner_count = vote_counter.most_common(1)[0]
        winner_idx = vote_keys.index(winner_key)
        winner_response = response_texts[winner_idx]
        
        return {
            "winner": winner_response,
            "votes": dict(vote_counter),
            "winner_count": winner_count,
            "total_votes": len(response_texts),
            "agreement_ratio": winner_count / len(response_texts),
            "method": "majority"
        }
    
    def _weighted_vote(self, responses: List[Dict[str, Any]], weights: Dict[str, float]) -> Dict[str, Any]:
        """Weighted voting based on model weights."""
        weighted_votes = defaultdict(float)
        
        for resp in responses:
            if resp["response"]:
                model = resp["model"]
                weight = weights.get(model, 1.0)
                vote_key = resp["response"][:50]
                weighted_votes[vote_key] += weight
        
        if not weighted_votes:
            return {"winner": None, "votes": {}, "method": "weighted"}
        
        winner_key = max(weighted_votes, key=weighted_votes.get)
        winner_response = next(r["response"] for r in responses 
                              if r["response"] and r["response"][:50] == winner_key)
        
        total_weight = sum(weighted_votes.values())
        
        return {
            "winner": winner_response,
            "weighted_votes": dict(weighted_votes),
            "winner_weight": weighted_votes[winner_key],
            "total_weight": total_weight,
            "agreement_ratio": weighted_votes[winner_key] / total_weight,
            "method": "weighted"
        }
    
    def _confidence_vote(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Vote weighted by confidence scores."""
        confidence_votes = defaultdict(float)
        
        for resp in responses:
            if resp["response"] and "confidence" in resp:
                vote_key = resp["response"][:50]
                confidence_votes[vote_key] += resp["confidence"]
        
        if not confidence_votes:
            return {"winner": None, "votes": {}, "method": "confidence"}
        
        winner_key = max(confidence_votes, key=confidence_votes.get)
        winner_response = next(r["response"] for r in responses 
                              if r["response"] and r["response"][:50] == winner_key)
        
        total_confidence = sum(confidence_votes.values())
        
        return {
            "winner": winner_response,
            "confidence_votes": dict(confidence_votes),
            "winner_confidence": confidence_votes[winner_key],
            "total_confidence": total_confidence,
            "agreement_ratio": confidence_votes[winner_key] / total_confidence,
            "method": "confidence"
        }
    
    def _hierarchical_vote(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Hierarchical voting - use expensive models only for ties."""
        # Separate by model tier
        tier1_models = ["gpt-3.5", "claude-2", "gemini-1.5"]
        tier2_models = ["gpt-4", "claude-3", "gemini-pro"]
        
        tier1_responses = [r for r in responses if r["model"] in tier1_models]
        tier2_responses = [r for r in responses if r["model"] in tier2_models]
        
        # First try tier 1
        if tier1_responses:
            tier1_result = self._majority_vote(tier1_responses)
            
            # If strong agreement, use it
            if tier1_result.get("agreement_ratio", 0) > 0.66:
                return {
                    **tier1_result,
                    "method": "hierarchical_tier1",
                    "tier": 1
                }
        
        # Otherwise use tier 2
        if tier2_responses:
            tier2_result = self._majority_vote(tier2_responses)
            return {
                **tier2_result,
                "method": "hierarchical_tier2",
                "tier": 2
            }
        
        # Fallback to all responses
        return self._majority_vote(responses)
    
    def _get_weights(self) -> Dict[str, float]:
        """Get model weights from configuration."""
        # Default weights
        return {
            "gpt-4": 0.35,
            "claude-3": 0.35,
            "gemini-pro": 0.30,
            "gpt-3.5": 0.20,
            "claude-2": 0.20,
            "gemini-1.5": 0.15
        }
    
    def post(self, shared: Dict[str, Any], responses: List[Dict], result: Dict[str, Any]) -> None:
        """Store voting result."""
        shared["voting_result"] = result
        shared["consensus_method"] = result["method"]
        shared["final_response"] = result.get("winner", "No consensus reached")
        
        # Store detailed voting information
        shared["voting_details"] = {
            "method": result["method"],
            "agreement_score": result.get("agreement_ratio", 0),
            "votes": result.get("votes") or result.get("weighted_votes") or result.get("confidence_votes", {})
        }


class ConfidenceCalculatorNode(Node):
    """Calculate overall confidence in the consensus result."""
    
    def __init__(self):
        super().__init__(node_id="confidence_calculator")
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get voting result and responses."""
        return {
            "voting_result": shared.get("voting_result", {}),
            "responses": shared.get("llm_responses", []),
            "method": shared.get("consensus_method", "unknown")
        }
    
    def exec(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score."""
        voting_result = data["voting_result"]
        responses = data["responses"]
        
        # Base confidence from agreement ratio
        base_confidence = voting_result.get("agreement_ratio", 0.5)
        
        # Adjust based on number of models
        model_count_factor = min(len(responses) / 5, 1.0)  # Max benefit at 5 models
        
        # Adjust based on individual model confidences
        if responses:
            avg_model_confidence = statistics.mean(
                r.get("confidence", 0.5) for r in responses
            )
        else:
            avg_model_confidence = 0.5
        
        # Combine factors
        confidence = (
            base_confidence * 0.5 +
            model_count_factor * 0.2 +
            avg_model_confidence * 0.3
        )
        
        # Penalty for failed queries
        failed_count = len(shared.get("failed_queries", []))
        if failed_count > 0:
            confidence *= (1 - failed_count * 0.1)
        
        return max(0.0, min(1.0, confidence))
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, confidence: float) -> None:
        """Store confidence score."""
        shared["confidence"] = confidence
        
        # Determine confidence level
        if confidence >= 0.8:
            shared["confidence_level"] = "high"
        elif confidence >= 0.6:
            shared["confidence_level"] = "medium"
        else:
            shared["confidence_level"] = "low"
        
        logger.info(f"Consensus confidence: {confidence:.2%} ({shared['confidence_level']})")


class ResultFormatterNode(Node):
    """Format the final result with metadata."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all result data."""
        return {
            "response": shared.get("final_response"),
            "confidence": shared.get("confidence", 0),
            "method": shared.get("consensus_method"),
            "models_used": shared.get("models_used", []),
            "voting_details": shared.get("voting_details", {})
        }
    
    def exec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the result."""
        return {
            "answer": data["response"],
            "confidence": data["confidence"],
            "consensus_method": data["method"],
            "models_consulted": data["models_used"],
            "metadata": {
                "voting_details": data["voting_details"],
                "timestamp": time.time()
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, result: Dict) -> None:
        """Store formatted result."""
        shared["formatted_result"] = result
        shared["total_time"] = time.time() - shared.get("start_time", time.time())


if __name__ == "__main__":
    # Test consensus nodes
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test vote aggregation
    aggregator = VoteAggregatorNode(strategy="majority")
    
    test_responses = [
        {"model": "gpt-4", "response": "Paris is the capital of France", "confidence": 0.95},
        {"model": "claude-3", "response": "Paris is the capital of France", "confidence": 0.92},
        {"model": "gemini-pro", "response": "Paris is the capital of France", "confidence": 0.90},
    ]
    
    result = aggregator.exec(test_responses)
    print(f"Voting result: {result}")
    print(f"Agreement ratio: {result['agreement_ratio']:.2%}")