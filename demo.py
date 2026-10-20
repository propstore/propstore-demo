"""A disposable, repository-backed applicability argument. No patient advice."""

from pathlib import Path
from tempfile import TemporaryDirectory

from argumentation.core.dung import grounded_extension, range_of
from condition_ir import KindType

from propstore.aspic_bridge.projection import build_aspic_projection
from propstore.core.environment import Environment
from propstore.core.source_types import SourceKind, SourceOriginType
from propstore.families.claims import Claim, ClaimType
from propstore.families.contexts import Context, LiftingRule
from propstore.families.forms import FormDefinition
from propstore.families.identity.justifications import derive_justification_artifact_id
from propstore.families.identity.stances import derive_stance_artifact_id
from propstore.families.justifications import Justification
from propstore.families.relations import Stance
from propstore.merge.merge_commit import create_merge_commit
from propstore.repository import Repository
from propstore.source.claims import commit_source_claim_proposal
from propstore.source.common import init_source_branch
from propstore.source.concepts import commit_source_concept_proposal
from propstore.source.finalize import finalize_source_branch
from propstore.source.promote import promote_source_branch
from propstore.stances import StanceType
from propstore.world import OverlayWorld, WorldQuery


def seed(root: Path) -> tuple[Repository, str]:
    repo = Repository.init(root)
    repo.families.form.save("dimensionless", FormDefinition(
        name="dimensionless", kind=KindType.QUANTITY, is_dimensionless=True
    ), message="Dimensionless form")
    for context in ("att", "target", "unrelated"):
        repo.families.context.save(context, Context(
            context_id=context, name=context,
            description="ATT report context" if context == "att" else "Reviewer-authored demo context"
        ), message="Context")
    source = "ATT_2009_Appendix_Excerpt"
    init_source_branch(repo, source, kind=SourceKind.ACADEMIC_PAPER,
                       origin_type=SourceOriginType.MANUAL,
                       origin_value="Aspirin in the primary and secondary prevention of vascular disease, web appendix, printed p.21, Web Figure 18")
    commit_source_concept_proposal(repo, source, local_name="reported_result",
                                  definition="A source's reported trial summary", form="dimensionless")
    report = commit_source_claim_proposal(
        repo, source, claim_id="report", claim_type=ClaimType.OBSERVATION,
        context="att", concepts=("reported_result",), page=21, figure="Web Figure 18",
        statement="ATT 2009 reports a pooled primary-prevention serious-vascular-event rate ratio.",
        notes="This historical report remains separate from its applicability to another context."
    )
    finalize_source_branch(repo, source)
    promoted = promote_source_branch(repo, source)
    if promoted.blocked_claims or report.artifact_id is None:
        raise RuntimeError(f"Report promotion failed: {promoted.blocked_claims}")
    report_id = report.artifact_id
    concept_id = repo.families.claim.load(report_id).concepts[0]
    repo.families.lifting_rule.save("reviewer-lift", LiftingRule(
        rule_id="reviewer-lift", source_context="att", target_context="target",
        justification="Reviewer-authored demonstration permission to consider the report in target; not a medical transportability finding."
    ), message="Explicit reviewer context bridge")
    for claim_id, statement in (
        ("transport_permission", "Reviewer modelling assumption: allow the ATT report to support this target-context inference."),
        ("applicability", "Under the reviewer's transport assumption, the ATT report supplies target-context support."),
    ):
        repo.families.claim.save(claim_id, Claim(
            claim_id=claim_id, context_id="target", claim_type=ClaimType.OBSERVATION,
            concepts=(concept_id,), statement=statement,
            notes="Demo author modelling assertion, not a statement extracted from a clinical paper."
        ), message="Reviewer modelling claim")
    justification_id = derive_justification_artifact_id(
        conclusion="applicability", premises=(report_id, "transport_permission"),
        rule_kind="scope_limitation", rule_strength="defeasible"
    )
    repo.families.justification.save(justification_id, Justification(
        justification_id=justification_id, conclusion="applicability",
        premises=(report_id, "transport_permission"), rule_kind="scope_limitation",
        rule_strength="defeasible"
    ), message="Explicit two-premise applicability inference")
    return repo, report_id


def inspect(world: WorldQuery, context: str, report_id: str,
            remove: tuple[str, ...] = ()) -> dict[str, str]:
    bound = world.bind(Environment(context_id=context))
    view = OverlayWorld(bound, remove=remove) if remove else bound
    projection = build_aspic_projection(
        view.store, view.active_claims(), bundle=world.grounding_bundle()
    )
    accepted = grounded_extension(projection.framework)
    defeated = range_of(accepted, projection.framework.defeats) - accepted
    active = {claim.claim_id for claim in view.active_claims()}
    result: dict[str, str] = {}
    for label, claim_id in (("report", report_id), ("inference", "applicability")):
        arguments = set(projection.claim_to_argument_ids.get(claim_id, ()))
        if claim_id not in active:
            status = "inactive"
        elif not arguments:
            status = "unsupported"
        elif arguments & accepted:
            status = "accepted"
        elif arguments <= defeated:
            status = "defeated"
        else:
            status = "undecided"
        result[label] = status
    dependencies = sorted({dependency for argument in projection.arguments
                           if argument.claim_id == "applicability"
                           for dependency in argument.dependency_claim_ids})
    print(f"context={context} remove={list(remove)} {result}")
    print(f"  actual inference dependencies: {dependencies}")
    return result


def run(root: Path) -> None:
    repo, report_id = seed(root)
    print("ASPIC / grounded semantics. Reviewer modelling assumptions; no treatment recommendation.")
    print(f"Promoted report: {report_id}")
    with WorldQuery(repo) as world:
        assert inspect(world, "att", report_id) == {"report": "accepted", "inference": "inactive"}
        assert inspect(world, "target", report_id) == {"report": "accepted", "inference": "accepted"}
        assert inspect(world, "unrelated", report_id) == {"report": "inactive", "inference": "inactive"}
        assert inspect(world, "target", report_id, ("transport_permission",)) == {"report": "accepted", "inference": "unsupported"}
        assert inspect(world, "target", report_id, (report_id,)) == {"report": "inactive", "inference": "unsupported"}
        assert inspect(world, "target", report_id)["inference"] == "accepted"
    git = repo.require_git()
    git.create_branch("review/scope-objection", source_commit=git.head_sha())
    concept_id = repo.families.claim.load(report_id).concepts[0]
    repo.families.claim.save("scope_objection", Claim(
        claim_id="scope_objection", context_id="target", claim_type=ClaimType.OBSERVATION,
        concepts=(concept_id,), statement="Reviewer objection: this demonstration does not establish that transport assumption.",
        notes="Authored reviewer challenge to the inference, not new clinical evidence or a rebuttal of the reported measurement."
    ), branch="review/scope-objection", message="Independent reviewer objection")
    stance_id = derive_stance_artifact_id(source_claim_id="scope_objection",
        target_claim_id="applicability", stance_type=StanceType.UNDERCUTS.value)
    repo.families.stance.save(stance_id, Stance(
        stance_id=stance_id, source_claim_id="scope_objection",
        target_claim_id="applicability", stance_type=StanceType.UNDERCUTS
    ), branch="review/scope-objection", message="Challenge the sole applicability inference")
    merge_sha = create_merge_commit(repo, "master", "review/scope-objection")
    print(f"Merged reviewer branch: {merge_sha}")
    with WorldQuery(repo) as world:
        assert inspect(world, "target", report_id) == {"report": "accepted", "inference": "defeated"}
        assert inspect(world, "target", report_id, ("scope_objection",))["inference"] == "accepted"
        assert inspect(world, "target", report_id)["inference"] == "defeated"
        assert world.get_claim(report_id) is not None
        assert world.get_claim("scope_objection") is not None
    print("All transitions verified against computed arguments. Original stores were not opened.")


if __name__ == "__main__":
    with TemporaryDirectory(prefix="propstore-aspirin-demo-") as directory:
        run(Path(directory) / "knowledge")
