"""
Automatic Dataset Collector Module

Fully automatic dataset collection without requiring user feedback.
Uses heuristics and behavioral signals to determine data quality.

Author: Promptlyzer Team
"""

import time
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re
import statistics


@dataclass
class AutoQualitySignals:
    """Automatic quality signals without user feedback"""
    
    # Response characteristics
    response_time_ms: float = 0
    output_length: int = 0
    input_output_ratio: float = 0
    
    # Behavioral signals
    time_to_next_query: Optional[float] = None  # Long time = good response
    session_continued: bool = False  # User continued conversation = good
    response_copied: bool = False  # Response was copied = good
    response_modified: bool = False  # Response was edited = needs improvement
    query_reformulated: bool = False  # Same query asked differently = bad
    
    # Content quality signals
    has_code_blocks: bool = False
    has_structured_output: bool = False
    grammar_score: float = 0.0
    completeness_score: float = 0.0
    
    # Error indicators
    has_error_messages: bool = False
    has_apology: bool = False
    truncated_response: bool = False
    
    # Model confidence
    model_confidence: Optional[float] = None
    temperature_used: float = 0.7
    
    def calculate_quality_score(self) -> float:
        """Calculate overall quality score from signals"""
        score = 0.5  # Base score
        
        # Positive signals
        if self.time_to_next_query and self.time_to_next_query > 30:  # 30+ seconds
            score += 0.15  # User spent time with response
        
        if self.session_continued:
            score += 0.1  # Conversation continued naturally
        
        if self.response_copied:
            score += 0.2  # Strong positive signal
        
        if 0.5 <= self.input_output_ratio <= 3.0:
            score += 0.1  # Reasonable response length
        
        if self.has_structured_output or self.has_code_blocks:
            score += 0.1  # Well-formatted response
        
        if self.response_time_ms < 1000:
            score += 0.05  # Fast response
        
        # Negative signals
        if self.has_error_messages or self.has_apology:
            score -= 0.3
        
        if self.query_reformulated:
            score -= 0.2  # User had to ask again
        
        if self.response_modified:
            score -= 0.1  # User edited response
        
        if self.truncated_response:
            score -= 0.15
        
        # Model confidence bonus
        if self.model_confidence and self.model_confidence > 0.8:
            score += 0.1
        
        return max(0.0, min(1.0, score))


@dataclass 
class SessionContext:
    """Track session context for quality assessment"""
    session_id: str
    start_time: datetime
    last_activity: datetime
    messages: List[Dict[str, Any]] = field(default_factory=list)
    
    # Pattern tracking
    query_patterns: List[str] = field(default_factory=list)
    response_patterns: List[str] = field(default_factory=list)
    
    # Session health
    error_count: int = 0
    successful_turns: int = 0
    average_response_time: float = 0
    
    def add_turn(self, query: str, response: str, response_time: float):
        """Add a conversation turn"""
        self.messages.append({
            "timestamp": datetime.now(timezone.utc),
            "query": query,
            "response": response,
            "response_time": response_time
        })
        
        # Update patterns
        self.query_patterns.append(self._extract_pattern(query))
        self.response_patterns.append(self._extract_pattern(response))
        
        # Update metrics
        self.last_activity = datetime.now(timezone.utc)
        total_time = self.average_response_time * len(self.messages)
        self.average_response_time = (total_time + response_time) / (len(self.messages) + 1)
        
        # Check for errors
        if any(err in response.lower() for err in ["error", "failed", "cannot"]):
            self.error_count += 1
        else:
            self.successful_turns += 1
    
    def _extract_pattern(self, text: str) -> str:
        """Extract query pattern for similarity detection"""
        # Remove specific values, keep structure
        pattern = re.sub(r'\b\d+\b', 'NUM', text)
        pattern = re.sub(r'"[^"]*"', 'STR', pattern)
        pattern = re.sub(r'\'[^\']*\'', 'STR', pattern)
        return pattern.lower()
    
    def detect_reformulation(self, new_query: str) -> bool:
        """Detect if query is reformulation of recent query"""
        if len(self.query_patterns) < 2:
            return False
        
        new_pattern = self._extract_pattern(new_query)
        recent_patterns = self.query_patterns[-3:]  # Last 3 queries
        
        # Simple similarity check (could use more sophisticated methods)
        for pattern in recent_patterns:
            if self._pattern_similarity(pattern, new_pattern) > 0.7:
                return True
        
        return False
    
    def _pattern_similarity(self, p1: str, p2: str) -> float:
        """Calculate pattern similarity (simple version)"""
        words1 = set(p1.split())
        words2 = set(p2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)


class AutoDatasetCollector:
    """
    Fully automatic dataset collector using behavioral signals and heuristics.
    
    Key features:
    - No user feedback required
    - Automatic quality assessment
    - Pattern detection for bad responses
    - Session health tracking
    - Smart filtering and validation
    """
    
    def __init__(
        self,
        min_quality_score: float = 0.7,
        min_session_turns: int = 2,
        collection_window_hours: int = 24
    ):
        self.min_quality_score = min_quality_score
        self.min_session_turns = min_session_turns
        self.collection_window = timedelta(hours=collection_window_hours)
        
        # Storage
        self.sessions: Dict[str, SessionContext] = {}
        self.quality_data: List[Tuple[Dict, AutoQualitySignals]] = []
        self.validated_dataset: List[Dict] = []
        
        # Pattern learning
        self.good_patterns = defaultdict(int)
        self.bad_patterns = defaultdict(int)
        
        # Real-time metrics
        self.quality_distribution = []
        self.model_performance = defaultdict(lambda: {"good": 0, "bad": 0})
    
    def track_inference(
        self,
        session_id: str,
        query: str,
        response: str,
        model: str,
        response_time_ms: float,
        **metadata
    ) -> str:
        """
        Track an inference for automatic quality assessment.
        
        Returns:
            Data point ID for tracking
        """
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionContext(
                session_id=session_id,
                start_time=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc)
            )
        
        session = self.sessions[session_id]
        
        # Create quality signals
        signals = AutoQualitySignals(
            response_time_ms=response_time_ms,
            output_length=len(response),
            input_output_ratio=len(response) / max(len(query), 1),
            temperature_used=metadata.get("temperature", 0.7)
        )
        
        # Check for reformulation
        if session.detect_reformulation(query):
            signals.query_reformulated = True
        
        # Content analysis
        signals.has_code_blocks = "```" in response
        signals.has_structured_output = any(marker in response for marker in ["1.", "- ", "* ", "##"])
        signals.has_error_messages = any(err in response.lower() for err in ["error", "exception", "failed"])
        signals.has_apology = any(phrase in response.lower() for phrase in ["sorry", "apologize", "cannot help"])
        signals.truncated_response = response.endswith("...") or len(response) > 3900
        
        # Add to session
        session.add_turn(query, response, response_time_ms)
        
        # Create data point
        data_point = {
            "id": f"{session_id}_{len(session.messages)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "input": query,
            "output": response,
            "model": model,
            "turn_number": len(session.messages),
            "session_duration": (datetime.now(timezone.utc) - session.start_time).total_seconds(),
            **metadata
        }
        
        # Store with signals
        self.quality_data.append((data_point, signals))
        
        # Schedule quality assessment after delay
        self._schedule_quality_assessment(data_point["id"])
        
        return data_point["id"]
    
    def track_user_action(self, data_id: str, action: str, timestamp: Optional[datetime] = None):
        """
        Track user actions to infer quality.
        
        Actions:
        - "next_query": User asked another question
        - "copy_response": User copied the response
        - "close_session": User ended session
        - "modify_response": User edited the response
        - "navigate_away": User left quickly
        """
        timestamp = timestamp or datetime.now(timezone.utc)
        
        # Find the data point
        for i, (data_point, signals) in enumerate(self.quality_data):
            if data_point["id"] == data_id:
                # Update signals based on action
                if action == "next_query":
                    # Calculate time to next query
                    data_time = datetime.fromisoformat(data_point["timestamp"])
                    time_diff = (timestamp - data_time).total_seconds()
                    signals.time_to_next_query = time_diff
                    signals.session_continued = True
                
                elif action == "copy_response":
                    signals.response_copied = True
                
                elif action == "modify_response":
                    signals.response_modified = True
                
                elif action == "navigate_away":
                    # Quick navigation = potentially bad response
                    data_time = datetime.fromisoformat(data_point["timestamp"])
                    if (timestamp - data_time).total_seconds() < 5:
                        signals.time_to_next_query = 5  # Very short
                
                break
    
    def _schedule_quality_assessment(self, data_id: str):
        """
        Schedule quality assessment after a delay.
        In production, this would use a task queue.
        """
        # For now, we'll assess immediately
        # In production: schedule for 30-60 seconds later
        self._assess_quality(data_id)
    
    def _assess_quality(self, data_id: str):
        """Assess quality of a data point"""
        for data_point, signals in self.quality_data:
            if data_point["id"] == data_id:
                # Calculate quality score
                quality_score = signals.calculate_quality_score()
                
                # Update metrics
                self.quality_distribution.append(quality_score)
                
                # Track model performance
                model = data_point["model"]
                if quality_score >= self.min_quality_score:
                    self.model_performance[model]["good"] += 1
                else:
                    self.model_performance[model]["bad"] += 1
                
                # Add to validated dataset if good quality
                if quality_score >= self.min_quality_score:
                    validated_entry = {
                        **data_point,
                        "quality_score": quality_score,
                        "quality_signals": {
                            "time_to_next_query": signals.time_to_next_query,
                            "session_continued": signals.session_continued,
                            "response_copied": signals.response_copied,
                            "has_structured_output": signals.has_structured_output
                        },
                        "auto_validated": True,
                        "validation_method": "behavioral_signals"
                    }
                    self.validated_dataset.append(validated_entry)
                    
                    # Learn patterns
                    pattern = self._extract_success_pattern(data_point)
                    self.good_patterns[pattern] += 1
                else:
                    # Learn failure patterns
                    pattern = self._extract_success_pattern(data_point)
                    self.bad_patterns[pattern] += 1
                
                break
    
    def get_validated_dataset(
        self,
        min_turns_per_session: Optional[int] = None,
        time_window: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """
        Get automatically validated dataset.
        
        Args:
            min_turns_per_session: Minimum conversation turns
            time_window: Only include recent data
            
        Returns:
            List of validated data points
        """
        dataset = []
        min_turns = min_turns_per_session or self.min_session_turns
        cutoff_time = datetime.now(timezone.utc) - (time_window or self.collection_window)
        
        for entry in self.validated_dataset:
            # Time filter
            if datetime.fromisoformat(entry["timestamp"]) < cutoff_time:
                continue
            
            # Session quality filter
            session = self.sessions.get(entry["session_id"])
            if session and len(session.messages) >= min_turns:
                # Add session context
                entry["session_context"] = {
                    "total_turns": len(session.messages),
                    "session_duration": entry["session_duration"],
                    "error_rate": session.error_count / max(len(session.messages), 1),
                    "avg_response_time": session.average_response_time
                }
                dataset.append(entry)
        
        return dataset
    
    def get_quality_insights(self) -> Dict[str, Any]:
        """Get insights about data quality and model performance"""
        if not self.quality_distribution:
            return {}
        
        return {
            "quality_metrics": {
                "average_quality": statistics.mean(self.quality_distribution),
                "median_quality": statistics.median(self.quality_distribution),
                "high_quality_ratio": sum(1 for q in self.quality_distribution if q >= self.min_quality_score) / len(self.quality_distribution)
            },
            "model_performance": dict(self.model_performance),
            "dataset_size": len(self.validated_dataset),
            "active_sessions": len(self.sessions),
            "top_success_patterns": dict(sorted(self.good_patterns.items(), key=lambda x: x[1], reverse=True)[:10]),
            "top_failure_patterns": dict(sorted(self.bad_patterns.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def export_for_training(self) -> Dict[str, Any]:
        """Export dataset formatted for training"""
        dataset = self.get_validated_dataset()
        
        # Group by quality tiers
        high_quality = [d for d in dataset if d["quality_score"] >= 0.8]
        medium_quality = [d for d in dataset if 0.6 <= d["quality_score"] < 0.8]
        
        return {
            "metadata": {
                "collection_method": "automatic_behavioral",
                "total_samples": len(dataset),
                "quality_distribution": {
                    "high": len(high_quality),
                    "medium": len(medium_quality),
                    "average_quality": statistics.mean([d["quality_score"] for d in dataset]) if dataset else 0
                },
                "collection_period": {
                    "start": min(d["timestamp"] for d in dataset) if dataset else None,
                    "end": max(d["timestamp"] for d in dataset) if dataset else None
                }
            },
            "training_data": [
                {
                    "input": d["input"],
                    "output": d["output"],
                    "quality_tier": "high" if d["quality_score"] >= 0.8 else "medium",
                    "model": d["model"],
                    "context": d.get("session_context", {})
                }
                for d in dataset
            ],
            "quality_insights": self.get_quality_insights()
        }
    
    def _extract_success_pattern(self, data_point: Dict) -> str:
        """Extract pattern for learning what works"""
        # Simple pattern: query type + response type
        query = data_point["input"].lower()
        response = data_point["output"].lower()
        
        query_type = "unknown"
        if any(q in query for q in ["how", "what", "why", "when", "where"]):
            query_type = "question"
        elif any(c in query for c in ["create", "make", "build", "write"]):
            query_type = "creation"
        elif any(d in query for d in ["debug", "fix", "error", "problem"]):
            query_type = "debugging"
        
        response_type = "unknown"
        if "```" in data_point["output"]:
            response_type = "code"
        elif any(marker in data_point["output"] for marker in ["1.", "2.", "- ", "* "]):
            response_type = "structured"
        else:
            response_type = "text"
        
        return f"{query_type}:{response_type}"
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old sessions to prevent memory growth"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        
        to_remove = []
        for session_id, session in self.sessions.items():
            if session.last_activity < cutoff:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.sessions[session_id]