import re
from typing import Dict, Tuple


class BooleanExpressionParser:
    def __init__(self):
        self.variables = {'x', 'y', 'z', 'w'}
        self.operators = {
            '∨': lambda a, b: a or b,
            '∧': lambda a, b: a and b,
            '→': lambda a, b: not a or b,
            '≡': lambda a, b: a == b,
            '¬': lambda a: not a,
        }
    
    def parse_expression(self, expression: str) -> str:
        expr = expression.replace(' ', '').lower()
        
        replacements = {
            'v': '∨',
            '&': '∧', 
            'and': '∧',
            'or': '∨',
            '->': '→',
            '=>': '→',
            '==': '≡',
            '=': '≡',
            'not': '¬',
            '!': '¬',
        }
        
        for old, new in replacements.items():
            expr = expr.replace(old, new)
        
        return expr
    
    def validate_expression(self, expression: str) -> Tuple[bool, str]:
        try:
            expr = self.parse_expression(expression)
            
            variables_in_expr = set(re.findall(r'[xyzw]', expr))
            invalid_vars = variables_in_expr - self.variables
            if invalid_vars:
                return False, f"Invalid variables: {invalid_vars}. Only x, y, z, w are allowed."
            
            if expr.count('(') != expr.count(')'):
                return False, "Unbalanced parentheses"
            
            if not re.match(r'^[xyzw∨∧→≡¬()]+$', expr):
                return False, "Invalid characters in expression"
            
            return True, expr
            
        except Exception as e:
            return False, f"Parse error: {str(e)}"
    
    def evaluate_expression(self, expression: str, values: Dict[str, bool]) -> bool:
        try:
            expr = expression.lower()

            expr = expr.replace('and', ' and ')
            expr = expr.replace('or', ' or ')
            expr = expr.replace('not', ' not ')
            expr = expr.replace(' → ', ' <= ')
            expr = expr.replace('→', ' <= ')
            expr = expr.replace('xor', ' ^ ')
            expr = expr.replace('∧', ' and ')
            expr = expr.replace('∨', ' or ')
            expr = expr.replace('≡', ' == ')
            expr = expr.replace('¬', ' 1- ')

            for var, value in values.items():
                expr = expr.replace(var, str(value))

            return bool(eval(expr))
        except Exception as e:
            raise ValueError(f"Ошибка в выражении: {e}")

