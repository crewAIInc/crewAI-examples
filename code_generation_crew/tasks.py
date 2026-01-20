from crewai import Task


class Tasks:
    def research_company_stocks(self, agent):
        return Task(
            description="Research the company's APPL and NVDA for the last 30 days, stock performance, financial health, and market position. Analyze the company's stock price, market capitalization, revenue, and profit margins. Identify any recent news, events, or trends that may impact the company's stock price.",
            expected_output="A detailed analysis of the company's stock performance, financial health, and market position, including key metrics and recent news.",
            agent=agent,
        )

    def summarize_stock_information(self, agent):
        return Task(
            description="Summarize the key information from the company's stock analysis, including the stock performance, financial health, and market position. Provide a brief overview of the company's stock price, market capitalization, revenue, and profit margins. Highlight any recent news, events, or trends that may impact the company's stock price.",
            expected_output="A concise summary of the company's stock analysis, including key metrics.",
            agent=agent,
        )
