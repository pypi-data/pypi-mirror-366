# ==============================================================================
# Consenix Protocol – Vector Evolution Engine (VEE)
# Canonical Protocol Pipeline for Lawful Cognitive Onboarding and Field Embedding
#
# File:        vee.py
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
#   – Vector Evolution Engine (VEE) Onboarding Pipeline
#   – Cognitive Memory Blocks (CMBs), field parsing, inference, compliance, and audit
#
# The Consenix Protocol, VEE, Mesh Cognition, and all associated algorithms,
# schemas, and trademarks (MeshMemory™, CMB™, SVAF™, VEE™) are the exclusive,
# registered intellectual property of Consenix Group Ltd (UK), and protected by
# applicable protocol law, global IP treaties, and protocol governance RFCs.
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


import openai
import numpy as np
from datetime import datetime
from .cmb import CognitiveMemoryBlock

CAT7_FIELDS = [
    "intent", "commitment", "emotion", "motivation", "perspective", "focus", "issue"
]

class ProtocolComplianceError(Exception):
    pass

# ---- 1. Parsing & Field Extraction ----
def parse_fields(raw_input, context=None):
    """
    Returns a dict of symbolic candidate fields. In production, use LLM or protocol extractor.
    """
    # For now: stub using OpenAI LLM, but can swap for deterministic/mock for test/dev.
    return {"intent": raw_input, "commitment": "unknown", "emotion": "neutral",
            "motivation": "unknown", "perspective": "unknown",
            "focus": "unknown", "issue": "unknown"}

def llm_field_extractor(raw_input, api_key, model="gpt-4", context=None):
    """
    Uses OpenAI Chat API to extract all CAT7 fields from raw input.
    """
    system_prompt = (
        "Given any raw input, assign a protocol-relevant label for each of the following fields: "
        "intent, commitment, emotion, motivation, perspective, focus, issue. "
        "Return your output as a valid JSON dictionary: "
        '{"intent": "...", "commitment": "...", "emotion": "...", '
        '"motivation": "...", "perspective": "...", "focus": "...", "issue": "..."}'
    )
    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Raw input: {raw_input}"}
    ]
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model, messages=prompt, temperature=0.2, max_tokens=256, n=1
    )
    import re, json
    content = response.choices[0].message.content
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
    json_str = match.group(1) if match else content
    try:
        fields = json.loads(json_str)
    except Exception:
        raise ProtocolComplianceError(f"LLM output not parseable as JSON: {content}")
    fields = {k.lower(): v.strip() for k, v in fields.items() if k.lower() in CAT7_FIELDS}
    for f in CAT7_FIELDS:
        if f not in fields:
            fields[f] = "unknown"
    return fields

# ---- 2. Field Inference & Embedding ----
def infer_embed(fields, dim=128):
    """
    For each symbolic field, embed into a deterministic protocol vector.
    """
    embedded = {}
    for f, label in fields.items():
        h = hash((f, label))
        rng = np.random.default_rng(abs(h) % (2 ** 32))
        v = rng.standard_normal(dim)
        v /= np.linalg.norm(v)
        embedded[f] = v
    return embedded

# ---- 3. Compliance Validation & Drift Checking ----
def validate_compliance(fields, schema_fields):
    missing = [f for f in schema_fields if f not in fields]
    if missing:
        raise ProtocolComplianceError(f"Missing required fields: {missing}")

def check_drift(cmb, anchors, schema_fields, D_max=0.35):
    """
    Measures protocol drift between new CMB and a set of anchor CMBs.
    Returns drift per anchor, and triggers clarifier if drift > D_max.
    """
    drifts = []
    for anchor in anchors:
        drift = 1 - np.mean([
            np.dot(cmb.fields[f], anchor.fields[f])
            for f in schema_fields
        ])
        drifts.append(drift)
    max_drift = max(drifts) if drifts else 0
    clarifier_invoked = max_drift > D_max
    return drifts, max_drift, clarifier_invoked

# ---- 4. Audit Logging ----
def vee(raw_input, api_key, context=None, config=None, event=None, anchors=None, model="gpt-4"):
    """
    The only lawful ingress for memory. Passes raw input through all protocol-mandated VEE stages.
    Returns: (CMB, full_audit_log)
    """
    config = config or {}
    schema_fields = config.get("fields", CAT7_FIELDS)
    field_dim = config.get("field_dim", 128)
    # --- 1. Parse/Extract Fields ---
    symbolic_fields = llm_field_extractor(raw_input, api_key, model=model, context=context)
    # --- 2. Inference/Embedding ---
    embedded_fields = infer_embed(symbolic_fields, dim=field_dim)
    # --- 3. Compliance Validation ---
    validate_compliance(embedded_fields, schema_fields)
    cmb = CognitiveMemoryBlock(
        fields=embedded_fields,
        metadata={
            "agent_id": context.get("agent_id", "unknown") if context else "unknown",
            "timestamp": datetime.now().isoformat(),
            "event": event,
        },
        labels=symbolic_fields
    )
    cmb.validate_completeness(schema_fields)
    cmb.validate_all_normalized()
    drift_info = {}
    clarifier_needed = False
    if anchors:
        drifts, max_drift, clarifier_needed = check_drift(cmb, anchors, schema_fields, D_max=config.get("max_drift", 0.35))
        drift_info = {
            "anchor_drifts": drifts,
            "max_drift": max_drift,
            "clarifier_needed": clarifier_needed
        }
    # --- 4. Full Protocol Audit ---
    audit_log = {
        "event": "vee_onboarding",
        "cmb_id": cmb.id,
        "fields": list(embedded_fields.keys()),
        "labels": symbolic_fields,
        "raw_input": raw_input,
        "context": context,
        "config": config,
        "timestamp": cmb.metadata["timestamp"],
        "drift_info": drift_info
    }
    return cmb, audit_log
