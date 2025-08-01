# MeshMemory SDK

**MeshMemory™** is the protocol-native, event-driven substrate for composable, auditable cognitive memory in AI and multi-agent systems—built and owned by Consenix Group Ltd.

---

## 🚀 What is MeshMemory?

MeshMemory is the backbone protocol for the Mesh Cognition era.
It enables:

* **Structured cognitive onboarding** (from any raw input, agent, or event)
* **Semantic–vector fusion and remix** with full field-level traceability
* **Clarifier agents** for drift review and protocol alignment
* **Canonical memory evolution** (create, remix, clarify, collapse, canonize)
* **Mesh-native audit trails and field evolution graphs**
* **Composable, explainable intelligence—beyond LLM vector stores**

**All memory evolution in MeshMemory is governed by explicit, protocol-lawful events.**

> **See [Protocol Whitepaper](https://consenix.com/papers/mesh-memory-white-paper) and [AAAI-26 submission](https://github.com/meshmemory/meshmemory-sdk)**

---

## 🧑‍💻 Developer Quickstart

**Install from PyPI:**

```bash
pip install meshmemory
```

**From source:**

```bash
git clone https://github.com/meshmemory/meshmemory-sdk.git
cd meshmemory-sdk
pip install -e .
```

> See [`examples/`](./examples/) for ready-to-run demos.

---

### 🔹 **Universal Mesh Protocol Events**

MeshMemory exposes **lawful, event-driven protocol operations**:

#### **1. Create (Onboard raw input)**

```python
from meshmemory import create
cmb, audit = create("Summarize regulatory risks for Q3.", api_key="sk-...")
print(cmb.labels)   # {'intent': ..., 'commitment': ...}
print(cmb.fields)   # field: normalized vector
```

#### **2. Remix (Fuse CMBs)**

```python
fused_cmb, audit = remix(cmb, [cmb2, cmb3])
print(audit["cmb_field_evolution"]["intent"])
```

#### **3. Clarify (Drift/Contradiction)**

```python
decision, clarifier_audit = clarify(fused_cmb, drift_scores, config)
# decision is one of: "accepted", "review", "rejected"
```

#### **4. Collapse & Canonize (Trail Evolution/Assetization)**

```python
collapsed_cmb, collapse_audit = collapse([cmb, cmb2, fused_cmb])
canonical_cmb, canonize_audit = canonize([cmb, cmb2, fused_cmb])
```

**All operations return a full audit log** with field-by-field semantic evolution and mesh ancestry.

---

### 🟩 **Minimal Example: Onboarding to CMB**

```python
from meshmemory import create

raw_input = "List the main compliance and technical risks for Q4."
cmb, audit = create(raw_input, api_key="sk-...")
print("CMB ID:", cmb.id)
print("Labels:", cmb.labels)
print("Vectors:", {k: v.shape for k, v in cmb.fields.items()})
print("Audit log:", audit)
```

---

## 📖 Documentation

* [Protocol Overview](./docs/protocol_overview.md)
* [SVAF API Reference](./docs/svaf_api_reference.md)
* [Memory Evolution API Reference](./docs/memory_evolution_api_reference.md)
* [Metrics & Experiments](./docs/metrics.md)
* [Replication & Reproducibility](./docs/replication.md)

---

## 🔬 Reproducibility & Research

* All code, configs, and scripts for AAAI-26 MeshMemory and SVAF experiments are provided.
* See [docs/replication.md](./docs/replication.md) for instructions and environment setup.

---

## 💼 IP, Licensing, and Commercial Use

MeshMemory SDK and protocol are **exclusive IP of Consenix Group Ltd**.

* **No commercial use, redistribution, or integration permitted** without written license.
* See [LICENSE](./LICENSE) and [IP\_NOTICE.md](./IP_NOTICE.md).

For enterprise, OEM, or partnership:
[licensing@consenix.com](mailto:licensing@consenix.com)
or [https://consenix.com/license](https://consenix.com/license)

---

## 🤝 Contributing

* Bugs and docs suggestions are welcome.
* Protocol changes/features require RFC via Consenix governance.
* All contributions are subject to IP assignment.

See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## 📢 VC/Acquirer/Legal Review

* Canonical protocol implementation and SDK.
* All code, data, audit, and legal boundaries mapped to protocol and IP.
* Diligence, partnership, and transfer inquiries welcome.

---

## 📚 Citation

If using MeshMemory in research, cite:

> Xu, H. (2025). Mesh Memory Protocol: A Protocol-Governed Architecture for Structured Cognition and Semantic Continuity in Multi-Agent Systems. AAAI-26 Submission.

---

© 2025 Consenix Group Ltd. All Rights Reserved.
MeshMemory™, CMB™, SVAF™, CAT7™, and SYMBit™ are trademarks of Consenix Group Ltd.
