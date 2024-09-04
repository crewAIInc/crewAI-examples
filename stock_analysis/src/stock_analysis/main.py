import sys
from stock_analysis.crew import StockAnalysisCrew

def run():
    inputs = {
        'query': 'What is the best running shoe for beginner',
        'company_stock': 'AMZN',
    }
    StockAnalysisCrew().crew().kickoff(inputs=inputs)



def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'query': 'What is last years revenue',
        'company_stock': 'AMZN',
    }
    try:
        StockAnalysisCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")
