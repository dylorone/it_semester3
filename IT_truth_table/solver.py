from itertools import product, permutations
from parser import BooleanExpressionParser


class VariableAssignmentSolver:
    def __init__(self):
        self.parser = BooleanExpressionParser()
    
    def create_function(self, expression: str):
        def f(x, y, z, w):
            try:
                result = self.parser.evaluate_expression(expression, {'x': x, 'y': y, 'z': z, 'w': w})
                return int(result)
            except:
                return 0
        return f
    
    def solve_variable_assignment(self, mask_table, boolean_function, result_column=None):
        f = self.create_function(boolean_function)
        solutions = []
        
        filled_rows = []
        for row in mask_table:
            if any(val is not None for val in row):
                filled_rows.append(row)
        
        if not filled_rows:
            return solutions
        
        for perm in permutations('xyzw'):
            if self.validate_assignment(perm, filled_rows, f, result_column):
                solutions.append(perm)
        
        return solutions
    
    def validate_assignment(self, perm, filled_rows, f, result_column=None):
        all_combinations = []
        for row in filled_rows:
            missing_indices = [i for i, val in enumerate(row) if val is None]
            if missing_indices:
                combinations = list(product([0, 1], repeat=len(missing_indices)))
                all_combinations.append(combinations)
            else:
                all_combinations.append([[]])
        
        for combo_set in product(*all_combinations):
            complete_rows = []
            for i, row in enumerate(filled_rows):
                complete_row = list(row)
                combo = combo_set[i]
                missing_indices = [j for j, val in enumerate(row) if val is None]
                for j, idx in enumerate(missing_indices):
                    complete_row[idx] = combo[j]
                complete_rows.append(tuple(complete_row))
            
            if len(set(complete_rows)) != len(complete_rows):
                continue
            
            if self.check_rows_with_function(complete_rows, perm, f, result_column):
                return True
        
        return False
    
    def check_rows_with_function(self, rows, perm, f, result_column=None):
        for i, row in enumerate(rows):
            x, y, z, w = row
            var_map = dict(zip(perm, ['x', 'y', 'z', 'w']))
            args = {}
            for var, pos in var_map.items():
                if pos == 'x':
                    args[var] = x
                elif pos == 'y':
                    args[var] = y
                elif pos == 'z':
                    args[var] = z
                elif pos == 'w':
                    args[var] = w
            
            result = f(**args)
            
            if result_column is not None and i < len(result_column):
                expected_result = result_column[i]
                if expected_result is not None and result != expected_result:
                    return False
        
        return True


def solve_variable_assignment(mask_table, boolean_function, result_column=None):
    solver = VariableAssignmentSolver()
    return solver.solve_variable_assignment(mask_table, boolean_function, result_column)


if __name__ == "__main__":
    mask_table = [
        [1, 1, None, None],
        [1, 1, None, 1],
        [None, 1, 1, None],
    ]
    
    result_column = [0, 0, 0]
    
    boolean_function = "(x ≡ ¬y) → ((x ∧ w) ≡ z)"
    
    solutions = solve_variable_assignment(mask_table, boolean_function, result_column)
    
    print("Solutions found:")
    for i, solution in enumerate(solutions):
        print(f"Solution {i+1}: {solution}")
