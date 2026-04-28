# ⚖️ FairAI Studio  
### Empowering Ethical Recruitment through Responsible AI

FairAI Studio is an end-to-end platform designed to **detect, explain, and mitigate bias in AI-driven recruitment systems**. It transforms traditional “black-box” models into **transparent, fair, and accountable decision-making systems**, ensuring that hiring is based on merit—not demographic attributes.

Built as part of the **Google Solution Challenge**, this project demonstrates a practical and scalable approach to **Responsible AI**.

---

## 🌟 Problem Statement

Modern recruitment systems increasingly rely on machine learning models. However, these models often inherit **hidden biases from historical data**, leading to unfair hiring decisions based on factors like gender or background.

Key challenges:
- ❌ Lack of visibility into model bias  
- ❌ Difficulty in interpreting AI decisions  
- ❌ Complexity in mitigating bias without reducing accuracy  

---

## 🚀 Our Solution

FairAI Studio provides a **complete fairness pipeline**:

### 🔍 1. Bias Auditing
- Computes fairness metrics:
  - Disparate Impact (DI)
  - Statistical Parity Difference (SPD)
- Detects unfair treatment across demographic groups

---

### 🧠 2. Explainable AI (XAI)
- Uses **SHAP (SHapley Additive Explanations)**  
- Visualizes feature importance  
- Detects hidden **proxy bias variables**

---

### ⚖️ 3. Bias Mitigation
- Applies **reweighing and resampling techniques**  
- Reduces bias while maintaining model accuracy  
- Produces a **Fair Model**

---

### 🤖 4. Generative Fairness Insights (Google Gemini)
- Converts complex fairness metrics into:
  - Clear explanations  
  - Actionable hiring recommendations  
- Makes the system accessible to **non-technical users**

---

## 📊 Key Results

| Metric | Biased Model | Fair Model |
|------|------------|------------|
| Disparate Impact | ~0.45 | ~1.00 |
| Statistical Parity | -0.31 | ~0.00 |
| Accuracy | ~85% | ~84% |

✔ Achieved **~99% fairness improvement**  
✔ Maintained strong predictive performance  

---

## 🛠️ Tech Stack

### 🔧 Backend
- Python
- FastAPI

### 🤖 Machine Learning
- Scikit-learn  
- Pandas  
- NumPy  

### 📊 Explainability & Visualization
- SHAP  
- Matplotlib  

### 🌐 Frontend
- Interactive Dashboard (Custom UI)

### ☁️ AI Integration
- Google Gemini API (Gemini 2.5 Flash)  
- Google GenAI SDK  

### 🚀 Deployment
- Docker (Cloud-ready)  
- Hosted prototype:  
👉 https://fair-ai-studio.onrender.com/

---

## 🧩 Architecture Overview
<img width="1003" height="669" alt="image" src="https://github.com/user-attachments/assets/db575825-60e1-48d2-87b0-292312cc3a7a" />

---

## 👥 Team Structure

| Member | Role | Responsibility |
|--------|------|----------------|
| 👤 Athira V | Data Scientist | Data preprocessing & baseline model |
| 👤 Fathima Mehrin V S | Forensic Auditor | Bias detection & SHAP explainability |
| 👤 Anna T Jeby | Fairness Engineer | Bias mitigation & model optimization |
| 👤 Esha Byju Nair | Platform Architect | Backend + UI integration |

---

## 📂 Project Outputs

- `biased_model.pkl` → Baseline model  
- `cleaned_data.csv` → Processed dataset  
- `predictions.csv` → Model predictions  
- Fairness reports & visualizations  

---

## 🛠️ Installation & Setup

```bash
# Clone repository
git clone https://github.com/FathimaMehrinVS/fair-ai-studio.git

cd fair-ai-studio

# Install dependencies
pip install -r requirements.txt

# Run backend
uvicorn main:app --reload
```
## 🎥 Demo

👉 **Live Prototype:**  
https://fair-ai-studio.onrender.com/

---

## 🌍 Impact

FairAI Studio aligns with:

- 🌐 **UN SDG 10: Reduced Inequalities**  
- 💼 **UN SDG 8: Decent Work and Economic Growth**

By promoting fairness in hiring, it helps organizations:
- build diverse teams  
- reduce discrimination  
- ensure ethical AI adoption  

---

## 🚀 Future Scope

- Integration with real-world HR systems  
- Support for multiple domains (e.g., loans, education)  
- Advanced fairness metrics and auditing tools  

---

## 🧠 Key Innovation

The core innovation is the **combination of fairness metrics + generative AI**:

> Making ethical AI understandable, actionable, and accessible to everyone.

---

## 📜 License

This project is developed for educational and research purposes under the Google Solution Challenge.
