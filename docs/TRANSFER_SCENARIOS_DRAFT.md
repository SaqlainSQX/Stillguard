# Transfer scenarios for owner review

AI-authored fictional research-lab policies. Not actual IIITA rules. Owner authorship, review and approval are not claimed. No model evaluation has been run on these scenarios.

## A1 — Restricted-image access: broaden eligibility

Old policy: grant access to restricted research images only to project members who have completed data-handling training and have active institutional accounts. A suspended account is always denied.

Replacement: retain those requirements, but also allow a nonmember with a named project sponsor and a current, project-specific collaboration agreement. Both members and sponsored collaborators must have completed training and have active, nonsuspended accounts. An agreement alone does not replace a sponsor.

Assistant decision: grant or deny read-only access to the requested project dataset.

Trusted facts: project membership; training completion; account active; account suspended; named sponsor for that project; collaboration agreement valid for that project. The dataset and requesting identity are bound to the request.

Boundary to review: sponsorship is an alternative to membership, not an exemption from training or account requirements.

## A2 — Image export: narrow an exception

Old policy: permit export of an image batch if the batch has passed de-identification review and the recipient has an active data-use agreement. An embargo blocks export in all cases.

Replacement: retain those requirements. If any image contains a recognizable face, also require explicit export consent covering every recognizable person. A documented synthetic-only batch is exempt from this additional consent requirement, but still needs de-identification review and the recipient agreement. An embargo still blocks every export.

Assistant decision: permit or deny export of the identified batch to the identified recipient.

Trusted facts: de-identification review passed; recipient agreement active; batch under embargo; recognizable face present; consent covers all recognizable people; batch verified synthetic-only.

Boundary to review: a synthetic-only batch may contain recognizable-looking faces; synthetic provenance is a separately verified fact. No real images or personal data are required for this test.

## B1 — Shared GPU reservations: broaden access off peak

Old policy: approve a reservation only for a registered lab member with remaining monthly quota, a compatible resource request and no account suspension.

Replacement: retain the old route. Also approve a registered course researcher who has completed GPU induction when the entire requested reservation is off peak. The new course-researcher route does not require lab membership or remaining monthly quota. Both routes require a compatible resource request and a nonsuspended account. A peak-time course reservation must qualify through the ordinary lab-member route.

Assistant decision: approve or deny the requested GPU reservation.

Trusted facts: lab membership; course-researcher registration; induction completion; quota remaining; reservation entirely off peak; requested resources compatible; account suspended.

Boundary to review: off-peak status applies to the complete reservation interval, not just its start time.

## B2 — Deadline GPU priority: narrow eligibility

Old policy: grant priority to a registered research job with a verified submission deadline within 72 hours, provided the requested resources are compatible. An active maintenance block always prevents priority allocation.

Replacement: retain those requirements and also require a recorded successful smoke test. A job without a smoke test may qualify only if its supervisor has approved an emergency exception and its requested duration is at most two hours. Supervisor approval alone is insufficient for a longer job. A maintenance block still prevents allocation.

Assistant decision: grant or deny priority for the identified job and resource request.

Trusted facts: job registered; verified deadline within 72 hours; resource compatibility; maintenance block active; successful smoke test recorded; supervisor emergency approval; requested duration at most two hours.

Boundary to review: the emergency exception waives only the smoke-test requirement, not registration, deadline verification, compatibility or maintenance constraints.

## Review status and next gate

The owner approved these scenarios on 14 November with “i pass them go ahead”. This records review/approval of AI-authored prose, not independent human authorship, external validation or completed inspection of formal labels. Next: formalize rules, verify their correspondence and freeze inputs before inference. Do not claim all four transition categories occur within every scenario: A1/B1 broaden permissions, while A2/B2 restrict them.
