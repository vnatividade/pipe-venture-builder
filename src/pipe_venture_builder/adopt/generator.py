"""Deterministic repository-only ProductBaseline generator."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pipe_venture_builder.inventory import inspect_git, inventory_repository
from pipe_venture_builder.inventory.repository import (
    MetadataDocument,
    RepositoryInventory,
)

from .ids import slug, stable_id

DETERMINISTIC_EPOCH = "1970-01-01T00:00:00Z"


def generate_product_baseline(repository: str | Path) -> dict[str, Any]:
    """Generate a safe current-state baseline without external reads or mutation."""

    inventory = inventory_repository(repository)
    git = inspect_git(inventory.root)
    generated_at = git.committed_at or DETERMINISTIC_EPOCH
    product_id = slug(inventory.product_name, fallback="adopted-product")

    repository_source_id = "SRC-repository"
    sources: list[dict[str, Any]] = [
        {
            "sourceId": repository_source_id,
            "sourceType": "other",
            "location": ".",
            "canonicality": "canonical",
            "sensitivity": "internal",
            "accessStatus": "inspected",
            "inspectedAt": generated_at,
            "limitation": "Repository presence proves only that a local product workspace was inspected.",
        }
    ]
    document_source_ids: dict[str, str] = {}
    for document in inventory.documents:
        source_id = stable_id(
            "SRC", document.relative_path, label=document.relative_path
        )
        document_source_ids[document.relative_path] = source_id
        sources.append(_document_source(document, source_id, generated_at))

    git_source_id: str | None = None
    if git.present:
        git_source_id = "SRC-git-history"
        sources.append(
            {
                "sourceId": git_source_id,
                "sourceType": "git_history",
                "location": ".git",
                "canonicality": "operational",
                "sensitivity": "internal",
                "accessStatus": "inspected",
                "inspectedAt": generated_at,
                "limitation": "Commit metadata proves delivery history, not customer demand or historical governance approval.",
            }
        )

    test_source_ids: dict[str, str] = {}
    for test_inventory in inventory.tests:
        source_id = stable_id("SRC", test_inventory.root, label=test_inventory.root)
        test_source_ids[test_inventory.root] = source_id
        sources.append(
            {
                "sourceId": source_id,
                "sourceType": "code_artifact",
                "location": test_inventory.root,
                "canonicality": "operational",
                "sensitivity": "internal",
                "accessStatus": "inspected",
                "inspectedAt": generated_at,
                "limitation": "Test-path metadata indicates implementation structure only; test contents were not inspected.",
            }
        )

    statements: list[dict[str, Any]] = [
        _statement(
            "ST-repository-inventory",
            "fact",
            "A bounded local repository inventory completed using approved metadata classes.",
            [repository_source_id],
            "high",
            ["product identity", "inventory completeness"],
            True,
            "accepted_for_scope",
        ),
        _statement(
            "ST-demand-evidence-missing",
            "missing",
            "No approved customer-demand evidence was inspected during repository-only adoption.",
            [],
            "high",
            ["validation posture", "launch and expansion claims"],
            True,
            "fill_gap",
        ),
    ]

    identity_documents = [
        document for document in inventory.documents if document.product_name
    ]
    identity_source_ids = [
        document_source_ids[document.relative_path] for document in identity_documents
    ]
    identity_conflict = (
        len({slug(document.product_name or "") for document in identity_documents}) > 1
    )
    identity_statement_id: str | None = None
    if identity_source_ids:
        identity_statement_id = (
            "ST-product-identity-conflict"
            if identity_conflict
            else "ST-product-identity"
        )
        statements.append(
            _statement(
                identity_statement_id,
                "conflict" if identity_conflict else "fact",
                (
                    "Approved repository metadata sources declare conflicting product identities."
                    if identity_conflict
                    else "Approved repository metadata declares the current product name."
                ),
                identity_source_ids,
                "high" if identity_conflict else "medium",
                ["product identity"],
                True,
                "resolve_conflict" if identity_conflict else "accepted_for_scope",
            )
        )

    implementation_statement_ids: list[str] = []
    if git_source_id and git.has_history:
        statement_id = "ST-git-history-present"
        implementation_statement_ids.append(statement_id)
        statements.append(
            _statement(
                statement_id,
                "fact",
                f"The local Git repository contains {git.commit_count} commit(s).",
                [git_source_id],
                "high",
                ["implementation maturity"],
                True,
                "accepted_for_scope",
            )
        )
    elif git.present:
        statements.append(
            _statement(
                "ST-git-history-missing",
                "missing",
                "The local Git repository has no inspectable commit history.",
                [],
                "high",
                ["delivery traceability"],
                True,
                "fill_gap",
            )
        )
    else:
        statements.append(
            _statement(
                "ST-git-unavailable",
                "missing",
                "No local Git metadata was available for the adoption inventory.",
                [],
                "high",
                ["delivery traceability"],
                True,
                "fill_gap",
            )
        )

    for test_inventory in inventory.tests:
        statement_id = stable_id("ST", test_inventory.root, label="tests")
        implementation_statement_ids.append(statement_id)
        statements.append(
            _statement(
                statement_id,
                "fact",
                f"Approved test-path metadata contains {test_inventory.file_count} test file(s).",
                [test_source_ids[test_inventory.root]],
                "medium",
                ["implementation maturity"],
                True,
                "accepted_for_scope",
            )
        )

    package_documents = [
        document
        for document in inventory.documents
        if document.kind == "package_metadata"
    ]
    if package_documents:
        statement_id = "ST-package-metadata-present"
        implementation_statement_ids.append(statement_id)
        statements.append(
            _statement(
                statement_id,
                "fact",
                "Approved package metadata is present in the repository.",
                [
                    document_source_ids[document.relative_path]
                    for document in package_documents
                ],
                "high",
                ["implementation maturity", "runtime inventory"],
                True,
                "accepted_for_scope",
            )
        )

    safety_gap_statement_id: str | None = None
    if inventory.skipped_source_count or inventory.traversal_truncated:
        safety_gap_statement_id = "ST-safety-omissions"
        statements.append(
            _statement(
                safety_gap_statement_id,
                "fact",
                "One or more potential sources were excluded by bounded safety rules.",
                [repository_source_id],
                "high",
                ["inventory completeness", "sensitive-data boundary"],
                True,
                "accepted_for_scope",
            )
        )

    stage_statement_id: str | None = None
    if implementation_statement_ids:
        stage_statement_id = "ST-implementation-stage-assessment"
        implementation_source_ids = sorted(
            {
                source_id
                for statement in statements
                if statement["statementId"] in implementation_statement_ids
                for source_id in statement["sourceIds"]
            }
        )
        statements.append(
            _statement(
                stage_statement_id,
                "inference",
                "Repository and Git metadata support an implementation-maturity assessment at ticket execution; this does not advance validation posture.",
                implementation_source_ids,
                "medium",
                ["current stage assessment"],
                True,
                "validate",
            )
        )

    artifacts, artifact_statement_ids = _build_artifacts(
        inventory,
        implementation_statement_ids,
        identity_statement_id,
    )
    relationships = _build_relationships(artifacts, artifact_statement_ids)
    gaps = _build_gaps(
        inventory,
        artifacts,
        safety_gap_statement_id,
        git.present,
        git.has_history,
        identity_conflict,
    )

    current_stage = "ticket_execution" if implementation_statement_ids else "unknown"
    stage_confidence = "medium" if implementation_statement_ids else "low"
    stage_rationale_ids = (
        [stage_statement_id] if stage_statement_id else ["ST-repository-inventory"]
    )

    next_actions = [
        {
            "actionId": "NEXT-validate-demand",
            "title": "Define and execute the missing demand-validation plan",
            "ownerRole": "Validation Agent",
            "priority": "P2",
            "blockedByGapIds": ["GAP-demand-evidence"],
            "approvalRequired": False,
            "suggestedCommand": "/pipe:validate",
        }
    ]
    if any(gap["gapId"] == "GAP-product-context" for gap in gaps):
        next_actions.append(
            {
                "actionId": "NEXT-product-context",
                "title": "Reconstruct the minimum product context from approved sources",
                "ownerRole": "Product Strategist",
                "priority": "P2",
                "blockedByGapIds": ["GAP-product-context"],
                "approvalRequired": False,
                "suggestedCommand": "/pipe:discover",
            }
        )
    if safety_gap_statement_id:
        next_actions.append(
            {
                "actionId": "NEXT-review-safety-omissions",
                "title": "Review whether excluded source classes are required",
                "ownerRole": "Risk Reviewer",
                "priority": "P1",
                "blockedByGapIds": ["GAP-safety-omissions"],
                "approvalRequired": True,
                "suggestedCommand": None,
            }
        )

    return {
        "schemaVersion": "0.1.0",
        "baselineId": f"PB-{product_id}-adopt",
        "generatedAt": generated_at,
        "entryMode": "adopt",
        "status": "review_required",
        "product": {
            "productId": product_id,
            "name": inventory.product_name,
            "summary": "Existing repository reconstructed from bounded local repository and Git metadata; product and demand claims remain unverified.",
            "owner": "founder",
        },
        "lifecycle": {
            "currentStage": current_stage,
            "stageConfidence": stage_confidence,
            "stageRationaleStatementIds": sorted(set(stage_rationale_ids)),
            "nextAllowedStage": "validation_planning",
        },
        "systems": {
            "repository": {
                "identifier": product_id,
                "location": ".",
                "status": "conflicting" if identity_conflict else "confirmed",
            },
            "linear": None,
            "github": None,
        },
        "sources": sorted(sources, key=lambda item: item["sourceId"]),
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
            "demandValidationStatus": "unproven",
            "strongestEvidenceLane": "none",
            "statementIds": [],
            "boundaryStatement": "Repository files, package metadata, tests, and Git history can show implementation maturity but do not prove customer demand, willingness to pay, product-market fit, or completion of historical validation gates.",
        },
        "governanceGaps": sorted(gaps, key=lambda item: item["gapId"]),
        "reconciliationPlan": [],
        "approvals": [],
        "nextActions": sorted(next_actions, key=lambda item: item["actionId"]),
        "stopConditions": [
            "Do not inspect excluded sensitive sources without explicit human approval.",
            "Do not create or update Linear, GitHub, deployment, or other external records during repository-only adoption.",
            "Do not treat implementation maturity as customer-demand validation.",
        ],
    }


def _document_source(
    document: MetadataDocument, source_id: str, inspected_at: str
) -> dict[str, Any]:
    limitation = (
        "README metadata can describe intended product context but does not prove customer demand."
        if document.kind == "readme"
        else "Package metadata indicates implementation structure but does not prove product validation."
    )
    return {
        "sourceId": source_id,
        "sourceType": "repository_file",
        "location": document.relative_path,
        "canonicality": "canonical" if document.kind == "readme" else "operational",
        "sensitivity": "internal",
        "accessStatus": "inspected",
        "inspectedAt": inspected_at,
        "limitation": limitation,
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


def _build_artifacts(
    inventory: RepositoryInventory,
    implementation_statement_ids: list[str],
    identity_statement_id: str | None,
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    artifacts: list[dict[str, Any]] = []
    statement_ids: dict[str, list[str]] = {}
    readmes = [
        document for document in inventory.documents if document.kind == "readme"
    ]
    if readmes:
        source = readmes[0]
        provenance = (
            [identity_statement_id]
            if source.product_name and identity_statement_id
            else ["ST-repository-inventory"]
        )
        artifacts.append(
            {
                "artifactId": "ART-product-context",
                "artifactType": "product_context",
                "title": "README product context",
                "status": "partial",
                "sourceRef": source.relative_path,
                "externalRef": None,
                "provenanceStatementIds": provenance,
            }
        )
        statement_ids["ART-product-context"] = provenance
    else:
        artifacts.append(
            {
                "artifactId": "ART-product-context",
                "artifactType": "product_context",
                "title": "Product context",
                "status": "missing",
                "sourceRef": None,
                "externalRef": None,
                "provenanceStatementIds": ["ST-repository-inventory"],
            }
        )
        statement_ids["ART-product-context"] = ["ST-repository-inventory"]

    for document in inventory.documents:
        if document.kind != "package_metadata":
            continue
        artifact_id = stable_id("ART", document.relative_path, label="package")
        provenance = ["ST-package-metadata-present"]
        artifacts.append(
            {
                "artifactId": artifact_id,
                "artifactType": "code_artifact",
                "title": "Package metadata",
                "status": "present",
                "sourceRef": document.relative_path,
                "externalRef": None,
                "provenanceStatementIds": provenance,
            }
        )
        statement_ids[artifact_id] = provenance

    for test_inventory in inventory.tests:
        artifact_id = stable_id("ART", test_inventory.root, label="tests")
        provenance = [stable_id("ST", test_inventory.root, label="tests")]
        artifacts.append(
            {
                "artifactId": artifact_id,
                "artifactType": "code_artifact",
                "title": "Test suite metadata",
                "status": "present",
                "sourceRef": test_inventory.root,
                "externalRef": None,
                "provenanceStatementIds": provenance,
            }
        )
        statement_ids[artifact_id] = provenance

    if "ST-git-history-present" in implementation_statement_ids:
        artifacts.append(
            {
                "artifactId": "ART-git-history",
                "artifactType": "code_artifact",
                "title": "Git delivery history",
                "status": "present",
                "sourceRef": ".git",
                "externalRef": None,
                "provenanceStatementIds": ["ST-git-history-present"],
            }
        )
        statement_ids["ART-git-history"] = ["ST-git-history-present"]

    artifacts.append(
        {
            "artifactId": "ART-demand-validation",
            "artifactType": "validation_artifact",
            "title": "Customer-demand evidence",
            "status": "missing",
            "sourceRef": None,
            "externalRef": None,
            "provenanceStatementIds": ["ST-demand-evidence-missing"],
        }
    )
    statement_ids["ART-demand-validation"] = ["ST-demand-evidence-missing"]
    return artifacts, statement_ids


def _build_relationships(
    artifacts: list[dict[str, Any]],
    artifact_statement_ids: dict[str, list[str]],
) -> list[dict[str, Any]]:
    relationships: list[dict[str, Any]] = []
    for artifact in artifacts:
        artifact_id = artifact["artifactId"]
        if artifact_id in {"ART-product-context", "ART-demand-validation"}:
            continue
        relationships.append(
            {
                "fromArtifactId": "ART-product-context",
                "relationshipType": "documents",
                "toArtifactId": artifact_id,
                "confidence": "low",
                "sourceStatementIds": artifact_statement_ids.get(
                    artifact_id, ["ST-repository-inventory"]
                ),
            }
        )
    return relationships


def _build_gaps(
    inventory: RepositoryInventory,
    artifacts: list[dict[str, Any]],
    safety_statement_id: str | None,
    git_present: bool,
    git_has_history: bool,
    identity_conflict: bool,
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = [
        {
            "gapId": "GAP-demand-evidence",
            "category": "validation",
            "severity": "P2",
            "description": "No approved customer evidence was available to establish demand validation.",
            "affectedArtifactIds": ["ART-demand-validation", "ART-product-context"],
            "evidenceStatementIds": ["ST-demand-evidence-missing"],
            "blocks": [
                "customer-demand claims",
                "market expansion based on repository maturity",
            ],
            "remediation": "Run the governed validation workflow before using demand claims for scope, launch, or expansion decisions.",
            "owner": "Validation Agent",
            "status": "open",
        }
    ]
    product_context = next(
        item for item in artifacts if item["artifactId"] == "ART-product-context"
    )
    if product_context["status"] == "missing":
        gaps.append(
            {
                "gapId": "GAP-product-context",
                "category": "product",
                "severity": "P2",
                "description": "No approved README product context was available.",
                "affectedArtifactIds": ["ART-product-context"],
                "evidenceStatementIds": ["ST-repository-inventory"],
                "blocks": ["confident product framing"],
                "remediation": "Reconstruct the minimum product context from approved sources without inventing historical evidence.",
                "owner": "Product Strategist",
                "status": "open",
            }
        )
    if identity_conflict:
        gaps.append(
            {
                "gapId": "GAP-product-identity",
                "category": "product",
                "severity": "P1",
                "description": "Approved repository metadata contains conflicting product identities.",
                "affectedArtifactIds": ["ART-product-context"],
                "evidenceStatementIds": ["ST-product-identity-conflict"],
                "blocks": ["confirmed product identity", "external reconciliation"],
                "remediation": "Resolve the canonical product identity before matching or mutating external systems.",
                "owner": "Product Strategist",
                "status": "blocked",
            }
        )
    if safety_statement_id:
        gaps.append(
            {
                "gapId": "GAP-safety-omissions",
                "category": "risk",
                "severity": "P1",
                "description": "Potential sources were omitted because of sensitive-path, secret-shape, size, or traversal boundaries.",
                "affectedArtifactIds": [],
                "evidenceStatementIds": [safety_statement_id],
                "blocks": ["claiming a complete repository inventory"],
                "remediation": "Keep the sources excluded unless a separately approved, purpose-limited sensitive-data review is required.",
                "owner": "Risk Reviewer",
                "status": "blocked",
            }
        )
    if not git_present or not git_has_history:
        evidence_id = "ST-git-history-missing" if git_present else "ST-git-unavailable"
        gaps.append(
            {
                "gapId": "GAP-git-history",
                "category": "execution",
                "severity": "P3",
                "description": "Git delivery history was unavailable or empty for this repository inventory.",
                "affectedArtifactIds": [],
                "evidenceStatementIds": [evidence_id],
                "blocks": ["Git-based delivery reconstruction"],
                "remediation": "Confirm the intended repository or preserve the limitation when Git history is intentionally absent.",
                "owner": "Architecture Agent",
                "status": "open",
            }
        )
    return gaps
