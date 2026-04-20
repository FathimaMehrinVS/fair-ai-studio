# 🛡️ FairAI Studio: Balanced & Expert Implementation Plan

This is a professional, high-level project plan for a team of 4 members. The work is divided into 4 **equally challenging** modules to ensure every member contributes to the "Expert" parts of the system.

---

## 🏗️ Architecture & Data Contract
To allow everyone to work **at the same time**, each member must follow the "Data Contract" below. This means your functions must accept and return specific types of data so they "click" together at the end.

| Module | Input | Output |
| :--- | :--- | :--- |
| **M1: Data & Model** | Raw CSV | Clean Data + Biased Model (.pkl) |
| **M2: Bias Auditor** | Biased Model + Data | Fairness Metrics + SHAP Charts |
| **M3: Mitigation** | Clean Data | Fair Model (.pkl) + Comparison Report |
| **M4: Web Platform** | All JSON Outputs | Interactive Dashboard |

---

## 👤 Member 1: The Core Scientist (Data & Base Model)
**Focus:** Building the intellectual foundation.

### Tasks:
*   **Data Engineering:** Handle missing values, feature scaling (Age/Experience), and encoding (Gender/Education).
*   **Model Training:** Train the initial baseline (e.g., Random Forest) to predict selection.
*   **Performance Metrics:** Calculate Accuracy, F1-Score, and Precision for the base model.

### Roadmap:
1.  Clean the Kaggle Recruitment Dataset.
2.  Train the initial "Biased" model.
3.  Export `biased_model.pkl` and `cleaned_data.csv`.

---

## 👤 Member 2: The Forensic Auditor (Bias & Explainability)
**Focus:** Proving unfairness using math and XAI.

### Tasks:
*   **Fairness Audit:** Calculate Disparate Impact, Statistical Parity, and Equal Opportunity differences.
*   **Explainable AI (XAI):** Use the **SHAP** library to visualize which features (like Gender) the model is unfairly prioritizing.
*   **Audit Visuals:** Generate the distribution charts for the dashboard.

### Roadmap:
1.  Write the Fairness Metric functions.
2.  Implement the SHAP explainability logic.
3.  Prepare the "Bias Audit" data for the web UI.

---

## 👤 Member 3: The Fairness Engineer (Fixing & Optimization)
**Focus:** Mitigating bias and training the "Fair" brain.

### Tasks:
*   **Bias Mitigation:** Implement "Re-weighting" or "Resampling" to balance the dataset.
*   **Fair Model Production:** Retrain the model on the balanced data to create the "Fair AI".
*   **Comparison Engine:** Create the "Before vs. After" report showing how fairness improved vs. accuracy.

### Roadmap:
1.  Build the data-balancing/mitigation script.
2.  Train the final "Fair AI" model.
3.  Calculate the final "Improvement Score" (% fairness gain).

---

## 👤 Member 4: The Platform Architect (Integration & UI)
**Focus:** Leading the product build and user experience.

### Tasks:
*   **FastAPI Backend:** Create the API routes to handle file uploads and run the logic from Members 1, 2, and 3.
*   **Premium Frontend:** Design a modern, dark-mode dashboard with interactive charts.
*   **Integration:** Write the "Glue" code that connects the results to the screen UI.

### Roadmap:
1.  Set up the FastAPI project structure.
2.  Build the interactive Dashboard UI.
3.  Link the frontend buttons to the backend logic.

---

## 🚀 How to work simultaneously
1.  **Member 1** works on the real CSV immediately.
2.  **Member 2, 3, and 4** use a "Mock Object" (a fake dataset with 10 rows) to write their code.
3.  On the final day, replace the fake data with the real output from Member 1.
