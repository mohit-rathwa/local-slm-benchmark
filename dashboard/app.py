# dashboard/app.py
#
# The Streamlit dashboard — your visual portfolio piece.
# It reads the CSV produced by runner.py and shows interactive charts.
#
# Run with:  streamlit run dashboard/app.py
# Then open: http://localhost:8501

import glob
import os

import pandas as pd
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Local SLM Benchmark",
    page_icon="🤖",
    layout="wide",
)

st.title("Local SLM Benchmark Dashboard")
st.caption("Comparing Llama 3, Mistral 7B, and Phi-3 Mini — running 100% offline on local hardware.")

# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    """
    Finds the most recent benchmark CSV and loads it into a DataFrame.
    @st.cache_data means Streamlit only reloads when the file changes.
    """
    files = sorted(glob.glob("benchmark/results/benchmark_*.csv"))
    if not files:
        return None
    return pd.read_csv(files[-1])  # most recent file


df = load_data()

if df is None:
    st.warning("No benchmark results found yet.")
    st.info("Run the benchmark first:\n```\npython -m benchmark.runner\n```")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────

st.sidebar.header("Filters")

selected_models = st.sidebar.multiselect(
    "Models",
    options=df["model"].unique().tolist(),
    default=df["model"].unique().tolist(),
)

selected_categories = st.sidebar.multiselect(
    "Task categories",
    options=df["category"].unique().tolist(),
    default=df["category"].unique().tolist(),
)

filtered = df[
    df["model"].isin(selected_models) &
    df["category"].isin(selected_categories)
]

if filtered.empty:
    st.warning("No data matches your filters.")
    st.stop()

# ── Summary metrics row ────────────────────────────────────────────────────────

st.subheader("Overall summary")
cols = st.columns(len(selected_models))

for i, model in enumerate(selected_models):
    m_df = filtered[filtered["model"] == model]
    avg_score = m_df["quality_score"].mean()
    avg_speed = m_df["tokens_per_sec"].mean()
    avg_latency = m_df["total_latency_ms"].mean()

    with cols[i]:
        st.metric("Model", model)
        st.metric("Avg quality score", f"{avg_score:.1f} / 5")
        st.metric("Avg speed (tok/s)", f"{avg_speed:.1f}")
        st.metric("Avg latency (ms)", f"{avg_latency:.0f}")

st.divider()

# ── Quality vs Speed scatter plot (the centrepiece chart) ─────────────────────

st.subheader("Quality vs Speed — the core tradeoff")
st.caption("Each point = one model's average across all prompts in the selected category. Higher = better quality. Further right = faster.")

scatter_data = (
    filtered.groupby(["model", "category"])
    .agg(
        avg_quality=("quality_score", "mean"),
        avg_speed=("tokens_per_sec", "mean"),
    )
    .reset_index()
)

# Streamlit's built-in scatter chart
st.scatter_chart(
    scatter_data,
    x="avg_speed",
    y="avg_quality",
    color="model",
    size="avg_quality",
)

st.divider()

# ── Per-category bar charts ───────────────────────────────────────────────────

st.subheader("Quality score by category")

col_a, col_b = st.columns(2)

with col_a:
    quality_pivot = (
        filtered.groupby(["category", "model"])["quality_score"]
        .mean()
        .unstack("model")
        .round(2)
    )
    st.caption("Average quality score (1–5) per task type")
    st.bar_chart(quality_pivot)

with col_b:
    speed_pivot = (
        filtered.groupby(["category", "model"])["tokens_per_sec"]
        .mean()
        .unstack("model")
        .round(1)
    )
    st.caption("Average tokens/sec per task type")
    st.bar_chart(speed_pivot)

st.divider()

# ── Latency comparison ────────────────────────────────────────────────────────

st.subheader("Latency breakdown")
col_c, col_d = st.columns(2)

with col_c:
    ttft = (
        filtered.groupby("model")["time_to_first_token_ms"]
        .mean()
        .round(0)
        .rename("Time to first token (ms)")
    )
    st.caption("Lower = more responsive (time until first word appears)")
    st.bar_chart(ttft)

with col_d:
    ram = (
        filtered.groupby("model")["ram_delta_mb"]
        .mean()
        .round(1)
        .rename("RAM delta (MB)")
    )
    st.caption("Average extra RAM used per inference")
    st.bar_chart(ram)

st.divider()

# ── Raw results table ─────────────────────────────────────────────────────────

st.subheader("Raw results")
st.caption("All individual benchmark runs")

show_cols = [
    "model", "category", "prompt_id",
    "tokens_per_sec", "total_latency_ms", "time_to_first_token_ms",
    "ram_delta_mb", "quality_score", "quality_reason",
]

st.dataframe(
    filtered[show_cols].sort_values(["model", "category"]),
    use_container_width=True,
    hide_index=True,
)

# Download button
csv_bytes = filtered.to_csv(index=False).encode()
st.download_button(
    label="Download CSV",
    data=csv_bytes,
    file_name="benchmark_results.csv",
    mime="text/csv",
)
