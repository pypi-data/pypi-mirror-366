# ==============================================================================
# Consenix Protocol – Symbolic–Vector Attention Fusion (SVAF) Engine
# Canonical Protocol Implementation for Mesh Cognition
#
# File:        svaf_fusion.py
# Version:     v0.1.0
# Date:        2025-08-01
# Author:      Consenix Labs Ltd (R&D subsidiary of Consenix Group Ltd)
# Principal Inventor: Hongwei Xu (hongwei@consenix.com)
#
# Protocol Reference: Consenix Mesh Memory Protocol White Paper v1.0, SVAF: Symbolic–Vector Attention Fusion for Mesh Cognition (AAAI-26 Submission), Genesis Yellow Paper v1.0
# Documentation:     https://consenix.com/papers/mesh-memory-white-paper | https://consenix.com/papers/mesh-memory-yellow-paper
# Official Website:  https://consenix.com
#
# -------------------------------------------------------------------------------
# PROTOCOL IP AND COPYRIGHT NOTICE
#
# © 2025 Consenix Group Ltd. All rights explicitly reserved.
#
# This source file is part of the Consenix Protocol and Mesh Cognition Stack,
# including all derivative works of:
#   – Mesh Memory Protocol
#   – SVAF (Symbolic–Vector Attention Fusion) Method
#   – Cognitive Memory Blocks (CMBs) and related structures
#
# The Consenix Protocol, SVAF, Mesh Cognition, and all associated algorithms,
# schemas, and trademarks (Consensus on Intelligence Exchange™, SVAF™, CMB™,
# Mesh Cognition™) are the exclusive, registered intellectual property of
# Consenix Group Ltd (UK), and protected by applicable protocol law, global IP
# treaties, and protocol governance RFCs.
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
#   – Xu, H. (2025). SVAF: Symbolic–Vector Attention Fusion for Mesh Cognition. AAAI-26 Submission.
#   – Consenix Protocol White Paper v1.0: Consensus on Intelligence Exchange.
#
# Provenance: Canonical codebase, protocol-audited. All edits and extensions must be RFC-logged and validator-signed.
#
# -------------------------------------------------------------------------------
# THIS FILE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# ==============================================================================

import datetime
import numpy as np
from typing import List, Dict, Any, Tuple

from .cmb import CognitiveMemoryBlock
from .audit import save_audit_log
from .validators.layer_transition import ProtocolLayerTransitionValidator, LayerTransitionError

# Protocol field names (CAT7)
CAT7_FIELDS = [
    "intent", "commitment", "emotion", "motivation", "perspective", "focus", "issue"
]

# Default protocol config values
DEFAULT_CONFIG = {
    "alpha_f": 1.0,
    "layer_gravity": 1.0,
    "temporal_decay": 0.05,
    "lambda_new": 1.0,
    "confidence": 1.0,
    "drift_threshold": 0.5,
}

class ProtocolComplianceError(Exception):
    """Raised if SVAF fusion or clarifier fails protocol law compliance."""

def field_cosine(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-8
    return float(np.dot(vec1, vec2) / denom)

def compute_time_diff_seconds(ts1, ts2) -> float:
    """Compute time difference in seconds between two timestamps."""
    diff = ts1 - ts2
    if isinstance(diff, datetime.timedelta):
        return diff.total_seconds()
    return float(diff)

def compute_anchor_score(
    cmb_new: CognitiveMemoryBlock,
    anchor: CognitiveMemoryBlock,
    field: str,
    config: Dict[str, Any]
) -> float:
    """
    Compute the protocol-canonical anchor score for a single anchor and field.
    """
    sim = field_cosine(cmb_new.fields[field], anchor.fields[field])
    layer = anchor.metadata.get("layer", 1)
    gravity = config.get("layer_gravity", DEFAULT_CONFIG["layer_gravity"]) * layer or 1.0
    time_diff = compute_time_diff_seconds(
        cmb_new.metadata.get("timestamp", 0),
        anchor.metadata.get("timestamp", 0)
    )
    recency = np.exp(-config.get("temporal_decay", DEFAULT_CONFIG["temporal_decay"]) * time_diff) or 1.0
    confidence = anchor.metadata.get("confidence", config.get("confidence", DEFAULT_CONFIG["confidence"])) or 1.0
    alpha_f = config.get("alpha_f", DEFAULT_CONFIG["alpha_f"])
    alpha = (alpha_f.get(field, 1.0) if isinstance(alpha_f, dict) else alpha_f) or 1.0
    return alpha * sim * gravity * recency * confidence

def compute_anchor_scores(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock],
    field: str,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Compute anchor scores for all anchors for a given field.
    """
    return np.array([
        compute_anchor_score(cmb_new, anchor, field, config)
        for anchor in anchor_cmbs
    ])

def protocol_field_fusion(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock],
    field: str,
    weights: np.ndarray,
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Lawful, protocol-weighted fusion of a single field.
    """
    anchor_vecs = [a.fields[field] for a in anchor_cmbs]
    lambda_new = config.get("lambda_new", DEFAULT_CONFIG["lambda_new"])
    fused_vector = lambda_new * cmb_new.fields[field]
    for i, anchor_vec in enumerate(anchor_vecs):
        fused_vector += weights[i] * anchor_vec
    total_weight = lambda_new + np.sum(weights)
    fused_vector /= total_weight
    norm = np.linalg.norm(fused_vector)
    if norm == 0:
        raise ValueError(f"Fused vector for field '{field}' has zero norm (protocol violation).")
    return fused_vector / norm

def compute_field_drifts(
    fused_vectors: Dict[str, np.ndarray],
    cmb_new: CognitiveMemoryBlock
) -> Dict[str, float]:
    """
    Compute drift for each field between fused and candidate vectors.
    """
    return {
        f: float(1 - np.dot(fused_vectors[f], cmb_new.fields[f]))
        for f in fused_vectors
    }

def compute_layer_drifts(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock]
) -> List[int]:
    """
    Compute absolute difference in protocol layer between candidate and each anchor.
    """
    candidate_layer = cmb_new.metadata.get("layer", 1)
    return [
        abs(candidate_layer - a.metadata.get("layer", 1))
        for a in anchor_cmbs
    ]

def derive_fused_layer(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock]
) -> int:
    """
    Return the mode (most common) layer among candidate and anchors.
    """
    layers = [cmb_new.metadata.get("layer", 1)] + [a.metadata.get("layer", 1) for a in anchor_cmbs]
    return max(set(layers), key=layers.count)

def svaf_fuse(
    cmb_new: CognitiveMemoryBlock,
    anchor_cmbs: List[CognitiveMemoryBlock],
    config: Dict[str, Any],
    validator: ProtocolLayerTransitionValidator = None,
    fields: List[str] = CAT7_FIELDS
) -> Tuple[CognitiveMemoryBlock, Dict[str, Any], Dict[str, Any]]:
    """
    Symbolic–Vector Attention Fusion (SVAF): Canonical, protocol-lawful field-wise fusion.
    No side effects: NO logging, NO auditing, NO file output. All auditing is to be performed by the API/caller.
    Returns:
        - fused_cmb: The new protocol-fused CognitiveMemoryBlock (with provenance).
        - metrics: {"block": ..., "fields": ...}
        - svaf_details: full computation details (anchor_weights, field_context, etc.)
    """
    fused_vectors = {}
    anchor_weights_all = {}
    field_context = {}

    # --- 1. Field-wise anchor scoring and fusion (with provenance) ---
    for f in fields:
        scores = compute_anchor_scores(cmb_new, anchor_cmbs, f, config)
        sum_scores = np.sum(scores)
        weights = scores / sum_scores if sum_scores != 0 else np.ones(len(scores)) / len(scores)
        anchor_weights_all[f] = weights.tolist()
        fused_vectors[f] = protocol_field_fusion(cmb_new, anchor_cmbs, f, weights, config)

        # Provenance trace construction (labels and anchor info)
        anchor_context = []
        for anchor, w in zip(anchor_cmbs, weights):
            anchor_id = getattr(anchor, "id", None)
            anchor_label = None
            if hasattr(anchor, "labels") and anchor.labels and f in anchor.labels:
                anchor_label = anchor.labels[f]
            elif hasattr(anchor, "provenance") and anchor.provenance and f in anchor.provenance:
                anchor_label = anchor.provenance[f].get("label")
            anchor_context.append({
                "anchor_id": anchor_id,
                "anchor_label": anchor_label,
                "vector": anchor.fields[f].tolist(),
                "weight": float(w),
            })
        fused_label = None
        if anchor_context:
            candidates = [ac["anchor_label"] for ac in anchor_context if ac["anchor_label"] is not None]
            if candidates:
                from collections import Counter
                fused_label = Counter(candidates).most_common(1)[0][0]

        field_context[f] = {
            "fused_vector": fused_vectors[f].tolist(),
            "fused_label": fused_label,
            "anchors": anchor_context
        }

    # --- 2. Assemble fused CMB with provenance ---
    fused_layer = derive_fused_layer(cmb_new, anchor_cmbs)
    fused_cmb = CognitiveMemoryBlock(
        fields=fused_vectors,
        metadata={"event": "svaf_fusion", "layer": fused_layer},
        provenance=field_context
    )

    # --- 3. Compute drifts for audit and clarifier ---
    field_drifts = compute_field_drifts(fused_vectors, cmb_new)
    block_drift = float(np.mean(list(field_drifts.values())))
    layer_drifts = compute_layer_drifts(cmb_new, anchor_cmbs)

    # --- 4. Lawful layer transition enforcement ---
    if validator is not None:
        prev_layer_vec = cmb_new.metadata.get("layer")
        fused_layer_vec = fused_cmb.metadata.get("layer")
        event_metadata = {
            "event": "svaf_fusion_layer_transition",
            "cmb_new_id": getattr(cmb_new, "id", None),
            "fused_cmb_id": getattr(fused_cmb, "id", None),
            "anchor_ids": [getattr(a, "id", None) for a in anchor_cmbs]
        }
        validator.check_transition(prev_layer_vec, fused_layer_vec, event_metadata)

    # --- 5. Protocol drift enforcement and clarifier logic (for caller) ---
    drift_threshold = config.get("drift_threshold", DEFAULT_CONFIG["drift_threshold"])
    clarifier_status = None
    clarifier_log = None
    if block_drift > drift_threshold:
        # The caller (API level) should invoke clarifier/exception if needed
        clarifier_status = "review"
        clarifier_log = {
            "block": block_drift,
            "fields": field_drifts
        }
        print(
            f"SVAF fusion rejected: block drift={block_drift:.3f} > threshold={drift_threshold}, not accepted by clarifier"
        )
    else:
        clarifier_status = "accepted"
        clarifier_log = None

    # --- 6. Collect protocol-grade details for audit/event layer ---
    svaf_details = {
        "anchor_weights": anchor_weights_all,
        "field_context": field_context,
        "field_drifts": field_drifts,
        "block_drift": block_drift,
        "layer_drifts": layer_drifts,
        "clarifier_status": clarifier_status,
        "clarifier_log": clarifier_log,
    }

    # --- 7. Return (no audit/logging here) ---
    return fused_cmb, {"block": block_drift, "fields": field_drifts}, svaf_details
