import os
import json
import csv
import time
import logging
from typing import Dict
from datetime import datetime
from openai import OpenAI

# =========================================================
# Environment & Configuration
# =========================================================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")
if not OPENAI_BASE_URL:
    raise RuntimeError("OPENAI_BASE_URL not set")

MODEL = "gpt-4o"
DELAY_BETWEEN_CALLS = 25

# =========================================================
# Logging
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# OpenAI Client
# =========================================================

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

# =========================================================
# Helpers
# =========================================================

def call_llm_rate_limited(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
    is_first_call: bool = False,
) -> str:
    if not is_first_call:
        time.sleep(DELAY_BETWEEN_CALLS)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=4000,
    )

    return response.choices[0].message.content.strip()


def parse_json(raw: str) -> Dict:
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    return json.loads(raw.strip())

# =========================================================
# API Call 1
# =========================================================

def fetch_market_and_analysis(crypto_name: str) -> Dict:
    system_prompt = (
        "You are an expert cryptocurrency analyst with real-time market data access. "
        "Provide market data, technical analysis, and sentiment analysis. "
        "Return ONLY valid JSON using December 2025 conditions."
    )

    user_prompt = (
        f"Analyze {crypto_name} cryptocurrency and return a single JSON object "
        "containing market_data, technical_analysis, and sentiment_analysis."
    )

    raw = call_llm_rate_limited(system_prompt, user_prompt, is_first_call=True)
    return parse_json(raw)

# =========================================================
# API Call 2
# =========================================================

def generate_predictions_and_advice(crypto_name: str, analysis: Dict) -> Dict:
    system_prompt = (
        "You are an advanced crypto prediction and advisory AI. "
        "Generate realistic probabilistic predictions and advice. "
        "Return ONLY valid JSON."
    )

    raw = call_llm_rate_limited(
        system_prompt=system_prompt,
        user_prompt=json.dumps(analysis),
        temperature=0.4,
        is_first_call=False,
    )

    return parse_json(raw)

# =========================================================
# Core Agent
# =========================================================

def crypto_analysis_agent(crypto_name: str) -> Dict:
    analysis = fetch_market_and_analysis(crypto_name)
    predictions = generate_predictions_and_advice(crypto_name, analysis)

    return {
        "cryptocurrency": analysis["market_data"],
        "technical_analysis": analysis["technical_analysis"],
        "sentiment_analysis": analysis["sentiment_analysis"],
        "predictions": predictions["predictions"],
        "advice": predictions["advice"],
        "timestamp": datetime.now().isoformat(),
        "disclaimer": "NOT FINANCIAL ADVICE. HIGH RISK. DYOR.",
    }

# =========================================================
# Persistence
# =========================================================

def save_to_csv(report: Dict, filename: str):
    crypto = report["cryptocurrency"]
    preds = report["predictions"]
    adv = report["advice"]

    rows = []
    for pred in preds:
        rows.append({
            "cryptocurrency": crypto["name"],
            "symbol": crypto["symbol"],
            "current_price": crypto["current_price_usd"],
            "timeframe": pred["timeframe"],
            "low_estimate": pred["low_estimate"],
            "mid_estimate": pred["mid_estimate"],
            "high_estimate": pred["high_estimate"],
            "probability_up": pred["probability_up"],
            "probability_down": pred["probability_down"],
            "confidence": pred["confidence_level"],
            "recommendation": adv["overall_recommendation"],
            "risk_level": adv["risk_level"],
            "timestamp": report["timestamp"],
        })

    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

# =========================================================
# Interactive Loop
# =========================================================

def run_interactive():
    while True:
        crypto_name = input("Enter cryptocurrency name (or 'quit'): ").strip()
        if crypto_name.lower() in {"quit", "exit", "q"}:
            break
        if not crypto_name:
            continue

        try:
            report = crypto_analysis_agent(crypto_name)

            # ✅ ONLY REQUEST RESULT OUTPUT
            print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)

            symbol = report["cryptocurrency"]["symbol"].lower()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_to_csv(report, f"{symbol}_analysis_{ts}.csv")

        except Exception as e:
            logger.error(e)

# =========================================================
# Entry Point
# =========================================================

def main():
    run_interactive()

if __name__ == "__main__":
    main()