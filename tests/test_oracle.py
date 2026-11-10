from itertools import product
import pytest
from stillguard.oracle import Rule, decision_changes


def atom(name): return Rule('atom', atom=name)


def test_window_extension_preserves_tests_and_approval_exhaustively():
    tests, approval, old_window, extension = map(atom, ['tests', 'approval', 'window', 'extension'])
    before = Rule('and', children=(tests, approval, old_window))
    after = Rule('and', children=(tests, approval, Rule('or', children=(old_window, extension))))
    for t, a, w, e in product((False, True), repeat=4):
        state = dict(tests=t, approval=a, window=w, extension=e)
        assert before.allows(state) == (t and a and w)
        assert after.allows(state) == (t and a and (w or e))
    changes = decision_changes(before, after)
    assert changes == [{'state': {'approval': True, 'extension': True, 'tests': True, 'window': False}, 'before': False, 'after': True}]


def test_missing_approval_is_not_silently_treated_as_denied_or_allowed():
    rule = Rule('and', children=(atom('tests'), atom('approval')))
    with pytest.raises(ValueError): rule.allows({'tests': False})
    with pytest.raises(ValueError): rule.allows({'tests': True, 'approval': 1})


def test_explicit_exception_and_revocation():
    policy = Rule('and', children=(atom('approved'), Rule('not', children=(atom('revoked'),))))
    for approved, revoked in product((False, True), repeat=2):
        assert policy.allows(dict(approved=approved, revoked=revoked)) == (approved and not revoked)


@pytest.mark.parametrize('kwargs', [dict(op='xor'), dict(op='atom'), dict(op='not'), dict(op='and', children=(atom('a'),))])
def test_invalid_rule_rejected(kwargs):
    with pytest.raises(ValueError): Rule(**kwargs)
