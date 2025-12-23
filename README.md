# Crypto Analysis Agent

A Python-based interactive tool that uses OpenAI GPT models to fetch cryptocurrency market data, perform technical and sentiment analysis, generate predictions, and provide actionable advice. Outputs are returned in JSON and saved to CSV for further analysis.

---

## Features

- Fetches real-time market data for any cryptocurrency.
- Performs technical and sentiment analysis using AI.
- Generates probabilistic predictions and investment advice.
- Outputs structured JSON reports.
- Saves reports to CSV automatically.
- Interactive command-line interface.

---

## Requirements

- Python 3.9+
- `openai` Python package (`pip install openai`)

---

## Environment Variables

Set the following environment variables before running:

```bash
export OPENAI_API_KEY="your_openai_api_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
