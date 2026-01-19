from abc import ABC, abstractmethod


class BooleanOperation(ABC):
    def __init__(self):
        self.__input1 = False
        self.__input2 = False
        self._result = None

        self.__next = None
        self.__next_input = 0

    @abstractmethod
    def calc(self):
        raise NotImplementedError

    def link_to(self, next_, input_):
        self.__next = next_
        self.__next_input = input_

    @property
    def input1(self):
        return self.__input1

    @property
    def input2(self):
        return self.__input2

    @property
    def result(self):
        return self._result

    @input1.setter
    def input1(self, new):
        self.__input1 = new
        self.calc()
        if not self.__next:
            return

        if self.__next_input == 1:
            self.__next.input1 = self._result
        elif self.__next_input == 2:
            self.__next.input2 = self._result
        else:
            raise ValueError("Invalid next input number given")

    @input2.setter
    def input2(self, new):
        self.__input2 = new
        self.calc()
        if not self.__next:
            return

        if self.__next_input == 1:
            self.__next.input1 = self._result
        elif self.__next_input == 2:
            self.__next_input = self._result
        else:
            raise ValueError("Invalid next input number given")

class NotOperation(BooleanOperation):
    def __init__(self):
        super().__init__()

    def calc(self):
        self._result = not self.input1


class BinaryOperation(BooleanOperation, ABC):
    pass

class AndOperation(BinaryOperation):
    def __init__(self):
        super().__init__()

    def calc(self):
        self._result = self.input1 and self.input2

class OrOperation(BinaryOperation):
    def __init__(self):
        super().__init__()

    def calc(self):
        self._result = self.input1 or self.input2


if __name__ == "__main__":
    test = BooleanOperation()
    test.calc()

    not1 = NotOperation()
    and1 = AndOperation()
    not1.link_to(and1, 1)

    not2 = NotOperation()
    and2 = AndOperation()
    not2.link_to(and2, 2)

    or1 = OrOperation()
    and1.link_to(or1, 1)
    and2.link_to(or1, 2)

    for a in range(2):
        and1.input2 = a
        not2.input1 = a
        for b in range(2):
            and2.input1 = b
            not1.input1 = b
            print(or1.result)
