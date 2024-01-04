from langchain.tools import tool


class CalculatorTools():

  @tool("Make a calcualtion")
  def calculate(operation):
    """Useful to perform any mathematica calculations, 
    like sum, minus, mutiplication, division, etc.
    The input to this tool should be a mathematical 
    expression, a couple examples are `200*7` or `5000/2*10`
    """
    return eval(operation)
