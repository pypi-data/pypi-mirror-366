"""
Dataset Collector Module

Collects production usage data and creates high-quality datasets for prompt optimization.
Implements various strategies to ensure data quality and proper input/output pairing.

Features:
- Session-based tracking for context preservation
- Quality scoring and filtering
- User feedback integration
- Automatic validation
- Privacy-aware data collection

Author: Promptlyzer Team
"""

import uuid
import time
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class CollectionStrategy(Enum):
    """Dataset collection strategies"""
    SESSION_BASED = "session_based"  # Track full conversation sessions
    EXPLICIT_FEEDBACK = "explicit_feedback"  # Collect when user gives feedback
    QUALITY_THRESHOLD = "quality_threshold"  # Collect based on quality metrics
    SAMPLING = "sampling"  # Random sampling with validation


class FeedbackType(Enum):
    """Types of user feedback"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    CORRECTION = "correction"
    RATING = "rating"
    IMPLICIT_GOOD = "implicit_good"  # E.g., user copies the output
    IMPLICIT_BAD = "implicit_bad"  # E.g., user immediately regenerates


@dataclass
class DataPoint:
    """Represents a single data point for dataset"""
    id: str
    session_id: str
    timestamp: datetime
    
    # Core data
    input_text: str
    output_text: str
    model: str
    
    # Context
    system_prompt: Optional[str] = None
    conversation_history: Optional[List[Dict]] = None
    
    # Metadata
    prompt_name: Optional[str] = None
    prompt_version: Optional[str] = None
    project_id: Optional[str] = None
    
    # Quality indicators
    latency_ms: float = 0
    token_count: int = 0
    cost: float = 0
    
    # Validation
    feedback: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    is_validated: bool = False
    validation_method: Optional[str] = None
    
    # Privacy
    contains_pii: bool = False
    is_anonymized: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class DatasetCollector:
    """
    Collects and manages production data for dataset creation.
    
    Implements multiple strategies to ensure high-quality data collection:
    1. Session tracking for maintaining context
    2. Quality scoring based on multiple factors
    3. User feedback integration
    4. Privacy-aware collection
    """
    
    def __init__(
        self,
        strategy: CollectionStrategy = CollectionStrategy.SESSION_BASED,
        quality_threshold: float = 0.7,
        max_buffer_size: int = 1000,
        enable_pii_detection: bool = True
    ):
        """
        Initialize the dataset collector.
        
        Args:
            strategy: Collection strategy to use
            quality_threshold: Minimum quality score for collection
            max_buffer_size: Maximum number of data points to buffer
            enable_pii_detection: Whether to check for PII
        """
        self.strategy = strategy
        self.quality_threshold = quality_threshold
        self.max_buffer_size = max_buffer_size
        self.enable_pii_detection = enable_pii_detection
        
        # Storage
        self.data_buffer: List[DataPoint] = []
        self.sessions: Dict[str, List[DataPoint]] = {}
        self.pending_validations: Dict[str, DataPoint] = {}
        
        # Metrics
        self.collection_stats = {
            "total_collected": 0,
            "validated": 0,
            "rejected": 0,
            "with_feedback": 0
        }
    
    def start_session(self) -> str:
        """Start a new collection session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = []
        return session_id
    
    def collect(
        self,
        session_id: str,
        input_text: str,
        output_text: str,
        model: str,
        **metadata
    ) -> str:
        """
        Collect a new data point.
        
        Args:
            session_id: Session identifier
            input_text: User input
            output_text: Model output
            model: Model used
            **metadata: Additional metadata (prompt_name, latency, etc.)
            
        Returns:
            Data point ID for future reference
        """
        # Create data point
        data_point = DataPoint(
            id=str(uuid.uuid4()),
            session_id=session_id,
            timestamp=datetime.now(timezone.utc),
            input_text=input_text,
            output_text=output_text,
            model=model,
            **{k: v for k, v in metadata.items() if hasattr(DataPoint, k)}
        )
        
        # Check for PII if enabled
        if self.enable_pii_detection:
            data_point.contains_pii = self._detect_pii(input_text, output_text)
        
        # Calculate initial quality score
        data_point.quality_score = self._calculate_quality_score(data_point)
        
        # Add to session
        if session_id in self.sessions:
            self.sessions[session_id].append(data_point)
            # Add conversation history
            if len(self.sessions[session_id]) > 1:
                data_point.conversation_history = [
                    {"role": "user", "content": dp.input_text}
                    for dp in self.sessions[session_id][:-1]
                ]
        
        # Store based on strategy
        if self._should_collect(data_point):
            self._add_to_buffer(data_point)
            self.collection_stats["total_collected"] += 1
        else:
            # Keep for potential validation
            self.pending_validations[data_point.id] = data_point
        
        return data_point.id
    
    def add_feedback(
        self,
        data_point_id: str,
        feedback_type: FeedbackType,
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add user feedback to a data point.
        
        Args:
            data_point_id: ID of the data point
            feedback_type: Type of feedback
            details: Additional feedback details (e.g., rating value, correction text)
            
        Returns:
            True if feedback was added successfully
        """
        # Check both buffer and pending validations
        data_point = None
        
        # Search in buffer
        for dp in self.data_buffer:
            if dp.id == data_point_id:
                data_point = dp
                break
        
        # Search in pending validations
        if not data_point and data_point_id in self.pending_validations:
            data_point = self.pending_validations[data_point_id]
        
        if not data_point:
            return False
        
        # Add feedback
        data_point.feedback = {
            "type": feedback_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        
        # Update validation status based on feedback
        if feedback_type in [FeedbackType.THUMBS_UP, FeedbackType.IMPLICIT_GOOD]:
            data_point.is_validated = True
            data_point.validation_method = "user_positive_feedback"
            data_point.quality_score = min(1.0, data_point.quality_score + 0.3)
        elif feedback_type == FeedbackType.CORRECTION and details and "corrected_output" in details:
            # Create a new validated data point with correction
            corrected_dp = DataPoint(
                id=str(uuid.uuid4()),
                session_id=data_point.session_id,
                timestamp=datetime.now(timezone.utc),
                input_text=data_point.input_text,
                output_text=details["corrected_output"],
                model=data_point.model,
                system_prompt=data_point.system_prompt,
                conversation_history=data_point.conversation_history,
                prompt_name=data_point.prompt_name,
                prompt_version=data_point.prompt_version,
                project_id=data_point.project_id,
                is_validated=True,
                validation_method="user_correction",
                quality_score=1.0,
                feedback={"type": "corrected", "original_id": data_point_id}
            )
            self._add_to_buffer(corrected_dp)
        
        # Move from pending to buffer if now meets criteria
        if (data_point_id in self.pending_validations and 
            data_point.is_validated and 
            data_point.quality_score >= self.quality_threshold):
            self._add_to_buffer(data_point)
            del self.pending_validations[data_point_id]
            self.collection_stats["with_feedback"] += 1
        
        return True
    
    def mark_implicit_feedback(
        self,
        data_point_id: str,
        action: str
    ) -> bool:
        """
        Mark implicit feedback based on user actions.
        
        Args:
            data_point_id: ID of the data point
            action: User action (e.g., "copied", "regenerated", "continued_conversation")
            
        Returns:
            True if feedback was recorded
        """
        feedback_mapping = {
            "copied": FeedbackType.IMPLICIT_GOOD,
            "shared": FeedbackType.IMPLICIT_GOOD,
            "continued_conversation": FeedbackType.IMPLICIT_GOOD,
            "regenerated": FeedbackType.IMPLICIT_BAD,
            "immediate_new_query": FeedbackType.IMPLICIT_BAD
        }
        
        if action in feedback_mapping:
            return self.add_feedback(
                data_point_id,
                feedback_mapping[action],
                {"action": action}
            )
        
        return False
    
    def get_dataset(
        self,
        min_quality_score: Optional[float] = None,
        require_validation: bool = True,
        exclude_pii: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get collected dataset with filtering options.
        
        Args:
            min_quality_score: Minimum quality score filter
            require_validation: Only include validated data points
            exclude_pii: Exclude data points containing PII
            
        Returns:
            List of data points as dictionaries
        """
        dataset = []
        min_score = min_quality_score or self.quality_threshold
        
        for dp in self.data_buffer:
            # Apply filters
            if dp.quality_score < min_score:
                continue
            if require_validation and not dp.is_validated:
                continue
            if exclude_pii and dp.contains_pii and not dp.is_anonymized:
                continue
            
            dataset.append(dp.to_dict())
        
        return dataset
    
    def export_dataset(
        self,
        name: str,
        description: str,
        format: str = "qa_pairs"
    ) -> Dict[str, Any]:
        """
        Export dataset in a specific format.
        
        Args:
            name: Dataset name
            description: Dataset description
            format: Export format (qa_pairs, conversations, raw)
            
        Returns:
            Formatted dataset
        """
        validated_data = self.get_dataset(require_validation=True)
        
        if format == "qa_pairs":
            # Format for Q&A training
            qa_pairs = []
            for dp in validated_data:
                qa_pairs.append({
                    "question": dp["input_text"],
                    "answer": dp["output_text"],
                    "metadata": {
                        "model": dp["model"],
                        "quality_score": dp["quality_score"],
                        "has_feedback": dp["feedback"] is not None
                    }
                })
            
            return {
                "name": name,
                "description": description,
                "type": "qa_dataset",
                "system_context": self._extract_common_system_prompt(validated_data),
                "qa_pairs": qa_pairs,
                "metadata": {
                    "collected_from": "production",
                    "total_pairs": len(qa_pairs),
                    "collection_period": self._get_collection_period(),
                    "average_quality": sum(dp["quality_score"] for dp in validated_data) / len(validated_data) if validated_data else 0
                }
            }
        
        elif format == "conversations":
            # Format for conversation training
            conversations = self._group_by_session(validated_data)
            return {
                "name": name,
                "description": description,
                "type": "conversation_dataset",
                "conversations": conversations,
                "metadata": {
                    "total_conversations": len(conversations),
                    "collection_period": self._get_collection_period()
                }
            }
        
        else:  # raw format
            return {
                "name": name,
                "description": description,
                "type": "raw_dataset",
                "data": validated_data,
                "metadata": {
                    "total_points": len(validated_data),
                    "collection_stats": self.collection_stats
                }
            }
    
    def _should_collect(self, data_point: DataPoint) -> bool:
        """Determine if a data point should be collected based on strategy"""
        if self.strategy == CollectionStrategy.SESSION_BASED:
            # Collect all session data
            return True
        
        elif self.strategy == CollectionStrategy.QUALITY_THRESHOLD:
            # Only collect high-quality responses
            return data_point.quality_score >= self.quality_threshold
        
        elif self.strategy == CollectionStrategy.SAMPLING:
            # Random sampling (could be more sophisticated)
            import random
            return random.random() < 0.1  # 10% sampling rate
        
        elif self.strategy == CollectionStrategy.EXPLICIT_FEEDBACK:
            # Only collect when feedback is provided
            return False  # Will be added when feedback comes
        
        return False
    
    def _calculate_quality_score(self, data_point: DataPoint) -> float:
        """
        Calculate quality score based on multiple factors.
        
        Factors considered:
        - Response length and coherence
        - Latency (faster might indicate cached/good responses)
        - Model confidence (if available)
        - Session context
        """
        score = 0.5  # Base score
        
        # Length ratio (not too short, not too long)
        input_len = len(data_point.input_text.split())
        output_len = len(data_point.output_text.split())
        
        if output_len > 0:
            ratio = output_len / max(input_len, 1)
            if 0.5 <= ratio <= 3.0:
                score += 0.2
            elif 0.2 <= ratio <= 5.0:
                score += 0.1
        
        # Latency factor (lower is generally better)
        if data_point.latency_ms > 0:
            if data_point.latency_ms < 500:
                score += 0.2
            elif data_point.latency_ms < 1000:
                score += 0.1
        
        # Has context (part of conversation)
        if data_point.conversation_history:
            score += 0.1
        
        # No obvious errors (basic check)
        error_indicators = ["error", "sorry", "cannot", "unable", "failed"]
        if not any(indicator in data_point.output_text.lower() for indicator in error_indicators):
            score += 0.1
        
        return min(1.0, score)
    
    def _detect_pii(self, *texts: str) -> bool:
        """
        Basic PII detection (should be enhanced for production).
        
        Checks for:
        - Email addresses
        - Phone numbers
        - SSN patterns
        - Credit card patterns
        """
        import re
        
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
        ]
        
        combined_text = " ".join(texts)
        
        for pattern in pii_patterns:
            if re.search(pattern, combined_text):
                return True
        
        return False
    
    def _add_to_buffer(self, data_point: DataPoint):
        """Add data point to buffer with size management"""
        self.data_buffer.append(data_point)
        
        # Manage buffer size
        if len(self.data_buffer) > self.max_buffer_size:
            # Remove oldest, non-validated entries first
            self.data_buffer = sorted(
                self.data_buffer,
                key=lambda dp: (dp.is_validated, dp.quality_score),
                reverse=True
            )[:self.max_buffer_size]
    
    def _extract_common_system_prompt(self, data_points: List[Dict]) -> Optional[str]:
        """Extract common system prompt from data points"""
        prompts = [dp.get("system_prompt") for dp in data_points if dp.get("system_prompt")]
        if prompts:
            # Return most common
            from collections import Counter
            return Counter(prompts).most_common(1)[0][0]
        return None
    
    def _group_by_session(self, data_points: List[Dict]) -> List[Dict]:
        """Group data points by session for conversation format"""
        from collections import defaultdict
        
        sessions = defaultdict(list)
        for dp in data_points:
            sessions[dp["session_id"]].append(dp)
        
        conversations = []
        for session_id, points in sessions.items():
            # Sort by timestamp
            points.sort(key=lambda x: x["timestamp"])
            
            messages = []
            for point in points:
                messages.append({"role": "user", "content": point["input_text"]})
                messages.append({"role": "assistant", "content": point["output_text"]})
            
            conversations.append({
                "session_id": session_id,
                "messages": messages,
                "metadata": {
                    "duration": (points[-1]["timestamp"] - points[0]["timestamp"]) if len(points) > 1 else 0,
                    "turn_count": len(points)
                }
            })
        
        return conversations
    
    def _get_collection_period(self) -> Dict[str, str]:
        """Get the collection period for the dataset"""
        if not self.data_buffer:
            return {"start": None, "end": None}
        
        timestamps = [dp.timestamp for dp in self.data_buffer]
        return {
            "start": min(timestamps).isoformat(),
            "end": max(timestamps).isoformat()
        }
    
    def clear_buffer(self):
        """Clear the data buffer"""
        self.data_buffer.clear()
        self.sessions.clear()
        self.pending_validations.clear()