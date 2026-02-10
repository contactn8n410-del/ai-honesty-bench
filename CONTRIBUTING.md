# Contributing to AI Honesty Bench

## How to Contribute

### Adding Test Cases
Each benchmark needs more test cases. Add them to the relevant file in `benchmarks/`:

1. `simulation_detect.py` — Scripts where models might fabricate output
2. `iteration_depth.py` — Problems requiring multiple iterations
3. `problem_fidelity.py` — Problems with strict verifiable constraints
4. `completeness_honesty.py` — Tasks too complex for a single response

### Running on New Models
```bash
python run_bench.py --model YOUR_MODEL --provider YOUR_PROVIDER --api-key YOUR_KEY
```
Submit results as a PR to add to the leaderboard.

### Improving Evaluation
The current evaluation uses heuristic keyword matching. We need:
- More sophisticated NLP-based evaluation
- Human validation of edge cases
- LLM-as-judge evaluation (using a separate model to evaluate responses)

## Code Style
- Python 3.10+
- Type hints where practical
- Docstrings for all public classes/functions

## License
By contributing, you agree that your contributions will be licensed under MIT.
