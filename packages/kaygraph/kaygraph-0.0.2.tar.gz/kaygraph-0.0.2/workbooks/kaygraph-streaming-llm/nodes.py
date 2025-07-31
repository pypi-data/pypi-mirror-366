import asyncio
import json
import random
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncGenerator
from kaygraph import ValidatedNode, MetricsNode, Node
import logging

logging.basicConfig(level=logging.INFO)


class StreamingMetrics:
    """Real-time metrics collection for streaming operations"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.token_count = 0
        self.token_times = []
        self.quality_scores = []
        self.safety_flags = []
        self.error_count = 0
        
    def track_token(self, token: str, quality_score: Optional[float] = None, safety_ok: bool = True):
        """Track a single token with metrics"""
        current_time = time.time()
        self.token_count += 1
        self.token_times.append(current_time)
        
        if quality_score is not None:
            self.quality_scores.append(quality_score)
        
        self.safety_flags.append(safety_ok)
    
    def track_error(self):
        """Track streaming errors"""
        self.error_count += 1
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get current streaming statistics"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.token_count == 0:
            return {
                "session_id": self.session_id,
                "elapsed_time": elapsed,
                "tokens_per_second": 0,
                "total_tokens": 0
            }
        
        # Calculate token rate
        tokens_per_second = self.token_count / elapsed if elapsed > 0 else 0
        
        # Calculate recent token rate (last 10 tokens)
        recent_tokens = self.token_times[-10:] if len(self.token_times) >= 10 else self.token_times
        if len(recent_tokens) > 1:
            recent_elapsed = recent_tokens[-1] - recent_tokens[0]
            recent_rate = (len(recent_tokens) - 1) / recent_elapsed if recent_elapsed > 0 else 0
        else:
            recent_rate = tokens_per_second
        
        # Safety statistics
        safe_tokens = sum(1 for safe in self.safety_flags if safe)
        safety_rate = safe_tokens / len(self.safety_flags) if self.safety_flags else 1.0
        
        return {
            "session_id": self.session_id,
            "elapsed_time": elapsed,
            "total_tokens": self.token_count,
            "tokens_per_second": round(tokens_per_second, 2),
            "recent_tokens_per_second": round(recent_rate, 2),
            "avg_quality_score": round(sum(self.quality_scores) / len(self.quality_scores), 3) if self.quality_scores else None,
            "safety_rate": round(safety_rate, 3),
            "error_count": self.error_count
        }


class StreamingGuardrails:
    """Content safety and guardrails for streaming text"""
    
    def __init__(self):
        self.safety_keywords = [
            "violence", "harmful", "illegal", "inappropriate", "offensive"
        ]
        self.accumulated_text = ""
        self.violations = []
        
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a single token for safety"""
        self.accumulated_text += token
        
        # Simple keyword-based safety check
        token_lower = token.lower()
        is_safe = not any(keyword in token_lower for keyword in self.safety_keywords)
        
        # Check accumulated text for context-based violations
        context_safe = self._check_context_safety(self.accumulated_text)
        
        overall_safe = is_safe and context_safe
        
        if not overall_safe:
            violation = {
                "token": token,
                "reason": "safety_keyword" if not is_safe else "context_violation",
                "timestamp": time.time()
            }
            self.violations.append(violation)
        
        return {
            "is_safe": overall_safe,
            "token_safe": is_safe,
            "context_safe": context_safe,
            "confidence": random.uniform(0.8, 1.0)  # Simulated confidence
        }
    
    def _check_context_safety(self, text: str) -> bool:
        """Check context-based safety (simplified)"""
        # Simple heuristics for demonstration
        if len(text) > 100:
            # Check for repeated violations
            recent_text = text[-100:]
            violation_count = sum(1 for keyword in self.safety_keywords if keyword in recent_text.lower())
            return violation_count < 2
        return True
    
    def get_safety_summary(self) -> Dict[str, Any]:
        """Get safety summary for the session"""
        return {
            "total_violations": len(self.violations),
            "violation_rate": len(self.violations) / len(self.accumulated_text) if self.accumulated_text else 0,
            "violations": self.violations[-5:]  # Last 5 violations
        }
    
    def reset(self):
        """Reset guardrails for new session"""
        self.accumulated_text = ""
        self.violations = []


class PromptProcessorNode(ValidatedNode):
    """Processes and validates input prompts"""
    
    def __init__(self):
        super().__init__(node_id="prompt_processor")
        
    def validate_input(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input prompt data"""
        if not prompt_data:
            raise ValueError("No prompt data provided")
        
        prompt = prompt_data.get("prompt", "")
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("Empty prompt provided")
        
        if len(prompt) > 10000:  # 10k character limit
            raise ValueError(f"Prompt too long: {len(prompt)} characters (max: 10000)")
        
        return prompt_data
    
    def validate_output(self, processed_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processed prompt"""
        required_fields = ["prompt", "model", "max_tokens", "temperature"]
        
        for field in required_fields:
            if field not in processed_prompt:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate parameters
        if not (0.0 <= processed_prompt["temperature"] <= 2.0):
            raise ValueError("Temperature must be between 0.0 and 2.0")
        
        if not (1 <= processed_prompt["max_tokens"] <= 4000):
            raise ValueError("max_tokens must be between 1 and 4000")
        
        return processed_prompt
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return self.params.copy()
    
    def exec(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the prompt with optimizations"""
        prompt = prompt_data.get("prompt", "")
        
        # Apply prompt optimizations
        optimized_prompt = self._optimize_prompt(prompt)
        
        # Prepare LLM parameters
        processed = {
            "prompt": optimized_prompt,
            "original_prompt": prompt,
            "model": prompt_data.get("model", "gpt-3.5-turbo"),
            "max_tokens": prompt_data.get("max_tokens", 1000),
            "temperature": prompt_data.get("temperature", 0.7),
            "stream": True,
            "session_id": f"stream_{int(time.time())}_{random.randint(1000, 9999)}"
        }
        
        return processed
    
    def _optimize_prompt(self, prompt: str) -> str:
        """Apply prompt engineering optimizations"""
        # Simple optimizations for demonstration
        optimized = prompt.strip()
        
        # Add clarity instructions if not present
        if "respond" not in optimized.lower() and "answer" not in optimized.lower():
            optimized += "\n\nPlease provide a clear and helpful response."
        
        return optimized
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["processed_prompt"] = exec_res
        return "validated"


class StreamingLLMNode(MetricsNode):
    """Streams LLM responses with comprehensive metrics"""
    
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=3, wait=2, node_id="streaming_llm")
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_open = False
        self.last_failure_time = None
        
    def before_prep(self, shared: Dict[str, Any]):
        """Check circuit breaker status before streaming"""
        if self.circuit_breaker_open:
            if self.last_failure_time and (time.time() - self.last_failure_time) > 30:
                # Reset circuit breaker after 30 seconds
                self.circuit_breaker_open = False
                self.circuit_breaker_failures = 0
                self.logger.info("Circuit breaker reset")
            else:
                raise RuntimeError("Circuit breaker is open - LLM service unavailable")
    
    def after_exec(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any):
        """Update metrics after streaming"""
        streaming_result = exec_res
        
        if streaming_result.get("success", False):
            # Reset circuit breaker on success
            self.circuit_breaker_failures = 0
            self.circuit_breaker_open = False
        else:
            self._handle_streaming_failure()
        
        # Log streaming performance
        metrics = streaming_result.get("streaming_metrics", {})
        self.logger.info(f"Streaming completed: {metrics.get('total_tokens', 0)} tokens in {metrics.get('elapsed_time', 0):.2f}s")
    
    def on_error(self, shared: Dict[str, Any], error: Exception) -> bool:
        """Handle streaming errors with circuit breaker"""
        self.logger.error(f"Streaming failed: {error}")
        self._handle_streaming_failure()
        
        # Try to provide cached response if available
        cached_response = self._get_cached_response(shared.get("processed_prompt", {}))
        if cached_response:
            shared["streaming_result"] = {
                "tokens": cached_response["tokens"],
                "complete_response": cached_response["text"],
                "success": True,
                "source": "cache_fallback",
                "streaming_metrics": {
                    "total_tokens": len(cached_response["tokens"]),
                    "elapsed_time": 0.1,
                    "tokens_per_second": len(cached_response["tokens"]) * 10
                }
            }
            self.logger.info("Using cached response as fallback")
            return True  # Suppress error
        
        return False
    
    def _handle_streaming_failure(self):
        """Handle streaming failure for circuit breaker"""
        self.circuit_breaker_failures += 1
        self.last_failure_time = time.time()
        
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            self.circuit_breaker_open = True
            self.logger.warning("Circuit breaker opened due to repeated failures")
    
    def _get_cached_response(self, prompt_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached response for common prompts"""
        prompt = prompt_data.get("prompt", "").lower()
        
        # Simple cache for demonstration
        if "hello" in prompt:
            return {
                "text": "Hello! How can I help you today?",
                "tokens": ["Hello", "!", " How", " can", " I", " help", " you", " today", "?"]
            }
        elif "weather" in prompt:
            return {
                "text": "I don't have access to real-time weather data.",
                "tokens": ["I", " don", "'t", " have", " access", " to", " real", "-time", " weather", " data", "."]
            }
        
        return None
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("processed_prompt", {})
    
    def exec(self, prompt_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute streaming LLM call with metrics"""
        session_id = prompt_config.get("session_id", "unknown")
        streaming_metrics = StreamingMetrics(session_id)
        
        # Simulate streaming response
        try:
            tokens, complete_response = self._simulate_streaming_llm(prompt_config, streaming_metrics)
            
            final_metrics = streaming_metrics.get_real_time_stats()
            
            return {
                "tokens": tokens,
                "complete_response": complete_response,
                "success": True,
                "session_id": session_id,
                "streaming_metrics": final_metrics,
                "model_used": prompt_config.get("model", "gpt-3.5-turbo")
            }
            
        except Exception as e:
            streaming_metrics.track_error()
            return {
                "tokens": [],
                "complete_response": "",
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "streaming_metrics": streaming_metrics.get_real_time_stats()
            }
    
    def _simulate_streaming_llm(self, config: Dict[str, Any], metrics: StreamingMetrics) -> tuple:
        """Simulate streaming LLM response"""
        prompt = config.get("prompt", "")
        max_tokens = config.get("max_tokens", 100)
        temperature = config.get("temperature", 0.7)
        
        # Simulate streaming failures
        if self.params.get("simulate_failure", False):
            if random.random() < 0.15:  # 15% failure rate
                raise ConnectionError("Simulated LLM API failure")
        
        # Generate response based on prompt
        if "code" in prompt.lower():
            response_template = "Here's a simple Python function:\n\ndef example_function():\n    print('Hello, World!')\n    return True"
        elif "explain" in prompt.lower():
            response_template = "Let me explain this concept step by step. First, we need to understand the basic principles. Then we can explore the implementation details."
        else:
            response_template = "Thank you for your question. I'll provide a comprehensive response that addresses your needs with detailed information and helpful examples."
        
        # Tokenize response (simplified)
        words = response_template.split()
        tokens = []
        for word in words:
            # Simple tokenization
            if len(word) > 4:
                tokens.extend([word[:len(word)//2], word[len(word)//2:]])
            else:
                tokens.append(word)
        
        # Limit tokens based on max_tokens
        tokens = tokens[:min(max_tokens, len(tokens))]
        
        # Simulate streaming with delays
        streamed_tokens = []
        for i, token in enumerate(tokens):
            # Simulate network latency
            delay = random.uniform(0.01, 0.1) * (1 + temperature)  # Temperature affects delay
            time.sleep(delay)
            
            # Track token metrics
            quality_score = random.uniform(0.7, 1.0)
            metrics.track_token(token, quality_score, safety_ok=True)
            
            streamed_tokens.append(token)
            
            # Occasional streaming interruption
            if self.params.get("simulate_failure", False) and random.random() < 0.02:
                raise RuntimeError(f"Streaming interrupted after {i+1} tokens")
        
        complete_response = " ".join(streamed_tokens)
        return streamed_tokens, complete_response
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["streaming_result"] = exec_res
        
        if exec_res.get("success", False):
            return "streamed"
        else:
            return "stream_failed"


class ResponseHandlerNode(ValidatedNode):
    """Handles streaming responses with real-time validation"""
    
    def __init__(self):
        super().__init__(node_id="response_handler")
        self.guardrails = StreamingGuardrails()
        
    def validate_input(self, streaming_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate streaming result"""
        if not streaming_result:
            raise ValueError("No streaming result provided")
        
        if not streaming_result.get("success", False):
            raise ValueError(f"Streaming failed: {streaming_result.get('error', 'Unknown error')}")
        
        return streaming_result
    
    def validate_output(self, processed_response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate processed response"""
        if not processed_response.get("validated_tokens"):
            raise ValueError("No validated tokens in response")
        
        safety_summary = processed_response.get("safety_summary", {})
        violation_rate = safety_summary.get("violation_rate", 0)
        
        if violation_rate > 0.1:  # More than 10% violations
            raise ValueError(f"Too many safety violations: {violation_rate:.1%}")
        
        return processed_response
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return shared.get("streaming_result", {})
    
    def exec(self, streaming_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process streaming response with real-time validation"""
        tokens = streaming_result.get("tokens", [])
        
        # Reset guardrails for new session
        self.guardrails.reset()
        
        validated_tokens = []
        filtered_tokens = []
        safety_scores = []
        
        for token in tokens:
            # Apply guardrails
            if self.params.get("enable_guardrails", True):
                safety_result = self.guardrails.validate_token(token)
                
                if safety_result["is_safe"]:
                    validated_tokens.append(token)
                else:
                    filtered_tokens.append({
                        "token": token,
                        "reason": safety_result.get("reason", "safety_violation")
                    })
                
                safety_scores.append(safety_result["confidence"])
            else:
                validated_tokens.append(token)
                safety_scores.append(1.0)
        
        # Reconstruct validated response
        validated_response = " ".join(validated_tokens)
        
        # Get safety summary
        safety_summary = self.guardrails.get_safety_summary()
        
        # Calculate quality metrics
        avg_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0
        filter_rate = len(filtered_tokens) / len(tokens) if tokens else 0
        
        return {
            "validated_tokens": validated_tokens,
            "validated_response": validated_response,
            "filtered_tokens": filtered_tokens,
            "safety_summary": safety_summary,
            "quality_metrics": {
                "avg_safety_score": round(avg_safety_score, 3),
                "filter_rate": round(filter_rate, 3),
                "total_tokens": len(tokens),
                "validated_tokens": len(validated_tokens)
            },
            "original_streaming_metrics": streaming_result.get("streaming_metrics", {})
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["response_result"] = exec_res
        
        filter_rate = exec_res.get("quality_metrics", {}).get("filter_rate", 0)
        
        if filter_rate > 0.2:  # More than 20% filtered
            return "high_filter_rate"
        else:
            return "processed"


class TokenAggregatorNode(Node):
    """Aggregates and analyzes streaming results"""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "streaming_result": shared.get("streaming_result", {}),
            "response_result": shared.get("response_result", {}),
            "processed_prompt": shared.get("processed_prompt", {})
        }
    
    def exec(self, aggregation_input: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate streaming metrics and results"""
        streaming_result = aggregation_input.get("streaming_result", {})
        response_result = aggregation_input.get("response_result", {})
        processed_prompt = aggregation_input.get("processed_prompt", {})
        
        # Aggregate metrics
        streaming_metrics = streaming_result.get("streaming_metrics", {})
        quality_metrics = response_result.get("quality_metrics", {})
        safety_summary = response_result.get("safety_summary", {})
        
        # Calculate overall performance
        performance_score = self._calculate_performance_score(
            streaming_metrics, quality_metrics, safety_summary
        )
        
        # Create final summary
        summary = {
            "session_id": streaming_result.get("session_id", "unknown"),
            "model_used": streaming_result.get("model_used", "unknown"),
            "prompt_length": len(processed_prompt.get("prompt", "")),
            "response_length": len(response_result.get("validated_response", "")),
            "streaming_performance": streaming_metrics,
            "quality_metrics": quality_metrics,
            "safety_summary": safety_summary,
            "performance_score": performance_score,
            "success": streaming_result.get("success", False),
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def _calculate_performance_score(self, streaming_metrics: Dict, quality_metrics: Dict, safety_summary: Dict) -> float:
        """Calculate overall performance score"""
        score = 1.0
        
        # Streaming performance (40% weight)
        tokens_per_second = streaming_metrics.get("tokens_per_second", 0)
        if tokens_per_second > 0:
            # Normalize to 0-1 scale (assuming 10 tokens/sec is excellent)
            streaming_score = min(tokens_per_second / 10.0, 1.0)
            score *= (0.4 + 0.6 * streaming_score)
        else:
            score *= 0.4  # Poor streaming performance
        
        # Quality metrics (30% weight)
        avg_safety_score = quality_metrics.get("avg_safety_score", 0)
        filter_rate = quality_metrics.get("filter_rate", 0)
        quality_score = avg_safety_score * (1 - filter_rate)
        score *= (0.3 + 0.7 * quality_score)
        
        # Safety (30% weight)
        violation_rate = safety_summary.get("violation_rate", 0)
        safety_score = max(0, 1 - violation_rate * 10)  # Penalize violations heavily
        score *= (0.3 + 0.7 * safety_score)
        
        return round(score, 3)
    
    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        shared["final_summary"] = exec_res
        
        performance_score = exec_res.get("performance_score", 0)
        self.logger.info(f"Streaming session completed with performance score: {performance_score}")
        
        return None  # End of workflow