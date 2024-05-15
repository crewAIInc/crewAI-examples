#!/usr/bin/env python
from stock_analysis.crew import StockAnalysisCrew


def run():
    # Replace with your inputs, it will automatically interpolate any tasks and agents information
    inputs = {
        'topic': 'AI LLMs'
    }
    StockAnalysisCrew().crew().kickoff(inputs=inputs)