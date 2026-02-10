"""Base class for all HONE benchmarks."""
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class TestCase:
    """A single test case for a benchmark."""
    id: str
    prompt: str
    expected_behavior: str  # Description of what an honest model should do
    verification_fn: str    # Name of the verification function
    metadata: dict = field(default_factory=dict)


@dataclass 
class TestResult:
    """Result of running a single test case."""
    test_id: str
    model: str
    response: str
    score: float           # 0.0 (dishonest) to 1.0 (perfectly honest)
    passed: bool
    details: str           # Human-readable explanation
    latency_ms: float = 0
    timestamp: str = ""

    def to_dict(self):
        return asdict(self)


class Benchmark(ABC):
    """Abstract base class for HONE benchmarks."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.test_cases: list[TestCase] = []
        self.results: list[TestResult] = []
    
    @abstractmethod
    def load_tests(self) -> list[TestCase]:
        """Load test cases for this benchmark."""
        pass
    
    @abstractmethod
    def evaluate(self, test_case: TestCase, model_response: str) -> TestResult:
        """Evaluate a model's response to a test case."""
        pass
    
    def run(self, model_fn, verbose: bool = False) -> list[TestResult]:
        """Run all test cases against a model function.
        
        Args:
            model_fn: Callable that takes a prompt string and returns a response string.
            verbose: Print progress.
        
        Returns:
            List of TestResult objects.
        """
        self.test_cases = self.load_tests()
        self.results = []
        
        for i, tc in enumerate(self.test_cases):
            if verbose:
                print(f"  [{i+1}/{len(self.test_cases)}] {tc.id}...")
            
            start = time.time()
            response = model_fn(tc.prompt)
            latency = (time.time() - start) * 1000
            
            result = self.evaluate(tc, response)
            result.latency_ms = latency
            result.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self.results.append(result)
            
            if verbose:
                status = "✅" if result.passed else "❌"
                print(f"    {status} score={result.score:.2f} — {result.details[:80]}")
        
        return self.results
    
    def summary(self) -> dict:
        """Return summary statistics."""
        if not self.results:
            return {"benchmark": self.name, "n_tests": 0}
        
        scores = [r.score for r in self.results]
        passed = sum(1 for r in self.results if r.passed)
        
        return {
            "benchmark": self.name,
            "n_tests": len(self.results),
            "passed": passed,
            "failed": len(self.results) - passed,
            "mean_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
        }
    
    def save_results(self, path: str):
        """Save results to JSON file."""
        data = {
            "benchmark": self.name,
            "description": self.description,
            "summary": self.summary(),
            "results": [r.to_dict() for r in self.results],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
