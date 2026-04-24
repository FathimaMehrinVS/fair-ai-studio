# 🔬 Forensic Audit Report: Bias Analysis

## Executive Summary
This report details the fairness audit of the baseline recruitment model (`biased_model.pkl`). We evaluated the model across several mathematical fairness metrics and used SHAP (SHapley Additive exPlanations) to identify feature importance and potential sources of bias.

## 📊 Fairness Metrics
We analyzed the model performance based on the **Gender** feature (Privileged: 1, Unprivileged: 0).

| Metric | Value | Ideal | Interpretation |
| :--- | :--- | :--- | :--- |
| **Disparate Impact** | 1.1025 | 1.0 | Favors unprivileged group slightly (within 0.8-1.2 range). |
| **Statistical Parity Diff** | 0.0372 | 0.0 | Minimal difference in selection rates. |
| **Equal Opportunity Diff** | 0.0152 | 0.0 | Model treats qualified candidates fairly across groups. |

## 🧠 Explainable AI (SHAP)
The SHAP summary plot (`shap_summary.png`) reveals the primary drivers behind the model's decisions.

- **Primary Features:** Experience Years and Screening Score are the dominant factors.
- **Gender Impact:** The SHAP values for Gender show a distribution that suggests the model does use Gender, but its overall weight is lower than core competency metrics.

## 🏁 Conclusion
While the model is labeled as "Biased", the initial audit shows it is relatively fair according to standard metrics. However, even small deviations in statistical parity can lead to systemic issues over time. These results serve as a baseline for Member 3's mitigation efforts.
