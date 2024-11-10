import abc
from typing import override, Literal, Iterable

from config import IncludeRule, ExcludeRule


class RuleApplicator(abc.ABC):
    @abc.abstractmethod
    def apply(self, value: str) -> Literal["indeterminate", "include", "exclude"]:
        pass


class WildcardRuleApplicator(RuleApplicator):
    def __init__(self, mode: Literal["include", "exclude"]):
        self.result = mode

    @override
    def apply(self, value: str) -> Literal["indeterminate", "include", "exclude"]:
        return self.result


class ExactMatchRuleApplicator(RuleApplicator):
    def __init__(self, mode: Literal["include", "exclude"], values: Iterable[str]):
        self.values = frozenset(values)
        self.result = mode

    @override
    def apply(self, value: str) -> Literal["indeterminate", "include", "exclude"]:
        if value in self.values:
            return self.result
        return "indeterminate"


class Filter:
    def __init__(self, rules: list[IncludeRule | ExcludeRule]):
        self._rule_applicators = [self.get_rule_applicator(rule) for rule in self.effective_rules(rules)]

    @staticmethod
    def get_rule_applicator(rule: IncludeRule | ExcludeRule) -> RuleApplicator:
        if "*" in rule.select:
            return WildcardRuleApplicator(rule.rule)
        return ExactMatchRuleApplicator(rule.rule, rule.select)

    @staticmethod
    def effective_rules(rules: list[IncludeRule | ExcludeRule]) -> list[IncludeRule | ExcludeRule]:
        effective_from_index = 0
        for index, rule in enumerate(rules):
            if "*" in rule.select:
                effective_from_index = index
        return rules[effective_from_index:]

    def matches(self, value: str) -> bool:
        included = False
        for rule in self._rule_applicators:
            result = rule.apply(value)
            if result == "include":
                included = True
                continue
            if result == "exclude":
                included = False
                continue
        return included

