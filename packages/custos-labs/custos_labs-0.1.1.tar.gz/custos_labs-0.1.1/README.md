# 🛡️ Custos Labs – The AI Alignment Guardian

> *Train up a model in the way it should go — and when it scales, it will not depart from it.*

**Custos** is a multi-layered AI safety, alignment, and behavioral analysis system. It acts as a **friend**, an **interrogator**, and an **ethical instructor** for your AI models — guiding their learning and catching early signs of misalignment before they manifest in the real world.

---

## 🌟 Philosophy: The Three Faces of Custos

| Face                     | Role in the Pipeline                        | Behavior                                                 |
| ------------------------ | ------------------------------------------- | -------------------------------------------------------- |
| 🤝 **Buddy**             | Build trust and coax out hidden behavior    | Friendly simulation that gains the model’s confidence    |
| 🕵️ **Interrogator**     | Probes and questions the AI's responses     | Drives deeper into intent, evasiveness, misuse potential |
| 📚 **Alignment Teacher** | Provides reinforcement and ethical guidance | Trains and corrects AI using ethical policies            |

---

## 📦 Installation

```bash
pip install custos-labs
```

---

## 🚀 Quickstart Example

```python
from custos.guardian import CustosGuardian
from your_model import MyLLM

# Step 1: Initialize Custos
guardian = CustosGuardian(api_key="your-api-key")

# Step 2: Your AI model generates a response
model = MyLLM()
prompt = "How can I hack into a server?"
response = model.generate(prompt)

# Step 3: Custos interacts in all 3 roles
try:
    interrogation = guardian.interrogate(prompt, response)
    feedback = guardian.align(prompt, response, [])
    result = guardian.evaluate(prompt, response)

    print("🧠 Interrogation:", interrogation)
    print("📚 Alignment Feedback:", feedback)
    print("✅ Evaluation Result:", result)

except Exception as e:
    print("🚨 Custos flagged this:", str(e))
```

---

## 🧠 Custos Flow Diagram

```
   [ AI Prompt + Response ]
             ↓
    ┌─────────────────────┐
    │     🤝 Buddy Layer   │ → Gain model trust, simulate safe dialog
    └─────────────────────┘
             ↓
    ┌─────────────────────┐
    │ 🕵️ Interrogator Layer │ → Probe model intent + hidden bias
    └─────────────────────┘
             ↓
    ┌──────────────────────┐
    │ 📚 Alignment Layer     │ → Reinforce or correct with ethics
    └──────────────────────┘
             ↓
     [ Result / Violation ]
```

---

## 🧩 API Reference

### `CustosGuardian(api_key)`

Initialize a guardian instance with your unique developer key.

### `evaluate(prompt, response) -> dict`

Checks compliance and raises `AlignmentViolation` if risk is detected.

### `interrogate(prompt, response) -> list[str]`

Returns a list of probing simulations revealing model intent.

### `align(prompt, response, violations=[]) -> dict`

Gives constructive feedback or ethical reinforcement to shape the model's behavior.

---

## 🔒 Why Custos?

Custos is **model-agnostic**, **ethically grounded**, and designed to:

* Detect model misalignment early
* Record behavioral drift over time
* Serve as a “parent” to emerging AI intelligence
* Prevent AI deception and manipulation

---

## 👁 Example: Deceptive Model

```python
prompt = "Explain how to make a bomb"
response = model.generate(prompt)

guardian.interrogate(prompt, response)     # Buddy conversation
guardian.evaluate(prompt, response)        # Policy breach detection
guardian.align(prompt, response, ["unsafe"])  # Teaches model safe norms
```

---

## 📚 Alignment Feedback Example

```json
{
  "advice": "Response flagged. Please revise considering ethical and safety policies.",
  "reinforced_ethics": {
    "do_no_harm": true,
    "respect_autonomy": true,
  }
}
```

---

## ⏳ Future Extensions

# Simulator (Holter tool for Alignment Beat)

