from abc import ABC, abstractmethod
from typing import Dict, List

class Operator(ABC):
    @abstractmethod
    def __init__(self, args: List[Operator]):
        self.args = args

    @abstractmethod
    def evaluate(self) -> bool:
        raise NotImplementedError

class ConstantOperator(Operator):
    def __init__(self, value: bool):
        super().__init__([])
        self.value = value
    
    def evaluate(self) -> bool:
        return self.value

class VariableOperator(Operator):
    def __init__(self, name: str):
        super().__init__([])
        self.__name = name
        self.__value = None
    
    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        self.__value = value
    
    def evaluate(self) -> bool:
        if not self.__value:
            raise ValueError(f"Variable {self.__name} was not set")

        return self.__value

class UnaryOperator(Operator):
    def __init__(self, arg: Operator):
        super().__init__([arg])

class NotOperator(UnaryOperator):
    def __init__(self, arg: Operator):
        super().__init__(arg)

    def evaluate(self) -> bool:
        return not self.arg.evaluate()

class BinaryOperator(Operator):
    def __init__(self, arg1: Operator, arg2: Operator):
        super().__init__([arg1, arg2])

        self.arg1 = arg1
        self.arg2 = arg2

class AndOperator(BinaryOperator):
    def evaluate(self) -> bool:
        return self.arg1.evaluate() and self.arg2.evaluate()

class OrOperator(BinaryOperator):
    def evaluate(self) -> bool:
        return self.arg1.evaluate() or self.arg2.evaluate()

class ImplicationOperator(BinaryOperator):
    def evaluate(self) -> bool:
        return not self.arg1.evaluate() or self.arg2.evaluate()

class EquivalenceOperator(BinaryOperator):
    def evaluate(self) -> bool:
        return self.arg1.evaluate() == self.arg2.evaluate()

class BooleanExpression:
    def __init__(self, root: Operator) -> None:
        self.root = root
        self.__variables: Dict[str, VariableOperator] = None

    def set_variable(self, name: str, value: bool):
        if not self.__variables:
            raise ValueError("Variables have not been traversed")
        
        if name not in self.__variables:
            raise ValueError(f"Variable with name {name} doesn't exist")

        self.__variables[name].value = value
    
    def traverse_for_variables(self):
        self.__variables = {}
        self.__traverse_for_variables(self.root)
    
    def __traverse_for_variables(self, node: Operator):
        if isinstance(node, VariableOperator):
            self.__variables[node.name] = node
        
        for arg in node.args:
            self.__traverse_for_variables(arg)
        