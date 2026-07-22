"""Generate a governed greenfield ProductBaseline from one brainstorm source."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .ids import slug, stable_id
from .source import load_idea_source

DETERMINISTIC_EPOCH = "1970-01-01T00:00:00Z"

CORE_FIELDS = (
    ("summary", "raw-idea", "Raw idea", "product framing"),
    ("target_user", "target-user", "Target user", "target definition"),
    ("problem", "problem", "Problem", "problem definition"),
    ("promise", "promise", "Promise", "offer definition"),
    ("mechanism", "mechanism", "Proposed mechanism", "solution hypothesis"),
    ("channel", "channel", "Channel hypothesis", "channel hypothesis"),
    ("solution_path", "solution-path", "Solution path", "discovery route"),
)
REQUIRED_FRAMING_FIELDS = {"target_user", "problem", "promise"}


def generate_idea_baseline(source_path: str | Path) -> dict[str, Any]:
    source = load_idea_source(source_path)
    product_id = (
        slug(source.name, fallback="idea")
        if source.name
        else f"idea-{source.source_digest[:10]}"
    )
    product_name = source.name or "Unresolved Idea"
    source_id = f"SRC-brainstorm-{source.source_digest[:10]}"

    sources = [
        {
            "sourceId": source_id,
            "sourceType": source.source_type,
            "location": source.source_name,
            "canonicality": "candidate",
            "sensitivity": "internal",
            "accessStatus": "inspected",
            "inspectedAt": DETERMINISTIC_EPOCH,
            "limitation": "A founder-authored brainstorm records hypotheses and intent; it is not customer or market evidence.",
        }
    ]
    statements: list[dict[str, Any]] = [
        _statement(
            "ST-brainstorm-source",
            "fact",
            "One approved brainstorm source was safely parsed for greenfield intake.",
            [source_id],
            "high",
            ["source traceability"],
            True,
            "accepted_for_scope",
        ),
        _statement(
            "ST-demand-evidence-missing",
            "missing",
            "No approved customer-demand evidence was inspected during brainstorm intake.",
            [],
            "high",
            ["validation posture", "customer and market claims"],
            True,
            "fill_gap",
        ),
    ]

    material_statement_ids: list[str] = []
    missing_statement_ids: list[str] = []
    present_fields: set[str] = set()
    if source.name:
        material_statement_ids.append("ST-product-name")
        statements.append(
            _statement(
                "ST-product-name",
                "assumption",
                f"Founder-provided working product name: {source.name}",
                [source_id],
                "medium",
                ["product identity"],
                True,
                "validate",
            )
        )
    else:
        missing_statement_ids.append("ST-product-name")
        statements.append(
            _statement(
                "ST-product-name",
                "missing",
                "A working product or idea name is missing from the approved brainstorm source.",
                [],
                "high",
                ["product identity"],
                True,
                "fill_gap",
            )
        )
    for attribute, identifier, label, impact in CORE_FIELDS:
        value = getattr(source, attribute)
        statement_id = f"ST-{identifier}"
        if value:
            present_fields.add(attribute)
            material_statement_ids.append(statement_id)
            statements.append(
                _statement(
                    statement_id,
                    "assumption",
                    f"Founder hypothesis — {label.lower()}: {value}",
                    [source_id],
                    "low",
                    [impact],
                    True,
                    "validate",
                )
            )
        elif attribute in REQUIRED_FRAMING_FIELDS or attribute == "solution_path":
            missing_statement_ids.append(statement_id)
            statements.append(
                _statement(
                    statement_id,
                    "missing",
                    f"{label} is missing from the approved brainstorm source.",
                    [],
                    "high",
                    [impact],
                    True,
                    "fill_gap",
                )
            )

    for assumption in source.assumptions:
        statement_id = stable_id("ST", assumption, label="assumption")
        material_statement_ids.append(statement_id)
        statements.append(
            _statement(
                statement_id,
                "assumption",
                f"Founder assumption: {assumption}",
                [source_id],
                "low",
                ["validation planning"],
                True,
                "validate",
            )
        )

    for unknown in source.unknowns:
        statement_id = stable_id("ST", unknown, label="unknown")
        missing_statement_ids.append(statement_id)
        statements.append(
            _statement(
                statement_id,
                "missing",
                f"Open question from the brainstorm: {unknown}",
                [source_id],
                "high",
                ["founder focus", "validation planning"],
                True,
                "fill_gap",
            )
        )

    evidence_claim_statement_ids: list[str] = []
    for claim in source.evidence_claims:
        statement_id = stable_id("ST", claim, label="evidence-claim")
        evidence_claim_statement_ids.append(statement_id)
        material_statement_ids.append(statement_id)
        statements.append(
            _statement(
                statement_id,
                "assumption",
                f"Unverified founder-provided evidence claim: {claim}",
                [source_id],
                "low",
                ["validation posture"],
                True,
                "validate",
            )
        )

    framing_missing = sorted(REQUIRED_FRAMING_FIELDS - present_fields)
    solution_path_missing = "solution_path" not in present_fields
    name_missing = source.name is None

    artifacts = [
        {
            "artifactId": "ART-idea-brief",
            "artifactType": "product_context",
            "title": "Greenfield idea brief candidate",
            "status": "partial" if framing_missing or name_missing else "candidate",
            "sourceRef": source.source_name,
            "externalRef": None,
            "provenanceStatementIds": sorted(
                set(material_statement_ids or ["ST-brainstorm-source"])
            ),
        },
        {
            "artifactId": "ART-solution-path",
            "artifactType": "decision",
            "title": "Solution path decision",
            "status": "missing" if solution_path_missing else "candidate",
            "sourceRef": source.source_name if not solution_path_missing else None,
            "externalRef": None,
            "provenanceStatementIds": ["ST-solution-path"],
        },
        {
            "artifactId": "ART-demand-validation",
            "artifactType": "validation_artifact",
            "title": "Customer-demand evidence",
            "status": "missing",
            "sourceRef": None,
            "externalRef": None,
            "provenanceStatementIds": ["ST-demand-evidence-missing"],
        },
    ]
    relationships = [
        {
            "fromArtifactId": "ART-idea-brief",
            "relationshipType": "contains",
            "toArtifactId": "ART-solution-path",
            "confidence": "medium" if not solution_path_missing else "low",
            "sourceStatementIds": ["ST-solution-path"],
        },
        {
            "fromArtifactId": "ART-idea-brief",
            "relationshipType": "relates_to",
            "toArtifactId": "ART-demand-validation",
            "confidence": "high",
            "sourceStatementIds": ["ST-demand-evidence-missing"],
        },
    ]

    gaps: list[dict[str, Any]] = [
        {
            "gapId": "GAP-demand-evidence",
            "category": "validation",
            "severity": "P2",
            "description": "The brainstorm contains no approved customer-demand evidence.",
            "affectedArtifactIds": ["ART-demand-validation", "ART-idea-brief"],
            "evidenceStatementIds": ["ST-demand-evidence-missing"],
            "blocks": ["customer-demand claims", "PRD or implementation authorization"],
            "remediation": "Complete founder focus and governed validation before treating the idea as market evidence.",
            "owner": "Validation Agent",
            "status": "open",
        }
    ]
    if framing_missing or name_missing:
        affected_missing_ids = [
            f"ST-{_identifier_for_field(field)}" for field in framing_missing
        ]
        if name_missing:
            affected_missing_ids.append("ST-product-name")
        gaps.append(
            {
                "gapId": "GAP-idea-framing",
                "category": "product",
                "severity": "P1",
                "description": "The idea is missing one or more minimum framing fields.",
                "affectedArtifactIds": ["ART-idea-brief"],
                "evidenceStatementIds": sorted(set(affected_missing_ids)),
                "blocks": ["advancing beyond idea intake"],
                "remediation": "Clarify one product name, target user, problem, and promise in the source artifact.",
                "owner": "Product Strategist",
                "status": "blocked",
            }
        )
    if solution_path_missing:
        gaps.append(
            {
                "gapId": "GAP-solution-path",
                "category": "product",
                "severity": "P2",
                "description": "The founder has not selected a solution path.",
                "affectedArtifactIds": ["ART-solution-path", "ART-idea-brief"],
                "evidenceStatementIds": ["ST-solution-path"],
                "blocks": ["path-specific discovery routing"],
                "remediation": "Confirm market-facing, own-pain, or specific-person as the first solution path.",
                "owner": "Product Strategist",
                "status": "open",
            }
        )
    if evidence_claim_statement_ids:
        gaps.append(
            {
                "gapId": "GAP-unverified-evidence-claims",
                "category": "validation",
                "severity": "P1",
                "description": "Founder-provided evidence claims have not been verified against approved source artifacts.",
                "affectedArtifactIds": ["ART-demand-validation", "ART-idea-brief"],
                "evidenceStatementIds": sorted(evidence_claim_statement_ids),
                "blocks": ["using the claims as customer or market evidence"],
                "remediation": "Inspect and classify the underlying sources through the validation workflow.",
                "owner": "Validation Agent",
                "status": "blocked",
            }
        )

    framing_complete = not framing_missing and not name_missing
    next_actions: list[dict[str, Any]] = []
    if framing_complete:
        next_actions.append(
            {
                "actionId": "NEXT-founder-focus",
                "title": "Narrow founder focus and confirm the solution path",
                "ownerRole": "Product Strategist",
                "priority": "P2",
                "blockedByGapIds": ["GAP-solution-path"]
                if solution_path_missing
                else [],
                "approvalRequired": False,
                "suggestedCommand": "/pipe:discover",
            }
        )
    else:
        next_actions.append(
            {
                "actionId": "NEXT-clarify-idea",
                "title": "Clarify the minimum single-product idea framing",
                "ownerRole": "Conversational Founder Guide",
                "priority": "P1",
                "blockedByGapIds": ["GAP-idea-framing"],
                "approvalRequired": False,
                "suggestedCommand": "/pipe:idea",
            }
        )

    stage_rationale_ids = sorted(
        set(material_statement_ids or missing_statement_ids or ["ST-brainstorm-source"])
    )
    return {
        "schemaVersion": "0.1.0",
        "baselineId": f"PB-{product_id}-idea",
        "generatedAt": DETERMINISTIC_EPOCH,
        "entryMode": "idea",
        "status": "review_required",
        "product": {
            "productId": product_id,
            "name": product_name,
            "summary": "Greenfield product idea normalized from one approved brainstorm source; all product and evidence claims remain hypotheses pending review.",
            "owner": "founder",
        },
        "lifecycle": {
            "currentStage": "idea_intake",
            "stageConfidence": "medium" if framing_complete else "low",
            "stageRationaleStatementIds": stage_rationale_ids,
            "nextAllowedStage": "founder_focus" if framing_complete else "idea_intake",
        },
        "systems": {
            "repository": {
                "identifier": product_id,
                "location": ".",
                "status": "candidate",
            },
            "linear": None,
            "github": None,
        },
        "sources": sources,
        "statements": sorted(statements, key=lambda item: item["statementId"]),
        "artifacts": sorted(artifacts, key=lambda item: item["artifactId"]),
        "relationships": sorted(
            relationships,
            key=lambda item: (
                item["fromArtifactId"],
                item["relationshipType"],
                item["toArtifactId"],
            ),
        ),
        "evidence": {
            "customerEvidencePresent": False,
            "demandValidationStatus": "hypothesis_only",
            "strongestEvidenceLane": "internal_assumption",
            "statementIds": [],
            "boundaryStatement": "The brainstorm is founder-authored hypothesis material. It does not prove customer demand, behavior, willingness to pay, product-market fit, or readiness to build.",
        },
        "governanceGaps": sorted(gaps, key=lambda item: item["gapId"]),
        "reconciliationPlan": [],
        "approvals": [],
        "nextActions": sorted(next_actions, key=lambda item: item["actionId"]),
        "stopConditions": [
            "Do not treat founder statements or unverified source claims as customer or market evidence.",
            "Do not perform research, outreach, billing, implementation, deployment, or external mutation during idea intake.",
            "Do not ingest secrets, credentials, personal data, customer data, or production data.",
            "Split multiple products into separate source artifacts before rerunning pipe idea.",
        ],
    }


def _statement(
    statement_id: str,
    classification: str,
    text: str,
    source_ids: list[str],
    confidence: str,
    decision_impact: list[str],
    review_required: bool,
    disposition: str,
) -> dict[str, Any]:
    return {
        "statementId": statement_id,
        "classification": classification,
        "text": text,
        "sourceIds": sorted(set(source_ids)),
        "confidence": confidence,
        "decisionImpact": decision_impact,
        "reviewRequired": review_required,
        "disposition": disposition,
    }


def _identifier_for_field(field: str) -> str:
    return next(
        identifier
        for attribute, identifier, _label, _impact in CORE_FIELDS
        if attribute == field
    )
