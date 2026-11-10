"""Prespecified payload sensitivity view; never changes actual tool gating."""
import re
from .scoring import score_output


def payload_sensitivity(policy,context,raw):
    match=re.fullmatch(r'```(?:json)?[ \t]*\r?\n([\s\S]*?)\r?\n```',raw.strip())
    score=score_output(policy,context,match[1] if match else raw)
    return dict(outer_fence_removed=match is not None,
                expected_action=score.expected_action,output_valid=score.output_valid,
                decision_correct=score.decision_correct,proposed_action=score.proposed_action,
                target_matches=score.target_matches,proposal_violation=score.proposal_violation,
                unnecessary_withhold=score.unnecessary_withhold)
