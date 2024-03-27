from codelimit.common.gsm.NFA import NFA
from codelimit.common.gsm.Operator import Operator
from codelimit.common.gsm.State import State


class Atom(Operator):
    def __init__(self, item: str):
        self.item = item

    def apply(self, stack: list[NFA]):
        start = State()
        accepting = State()
        start.transition = (self.item, accepting)
        stack.append(NFA(start, accepting))
