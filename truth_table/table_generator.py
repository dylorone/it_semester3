from typing import Any, Dict, List
from parser import BooleanExpressionParser


class TruthTableGenerator:
    def __init__(self):
        self.parser = BooleanExpressionParser()
    
    def generate_truth_table(self, expression: str) -> List[Dict[str, Any]]:
        is_valid, parsed_expr = self.parser.validate_expression(expression)
        if not is_valid:
            raise ValueError(parsed_expr)
        
        variables = ['x', 'y', 'z', 'w']
        table = []
        
        for i in range(16):
            values = {}
            for j, var in enumerate(variables):
                values[var] = bool((i >> (3-j)) & 1)
            
            try:
                result = self.parser.evaluate_expression(expression, values)
                row = {**values, 'result': result}
                table.append(row)
            except ValueError as e:
                raise ValueError(f"Error evaluating expression: {str(e)}")
        
        return table