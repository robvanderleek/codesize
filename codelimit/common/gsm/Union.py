from codelimit.common.gsm.Expression import expression_to_nfa
from codelimit.common.gsm.Automata import Automata
from codelimit.common.gsm.Operator import Operator
from codelimit.common.gsm.State import State


class Union(Operator):
    def __init__(self, left: Operator | str | list[Operator | str], right: Operator | str | list[Operator | str]):
        self.left = left if isinstance(left, list) else [left]
        self.right = right if isinstance(right, list) else [right]

    def apply(self, stack: list[Automata]):
        start = State()
        nfa1 = expression_to_nfa(self.left)
        nfa2 = expression_to_nfa(self.right)
        start.epsilon_transitions = [nfa1.start, nfa2.start]
        accepting = State()
        nfa1.accepting.epsilon_transitions = [accepting]
        nfa2.accepting.epsilon_transitions = [accepting]
        stack.append(Automata(start, accepting))
