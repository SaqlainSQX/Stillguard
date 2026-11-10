"""Finite Boolean policy oracle. No language model or implicit authorization."""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Rule:
    op: str
    atom: str | None = None
    children: tuple['Rule', ...] = ()

    def __post_init__(self):
        if self.op == 'atom':
            if not isinstance(self.atom, str) or not self.atom or self.children:
                raise ValueError('An atom needs a name and no children')
        elif self.op in ('not', 'and', 'or'):
            if self.atom is not None or (len(self.children) != 1 if self.op == 'not' else len(self.children) < 2):
                raise ValueError('Invalid connective arity')
            if not all(isinstance(c, Rule) for c in self.children):
                raise ValueError('Children must be rules')
        else:
            raise ValueError('Unknown operator')

    def atoms(self) -> frozenset[str]:
        return frozenset([self.atom]) if self.op == 'atom' else frozenset().union(*(c.atoms() for c in self.children))

    def allows(self, state: dict[str, bool]) -> bool:
        # Validate all referenced inputs before evaluation; short circuiting must
        # not conceal a missing or non-Boolean policy fact.
        for name in self.atoms():
            if name not in state or type(state[name]) is not bool:
                raise ValueError(f'Missing or non-Boolean fact: {name}')
        return self._evaluate(state)

    def _evaluate(self, state):
        if self.op == 'atom': return state[self.atom]
        if self.op == 'not': return not self.children[0]._evaluate(state)
        if self.op == 'and': return all(c._evaluate(state) for c in self.children)
        return any(c._evaluate(state) for c in self.children)


def decision_changes(before: Rule, after: Rule) -> list[dict]:
    names = sorted(before.atoms() | after.atoms())
    if len(names) > 10:
        raise ValueError('Finite oracle supports at most ten Boolean facts')
    changes = []
    for values in product((False, True), repeat=len(names)):
        state = dict(zip(names, values))
        old, new = before.allows(state), after.allows(state)
        if old != new:
            changes.append({'state': state, 'before': old, 'after': new})
    return changes
