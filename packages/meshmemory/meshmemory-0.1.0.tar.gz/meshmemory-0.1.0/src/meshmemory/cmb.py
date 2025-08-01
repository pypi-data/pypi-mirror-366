# ==============================================================================
# Consenix Protocol – Cognitive Memory Block (CMB) – Canonical Implementation
# Canonical Protocol Unit for MeshMemory, Mesh Cognition, and Protocol-Lawful AI
#
# File:        cmb.py
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
#   – Cognitive Memory Block (CMB) canonical unit
#   – SVAF (Symbolic–Vector Attention Fusion) and related event logic
#
# The Consenix Protocol, Mesh Cognition, CMB, and all associated schemas,
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

from datetime import datetime
import numpy as np
import uuid

class CognitiveMemoryBlock:
    """
    MeshMemory Protocol: Cognitive Memory Block (CMB)
    Reference: Protocol Overview §CMB, AAAI-26 Section 3.1, docs/protocol_overview.md

    A field-complete, protocol-normalized, immutable memory unit.
    - Each field is a named, normalized vector (e.g., intent, commitment, etc.).
    - Unique ID is assigned at creation (for mesh trails/graph).
    - Edges record ancestry (fusion, collapse, remix) as per mesh protocol law.
    - Metadata may include agent_id, timestamp, validator_id, protocol event info.
    - Provenance (optional): per-field semantic context trace for full auditability.
    - Labels (optional): per-field symbolic label for audit/test/demo.
    """

    def __init__(
        self,
        fields: dict,
        metadata: dict = None,
        provenance: dict = None,
        labels: dict = None,
        edges: list = None,
        id: str = None
    ):
        """
        Initialize a CognitiveMemoryBlock.
        Args:
            fields: dict mapping field names (str) to np.ndarray (protocol-normalized)
            metadata: dict, optional. Agent/timestamp/event metadata.
            provenance: dict, optional. Per-field semantic context.
            labels: dict, optional. Per-field symbolic label.
            edges: list, optional. List of edge dicts: {"from": [...], "relation": "..."}
            id: str, optional. Unique CMB ID (auto-generated if None)
        Raises:
            ValueError if any field vector is zero or normalization fails.
        """
        self.fields = {k: self._normalize(v) for k, v in fields.items()}
        self.metadata = dict(metadata or {})
        if "timestamp" not in self.metadata:
            self.metadata["timestamp"] = datetime.now()
        self.provenance = provenance or {}
        self.labels = labels or {}
        self.edges = edges or []
        self.id = id or str(uuid.uuid4())

    def _normalize(self, v):
        """Ensures vector is protocol-normalized (unit norm)."""
        v = np.array(v)
        norm = np.linalg.norm(v)
        if norm == 0:
            raise ValueError("Field vector cannot be zero (protocol violation)")
        return v / norm

    def to_dict(self):
        """
        Serializes the CMB to a dictionary (for audit log, mesh export, or storage).
        Returns:
            dict with all fields, metadata, id, edges, provenance, and labels.
        """
        out = {
            "id": self.id,
            "fields": {k: v.tolist() for k, v in self.fields.items()},
            "metadata": self.metadata,
            "edges": self.edges
        }
        if self.provenance:
            out["provenance"] = self.provenance
        if self.labels:
            out["labels"] = self.labels
        return out

    @staticmethod
    def from_dict(d):
        """
        Instantiates a CMB from a dictionary (e.g., from storage or network).
        Args:
            d: dict with "fields", "metadata", "provenance", "labels", "edges", "id"
        Returns:
            CognitiveMemoryBlock
        """
        provenance = d.get("provenance", {})
        labels = d.get("labels", {})
        edges = d.get("edges", [])
        id = d.get("id")
        return CognitiveMemoryBlock(
            {k: np.array(v) for k, v in d["fields"].items()},
            d.get("metadata", {}),
            provenance=provenance,
            labels=labels,
            edges=edges,
            id=id
        )

    def validate_completeness(self, required_fields):
        """Checks that all required fields are present."""
        missing = [f for f in required_fields if f not in self.fields]
        if missing:
            raise ValueError(f"CMB is missing required fields: {missing}")

    def validate_all_normalized(self, tol=1e-6):
        """Checks all fields are normalized to unit norm (within tolerance)."""
        for k, v in self.fields.items():
            if abs(np.linalg.norm(v) - 1.0) > tol:
                raise ValueError(f"Field '{k}' not protocol-normalized: {v}")

    def get_field_provenance(self, field):
        """Returns the provenance for a field, if present."""
        return self.provenance.get(field)

    def get_field_label(self, field):
        """Returns the symbolic label for a field, if present."""
        return self.labels.get(field)

    def __repr__(self):
        return (
            f"<CognitiveMemoryBlock(id={self.id}, fields={list(self.fields.keys())}, "
            f"metadata={self.metadata}, edges={self.edges}, "
            f"provenance_keys={list(self.provenance.keys())}, "
            f"labels_keys={list(self.labels.keys())})>"
        )
