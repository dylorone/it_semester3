# game_model.py
from enum import Enum, auto
from functools import lru_cache

class GameStateType(Enum):
    """
    Перечисление для типов игровых состояний.
    W  - Winning: Позиция, из которой игрок уже выиграл (камней >= win_condition).
    P1 - Petya 1 (Победа за 1 ход): Можно сделать ход в позицию W.
    V1 - Vanya 1 (Проигрыш за 1 ход): Все ходы ведут в позицию P1.
    P2 - Petya 2 (Победа за 2 хода): Можно сделать ход в позицию V1.
    V2 - Vanya 2 (Проигрыш за 2 хода / Победа Вани 1-2 ходом): Все ходы ведут в P1 или P2.
    UNKNOWN - Неизвестное состояние (обычно означает, что выигрыш более чем за 2 хода).
    """
    W = auto()
    P1 = auto()
    V1 = auto()
    P2 = auto()
    V2 = auto()
    UNKNOWN = auto()

class GameOperation:
    """
    Представляет одну операцию в игре, например, "+5" или "*3".
    """
    def __init__(self, op_string: str):
        """
        Парсит строку операции, например, "+2", "*3".
        """
        op_string = op_string.strip()
        if not op_string or len(op_string) < 2:
            raise ValueError(f"Некорректный формат операции: '{op_string}'")

        self.operator = op_string[0]
        self.value = int(op_string[1:])
        self.op_string = op_string

        if self.operator not in ('+', '*', '-'):
            raise ValueError(f"Неподдерживаемый оператор: '{self.operator}'")

    def apply(self, stones: int) -> int:
        """
        Применяет операцию к текущему количеству камней.
        """
        if self.operator == '+':
            return stones + self.value
        if self.operator == '*':
            return stones * self.value
        if self.operator == '-':
            return stones - self.value
        return stones

    def __repr__(self):
        return f"GameOperation('{self.op_string}')"

    def __str__(self):
        return self.op_string


class WinCondition:
    """
    Определяет условие выигрыша в игре.
    Для одной кучи это просто достижение определенного количества камней.
    """
    def __init__(self, win_sum: int):
        self.win_sum = win_sum

    def is_win(self, stones: int) -> bool:
        """
        Проверяет, является ли текущее состояние выигрышным.
        """
        return stones >= self.win_sum

    def __repr__(self):
        return f"WinCondition(win_sum={self.win_sum})"


class GameModel:
    """
    Основной класс, инкапсулирующий всю логику игры и ее анализа.
    """
    def __init__(self, operations: list[GameOperation], win_condition: WinCondition):
        self.operations = operations
        self.win_condition = win_condition
        # Очищаем кэш для каждого нового экземпляра игры (новых правил)
        self.get_state_type.cache_clear()
        
        self.analysis_results = {}

    def get_next_states(self, s: int) -> list[int]:
        """
        Возвращает все возможные состояния после одного хода из состояния s.
        """
        return [op.apply(s) for op in self.operations]

    @lru_cache(maxsize=None)
    def get_state_type(self, s: int) -> GameStateType:
        """
        Определяет тип игровой позиции 's' с помощью рекурсии и мемоизации (кэширования).
        """
        # Базовый случай: если позиция уже выигрышная
        if self.win_condition.is_win(s):
            return GameStateType.W

        # Рекурсивный шаг: получаем типы всех следующих позиций
        next_states_types = [self.get_state_type(next_s) for next_s in self.get_next_states(s)]

        # Анализ на основе типов следующих позиций
        # Если есть ход в W, то это победа за 1 ход (P1)
        if any(t == GameStateType.W for t in next_states_types):
            return GameStateType.P1

        # Если ходов в W нет, но все ходы ведут в P1, то это проигрыш за 1 ход (V1)
        if all(t == GameStateType.P1 for t in next_states_types):
            return GameStateType.V1

        # Если есть ход в V1, то это победа за 2 хода (P2)
        if any(t == GameStateType.V1 for t in next_states_types):
            return GameStateType.P2
        
        # Если ходов в V1 нет, но все ходы ведут в P1 или P2, то это проигрыш за 2 хода (V2)
        if all(t in (GameStateType.P1, GameStateType.P2) for t in next_states_types):
            return GameStateType.V2

        return GameStateType.UNKNOWN

    def analyze_range(self, max_s: int):
        """
        Анализирует все состояния от 1 до max_s и сохраняет результаты.
        """
        self.analysis_results = {}
        for s in range(1, max_s + 1):
            state_type = self.get_state_type(s)
            if state_type not in self.analysis_results:
                self.analysis_results[state_type] = []
            self.analysis_results[state_type].append(s)
    
    def get_task_19_solution(self) -> list[int]:
        """Задача 19: S, при котором Ваня выигрывает первым ходом."""
        # Это состояние V1 (проигрыш для Пети за 1 ход)
        return self.analysis_results.get(GameStateType.V1, [])

    def get_task_20_solution(self) -> list[int]:
        """Задача 20: S, при котором Петя выигрывает вторым ходом."""
        # Это состояние P2 (победа для Пети за 2 хода)
        return self.analysis_results.get(GameStateType.P2, [])

    def get_task_21_solution(self) -> list[int]:
        """Задача 21: S, при котором Ваня выигрывает первым или вторым ходом."""
        # Это состояние V2 (проигрыш для Пети за 2 хода)
        return self.analysis_results.get(GameStateType.V2, [])

# Пример использования, независимый от GUI
if __name__ == '__main__':
    # Параметры из типичной задачи
    ops = [GameOperation("+1"), GameOperation("*2")]
    win_con = WinCondition(win_sum=29)
    max_s_to_analyze = 28 # Анализируем S от 1 до 28

    # Создаем и анализируем игру
    game = GameModel(operations=ops, win_condition=win_con)
    game.analyze_range(max_s_to_analyze)

    # --- Решение задачи 19 ---
    # Найдите такое значение S, при котором Петя не может выиграть за один ход,
    # но при любом ходе Пети Ваня выигрывает своим первым ходом.
    # Это в точности определение состояния V1.
    task_19_answers = game.get_task_19_solution()
    print(f"Задача 19 (V1): {task_19_answers}")
    if task_19_answers:
        print(f"Ответ на задачу 19 (минимальное S): {min(task_19_answers)}")

    # --- Решение задачи 20 ---
    # Найдите два таких наименьших значения S, при которых у Пети есть выигрышная стратегия,
    # причём Петя не может выиграть за один ход, но может выиграть своим вторым ходом.
    # Это в точности определение состояния P2.
    task_20_answers = game.get_task_20_solution()
    print(f"\nЗадача 20 (P2): {task_20_answers}")
    if len(task_20_answers) >= 2:
        # Сортируем и берем два наименьших
        task_20_answers.sort()
        print(f"Ответ на задачу 20 (два наименьших S): {task_20_answers[0]}, {task_20_answers[1]}")

    # --- Решение задачи 21 ---
    # Найдите максимальное значение S, при котором у Вани есть выигрышная стратегия,
    # позволяющая ему выиграть первым или вторым ходом, но нет стратегии,
    # которая гарантированно позволяет ему выиграть первым ходом.
    # Это в точности определение состояния V2.
    task_21_answers = game.get_task_21_solution()
    print(f"\nЗадача 21 (V2): {task_21_answers}")
    if task_21_answers:
        print(f"Ответ на задачу 21 (максимальное S): {max(task_21_answers)}")
