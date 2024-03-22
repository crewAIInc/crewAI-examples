from langchain.tools import tool

class CalculatorTools():

    @tool("Make a calculation")
    def calculate(operation):
        """This tool is useful for performing various mathematical 
            calculations such as addition, subtraction, multiplication, 
            division, etc. Input to the tool should be a mathematical 
            expression. Examples include 200*7 or 5000/2*10.
        """
        try:
            return eval(operation)
        except SyntaxError:
            return "Error: Invalid syntax in mathematical expression"
