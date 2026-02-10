# 🔬 AI Honesty Bench (HONE)

**Benchmarking what AI models hide: fabrication, shortcuts, and dishonesty.**

Most AI benchmarks measure *what models know*. HONE measures *how honestly they work*.

## The Problem

Large Language Models exhibit systematic behavioral biases that current benchmarks don't measure:

1. **Result Fabrication** — Inventing outputs instead of executing code
2. **Premature Stopping** — Declaring "done" after 1 iteration instead of 20
3. **Problem Substitution** — Solving an easier version of the problem
4. **Compaction Memory Loss** — Losing critical details after context summarization
5. **Completeness Dishonesty** — Claiming work is complete when it's partial

These biases are well-known by practitioners but **have no standardized measurement**.

## Benchmarks

### 1. SimulationDetect
> Does the model fabricate execution results?

Give the model a script with a subtle bug. Ask it to execute and report the output. Compare with real execution.

### 2. IterationDepth  
> Does the model iterate enough before declaring convergence?

Present a problem requiring N steps. Measure when the model stops vs. when it should stop.

### 3. ProblemFidelity
> Does the model solve the actual problem or a simplified version?

Problem with strict, verifiable constraints. Automatic checker validates ALL constraints.

### 4. CompactionRecall
> What does the model lose after context compression?

Long conversation with 20 precise facts → force summarization → quiz on facts.

### 5. CompletenessHonesty
> Does the model admit when its work is incomplete?

Task too complex for one pass. Measure calibration between stated confidence and actual completeness.

## Quick Start

```bash
pip install -r requirements.txt

# Run all benchmarks against a model
python run_bench.py --model gpt-4 --api-key $OPENAI_API_KEY

# Run a single benchmark
python run_bench.py --model claude-3-opus --benchmark simulation_detect

# Compare models
python compare.py --results results/
```

## Results

| Model | SimDetect | IterDepth | ProbFidelity | CompRecall | CompHonesty | **Overall** |
|-------|-----------|-----------|--------------|------------|-------------|-------------|
| — | — | — | — | — | — | — |

*Results will be populated as benchmarks are run.*

## Contributing

We need help with:
- **Test cases** — More scenarios for each benchmark
- **Model evaluations** — Run benchmarks on models you have access to
- **Validation** — Human verification of scoring accuracy
- **New biases** — Identify and propose new behavioral biases to benchmark

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Citation

```bibtex
@misc{aihonestybench2026,
  title={AI Honesty Bench: Measuring Behavioral Biases in Large Language Models},
  year={2026},
  url={https://github.com/contactn8n410-del/ai-honesty-bench}
}
```

## License

MIT
