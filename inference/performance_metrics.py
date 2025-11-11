"""Performance metrics tracking for model inference."""

import time
from dataclasses import dataclass, asdict
from typing import Optional, List
import statistics


@dataclass
class PerformanceMetrics:
    """Track timing and throughput metrics for inference."""
    
    total_time: float  # seconds
    tokens_generated: int  # Total tokens output
    tokens_per_second: float  # Throughput metric
    input_tokens: int = 0  # Total tokens in input
    total_tokens_processed: int = 0  # input + output tokens
    peak_memory_mb: float = 0.0  # Peak GPU/CPU memory usage
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def __str__(self):
        """Format metrics for display."""
        lines = [
            f"Total Time: {self.total_time:.2f}s",
            f"Tokens Generated: {self.tokens_generated}",
            f"Throughput: {self.tokens_per_second:.2f} tokens/sec",
        ]
        if self.input_tokens > 0:
            lines.append(f"Input Tokens: {self.input_tokens}")
        if self.total_tokens_processed > 0:
            lines.append(f"Total Tokens Processed: {self.total_tokens_processed}")
        if self.peak_memory_mb > 0:
            lines.append(f"Peak Memory: {self.peak_memory_mb:.1f} MB")
        return "\n".join(lines)


@dataclass
class AggregateMetrics:
    """Aggregate metrics across multiple operations."""
    
    num_operations: int
    total_time: float  # seconds
    total_tokens_generated: int
    
    # Statistics
    min_time: float
    max_time: float
    avg_time: float
    
    min_tokens_per_sec: float
    max_tokens_per_sec: float
    avg_tokens_per_sec: float
    
    total_input_tokens: int = 0
    total_tokens_processed: int = 0
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def __str__(self):
        """Format metrics for display."""
        lines = [
            "="*60,
            "PERFORMANCE SUMMARY",
            "="*60,
            f"Operations: {self.num_operations}",
            f"Total Time: {self.total_time:.2f}s",
            f"Avg Time per Operation: {self.avg_time:.2f}s",
            f"Min Time: {self.min_time:.2f}s",
            f"Max Time: {self.max_time:.2f}s",
            "",
            f"Total Tokens Generated: {self.total_tokens_generated}",
            f"Avg Tokens/sec: {self.avg_tokens_per_sec:.2f}",
            f"Min Tokens/sec: {self.min_tokens_per_sec:.2f}",
            f"Max Tokens/sec: {self.max_tokens_per_sec:.2f}",
        ]
        if self.total_input_tokens > 0:
            lines.append(f"Total Input Tokens: {self.total_input_tokens}")
        if self.total_tokens_processed > 0:
            lines.append(f"Total Tokens Processed: {self.total_tokens_processed}")
        lines.append("="*60)
        return "\n".join(lines)


class PerformanceTracker:
    """Track performance metrics across multiple operations."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.start_time: Optional[float] = None
    
    def start(self):
        """Start timing an operation."""
        self.start_time = time.time()
    
    def end(self, tokens_generated: int, input_tokens: int = 0) -> PerformanceMetrics:
        """End timing an operation and record metrics."""
        if self.start_time is None:
            raise RuntimeError("PerformanceTracker.start() not called")
        
        elapsed = time.time() - self.start_time
        tokens_per_sec = tokens_generated / elapsed if elapsed > 0 else 0
        total_tokens = input_tokens + tokens_generated
        
        metrics = PerformanceMetrics(
            total_time=elapsed,
            tokens_generated=tokens_generated,
            tokens_per_second=tokens_per_sec,
            input_tokens=input_tokens,
            total_tokens_processed=total_tokens,
        )
        
        self.metrics.append(metrics)
        self.start_time = None
        return metrics
    
    def aggregate(self) -> AggregateMetrics:
        """Generate aggregate metrics from all tracked operations."""
        if not self.metrics:
            raise ValueError("No metrics recorded")
        
        times = [m.total_time for m in self.metrics]
        throughputs = [m.tokens_per_second for m in self.metrics]
        
        return AggregateMetrics(
            num_operations=len(self.metrics),
            total_time=sum(times),
            total_tokens_generated=sum(m.tokens_generated for m in self.metrics),
            min_time=min(times),
            max_time=max(times),
            avg_time=statistics.mean(times),
            min_tokens_per_sec=min(throughputs),
            max_tokens_per_sec=max(throughputs),
            avg_tokens_per_sec=statistics.mean(throughputs),
            total_input_tokens=sum(m.input_tokens for m in self.metrics),
            total_tokens_processed=sum(m.total_tokens_processed for m in self.metrics),
        )


def count_tokens(text: str, tokenizer) -> int:
    """Count tokens in text using tokenizer."""
    try:
        tokens = tokenizer.encode(text, add_special_tokens=True)
        return len(tokens)
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return max(1, len(text) // 4)
