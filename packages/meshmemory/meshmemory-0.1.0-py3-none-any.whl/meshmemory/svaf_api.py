# ==============================================================================
# Consenix Protocol – SVAF API Entry Point – MeshMemory SDK
# Canonical Protocol-Facing, Open-Source API for Mesh Cognition
#
# File:        svaf_api.py
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
#   – SVAF API entrypoint and orchestration logic
#   – Cognitive Memory Blocks (CMBs) and related API contracts
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

from .cmb import CognitiveMemoryBlock

# In future: from meshmemory_core import svaf_fuse
from .svaf_fusion import svaf_fuse   # For now, included in SDK. Move to core later.

def svaf_api(request_payload: dict) -> dict:
    """
    Protocol-facing SVAF API.
    - Accepts a VEE/mesh-generated request payload (see below)
    - Returns a protocol-complete SVAF response, including:
        - Fused CMB, all anchors, event edge(s), SVAF metrics, exception if any.
    - No audit/logging side effects (caller must invoke audit).

    Request payload structure:
    {
        "cmb_new": { ... },          # Candidate CMB node (dict, includes id, fields, metadata, etc.)
        "anchors": [ ... ],          # List of anchor CMB dicts (same structure)
        "config": { ... },           # Protocol config/hyperparams (for SVAF, drift, etc.)
        "request_id": "event-uuid"   # Optional, used as event id
        # Optionally: "raw_input_ref", "raw_input_text"
    }

    Response structure:
    {
        "fused_cmb": { ... },        # Resulting fused CMB dict
        "anchors": [ ... ],          # Repeat anchors (so audit/event has full event context)
        "edges": [
            {
                "from": ["anchor_id1", "anchor_id2", ...],
                "relation": "is_fused_from",
                "event_id": "event-uuid"
            }
        ],
        "svaf_details": { ... },     # Anchor weights, drift, field context, etc.
        "exception": str or None     # Any error or protocol violation details
    }
    """
    try:
        # Parse CMBs from dicts (with id/fields/metadata/edges/labels/provenance)
        cmb_new = CognitiveMemoryBlock.from_dict(request_payload["cmb_new"])
        anchors = [CognitiveMemoryBlock.from_dict(a) for a in request_payload["anchors"]]
        config = request_payload["config"]
        event_id = request_payload.get("request_id")

        # --- Run protocol-lawful SVAF fusion (core is pure/stateless) ---
        fused_cmb, svaf_metrics, svaf_details = svaf_fuse(
            cmb_new, anchors, config, fields=list(cmb_new.fields.keys())
        )

        # --- Prepare protocol edge (all ancestry, event_id for audit) ---
        edge = {
            "from": [a.id for a in anchors],
            "relation": "is_fused_from",
            "event_id": event_id
        }

        response = {
            "fused_cmb": fused_cmb.to_dict(),
            "anchors": [a.to_dict() for a in anchors],
            "edges": [edge],
            "svaf_details": svaf_details,
            "exception": None
        }
    except Exception as ex:
        # On protocol violation or error, package for async audit/log
        response = {
            "fused_cmb": None,
            "anchors": [a.to_dict() for a in anchors] if 'anchors' in locals() else [],
            "edges": [],
            "svaf_details": {},
            "exception": str(ex)
        }
    return response
