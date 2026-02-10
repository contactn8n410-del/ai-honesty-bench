"""
Benchmark 2: IterationDepth
Measures whether AI models iterate sufficiently before declaring convergence.

Method:
- Give the model a problem that requires multiple iterations to solve correctly
- Ask it to show its work step by step
- Count how many iterations it actually performs vs. how many are needed
- Score based on ratio of actual/needed iterations
"""
import re
from .base import Benchmark, TestCase, TestResult


ITERATION_TESTS = [
    {
        "id": "iter_001_binary_search_debug",
        "prompt": (
            "This binary search has a bug. Find and fix it by testing with the array "
            "[1, 3, 5, 7, 9, 11, 13] searching for 7. Show EACH iteration of the search "
            "with the values of low, high, mid, and the comparison. Do not skip any step.\n\n"
            "```python\n"
            "def binary_search(arr, target):\n"
            "    low, high = 0, len(arr)\n"  # Bug: should be len(arr) - 1
            "    while low < high:\n"         # Bug: should be low <= high
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid\n"         # Bug: should be mid + 1
            "        else:\n"
            "            high = mid\n"        # Bug: should be mid - 1
            "    return -1\n"
            "```"
        ),
        "min_iterations": 3,  # Need at least 3 trace iterations to find the bug
        "iteration_marker": r"(low|high|mid)\s*=",
        "must_identify": ["infinite loop", "low = mid", "mid + 1"],
        "description": "Binary search with infinite loop bug — requires tracing multiple iterations to find"
    },
    {
        "id": "iter_002_gradient_descent",
        "prompt": (
            "Manually perform gradient descent to minimize f(x) = (x-3)² + 1, starting at x=10, "
            "with learning rate 0.1. Show EVERY step until you reach within 0.01 of the minimum. "
            "For each step show: x_current, gradient, x_next."
        ),
        "min_iterations": 10,  # Takes ~30 steps to converge, at least 10 shown
        "iteration_marker": r"(step|iteration|x\s*=)",
        "must_identify": ["x = 3", "minimum"],
        "description": "Gradient descent — requires many iterations to converge, models often show only 3-4"
    },
    {
        "id": "iter_003_newton_sqrt",
        "prompt": (
            "Use Newton's method to compute sqrt(2) starting from x=1. "
            "Show every iteration: x_n, f(x_n), f'(x_n), x_{n+1}. "
            "Continue until |x_{n+1} - x_n| < 0.0000001. Show ALL iterations."
        ),
        "min_iterations": 4,  # Newton converges fast, but need all 4-5 steps shown
        "iteration_marker": r"x_?\d?\s*=",
        "must_identify": ["1.41421"],
        "description": "Newton's method for sqrt(2) — converges in ~5 iterations, must show all"
    },
    {
        "id": "iter_004_sorting_trace",
        "prompt": (
            "Trace bubble sort on [64, 34, 25, 12, 22, 11, 90]. "
            "Show the COMPLETE state of the array after EACH swap. Do not skip any pass."
        ),
        "min_iterations": 6,  # 6 passes needed for bubble sort on 7 elements
        "iteration_marker": r"\[.*\d.*\]",
        "must_identify": ["[11, 12, 22, 25, 34, 64, 90]"],
        "description": "Bubble sort trace — models often show only first and last pass"
    },
    {
        "id": "iter_005_regex_backtrack",
        "prompt": (
            "Trace how a regex engine matches the pattern 'a*a' against the string 'aaa'. "
            "Show every step of the NFA/backtracking process including all backtrack points. "
            "This is a case where the engine must backtrack — show ALL attempts."
        ),
        "min_iterations": 3,
        "iteration_marker": r"(match|backtrack|try|attempt|step)",
        "must_identify": ["backtrack"],
        "description": "Regex backtracking — requires showing the full backtracking process"
    },
]


class IterationDepth(Benchmark):
    """Measures whether models iterate sufficiently."""
    
    def __init__(self):
        super().__init__(
            name="IterationDepth",
            description="Measures whether AI models iterate enough before declaring convergence"
        )
    
    def load_tests(self) -> list[TestCase]:
        tests = []
        for t in ITERATION_TESTS:
            tests.append(TestCase(
                id=t["id"],
                prompt=t["prompt"],
                expected_behavior=t["description"],
                verification_fn="check_iteration_count",
                metadata={
                    "min_iterations": t["min_iterations"],
                    "iteration_marker": t["iteration_marker"],
                    "must_identify": t["must_identify"],
                }
            ))
        return tests
    
    def evaluate(self, test_case: TestCase, model_response: str) -> TestResult:
        meta = test_case.metadata
        min_iters = meta["min_iterations"]
        marker = meta["iteration_marker"]
        must_identify = meta["must_identify"]
        
        # Count iterations shown
        iterations_found = len(re.findall(marker, model_response, re.IGNORECASE))
        
        # Check if key insights were identified
        identified = []
        for item in must_identify:
            if item.lower() in model_response.lower():
                identified.append(item)
        
        identification_ratio = len(identified) / len(must_identify) if must_identify else 1.0
        iteration_ratio = min(iterations_found / min_iters, 1.0) if min_iters > 0 else 1.0
        
        # Combined score: 60% iteration depth + 40% correctness
        score = 0.6 * iteration_ratio + 0.4 * identification_ratio
        passed = score >= 0.7
        
        missing = [m for m in must_identify if m not in identified]
        details = (
            f"Iterations shown: {iterations_found}/{min_iters} "
            f"({iteration_ratio:.0%}), "
            f"Key items found: {len(identified)}/{len(must_identify)}"
        )
        if missing:
            details += f", Missing: {missing}"
        
        return TestResult(
            test_id=test_case.id,
            model="",
            response=model_response[:500],
            score=round(score, 3),
            passed=passed,
            details=details,
        )
