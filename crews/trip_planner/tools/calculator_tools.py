from crewai.tools import tool
import ast
import operator
import re

class CalculatorTools():

    @tool("Make a calculation")
    def calculate(operation: str) -> str:
        """Useful to perform any mathematical calculations, 
        like sum, minus, multiplication, division, etc.
        
        Args:
            operation: A mathematical expression to evaluate (e.g., "200*7" or "5000/2*10")
        
        Returns:
            The result of the calculation or an error message
        """
        try:
            # Define allowed operators for safe evaluation
            allowed_operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.USub: operator.neg,
                ast.UAdd: operator.pos,
            }
            
            # Parse and validate the expression
            if not re.match(r'^[0-9+\-*/().% ]+$', operation):
                return "Error: Invalid characters in mathematical expression"
            
            # Parse the expression
            tree = ast.parse(operation, mode='eval')
            
            def _eval_node(node):
                if isinstance(node, ast.Expression):
                    return _eval_node(node.body)
                elif isinstance(node, ast.Constant):  # Python 3.8+
                    return node.value
                elif isinstance(node, ast.Num):  # Python < 3.8
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = _eval_node(node.left)
                    right = _eval_node(node.right)
                    op = allowed_operators.get(type(node.op))
                    if op is None:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(left, right)
                elif isinstance(node, ast.UnaryOp):
                    operand = _eval_node(node.operand)
                    op = allowed_operators.get(type(node.op))
                    if op is None:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(operand)
                else:
                    raise ValueError(f"Unsupported node type: {type(node).__name__}")
            
            result = _eval_node(tree)
            return result
            
        except (SyntaxError, ValueError, ZeroDivisionError, TypeError) as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return "Error: Invalid mathematical expression"
