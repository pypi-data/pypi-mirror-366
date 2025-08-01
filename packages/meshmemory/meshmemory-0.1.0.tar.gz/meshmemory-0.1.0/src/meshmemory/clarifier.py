# ==============================================================================
# Consenix Protocol – Clarifier Agent/Event – Canonical Implementation
# Protocol-Lawful Arbitration and Semantic Drift Governance for MeshMemory
#
# File:        clarifier.py
# Version:     v0.1.0
# Date:        2025-08-01
# Author:      Consenix Labs Ltd (R&D subsidiary of Consenix Group Ltd)
# Principal Inventor: Hongwei Xu (hongwei@consenix.com)
#
# Protocol Reference: Consenix Mesh Memory Protocol White Paper v1.0, Mesh Memory Protocol (AAAI-26 Submission), Genesis Yellow Paper v1.0
# Documentation:     https://consenix.com/papers/mesh-memory-white-paper | https://consenix.com/papers/mesh-memory-yellow-paper
# Official Website:  https://consenix.com
#
# -------------------------------------------------------------------------------
# PROTOCOL IP AND COPYRIGHT NOTICE
#
# © 2025 Consenix Group Ltd. All rights explicitly reserved.
#
# This source file is part of the Consenix Protocol and Mesh Cognition Stack,
# including all canonical and derivative works of:
#   – Mesh Memory Protocol
#   – Clarifier Agent/Event logic
#   – SVAF (Symbolic–Vector Attention Fusion) and drift adjudication protocol
#
# The Consenix Protocol, Mesh Cognition, Clarifier Agent, and all associated
# schemas, algorithms, trademarks, and implementation standards are exclusive,
# registered intellectual property of Consenix Group Ltd (UK), and protected
# under protocol law, global IP treaties, and protocol governance RFCs.
#
# USE OF THIS CODE IS GOVERNED STRICTLY BY THE CONSENIX PROTOCOL LICENSE:
#   – No reproduction, distribution, modification, or commercial use except as
#     permitted under a signed, protocol-compliant license from Consenix Group Ltd.
#   – Unauthorized forking, remix, or canonicalization outside protocol bounds is
#     a violation of protocol law and subject to validator enforcement and legal action.
#   – Integration, deployment, or derivative use in enterprise or VC-backed
#     products must retain this header and notify licensing@consenix.com.
#
# Contact for licensing, legal, and protocol governance:
#   – Licensing: licensing@consenix.com
#   – Legal: legal@consenix.com
#   – Protocol Law: https://consenix.com/protocol-law
#
# For scientific citation or academic use, cite:
#   – Xu, H. (2025). Mesh Memory Protocol: A Protocol-Governed Architecture for Structured Cognition and Semantic Continuity in Multi-Agent Systems. AAAI-26 Submission.
#   – Consenix Protocol White Paper v1.0: Consensus on Intelligence Exchange.
#
# Provenance: Canonical codebase, protocol-audited. All edits and extensions must be RFC-logged and validator-signed.
#
# -------------------------------------------------------------------------------
# THIS FILE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# ==============================================================================

def clarifier_event(fused_cmb, drift_scores, config):
    """
    Canonical Clarifier Event for MeshMemory Protocol.
    Determines protocol-lawful outcome for a fused memory event
    based on block drift, and returns normalized decision with audit details.

    Args:
        fused_cmb: CognitiveMemoryBlock (result of fusion/remix)
        drift_scores: dict with at least 'block' (float), and optionally per-field scores
        config: dict, must include protocol thresholds:
            - 'drift_threshold': float, required for acceptance
            - 'clarifier_band': float, upper bound for auto-reject
            - (optional: 'timestamp', other audit metadata)
    Returns:
        decision: str ('accepted', 'review', or 'rejected')
        audit: dict with clarifier decision, drift, thresholds, timestamp, etc.

    Protocol References:
        - Protocol Overview §Clarifier, AAAI-26 Section 3.7
        - docs/protocol_overview.md, docs/metrics.md
    """
    block_drift = drift_scores.get("block")
    threshold = config.get("drift_threshold", 0.25)
    upper = config.get("clarifier_band", 0.5)
    timestamp = config.get("timestamp")

    # Lawful protocol decision logic (3-state Kanban)
    if block_drift is None:
        raise ValueError("clarifier_event: drift_scores must include 'block' drift value.")

    if block_drift > upper:
        decision = "rejected"   # Lawful stop
    elif block_drift > threshold:
        decision = "review"     # Needs cognitive/agent intervention
    else:
        decision = "accepted"   # Lawful, proceed

    audit = {
        "clarifier_decision": decision,
        "block_drift": block_drift,
        "drift_threshold": threshold,
        "clarifier_band": upper,
        "timestamp": timestamp,
        "fused_cmb_id": getattr(fused_cmb, "id", None),
        "kanban_status": decision,   # Optional: duplicate for Kanban UI/flow
        "recommended_action": {
            "accepted": "Proceed with next cognitive step.",
            "review": "Review this memory for possible clarification or realignment.",
            "rejected": "Protocol violation. Revise or abandon this memory."
        }[decision]
    }
    # Include per-field drifts, etc. as desired
    if "fields" in drift_scores:
        audit["field_drifts"] = drift_scores["fields"]

    return decision, audit
