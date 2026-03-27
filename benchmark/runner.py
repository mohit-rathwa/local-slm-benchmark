# benchmark/runner.py
#
# THE MAIN SCRIPT — run this to benchmark all 3 models.
#
# What it does:
#   1. Loops through every model (llama3, mistral, phi3:mini)
#   2. For each model, sends all 15 prompts one by one
#   3. Captures timing + RAM metrics for each inference
#   4. Asks the judge model to score each answer (1-5)
#   5. Saves everything to results/benchmark.csv
#
# Run with:  python -m benchmark.runner
# (from inside the local-slm-benchmark/ folder)

import csv
import os
import time
from datetime import datetime
from pathlib import Path

import ollama
from dotenv import load_dotenv

from benchmark.prompts import PROMPTS
from benchmark.metrics import get_ram_mb, now, calc_tokens_per_sec
from benchmark.judge import score_answer

load_dotenv()  # reads .env file

# ── Configuration ────────────────────────────────────────────────────────────

MODELS = os.getenv("MODELS", "llama3,mistral,phi3:mini").split(",")
RUNS_PER_PROMPT = int(os.getenv("RUNS_PER_PROMPT", "1"))
RESULTS_DIR = Path("benchmark/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# CSV column names — these become the header row in your spreadsheet
CSV_FIELDS = [
    "timestamp",
    "model",
    "prompt_id",
    "category",
    "prompt_text",
    "response_text",
    "time_to_first_token_ms",   # How long until the first word appeared (ms)
    "total_latency_ms",         # Total time from request to last token (ms)
    "tokens_generated",         # How many tokens the model produced
    "tokens_per_sec",           # Speed: tokens / total_latency
    "ram_before_mb",            # RAM usage before the call
    "ram_after_mb",             # RAM usage after the call
    "ram_delta_mb",             # Difference (how much RAM the inference used)
    "quality_score",            # Judge score 1-5 (0 = judge failed)
    "quality_reason",           # Judge's one-sentence explanation
]


# ── Helper: run one inference and capture all metrics ────────────────────────

def run_inference(model: str, prompt_text: str) -> dict:
    """
    Sends one prompt to one model and returns a dict of all metrics.
    Uses streaming so we can measure time-to-first-token accurately.
    """
    ram_before = get_ram_mb()
    full_response = ""
    first_token_time = None
    start = now()

    # ollama.chat with stream=True returns tokens one by one
    # This lets us record WHEN the first token arrives
    stream = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt_text}],
        stream=True,
        options={"temperature": 0.7},
    )

    for chunk in stream:
        token = chunk["message"]["content"]
        if token:
            if first_token_time is None:
                first_token_time = now()  # timestamp of the FIRST token
            full_response += token

    end = now()
    ram_after = get_ram_mb()

    total_latency_ms = round((end - start) * 1000, 1)
    ttft_ms = round((first_token_time - start) * 1000, 1) if first_token_time else 0

    # Estimate token count (Ollama doesn't always return exact count in stream mode)
    # Rough approximation: ~4 characters per token (good enough for benchmarking)
    token_count = len(full_response) // 4

    return {
        "response_text": full_response.strip(),
        "time_to_first_token_ms": ttft_ms,
        "total_latency_ms": total_latency_ms,
        "tokens_generated": token_count,
        "tokens_per_sec": calc_tokens_per_sec(token_count, (end - start)),
        "ram_before_mb": round(ram_before, 1),
        "ram_after_mb": round(ram_after, 1),
        "ram_delta_mb": round(ram_after - ram_before, 1),
    }


# ── Main benchmarking loop ────────────────────────────────────────────────────

def main():
    output_file = RESULTS_DIR / f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"\n Local SLM Benchmark")
    print(f"{'─'*50}")
    print(f"  Models  : {', '.join(MODELS)}")
    print(f"  Prompts : {len(PROMPTS)}")
    print(f"  Runs    : {RUNS_PER_PROMPT} per prompt")
    print(f"  Output  : {output_file}")
    print(f"{'─'*50}\n")

    total_runs = len(MODELS) * len(PROMPTS) * RUNS_PER_PROMPT
    completed = 0

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for model in MODELS:
            print(f"\n[MODEL] {model}")

            for prompt in PROMPTS:
                for run in range(RUNS_PER_PROMPT):
                    completed += 1
                    print(f"  [{completed}/{total_runs}] {prompt['id']} ({prompt['category']})...", end=" ", flush=True)

                    # Step 1: Run the inference
                    try:
                        metrics = run_inference(model, prompt["text"])
                    except Exception as e:
                        print(f"ERROR: {e}")
                        continue

                    print(f"{metrics['tokens_per_sec']} tok/s, {metrics['total_latency_ms']}ms", end=" ")

                    # Step 2: Score the answer with the judge
                    print("→ judging...", end=" ", flush=True)
                    judgment = score_answer(prompt["text"], metrics["response_text"])
                    print(f"score={judgment['score']}")

                    # Step 3: Write the row to CSV
                    row = {
                        "timestamp": datetime.now().isoformat(),
                        "model": model,
                        "prompt_id": prompt["id"],
                        "category": prompt["category"],
                        "prompt_text": prompt["text"][:200],  # truncate for CSV readability
                        "response_text": metrics["response_text"][:500],
                        **metrics,
                        "quality_score": judgment["score"],
                        "quality_reason": judgment["reason"],
                    }
                    writer.writerow(row)
                    f.flush()  # write to disk immediately (so you can open the CSV while running)

                    # Small pause between calls to avoid overwhelming Ollama
                    time.sleep(0.5)

    print(f"\n{'─'*50}")
    print(f"  Done! Results saved to: {output_file}")
    print(f"  Open with Excel, Google Sheets, or the Streamlit dashboard.")
    print(f"{'─'*50}\n")


if __name__ == "__main__":
    main()
