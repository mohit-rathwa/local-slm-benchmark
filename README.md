# Local SLM Benchmark — Project 2

> Compare Llama 3, Mistral 7B, and Phi-3 Mini running **100% offline** on your machine.
> Benchmark inference speed, quality, and resource usage. Document the tradeoffs.

---

## What this project does

This project:
1. Runs 3 local AI models using **Ollama** (no internet needed after setup)
2. Sends 15 prompts across 3 task categories to each model
3. Measures: speed (tokens/sec), latency, RAM usage, and quality score
4. Uses Phi-3 Mini as a **judge model** to automatically score answer quality
5. Wraps everything in a **FastAPI** REST endpoint
6. Visualises results in a **Streamlit** dashboard

---

## Folder structure

```
local-slm-benchmark/
├── README.md                   ← You are here
├── requirements.txt            ← Python dependencies
├── .env.example                ← Copy to .env and edit
│
├── benchmark/
│   ├── prompts.py              ← 15 prompts across 3 categories
│   ├── metrics.py              ← Timing + RAM helpers
│   ├── judge.py                ← LLM-as-judge quality scorer
│   ├── runner.py               ← MAIN SCRIPT — run this first
│   └── results/                ← CSV output goes here
│
├── api/
│   ├── schemas.py              ← Pydantic request/response models
│   └── main.py                 ← FastAPI server
│
└── dashboard/
    └── app.py                  ← Streamlit dashboard
```

---

## Step-by-step setup (beginner friendly)

### STEP 1 — Install Ollama

Ollama is the runtime that downloads and runs AI models locally.

**Mac / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download the installer from https://ollama.com/download

After installing, verify it works:
```bash
ollama --version
```

---

### STEP 2 — Pull the 3 models

This downloads the model weights to your machine (~4–5 GB each).
You only need to do this once. After this, everything works offline.

```bash
ollama pull llama3
ollama pull mistral
ollama pull phi3:mini
```

This will take a few minutes depending on your internet speed.

Check they downloaded correctly:
```bash
ollama list
```

You should see all 3 models listed.

---

### STEP 3 — Clone / download this project

If you have git:
```bash
git clone <your-repo-url>
cd local-slm-benchmark
```

Or just download the ZIP and unzip it, then open a terminal in the folder.

---

### STEP 4 — Create a Python virtual environment

A virtual environment keeps this project's dependencies separate from the rest of your system.

```bash
# Create the environment
python -m venv venv

# Activate it (Mac/Linux):
source venv/bin/activate

# Activate it (Windows):
venv\Scripts\activate
```

You'll know it's active because your terminal prompt shows `(venv)`.

---

### STEP 5 — Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs: ollama, fastapi, uvicorn, instructor, streamlit, psutil, pandas, and others.

---

### STEP 6 — Set up your .env file

```bash
# Mac/Linux:
cp .env.example .env

# Windows:
copy .env.example .env
```

Open `.env` in any text editor. The defaults are fine — you don't need to change anything.

---

### STEP 7 — Start Ollama

Open a new terminal window and run:
```bash
ollama serve
```

Leave this terminal open. Ollama needs to be running for the benchmark to work.

---

### STEP 8 — Run the benchmark

Back in your main terminal (with venv active):
```bash
python -m benchmark.runner
```

You'll see output like:
```
 Local SLM Benchmark
──────────────────────────────────────────────────
  Models  : llama3, mistral, phi3:mini
  Prompts : 15
  Runs    : 1 per prompt
  Output  : benchmark/results/benchmark_20240901_143022.csv
──────────────────────────────────────────────────

[MODEL] llama3
  [1/45] r1 (reasoning)... 42.3 tok/s, 3210ms → judging... score=5
  [2/45] r2 (reasoning)... 38.7 tok/s, 1840ms → judging... score=4
  ...
```

This takes about 20–40 minutes depending on your hardware (45 total runs across 3 models).

---

### STEP 9 — View the dashboard

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 in your browser.

You'll see:
- Quality vs Speed scatter plot (the main tradeoff chart)
- Bar charts by task category
- Latency breakdown
- Full results table with download button

---

### STEP 10 — Start the FastAPI server (optional)

```bash
uvicorn api.main:app --reload
```

Open http://localhost:8000/docs — you get a free interactive API explorer.

Try the `/generate` endpoint by clicking "Try it out", entering a model name and prompt, and clicking Execute.

---

## Understanding the metrics

| Metric | What it means | Better is... |
|--------|---------------|--------------|
| Tokens/sec | How fast the model generates text | Higher |
| Time to first token (ms) | How long until the first word appears | Lower |
| Total latency (ms) | Full response time | Lower |
| RAM delta (MB) | Extra memory used per inference | Lower |
| Quality score (1–5) | Answer quality judged by Phi-3 Mini | Higher |

---

## The tradeoffs you'll document

After running the benchmark, you should be able to write a paragraph like this:

> "Phi-3 Mini is 2.3× faster than Llama 3 (58 vs 25 tok/s) but scores 0.8 points lower on reasoning tasks. For production use cases where privacy is critical and latency matters more than accuracy — such as local code autocomplete — Phi-3 Mini is the right choice. For higher-stakes tasks like summarising sensitive documents, Llama 3's quality advantage justifies the slower speed."

That analysis is what makes this portfolio-grade.

---

## Privacy analysis

To prove no data leaves your machine:

**Mac/Linux:**
```bash
# In a separate terminal, monitor outbound connections while running the benchmark
sudo lsof -i -n | grep ollama
```

You'll see only connections to `127.0.0.1:11434` (localhost) — nothing external.

---

## Cost analysis

| Setup | Cost per 1,000 prompts |
|-------|----------------------|
| OpenAI GPT-4o | ~$5–15 |
| OpenAI GPT-3.5 Turbo | ~$0.50 |
| This project (local) | $0 + electricity (~$0.001) |

---

## Common problems

**"connection refused" when running the benchmark**
→ Start Ollama: `ollama serve`

**"model not found"**
→ Pull the model first: `ollama pull mistral`

**Out of memory / very slow**
→ Try only Phi-3 Mini first (smallest model): edit `.env` → `MODELS=phi3:mini`

**"No benchmark results found" in dashboard**
→ Run `python -m benchmark.runner` first
