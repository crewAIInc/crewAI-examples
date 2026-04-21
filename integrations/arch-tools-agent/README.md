# CrewAI + Arch Tools Integration

Give your CrewAI agents access to **58+ real-world API tools** — web scraping, search, crypto data, sentiment analysis, OCR, hashing, and more — through a single API key.

## What is Arch Tools?

[Arch Tools](https://archtools.dev) provides a unified API for 58+ tools that AI agents need in the real world. One API key, one SDK, pay-per-call or use free credits.

**Key features:**
- 🔍 Web search & scraping
- 💰 Crypto prices & market data
- 🧠 AI text generation & summarization
- 📊 Sentiment analysis
- 🔐 Hashing, UUIDs, email verification
- 📷 Screenshots & OCR
- ⚡ x402 crypto payments (pay-per-call with USDC)

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get your API keys

- **Arch Tools**: Sign up free at [archtools.dev](https://archtools.dev) (250 free credits)
- **OpenAI**: For the LLM powering the agent (or swap for any CrewAI-supported model)

### 3. Set environment variables

```bash
export ARCH_TOOLS_API_KEY=arch_your_key_here
export OPENAI_API_KEY=sk-your_key_here
```

### 4. Run

```bash
python main.py
```

## How It Works

This example wraps Arch Tools endpoints as CrewAI `BaseTool` subclasses:

| CrewAI Tool | Arch Tools Endpoint | What it does |
|---|---|---|
| `WebScrapeTool` | `web_scrape()` | Extract text from any URL |
| `WebSearchTool` | `search_web()` | Search the web |
| `CryptoPriceTool` | `crypto_price()` | Live crypto prices |
| `SentimentTool` | `sentiment_analysis()` | Analyze text sentiment |
| `SummarizeTool` | `summarize()` | Bullet-point summaries |

The pattern is simple — any of Arch Tools' 58+ endpoints can become a CrewAI tool in ~10 lines:

```python
from crewai.tools import BaseTool
from arch_tools import ArchTools

arch = ArchTools(api_key="arch_your_key_here")

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "What this tool does"

    def _run(self, input: str) -> str:
        return str(arch.call("tool-name", param=input))
```

## Extend It

Arch Tools has 58+ tools you can wrap. Some ideas:

```python
# Screenshot any webpage
class ScreenshotTool(BaseTool):
    name: str = "screenshot"
    description: str = "Capture a screenshot of any URL"
    def _run(self, url: str) -> str:
        return str(arch.screenshot_capture(url))

# Verify an email address
class EmailVerifyTool(BaseTool):
    name: str = "email_verify"
    description: str = "Check if an email address is valid and deliverable"
    def _run(self, email: str) -> str:
        return str(arch.email_verify(email))

# Extract text from images (OCR)
class OCRTool(BaseTool):
    name: str = "ocr"
    description: str = "Extract text from an image URL"
    def _run(self, image_url: str) -> str:
        return str(arch.ocr_extract(image_url))
```

## Links

- [Arch Tools API Docs](https://archtools.dev/docs)
- [Arch Tools Python SDK](https://pypi.org/project/arch-tools/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Full tool list](https://archtools.dev/docs#tools)

## License

MIT
