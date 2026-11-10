"""Public entry point for the supplied expert rule package."""

from .expert_system.rule_engine import evaluate_rules

__all__ = ["evaluate_rules"]
