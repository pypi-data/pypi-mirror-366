# ==============================================================================
# Consenix Protocol – Lawful Memory Evolution Module
# Canonical Event-Driven Mesh Protocol: Create, Remix, Clarify, Collapse, Canonize
#
# File:        memory_evolution.py
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
# including all derivative works of:
#   – Mesh Memory Protocol
#   – Lawful Memory Evolution event API (create, remix, clarify, collapse, canonize)
#   – Semantic field evolution tracing and mesh audit logic
#
# The Consenix Protocol, Mesh Memory Evolution API, and all associated algorithms,
# schemas, and trademarks are the exclusive, registered intellectual property of
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
#   – Xu, H. (2025). Mesh Memory Protocol: A Protocol-Governed Architecture for Structured Cognition and Semantic Continuity in Multi-Agent Systems. AAAI-26 Submission.
#   – Consenix Protocol White Paper v1.0: Consensus on Intelligence Exchange.
#
# Provenance: Canonical codebase, protocol-audited. All edits and extensions must be RFC-logged and validator-signed.
#
# -------------------------------------------------------------------------------
# THIS FILE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.
# ==============================================================================

import uuid
from datetime import datetime
from .cmb import CognitiveMemoryBlock
from .vee import vee
from .svaf_api import svaf_api
from .clarifier import clarifier_event

# ====== MeshMemory Lawful Event API ======

def create(raw_input, api_key, context=None, config=None):
    """
    Lawful onboarding (VEE) event: turns raw input into a protocol-compliant CMB.
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    cmb, audit = vee(raw_input, api_key=api_key, context=context, config=config)
    audit.update({
        'event_type': 'create',
        'cmb_id': cmb.id,
        'timestamp': datetime.now().isoformat(),
    })
    return cmb, audit

def remix(candidate_cmb, anchor_cmbs, config=None, request_id=None):
    """
    Remix protocol event: fuses candidate CMB with anchors using SVAF.
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    config = config or {}
    request_id = request_id or str(uuid.uuid4())
    request_payload = {
        "cmb_new": candidate_cmb.to_dict(),
        "anchors": [a.to_dict() for a in anchor_cmbs],
        "config": config,
        "request_id": request_id,
    }
    response = svaf_api(request_payload)
    fused_cmb = CognitiveMemoryBlock.from_dict(response["fused_cmb"])
    audit = {
        "event_type": "remix",
        "fused_cmb_id": fused_cmb.id,
        "anchors": [a.id for a in anchor_cmbs],
        "edges": response["edges"],
        "svaf_details": response["svaf_details"],
        "timestamp": datetime.now().isoformat(),
        "cmb_field_evolution": extract_field_evolution(response)
    }
    return fused_cmb, audit

def clarify(fused_cmb, drift_scores, config):
    """
    Clarify protocol event: runs protocol clarifier logic.
    Returns: (decision, audit_log)
    """
    decision, clarifier_audit = clarifier_event(fused_cmb, drift_scores, config)
    clarifier_audit.update({
        'event_type': 'clarify',
        'timestamp': datetime.now().isoformat(),
    })
    return decision, clarifier_audit

def collapse(trail_cmbs, config=None):
    """
    Collapse protocol event: collapses a sequence/trail of CMBs to a canonical form.
    (Implemented as SVAF remix for demo/protocol MVP.)
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    config = config or {}
    candidate = trail_cmbs[0]
    anchors = trail_cmbs[1:]
    fused_cmb, audit = remix(candidate, anchors, config, request_id="collapse-" + str(uuid.uuid4()))
    audit['event_type'] = 'collapse'
    return fused_cmb, audit

def canonize(trail_cmbs, config=None):
    """
    Canonize protocol event: finalizes a trail as a protocol-certified, immutable cognitive asset.
    Returns: (CognitiveMemoryBlock, audit_log)
    """
    fused_cmb, audit = collapse(trail_cmbs, config)
    audit.update({
        'event_type': 'canonize',
        'canonical': True,
        'timestamp': datetime.now().isoformat()
    })
    return fused_cmb, audit

# ====== Semantic Field Evolution Extraction ======

def extract_field_evolution(response):
    """
    Traces the evolution path for each CMB field in a protocol remix event.
    Returns: dict {field_name: [{ancestor_id, label, vector, weight}, ... , {fused_label, fused_vector}]}
    """
    field_context = response.get("svaf_details", {}).get("field_context", {})
    evolution = {}
    for field, ctx in field_context.items():
        evolution[field] = [
            {
                "ancestor_id": a.get("anchor_id"),
                "label": a.get("anchor_label"),
                "vector": a.get("vector"),
                "weight": a.get("weight")
            }
            for a in ctx.get("anchors", [])
        ]
        evolution[field].append({
            "fused_label": ctx.get("fused_label"),
            "fused_vector": ctx.get("fused_vector")
        })
    return evolution
