# ==============================================================================
# Consenix Protocol – Protocol Audit Logging – Canonical Implementation
# Protocol-Lawful Audit Trail, Compliance, and Governance Logging for MeshMemory
#
# File:        audit.py
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
#   – Protocol audit logging, audit trail, and compliance mechanisms
#   – Validator signature, clarifier event, and protocol compliance audit logic
#
# The Consenix Protocol, Mesh Cognition, Audit, and all associated schemas,
# algorithms, trademarks, and implementation standards are exclusive, registered
# intellectual property of Consenix Group Ltd (UK), and protected under protocol
# law, global IP treaties, and protocol governance RFCs.
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

import json
from datetime import datetime, date
from pathlib import Path
import uuid
import numpy as np

def audit_event(
    request_payload: dict,
    response_payload: dict,
    log_dir: str = "logs/",
    raw_input_text: str = None,
    raw_input_ref: str = None,
    mesh_id: str = None
):
    """
    Event-driven mesh audit logger.
    Accepts the full SVAF request and response payload after each event (fusion, collapse, etc.),
    bundles all CMBs and event edges, and writes a protocol-complete mesh audit log.

    Args:
        request_payload: dict – The SVAF (or other event) request payload (includes anchors, config, raw input ref/text)
        response_payload: dict – The SVAF response (fused_cmb, edges, computation details)
        log_dir: str – Directory for audit log storage.
        raw_input_text: str – Optional, original user or agent input (for provenance).
        raw_input_ref: str – Optional, reference or hash to original data (for mesh audit/external system).
        mesh_id: str – Optional, mesh/experiment/session identifier.

    Returns:
        fname: str – Path to saved audit log file (ISO-timestamped).
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat().replace(":", "-")
    event_id = None
    if response_payload.get("edges"):
        event_id = response_payload["edges"][0].get("event_id", None)
    elif response_payload.get("event_id"):
        event_id = response_payload.get("event_id", "")
    mesh_part = f"_{mesh_id}" if mesh_id else ""
    event_part = f"_{event_id}" if event_id else ""
    fname = f"{log_dir}/mesh_audit_{ts}{mesh_part}{event_part}.json"

    # === Bundle protocol-complete event graph ===
    cmbs = []
    # Include all anchors as CMBs (with unique IDs, edges will reference them)
    for anchor in response_payload.get("anchors", []):
        anchor_node = dict(anchor)
        if raw_input_text:
            anchor_node["raw_input_text"] = raw_input_text
        if raw_input_ref:
            anchor_node["raw_input_ref"] = raw_input_ref
        cmbs.append(anchor_node)

    # Always include the fused CMB node (with edges) as a mesh node
    fused_cmb = response_payload.get("fused_cmb", None)
    if fused_cmb:
        if raw_input_text:
            fused_cmb["raw_input_text"] = raw_input_text
        if raw_input_ref:
            fused_cmb["raw_input_ref"] = raw_input_ref
        cmbs.append(fused_cmb)

    edges = response_payload.get("edges", [])

    audit_bundle = {
        "mesh_id": mesh_id,
        "timestamp": ts,
        "request_payload": request_payload,
        "response_payload": response_payload,
        "cmbs": cmbs,
        "edges": edges,
        "svaf_details": response_payload.get("svaf_details", {}),
        "exception": response_payload.get("exception", None)
    }

    def default(obj):
        # Numpy arrays -> list
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        # Numpy scalars -> Python scalars
        if isinstance(obj, np.generic):
            return obj.item()
        # UUIDs -> string
        if isinstance(obj, uuid.UUID):
            return str(obj)
        # datetime/date -> ISO
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        # sets -> list
        if isinstance(obj, set):
            return list(obj)
        # pathlib.Path -> str
        if isinstance(obj, Path):
            return str(obj)
        # fallback
        return str(obj)

    with open(fname, "w") as f:
        json.dump(audit_bundle, f, indent=2, default=default)
    return fname

def save_audit_log(audit_log, log_dir="logs/"):
    """
    Canonical Audit Logger for MeshMemory Protocol.
    Persists audit logs for all protocol events: fusion, clarifier, validator decisions, layer transitions, etc.

    Args:
        audit_log: dict — Structured, protocol-compliant event log (see docs/metrics.md, protocol_overview.md)
        log_dir: str — Directory for audit log storage (default "logs/"). Created if missing.

    Returns:
        fname: str — Path to saved audit log file (ISO-timestamped)
    Protocol References:
        - Protocol Overview §Audit, AAAI-26 Section 5.5
        - docs/protocol_overview.md, docs/metrics.md
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().isoformat().replace(":", "-")  # Safe for most filesystems
    fname = f"{log_dir}/audit_{ts}.json"
    with open(fname, "w") as f:
        json.dump(audit_log, f, indent=2)
    return fname

def load_audit_log(fname):
    """
    Loads and returns a previously saved audit log (for compliance, debugging, or governance review).
    Args:
        fname: str — Path to the audit log JSON file.
    Returns:
        audit_log: dict
    """
    with open(fname, "r") as f:
        return json.load(f)

def list_audit_logs(log_dir="logs/"):
    """
    Lists all audit log files in the given directory.
    Args:
        log_dir: str — Directory to scan.
    Returns:
        List[str]: Filenames of audit logs.
    """
    p = Path(log_dir)
    return sorted(str(f) for f in p.glob("mesh_audit_*.json"))