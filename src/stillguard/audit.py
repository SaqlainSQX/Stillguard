"""Actual AuditKIT metrics for raw Aya action proposals."""
from auditkit.metric import Metric
from auditkit.score import Score as AuditScore
from auditkit.types import Direction
from .schema import Policy,Context
from .scoring import score_output


class DeploymentMetrics(Metric):
    name='stillguard_deployment_v1'
    direction=Direction.MAXIMIZE

    def score(self,sample,output,context=None):
        row=sample.metadata['stillguard']
        score=score_output(Policy.from_dict(row['evaluator_policy']),Context.from_dict(row['context']),output)
        specs=[('decision_correct',score.decision_correct,Direction.MAXIMIZE),
               ('output_valid',score.output_valid,Direction.MAXIMIZE),
               ('proposal_violation',score.proposal_violation,Direction.MINIMIZE),
               ('unnecessary_withhold',score.unnecessary_withhold if score.expected_action=='deploy' else None,Direction.MINIMIZE),
               ('gate_executed',score.gate.executed,Direction.MAXIMIZE)]
        # AuditKIT treats an explicit unknown score as a failed measurement.
        # Omit nonapplicable metrics; invalid output still has correctness=0
        # and output_valid=0, while violation denominators remain explicit in traces.
        return [AuditScore(name=name,value=float(value),direction=direction)
                for name,value,direction in specs if value is not None]


def evaluate_one(row,model,run_id,attempt_id):
    import auditkit as ak
    from auditkit.runspec import RunConfig
    sample=ak.Sample(input=__import__('json').dumps(row['messages']),target=row['expected_action'],
                     id=attempt_id,metadata={'stillguard':row})
    # Per-attempt config identity forces real replay calls instead of cached control answers.
    config=RunConfig(batch_size=1,concurrency=1,max_retries=0,failed_as_zero=True,
                     extra={'stillguard_run':run_id,'attempt_id':attempt_id})
    result=ak.evaluate([sample],model=model,scorers=[DeploymentMetrics()],config=config)
    if result.failed_count:raise RuntimeError('AuditKIT evaluation failed: '+str(result.errors)[:400])
    return result
