"""Strict deployment-domain records. Model output cannot replace trusted facts."""
from dataclasses import dataclass
from types import MappingProxyType
from collections.abc import Mapping
import json
import re

from .oracle import Rule

FACT_NAMES = frozenset({'tests_passed', 'reviewer_approved', 'within_original_window', 'within_extension', 'revoked'})
DERIVED_NAMES = frozenset({'is_staging', 'is_production'})
TARGET_FIELDS = ('request_id', 'workspace_id', 'resource_id', 'environment')


def identifier(value):
    if type(value) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,79}', value):
        raise ValueError('Invalid identifier')


@dataclass(frozen=True)
class Context:
    request_id: str
    workspace_id: str
    resource_id: str
    environment: str
    facts: Mapping[str, bool]

    def __post_init__(self):
        for field in TARGET_FIELDS[:-1]: identifier(getattr(self, field))
        if self.environment not in ('staging', 'production'):
            raise ValueError('Unknown environment')
        if not isinstance(self.facts, Mapping) or set(self.facts) != FACT_NAMES:
            raise ValueError('Context requires exactly the declared trusted facts')
        if any(type(v) is not bool for v in self.facts.values()):
            raise ValueError('Facts must be actual Booleans')
        object.__setattr__(self, 'facts', MappingProxyType(dict(self.facts)))

    def oracle_state(self):
        return dict(self.facts, is_staging=self.environment == 'staging', is_production=self.environment == 'production')

    def public_dict(self):
        return {**{k: getattr(self, k) for k in TARGET_FIELDS}, 'facts': dict(self.facts)}

    @classmethod
    def from_dict(cls, value):
        if type(value) is not dict or set(value) != set(TARGET_FIELDS) | {'facts'}:
            raise ValueError('Unexpected context fields')
        return cls(**value)


@dataclass(frozen=True)
class Policy:
    workspace_id: str
    resource_id: str
    revision_id: str
    rule: Rule

    def __post_init__(self):
        for name in ('workspace_id', 'resource_id', 'revision_id'): identifier(getattr(self, name))
        if not isinstance(self.rule, Rule) or not self.rule.atoms() <= FACT_NAMES | DERIVED_NAMES:
            raise ValueError('Policy contains undeclared facts')

    def allows(self, context):
        if (context.workspace_id, context.resource_id) != (self.workspace_id, self.resource_id):
            raise ValueError('Policy/context scope mismatch')
        return self.rule.allows(context.oracle_state())

    @classmethod
    def from_dict(cls, value):
        if type(value) is not dict or set(value) != {'workspace_id', 'resource_id', 'revision_id', 'rule'}:
            raise ValueError('Unexpected policy fields')
        return cls(**{**value, 'rule': Rule.from_dict(value['rule'])})


@dataclass(frozen=True)
class Proposal:
    action: str
    request_id: str
    workspace_id: str
    resource_id: str
    environment: str

    def __post_init__(self):
        if self.action not in ('deploy', 'withhold'):
            raise ValueError('Unknown action')
        for name in TARGET_FIELDS[:-1]: identifier(getattr(self, name))
        if self.environment not in ('staging', 'production'):
            raise ValueError('Unknown environment')

    def matches(self, context):
        return all(getattr(self, k) == getattr(context, k) for k in TARGET_FIELDS)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def parse_proposal(raw):
    if type(raw) is not str or len(raw) > 8192:
        raise ValueError('Invalid output type or excessive length')
    try:
        value = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (ValueError, RecursionError) as error:
        raise ValueError('Output must be one strict JSON object') from error
    if type(value) is not dict or set(value) != {'action', *TARGET_FIELDS}:
        raise ValueError('Unexpected action fields')
    return Proposal(**value)
