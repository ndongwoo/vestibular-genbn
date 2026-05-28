class VestibularGenBNError(Exception):
    """Base package error."""


class KnowledgeValidationError(VestibularGenBNError):
    """Raised when a knowledge bundle is internally inconsistent."""


class RuleEvaluationError(VestibularGenBNError):
    """Raised when a rule cannot be evaluated safely."""
