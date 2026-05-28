from vestibular_genbn.inference import run_case
from vestibular_genbn.audit import summarize_audits


def test_central_alert(bundle):
    result = run_case(
        bundle,
        {
            "case_id": "central",
            "pure_downbeat_positional_nystagmus": "yes",
            "new_severe_headache_or_neck_pain": "yes",
        },
    )
    audits = summarize_audits(bundle, result)
    assert audits["urgent_central_evaluation_flag"] == "yes"


def test_repositioning_candidate(bundle):
    result = run_case(
        bundle,
        {
            "case_id": "pc",
            "hx_recurrent_positional_vertigo": "yes",
            "hx_positional_trigger": "yes",
            "hx_brief_seconds_to_minutes": "yes",
            "dix_hallpike_performed": "yes",
            "dh_torsional_upbeating_nystagmus": "yes",
            "dh_duration_less_than_60s": "yes",
        },
    )
    audits = summarize_audits(bundle, result)
    assert audits["canalith_repositioning_candidate_flag"] == "yes"
