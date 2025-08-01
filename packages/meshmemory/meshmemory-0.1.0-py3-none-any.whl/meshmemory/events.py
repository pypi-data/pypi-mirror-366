# ==============================================================================
# Consenix Protocol – Mesh Memory Evolution Events (Event Ontology)
# Canonical Protocol Event Types and Event Logging for MeshMemory
#
# File:        events.py
# Version:     v1.0.0
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
#   – MeshProtocolEvent ontology (CREATE, REMIX, CLARIFY, COLLAPSE, CANONIZE)
#   – Mesh event logging, ancestry graph, and protocol audit logic
#
# The Consenix Protocol, Mesh Memory Events, and all associated schemas,
# algorithms, and trademarks are the exclusive, registered intellectual property of
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

from datetime import datetime

class MeshProtocolEvent:
    """
    Canonical mesh event types for lawful memory evolution.
    """
    CREATE = "create"         # Agent asserts a new VEE-validated CMB (starts a Trail)
    REMIX = "remix"           # Multiple CMBs/Trails fused via SVAF (creates new memory)
    CLARIFY = "clarify"       # Triggered by drift/contradiction; clarifier agents realign
    COLLAPSE = "collapse"     # Trails reduced to canonical state by validator consensus
    CANONIZE = "canonize"     # Trail finalized to immutable cognitive asset

def create_event(event_type, cmb, related_cmb_ids=None, **kwargs):
    """
    Creates a protocol event record for mesh audit/logging.
    """
    return {
        "event_type": event_type,
        "cmb_id": cmb.id,
        "related_cmb_ids": related_cmb_ids or [],
        "timestamp": datetime.now().isoformat(),
        "details": kwargs
    }
