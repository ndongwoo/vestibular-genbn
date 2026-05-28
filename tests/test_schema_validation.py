from vestibular_genbn.schema_validation import validate_bundle


def test_validate_bundle_passes(bundle):
    validate_bundle(bundle)
