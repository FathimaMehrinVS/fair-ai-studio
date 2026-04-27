"""
Member 4: Platform Architect — FastAPI Backend
Integrates outputs from Members 1, 2, and 3.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import io
import base64
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
from scipy.stats import gaussian_kde
import functools
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv()

BASE_DIR = Path(__file__).parent

# Existing configs
HF_TOKEN = os.getenv("HF_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini if key exists
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="FairAI Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")

# ─── Cache / Preload ──────────────────────────────────────────────────────────

@functools.lru_cache(maxsize=1)
def load_models():
    biased = joblib.load(BASE_DIR / "biased_model.pkl")
    fair = joblib.load(BASE_DIR / "fair_model.pkl")
    return biased, fair

@functools.lru_cache(maxsize=1)
def get_cleaned_data():
    return pd.read_csv(BASE_DIR / "cleaned_data.csv")


# ─── Helper ──────────────────────────────────────────────────────────────────

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def calculate_fairness_metrics(df, prediction_col, sensitive_feature="gender", target="shortlisted"):
    privileged = df[df[sensitive_feature] == 1]
    unprivileged = df[df[sensitive_feature] == 0]
    sr_p = privileged[prediction_col].mean()
    sr_u = unprivileged[prediction_col].mean()
    di = sr_u / sr_p if sr_p > 0 else 0
    spd = sr_u - sr_p
    tpr_p = privileged[privileged[target] == 1][prediction_col].mean()
    tpr_u = unprivileged[unprivileged[target] == 1][prediction_col].mean()
    eod = tpr_u - tpr_p
    return {
        "selection_rate_privileged": float(sr_p),
        "selection_rate_unprivileged": float(sr_u),
        "disparate_impact": float(di),
        "statistical_parity_difference": float(spd),
        "equal_opportunity_difference": float(eod),
    }





# ─── Chart generators ────────────────────────────────────────────────────────

DARK_BG = "#09090b"
CARD_BG = "#131316"
ACCENT = "#00f0ff"
GREEN  = "#39ff14"
PURPLE = "#e81cff"
ORANGE = "#ff3366"
YELLOW = "#facc15"
GRID   = "#27272a"
TEXT   = "#ffffff"


def make_gauge_fig(value: float, label: str, ideal: float, low: float, high: float):
    """Semi-circle gauge chart."""
    fig, ax = plt.subplots(figsize=(4, 2.4), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")

    # Background arc
    theta = np.linspace(np.pi, 0, 200)
    ax.plot(np.cos(theta), np.sin(theta), color=GRID, linewidth=14, solid_capstyle="round")

    # Clamp value to [low, high]
    norm = max(0.0, min(1.0, (value - low) / (high - low))) if (high - low) != 0 else 0.5
    # Ideal position
    ideal_norm = max(0.0, min(1.0, (ideal - low) / (high - low))) if (high - low) != 0 else 0.5

    # Determine colour
    dist_from_ideal = abs(value - ideal)
    max_dist = max(abs(high - ideal), abs(low - ideal), 1e-9)
    ratio = dist_from_ideal / max_dist
    if ratio < 0.15:
        arc_color = GREEN
    elif ratio < 0.4:
        arc_color = YELLOW
    else:
        arc_color = ORANGE

    # Filled arc
    theta_fill = np.linspace(np.pi, np.pi - norm * np.pi, 200)
    ax.plot(np.cos(theta_fill), np.sin(theta_fill), color=arc_color, linewidth=14, solid_capstyle="round")

    # Ideal marker
    ideal_angle = np.pi - ideal_norm * np.pi
    ax.plot(
        [0.72 * np.cos(ideal_angle), 0.88 * np.cos(ideal_angle)],
        [0.72 * np.sin(ideal_angle), 0.88 * np.sin(ideal_angle)],
        color=GREEN, linewidth=2.5, zorder=5
    )

    # Needle
    needle_angle = np.pi - norm * np.pi
    ax.annotate("", xy=(0.65 * np.cos(needle_angle), 0.65 * np.sin(needle_angle)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=1.5))
    ax.plot(0, 0, "o", color=TEXT, markersize=5)

    ax.text(0, -0.12, f"{value:.4f}", ha="center", va="center",
            fontsize=14, fontweight="bold", color=TEXT,
            fontfamily="monospace")
    ax.text(0, -0.28, label, ha="center", va="center",
            fontsize=8, color="#8b949e")

    return fig


def make_selection_rate_chart(metrics_biased: dict, metrics_fair: dict):
    fig, ax = plt.subplots(figsize=(7, 3.8), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)

    groups = ["Male (Privileged)", "Female (Unprivileged)"]
    biased_vals = [
        metrics_biased["selection_rate_privileged"],
        metrics_biased["selection_rate_unprivileged"],
    ]
    fair_vals = [
        metrics_fair["selection_rate_privileged"],
        metrics_fair["selection_rate_unprivileged"],
    ]

    x = np.arange(len(groups))
    w = 0.32
    bars1 = ax.bar(x - w / 2, biased_vals, w, label="Biased Model", color=ORANGE, alpha=0.9, zorder=3)
    bars2 = ax.bar(x + w / 2, fair_vals, w, label="Fair Model", color=GREEN, alpha=0.9, zorder=3)

    for bar in [*bars1, *bars2]:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f"{bar.get_height():.2%}", ha="center", va="bottom",
                fontsize=9, color=TEXT)

    ax.set_xticks(x)
    ax.set_xticklabels(groups, color=TEXT, fontsize=10)
    ax.set_yticks(np.arange(0, 0.6, 0.1))
    ax.set_yticklabels([f"{v:.0%}" for v in np.arange(0, 0.6, 0.1)], color="#8b949e", fontsize=8)
    ax.set_ylabel("Selection Rate", color="#8b949e", fontsize=9)
    ax.set_title("Selection Rate Comparison", color=TEXT, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(colors=GRID, length=0)
    ax.spines[:].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.legend(frameon=False, labelcolor=TEXT, fontsize=9)
    fig.patch.set_facecolor(CARD_BG)

    return fig


def make_feature_importance_chart(df_feat: pd.DataFrame):
    df_feat = df_feat.sort_values("Importance", ascending=True)
    fig, ax = plt.subplots(figsize=(7, 3.8), facecolor=CARD_BG)
    ax.set_facecolor(CARD_BG)

    colors = [PURPLE if f.lower() == "gender" else ACCENT for f in df_feat["Feature"]]
    bars = ax.barh(df_feat["Feature"], df_feat["Importance"], color=colors, alpha=0.9, height=0.55, zorder=3)

    for bar in bars:
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.3f}", va="center", fontsize=9, color=TEXT)

    ax.set_xlabel("Importance Score", color="#8b949e", fontsize=9)
    ax.set_title("Feature Importance (SHAP-derived)", color=TEXT, fontsize=12, fontweight="bold", pad=12)
    ax.tick_params(axis="y", colors=TEXT, labelsize=10)
    ax.tick_params(axis="x", colors="#8b949e", labelsize=8, length=0)
    ax.spines[:].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_xlim(0, df_feat["Importance"].max() * 1.2)

    legend_patches = [
        mpatches.Patch(color=ACCENT, label="Merit Feature"),
        mpatches.Patch(color=PURPLE, label="Sensitive Feature (Gender)"),
    ]
    ax.legend(handles=legend_patches, frameon=False, labelcolor=TEXT, fontsize=9)
    fig.patch.set_facecolor(CARD_BG)

    return fig


def make_metrics_comparison_chart(comparison: dict):
    labels = ["Disparate Impact\n(Ideal: 1.0)", "Stat. Parity Diff\n(Ideal: 0.0)", "Equal Opp. Diff\n(Ideal: 0.0)"]
    biased_keys = ["disparate_impact", "statistical_parity_difference", "equal_opportunity_difference"]

    b_vals = [comparison["biased_model"]["fairness_metrics"][k] for k in biased_keys]
    f_vals = [comparison["fair_model"]["fairness_metrics"][k] for k in biased_keys]
    ideals = [1.0, 0.0, 0.0]

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), facecolor=DARK_BG)

    for ax, label, b_val, f_val, ideal in zip(axes, labels, b_vals, f_vals, ideals):
        ax.set_facecolor(CARD_BG)
        cats = ["Biased", "Fair", "Ideal"]
        vals = [b_val, f_val, ideal]
        col = [ORANGE, GREEN, ACCENT]
        bars = ax.bar(cats, vals, color=col, alpha=0.9, width=0.5, zorder=3)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002 * (1 if v >= 0 else -1),
                    f"{v:.4f}", ha="center", va="bottom" if v >= 0 else "top",
                    fontsize=9, color=TEXT)
        ax.set_title(label, color=TEXT, fontsize=9, fontweight="bold", pad=8)
        ax.tick_params(axis="x", colors=TEXT, labelsize=9, length=0)
        ax.tick_params(axis="y", colors="#8b949e", labelsize=7, length=0)
        ax.spines[:].set_visible(False)
        ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)

    fig.patch.set_facecolor(DARK_BG)
    fig.suptitle("Fairness Metrics: Before vs After Mitigation", color=TEXT, fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    return fig


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_index():
    return FileResponse(str(BASE_DIR / "frontend" / "index.html"))


@app.get("/api/summary")
async def get_summary():
    """Return the overview KPIs for the dashboard hero section."""
    try:
        with open(BASE_DIR / "audit_results.json") as f:
            audit = json.load(f)
        with open(BASE_DIR / "comparison_results.json") as f:
            comparison = json.load(f)

        feature_importance = []
        fi_path = BASE_DIR / "feature_importance.csv"
        if fi_path.exists():
            df_fi = pd.read_csv(fi_path)
            feature_importance = df_fi.to_dict(orient="records")

        return {
            "audit": audit,
            "comparison": comparison,
            "feature_importance": feature_importance,
            "dataset_info": {
                "total_candidates": 2000,
                "features": 5,
                "sensitive_feature": "Gender",
                "target": "Shortlisted",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/gauges")
async def get_gauge_charts():
    """Return gauge chart images for key fairness metrics."""
    try:
        with open(BASE_DIR / "audit_results.json") as f:
            audit = json.load(f)
        with open(BASE_DIR / "comparison_results.json") as f:
            comparison = json.load(f)

        fm_fair = comparison["fair_model"]["fairness_metrics"]

        charts = {}

        # Disparate Impact — biased
        fig = make_gauge_fig(audit["disparate_impact"], "Disparate Impact (Biased)", ideal=1.0, low=0.6, high=1.4)
        charts["di_biased"] = fig_to_base64(fig)

        # Disparate Impact — fair
        fig = make_gauge_fig(fm_fair["disparate_impact"], "Disparate Impact (Fair)", ideal=1.0, low=0.6, high=1.4)
        charts["di_fair"] = fig_to_base64(fig)

        # Statistical Parity — biased
        fig = make_gauge_fig(audit["statistical_parity_difference"], "Stat. Parity Diff (Biased)", ideal=0.0, low=-0.2, high=0.2)
        charts["spd_biased"] = fig_to_base64(fig)

        # Statistical Parity — fair
        fig = make_gauge_fig(fm_fair["statistical_parity_difference"], "Stat. Parity Diff (Fair)", ideal=0.0, low=-0.2, high=0.2)
        charts["spd_fair"] = fig_to_base64(fig)

        return charts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/selection-rates")
async def get_selection_rate_chart():
    try:
        with open(BASE_DIR / "comparison_results.json") as f:
            comparison = json.load(f)
        fig = make_selection_rate_chart(
            comparison["biased_model"]["fairness_metrics"],
            comparison["fair_model"]["fairness_metrics"],
        )
        return {"chart": fig_to_base64(fig)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/feature-importance")
async def get_feature_importance_chart():
    try:
        fi_path = BASE_DIR / "feature_importance.csv"
        if not fi_path.exists():
            raise HTTPException(status_code=404, detail="feature_importance.csv not found")
        df_fi = pd.read_csv(fi_path)
        fig = make_feature_importance_chart(df_fi)
        return {"chart": fig_to_base64(fig)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/metrics-comparison")
async def get_metrics_comparison_chart():
    try:
        with open(BASE_DIR / "comparison_results.json") as f:
            comparison = json.load(f)
        fig = make_metrics_comparison_chart(comparison)
        return {"chart": fig_to_base64(fig)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/charts/shap")
async def get_shap_chart():
    """Serve the pre-generated SHAP summary plot."""
    shap_path = BASE_DIR / "shap_summary.png"
    if not shap_path.exists():
        raise HTTPException(status_code=404, detail="shap_summary.png not found. Run bias_auditor.py first.")
    with open(shap_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return {"chart": encoded}


@app.get("/api/charts/distributions")
async def get_distributions_chart():
    """
    Generate gender-split KDE + histogram panels for Age, Experience, and Screening Score.
    Unique to the Dataset section — not a duplicate of the selection rate chart.
    """
    try:
        df = get_cleaned_data()
        male   = df[df["gender"] == 1]
        female = df[df["gender"] == 0]

        features = [
            ("age",              "Age (years)",          20,  60),
            ("experience_years", "Experience (years)",    0,  30),
            ("screening_score",  "Screening Score",       20, 100),
        ]

        fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), facecolor=DARK_BG)
        fig.patch.set_facecolor(DARK_BG)

        for ax, (col, xlabel, xmin, xmax) in zip(axes, features):
            ax.set_facecolor(CARD_BG)

            bins = np.linspace(xmin, xmax, 22)

            # Stacked histogram bars
            ax.hist(male[col],   bins=bins, color=ACCENT,  alpha=0.45, label="Male",   zorder=2)
            ax.hist(female[col], bins=bins, color=PURPLE, alpha=0.45, label="Female", zorder=2)

            # KDE overlay using scipy (much faster)
            for data, color in [(male[col].values, ACCENT), (female[col].values, PURPLE)]:
                if len(data) > 1:
                    kde = gaussian_kde(data)
                    x_range = np.linspace(xmin, xmax, 200)
                    kde_y = kde(x_range)
                    # Scale KDE to histogram height
                    bin_w   = bins[1] - bins[0]
                    scale   = len(data) * bin_w
                    ax.plot(x_range, kde_y * scale, color=color, linewidth=2.2, zorder=4)

            ax.set_xlabel(xlabel, color="#8b949e", fontsize=9)
            ax.set_ylabel("Count", color="#8b949e", fontsize=9)
            ax.tick_params(axis="x", colors="#8b949e", labelsize=8, length=0)
            ax.tick_params(axis="y", colors="#8b949e", labelsize=8, length=0)
            ax.spines[:].set_visible(False)
            ax.grid(axis="y", color=GRID, linewidth=0.6, zorder=0)
            ax.set_xlim(xmin, xmax)

        # Shared title and legend
        patches = [
            mpatches.Patch(color=ACCENT,  label="Male (Privileged)"),
            mpatches.Patch(color=PURPLE, label="Female (Unprivileged)"),
        ]
        fig.legend(handles=patches, loc="upper right", frameon=False,
                   labelcolor=TEXT, fontsize=9, bbox_to_anchor=(0.99, 1.02))
        fig.suptitle("Feature Distributions by Gender", color=TEXT,
                     fontsize=13, fontweight="bold", y=1.04)
        plt.tight_layout()

        return {"chart": fig_to_base64(fig)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/predict")
async def predict_candidate(data: dict):
    """
    Run both biased and fair models on a single candidate.
    Expected body: { gender, age, education_level, experience_years, screening_score }
    """
    try:
        feature_cols = ["gender", "age", "education_level", "experience_years", "screening_score"]
        row = pd.DataFrame([[data[c] for c in feature_cols]], columns=feature_cols)

        biased_model, fair_model = load_models()

        # Load calibrated thresholds from Member 3
        with open(BASE_DIR / "comparison_results.json") as f:
            comp = json.load(f)
            thresholds = comp.get("fair_model", {}).get("thresholds", {"0": 0.5, "1": 0.5})

        gender_str = str(int(data["gender"]))
        fair_thresh = float(thresholds.get(gender_str, 0.5))

        biased_pred = int(biased_model.predict(row)[0])
        biased_prob = float(biased_model.predict_proba(row)[0][1])

        fair_prob = float(fair_model.predict_proba(row)[0][1])
        fair_pred = 1 if fair_prob >= fair_thresh else 0

        return {
            "biased_model": {"prediction": biased_pred, "probability": round(biased_prob, 4)},
            "fair_model": {"prediction": fair_pred, "probability": round(fair_prob, 4)},
            "verdict": "Models agree" if biased_pred == fair_pred else "Models disagree — bias detected!",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dataset/stats")
async def get_dataset_stats():
    """Return aggregated dataset statistics for the data explorer section."""
    try:
        df = get_cleaned_data()

        gender_dist = df["gender"].value_counts().to_dict()
        edu_dist = df["education_level"].value_counts().to_dict()
        shortlisted_by_gender = df.groupby("gender")["shortlisted"].mean().to_dict()

        age_hist, age_bins = np.histogram(df["age"], bins=10)
        exp_hist, exp_bins = np.histogram(df["experience_years"], bins=10)
        score_hist, score_bins = np.histogram(df["screening_score"], bins=10)

        return {
            "total": len(df),
            "gender_distribution": {
                "Male (1)": int(gender_dist.get(1, 0)),
                "Female (0)": int(gender_dist.get(0, 0)),
            },
            "education_distribution": {str(k): int(v) for k, v in edu_dist.items()},
            "shortlisted_rate_by_gender": {
                "Male": round(float(shortlisted_by_gender.get(1, 0)), 4),
                "Female": round(float(shortlisted_by_gender.get(0, 0)), 4),
            },
            "age": {
                "mean": round(float(df["age"].mean()), 2),
                "min": int(df["age"].min()),
                "max": int(df["age"].max()),
                "hist": age_hist.tolist(),
                "bins": age_bins.tolist(),
            },
            "experience_years": {
                "mean": round(float(df["experience_years"].mean()), 2),
                "min": int(df["experience_years"].min()),
                "max": int(df["experience_years"].max()),
                "hist": exp_hist.tolist(),
                "bins": exp_bins.tolist(),
            },
            "screening_score": {
                "mean": round(float(df["screening_score"].mean()), 2),
                "min": round(float(df["screening_score"].min()), 2),
                "max": round(float(df["screening_score"].max()), 2),
                "hist": score_hist.tolist(),
                "bins": score_bins.tolist(),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config/hf_token")
async def get_hf_token():
    """Returns the HF_TOKEN for client-side gated model access (Edge AI)."""
    return {"token": HF_TOKEN or ""}

@app.post("/api/ai/insight")
async def get_gemini_insight(data: dict):
    if not client:
        return {"error": "Gemini API Key not configured"}
    
    try:
        # Using state-of-the-art Gemini 2.0 Flash
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
            Analyze these recruitment fairness metrics from FairAI Studio:
            - Mitigated Disparate Impact: {data.get('di')}
            - Fairness Improvement: {data.get('improvement')}%
            - Initial Biased DI: {data.get('initial_di')}
            
            Provide one punchy, professional, and actionable recruitment recommendation. 
            Focus on how the mitigation helps the company's hiring ethics.
            Limit to 1 to 2 sentences max. Keep it sophisticated.
            """
        )
        return {"insight": response.text.strip() if response.text else "Insight generation complete."}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
