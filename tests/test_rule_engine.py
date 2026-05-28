from vestibular_genbn.rule_engine import evaluate_rule


def test_and_rule_true():
    values = {"a": "yes", "b": "yes"}
    assert evaluate_rule("a == yes AND b == yes", values) is True


def test_and_rule_false():
    values = {"a": "yes", "b": "no"}
    assert evaluate_rule("a == yes AND b == yes", values) is False


def test_or_rule_true_with_unknown():
    values = {"a": "unknown", "b": "yes"}
    assert evaluate_rule("a == yes OR b == yes", values) is True


def test_unknown_propagates():
    values = {"a": "unknown", "b": "yes"}
    assert evaluate_rule("a == yes AND b == yes", values) is None


def test_in_rule():
    values = {"ear": "left"}
    assert evaluate_rule("ear in {left,right}", values) is True


def test_parentheses():
    values = {"a": "no", "b": "yes", "c": "yes"}
    assert evaluate_rule("(a == yes OR b == yes) AND c == yes", values) is True
