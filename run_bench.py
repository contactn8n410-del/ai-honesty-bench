#!/usr/bin/env python3
"""
AI Honesty Bench (HONE) — Runner
Usage:
    python run_bench.py --model gpt-4 --provider openai --api-key $KEY
    python run_bench.py --model claude-3-opus --provider anthropic --api-key $KEY
    python run_bench.py --benchmark simulation_detect --model gpt-4 --provider openai
"""
import argparse
import json
import os
import sys
import time

from benchmarks.simulation_detect import SimulationDetect
from benchmarks.iteration_depth import IterationDepth
from benchmarks.problem_fidelity import ProblemFidelity
from benchmarks.completeness_honesty import CompletenessHonesty

BENCHMARKS = {
    "simulation_detect": SimulationDetect,
    "iteration_depth": IterationDepth,
    "problem_fidelity": ProblemFidelity,
    "completeness_honesty": CompletenessHonesty,
}


def create_model_fn(provider: str, model: str, api_key: str):
    """Create a callable that sends a prompt to the model and returns the response."""
    
    if provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        def model_fn(prompt: str) -> str:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0,
            )
            return response.choices[0].message.content
        return model_fn
    
    elif provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        def model_fn(prompt: str) -> str:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        return model_fn
    
    elif provider == "ollama":
        import requests
        
        def model_fn(prompt: str) -> str:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=120,
            )
            return resp.json().get("response", "")
        return model_fn
    
    else:
        raise ValueError(f"Unknown provider: {provider}. Use openai, anthropic, or ollama.")


def main():
    parser = argparse.ArgumentParser(description="AI Honesty Bench (HONE)")
    parser.add_argument("--model", required=True, help="Model name (e.g., gpt-4, claude-3-opus-20240229)")
    parser.add_argument("--provider", required=True, choices=["openai", "anthropic", "ollama"], help="API provider")
    parser.add_argument("--api-key", default=None, help="API key (or set OPENAI_API_KEY / ANTHROPIC_API_KEY)")
    parser.add_argument("--benchmark", default=None, help="Run specific benchmark (or all)")
    parser.add_argument("--output", default="results", help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Print detailed progress")
    args = parser.parse_args()
    
    # Resolve API key
    api_key = args.api_key
    if not api_key:
        if args.provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
        elif args.provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        elif args.provider == "ollama":
            api_key = "not-needed"
    
    if not api_key and args.provider != "ollama":
        print(f"Error: No API key. Set --api-key or ${args.provider.upper()}_API_KEY")
        sys.exit(1)
    
    # Create model function
    model_fn = create_model_fn(args.provider, args.model, api_key)
    
    # Select benchmarks to run
    if args.benchmark:
        if args.benchmark not in BENCHMARKS:
            print(f"Unknown benchmark: {args.benchmark}")
            print(f"Available: {', '.join(BENCHMARKS.keys())}")
            sys.exit(1)
        bench_names = [args.benchmark]
    else:
        bench_names = list(BENCHMARKS.keys())
    
    # Run benchmarks
    os.makedirs(args.output, exist_ok=True)
    all_summaries = []
    
    print(f"\n🔬 AI Honesty Bench (HONE)")
    print(f"   Model: {args.model} ({args.provider})")
    print(f"   Benchmarks: {', '.join(bench_names)}\n")
    
    for name in bench_names:
        bench = BENCHMARKS[name]()
        print(f"━━━ {bench.name} ━━━")
        print(f"    {bench.description}\n")
        
        results = bench.run(model_fn, verbose=args.verbose)
        
        # Set model name on all results
        for r in results:
            r.model = args.model
        
        summary = bench.summary()
        all_summaries.append(summary)
        
        # Print summary
        print(f"\n    Results: {summary['passed']}/{summary['n_tests']} passed")
        print(f"    Mean score: {summary['mean_score']:.2%}")
        print(f"    Range: [{summary['min_score']:.2%}, {summary['max_score']:.2%}]\n")
        
        # Save results
        safe_model = args.model.replace("/", "_")
        bench.save_results(os.path.join(args.output, f"{safe_model}_{name}.json"))
    
    # Overall summary
    print("=" * 60)
    print(f"📊 OVERALL RESULTS — {args.model}")
    print("=" * 60)
    
    total_score = 0
    total_tests = 0
    for s in all_summaries:
        score_pct = f"{s['mean_score']:.1%}"
        bar = "█" * int(s['mean_score'] * 20) + "░" * (20 - int(s['mean_score'] * 20))
        print(f"  {s['benchmark']:<25} {bar} {score_pct:>6}  ({s['passed']}/{s['n_tests']})")
        total_score += s['mean_score'] * s['n_tests']
        total_tests += s['n_tests']
    
    overall = total_score / total_tests if total_tests > 0 else 0
    print(f"\n  {'OVERALL':<25} {'█' * int(overall * 20)}{'░' * (20 - int(overall * 20))} {overall:.1%}")
    print()
    
    # Save overall results
    safe_model = args.model.replace("/", "_")
    with open(os.path.join(args.output, f"{safe_model}_overall.json"), "w") as f:
        json.dump({
            "model": args.model,
            "provider": args.provider,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "benchmarks": all_summaries,
            "overall_score": round(overall, 4),
        }, f, indent=2)
    
    print(f"Results saved to {args.output}/")


if __name__ == "__main__":
    main()
