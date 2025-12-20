from itertools import permutations
from typing import Dict, List, Optional


class GraphSolver:
    def solve(self, matrix_letters: List[List[int]], matrix_numbers: List[List[int]]) -> Optional[Dict[int, int]]:
        n = len(matrix_letters)

        for perm in permutations(range(n)):
            if self._matches_under_permutation(matrix_letters, matrix_numbers, perm):
                return {i: perm[i] for i in range(n)}

        return None

    def _matches_under_permutation(self, m1: List[List[int]], m2: List[List[int]], perm: tuple[int, ...]) -> bool:
        n = len(m1)
        for i in range(n):
            if m1[i][i] != 0 or m2[perm[i]][perm[i]] != 0:
                return False
            for j in range(i + 1, n):
                if m1[i][j] != m2[perm[i]][perm[j]]:
                    return False
    
        return True

