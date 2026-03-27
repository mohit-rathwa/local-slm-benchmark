# benchmark/judge.py
#
# This file scores the quality of each model's answer using Phi-3 Mini as a judge.
# Instead of manually reading 45 responses (15 prompts × 3 models), we ask a small
# model to score each answer from 1 to 5 using a clear rubric.
#
# This technique is called "LLM-as-Judge" and is widely used in AI research.

import ollama
import re


# The scoring rubric we give to the judge model.
# A clear rubric = more consistent, reliable scores.
JUDGE_SYSTEM_PROMPT = """You are an objective answer quality evaluator.

Score the given answer from 1 to 5 using ONLY this rubric:

5 - Correct, complete, well-structured. Directly addresses the question with no errors.
4 - Mostly correct, minor gaps or slight verbosity. Usable in production.
3 - Partially correct. Missing key points or contains minor factual errors.
2 - Mostly incorrect or significantly off-topic. Would mislead the user.
1 - Wrong, hallucinated, or refused to answer.

Respond with ONLY a JSON object in this exact format (no other text):
{"score": <integer 1-5>, "reason": "<one sentence explanation>"}"""


def score_answer(prompt: str, answer: str, judge_model: str = "phi3:mini") -> dict:
    """
    Sends the original prompt + the model's answer to the judge model.
    Returns a dict with 'score' (int 1-5) and 'reason' (string).

    If the judge fails or returns something unexpected, we return score=0
    so we know to flag it rather than silently corrupt the data.
    """
    judge_prompt = f"""ORIGINAL QUESTION:
{prompt}

ANSWER TO SCORE:
{answer}

Score this answer using the rubric. Reply with JSON only."""

    try:
        response = ollama.chat(
            model=judge_model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": judge_prompt},
            ],
            options={"temperature": 0},  # temperature=0 → deterministic, consistent scoring
        )

        raw = response["message"]["content"].strip()

        # Try to extract JSON even if the model added extra text around it
        json_match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if json_match:
            import json
            data = json.loads(json_match.group())
            score = int(data.get("score", 0))
            reason = str(data.get("reason", ""))
            # Clamp score to valid range
            score = max(1, min(5, score))
            return {"score": score, "reason": reason}

    except Exception as e:
        print(f"    [judge error] {e}")

    # Fallback if anything goes wrong
    return {"score": 0, "reason": "judge failed"}
