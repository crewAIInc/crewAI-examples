# E-commerce Scraper

A Python-based web scraping tool built with CrewAI and ScrapegraphAI ([Scrapegraph](https://scrapegraph.ai/)) that extracts product information from e-commerce websites. Currently configured to scrape keyboard listings from eBay Italy.

## Features

- Automated web scraping using CrewAI agents
- Integration with Scrapegraph for reliable data extraction
- Configurable for different product searches
- Environment-based configuration for API keys

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Scrapegraph API key

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ecommerce-scraper
   ```

2. Install the required dependencies:
   ```bash
   pip install crewai crewai-tools python-dotenv
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your API keys to the `.env` file:
   ```plaintext
   OPENAI_API_KEY="your_openai_api_key"
   SCRAPEGRAPH_API_KEY="your_scrapegraph_api_key"
   ```

## Usage

Run the scraper:
```bash
python ecommerce_scraper.py
```

The script will:
1. Connect to eBay Italy
2. Search for keyboards
3. Extract product information
4. Output the results

## Customization

To scrape different products or websites, modify the `website` variable in `ecommerce_scraper.py`:

```python
website = "https://www.ebay.it/sch/i.html?_from=R40&_trksid=m570.l1313&_nkw=your_search_term&_sacat=0"
```

Replace `your_search_term` with the product you want to search for.

## License

[Add your chosen license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.