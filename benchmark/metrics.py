# benchmark/metrics.py
#
# Helper functions for capturing performance metrics.
# We measure: time, speed, and memory usage.

import time
import psutil  # reads CPU and RAM from the OS


def get_ram_mb() -> float:
    """
    Returns how much RAM (in MB) the current Python process is using right now.
    We call this BEFORE and AFTER a model inference to see the difference.
    """
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # bytes → MB


def now() -> float:
    """
    Returns the current time in seconds (with sub-millisecond precision).
    Used like a stopwatch: call now() at the start, call now() at the end,
    subtract to get elapsed time.
    """
    return time.perf_counter()


def calc_tokens_per_sec(token_count: int, elapsed_seconds: float) -> float:
    """
    Given how many tokens were generated and how long it took,
    returns tokens per second. Returns 0 if time is basically zero.

    Example: 120 tokens in 3 seconds → 40.0 tokens/sec
    """
    if elapsed_seconds < 0.001:
        return 0.0
    return round(token_count / elapsed_seconds, 2)
