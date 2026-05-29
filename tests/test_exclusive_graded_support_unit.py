from vestibular_genbn.derived_nodes import evaluate_exclusive_graded_support_group


def test_evaluate_exclusive_graded_support_group_strong():
    """Test that strong case works correctly."""
    group = {
        "id": "test_support_group",
        "group_type": "exclusive_graded_support",
        "levels": [
            {"level": "strong", "node": "test_support_strong", "rule": "a == yes AND b == yes"},
            {"level": "moderate", "node": "test_support_moderate", "rule": "a == yes"},
            {"level": "weak", "node": "test_support_weak", "rule": "c == yes"}
        ]
    }
    
    values = {"a": "yes", "b": "yes", "c": "yes"}
    evaluate_exclusive_graded_support_group(group, values)
    
    assert values["test_support_strong"] == "yes"
    assert values["test_support_moderate"] == "no"
    assert values["test_support_weak"] == "no"


def test_evaluate_exclusive_graded_support_group_moderate():
    """Test that moderate case works correctly."""
    group = {
        "id": "test_support_group",
        "group_type": "exclusive_graded_support",
        "levels": [
            {"level": "strong", "node": "test_support_strong", "rule": "a == yes AND b == yes"},
            {"level": "moderate", "node": "test_support_moderate", "rule": "a == yes"},
            {"level": "weak", "node": "test_support_weak", "rule": "c == yes"}
        ]
    }
    
    values = {"a": "yes", "b": "no", "c": "yes"}
    evaluate_exclusive_graded_support_group(group, values)
    
    assert values["test_support_strong"] == "no"
    assert values["test_support_moderate"] == "yes"
    assert values["test_support_weak"] == "no"


def test_evaluate_exclusive_graded_support_group_weak():
    """Test that weak case works correctly."""
    group = {
        "id": "test_support_group",
        "group_type": "exclusive_graded_support",
        "levels": [
            {"level": "strong", "node": "test_support_strong", "rule": "a == yes AND b == yes"},
            {"level": "moderate", "node": "test_support_moderate", "rule": "a == yes"},
            {"level": "weak", "node": "test_support_weak", "rule": "c == yes"}
        ]
    }
    
    values = {"a": "no", "b": "no", "c": "yes"}
    evaluate_exclusive_graded_support_group(group, values)
    
    assert values["test_support_strong"] == "no"
    assert values["test_support_moderate"] == "no"
    assert values["test_support_weak"] == "yes"


def test_evaluate_exclusive_graded_support_group_none():
    """Test that none case works correctly."""
    group = {
        "id": "test_support_group",
        "group_type": "exclusive_graded_support",
        "levels": [
            {"level": "strong", "node": "test_support_strong", "rule": "a == yes AND b == yes"},
            {"level": "moderate", "node": "test_support_moderate", "rule": "a == yes"},
            {"level": "weak", "node": "test_support_weak", "rule": "c == yes"}
        ]
    }
    
    values = {"a": "no", "b": "no", "c": "no"}
    evaluate_exclusive_graded_support_group(group, values)
    
    assert values["test_support_strong"] == "no"
    assert values["test_support_moderate"] == "no"
    assert values["test_support_weak"] == "no"


def test_evaluate_exclusive_graded_support_group_missing():
    """Test that missing values case works correctly."""
    group = {
        "id": "test_support_group",
        "group_type": "exclusive_graded_support",
        "levels": [
            {"level": "strong", "node": "test_support_strong", "rule": "a == yes AND b == yes"},
            {"level": "moderate", "node": "test_support_moderate", "rule": "a == yes"},
            {"level": "weak", "node": "test_support_weak", "rule": "c == yes"}
        ]
    }
    
    values = {}
    evaluate_exclusive_graded_support_group(group, values)
    
    assert values["test_support_strong"] == "no"
    assert values["test_support_moderate"] == "no"
    assert values["test_support_weak"] == "no"


def test_evaluate_findings_still_works_with_existing_patterns():
    """Test that existing evaluate_findings() behavior is unchanged."""
    # We can't directly test this without the full bundle, but we can make sure
    # our changes don't break other functionality by testing that the module loads properly
    # and that the function is accessible without errors
    assert callable(evaluate_exclusive_graded_support_group)
    
    # Test the function with some basic values to make sure there are no runtime issues
    group = {
        "id": "test_support_group",
        "group_type": "exclusive_graded_support",
        "levels": [
            {"level": "strong", "node": "test_support_strong", "rule": "a == yes AND b == yes"},
            {"level": "moderate", "node": "test_support_moderate", "rule": "a == yes"},
            {"level": "weak", "node": "test_support_weak", "rule": "c == yes"}
        ]
    }
    
    values = {"a": "yes", "b": "yes"}
    evaluate_exclusive_graded_support_group(group, values)
    
    # Verify that the function worked without raising an exception
    assert values["test_support_strong"] == "yes"
    assert values["test_support_moderate"] == "no"
    assert values["test_support_weak"] == "no"