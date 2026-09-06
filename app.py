"""
EcoTrack AI – AI-Powered Campus Waste & Sustainability Assistant
1M1B AI for Sustainability Virtual Internship
IBM SkillsBuild x AICTE | SDG 12 – Responsible Consumption and Production

Run:  streamlit run app.py
"""

import os
import base64
import logging

import streamlit as st
import pandas as pd
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# ── Credentials ───────────────────────────────────────────────────────────────

def _secret(key, default=""):
    try:
        v = st.secrets.get(key, "")
        if v:
            return str(v)
    except Exception:
        pass
    return os.getenv(key, default)

API_KEY    = _secret("WATSONX_API_KEY")
PROJECT_ID = _secret("WATSONX_PROJECT_ID")
REGION     = _secret("WATSONX_REGION", "us-south")
VISION_ID  = _secret("WATSONX_VISION_DEPLOYMENT_ID")
BASE_URL   = f"https://{REGION}.ml.cloud.ibm.com"
TEXT_MODEL = "ibm/granite-3-3-8b-instruct"

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="EcoTrack AI", page_icon="♻️", layout="wide")

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("♻️ EcoTrack AI")
    st.caption("AI-Powered Campus Waste & Sustainability Assistant")

st.title("♻️ EcoTrack AI")
st.caption("Campus Waste & Sustainability Assistant | SDG 12")

tab1, tab2 = st.tabs(["📷 Waste Analyzer", "🤖 AI Assistant"])


# ═══════════════════════════════════════════════════════════════════════════════
# WASTE CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════

WASTE_INFO = {
    "plastic": {
        "label": "Plastic",
        "colour": "#2563EB",
        "tip": "Rinse and place in the blue dry-recycling bin. Remove caps and non-plastic parts.",
    },
    "paper": {
        "label": "Paper / Cardboard",
        "colour": "#D97706",
        "tip": "Flatten boxes. Soiled or greasy paper goes in general waste, not recycling.",
    },
    "food": {
        "label": "Food / Organic",
        "colour": "#16A34A",
        "tip": "Place in the green/organic bin or compost area. Drain excess liquid first.",
    },
    "e-waste": {
        "label": "E-Waste / Electronic",
        "colour": "#DC2626",
        "tip": "Never put in regular bins. Take to campus e-waste collection or an authorised recycler.",
    },
    "general": {
        "label": "General Waste",
        "colour": "#6B7280",
        "tip": "Use the general waste bin. Consider if the item can be reused or repaired first.",
    },
}

DEMO_EXAMPLES = [
    {"desc": "Plastic water bottle", "category": "plastic"},
    {"desc": "Crumpled newspaper",   "category": "paper"},
    {"desc": "Banana peel",          "category": "food"},
    {"desc": "Old mobile phone",     "category": "e-waste"},
    {"desc": "Torn rubber sole",     "category": "general"},
]

VISION_PROMPT = """You are a campus waste management assistant.
Look at the image and identify the type of waste.
Reply in this exact format only:
CATEGORY: <plastic, paper, food, e-waste, or general>
CONFIDENCE: <high, medium, or low>
REASONING: <one sentence>
DISPOSAL_TIP: <one practical sentence>"""


def parse_vision(raw):
    out = {"category": "general", "confidence": "low", "reasoning": raw, "tip": ""}
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("CATEGORY:"):
            cat = line.split(":", 1)[1].strip().lower()
            if cat in WASTE_INFO:
                out["category"] = cat
        elif line.startswith("CONFIDENCE:"):
            c = line.split(":", 1)[1].strip().lower()
            if c in ("high", "medium", "low"):
                out["confidence"] = c
        elif line.startswith("REASONING:"):
            out["reasoning"] = line.split(":", 1)[1].strip()
        elif line.startswith("DISPOSAL_TIP:"):
            out["tip"] = line.split(":", 1)[1].strip()
    return out


def show_category(cat_key, tip_override=""):
    info = WASTE_INFO.get(cat_key, WASTE_INFO["general"])
    st.markdown(
        f"<span style='background:{info['colour']};color:white;"
        f"padding:6px 18px;border-radius:12px;font-weight:bold;font-size:1.1em'>"
        f"🗑️ {info['label']}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.info(tip_override if tip_override else info["tip"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – WASTE IMAGE ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

with tab1:
    st.subheader("📷 Waste Image Analyzer")
    st.markdown("Upload a photo of any waste item to find out its category and how to dispose of it.")

    uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded:
        col_img, col_result = st.columns([1, 2])

        with col_img:
            st.image(Image.open(uploaded), caption="Uploaded image", use_container_width=True)

        with col_result:
            if API_KEY and VISION_ID:
                # ── Real AI Mode ──────────────────────────────────────────────
                with st.spinner("Analysing with IBM Granite Vision..."):
                    try:
                        import requests

                        tok = requests.post(
                            "https://iam.cloud.ibm.com/identity/token",
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            data={
                                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                                "apikey": API_KEY,
                            },
                            timeout=15,
                        )
                        tok.raise_for_status()
                        token = tok.json()["access_token"]

                        uploaded.seek(0)
                        img_b64 = base64.b64encode(uploaded.read()).decode()
                        mime = "image/png" if uploaded.name.lower().endswith(".png") else "image/jpeg"

                        resp = requests.post(
                            f"{BASE_URL}/ml/v1/deployments/{VISION_ID}/text/generation?version=2024-05-01",
                            headers={
                                "Authorization": f"Bearer {token}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "input": [
                                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                                    {"type": "text", "text": VISION_PROMPT},
                                ],
                                "parameters": {"max_new_tokens": 200, "temperature": 0.1},
                            },
                            timeout=30,
                        )
                        resp.raise_for_status()
                        raw = resp.json().get("results", [{}])[0].get("generated_text", "").strip()
                        p = parse_vision(raw)

                        conf_icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(p["confidence"], "🔴")
                        st.markdown(f"**Confidence:** {conf_icon} {p['confidence'].capitalize()}")
                        if p["reasoning"]:
                            st.markdown(f"*{p['reasoning']}*")
                        show_category(p["category"], p["tip"])
                        st.caption(
                            "🤖 Result generated by IBM Granite Vision via watsonx.ai. "
                            "AI can make mistakes — verify with campus facilities if unsure."
                        )

                    except Exception as e:
                        logging.error("Vision error: %s", e)
                        st.error(f"Could not analyse the image: {e}")

            else:
                # ── Demo Mode ─────────────────────────────────────────────────
                st.markdown("**Select a demo example below:**")
                idx = st.selectbox(
                    "Example",
                    range(len(DEMO_EXAMPLES)),
                    format_func=lambda i: DEMO_EXAMPLES[i]["desc"],
                )
                st.error(
                    "⚠️ **Demo Mode** — This result is a fixed example. "
                    "It is NOT based on your uploaded image and NOT real AI inference."
                )
                show_category(DEMO_EXAMPLES[idx]["category"])
                st.caption("Demo result — not real AI. Configure Vision AI credentials to enable real analysis.")

    else:
        st.markdown("👆 Upload an image to get started.")

    st.divider()
    st.markdown("#### Waste Category Guide")
    cols = st.columns(len(WASTE_INFO))
    for col, (key, info) in zip(cols, WASTE_INFO.items()):
        with col:
            st.markdown(
                f"<div style='background:{info['colour']};color:white;padding:8px;border-radius:8px;"
                f"text-align:center;font-weight:bold'>{info['label']}</div>",
                unsafe_allow_html=True,
            )
            st.caption(info["tip"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – AI ASSISTANT + IMPACT CALCULATOR + RESPONSIBLE AI
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (
    "You are EcoTrack AI, a campus sustainability assistant helping students "
    "understand waste management, recycling, and SDG 12 "
    "(Responsible Consumption and Production). "
    "Give concise, practical, encouraging answers. "
    "Do not fabricate statistics. If unsure, say so."
)

STARTERS = [
    "How do I dispose of a plastic bottle on campus?",
    "What is SDG 12?",
    "How can our cafeteria reduce food waste?",
    "Why is e-waste dangerous in regular bins?",
]

IMPACT_FACTORS = {
    "plastic": {"co2": 1.5, "water": 0.0,  "source": "WRAP UK (2022)"},
    "paper":   {"co2": 0.9, "water": 13.0, "source": "US EPA WARM v16 (2021)"},
    "food":    {"co2": 0.5, "water": 0.0,  "source": "IPCC AR6 WG3 (2022)"},
    "e-waste": {"co2": 0.0, "water": 0.0,  "source": "N/A – value is in hazardous waste diversion"},
    "general": {"co2": 0.0, "water": 0.0,  "source": "N/A – insufficient data for mixed waste"},
}

with tab2:
    st.subheader("🤖 AI Sustainability Assistant")

    if not (API_KEY and PROJECT_ID):
        # ── No credentials – show a friendly placeholder ──────────────────────
        st.markdown(
            "Ask any question about campus waste, recycling, or sustainability.  \n"
            "_AI responses require IBM watsonx.ai credentials. "
            "Add them to your `.env` file or Streamlit secrets to activate._"
        )
        st.divider()
        st.markdown("**Example questions you could ask:**")
        for q in STARTERS:
            st.markdown(f"- {q}")

    else:
        # ── Live AI chat ──────────────────────────────────────────────────────
        st.markdown("Ask anything about campus waste, recycling, or sustainability.")

        st.markdown("**💡 Try one of these:**")
        btn_cols = st.columns(len(STARTERS))
        for i, q in enumerate(STARTERS):
            with btn_cols[i]:
                if st.button(q, key=f"s{i}", use_container_width=True):
                    st.session_state["pending"] = q

        st.divider()

        if "chat" not in st.session_state:
            st.session_state["chat"] = [
                {
                    "role": "assistant",
                    "content": (
                        "Hi! I'm EcoTrack AI. "
                        "Ask me anything about waste management or sustainability."
                    ),
                }
            ]

        for msg in st.session_state["chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        pending  = st.session_state.pop("pending", None)
        user_in  = st.chat_input("Ask a sustainability question...")
        user_msg = pending or user_in

        if user_msg:
            st.session_state["chat"].append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        from ibm_watsonx_ai import Credentials
                        from ibm_watsonx_ai.foundation_models import ModelInference

                        model = ModelInference(
                            model_id=TEXT_MODEL,
                            project_id=PROJECT_ID,
                            credentials=Credentials(url=BASE_URL, api_key=API_KEY),
                            params={"max_new_tokens": 512, "temperature": 0.3},
                        )
                        reply = model.generate_text(
                            prompt=f"[SYSTEM]\n{SYSTEM_PROMPT}\n\n[USER]\n{user_msg}"
                        )
                        st.markdown(reply)
                        st.caption("🤖 IBM Granite (granite-3-3-8b-instruct) via watsonx.ai")
                        st.session_state["chat"].append({"role": "assistant", "content": reply})

                    except Exception as e:
                        err = f"Could not get a response right now: {e}"
                        st.error(err)
                        st.session_state["chat"].append({"role": "assistant", "content": err})

        if st.button("🗑️ Clear chat"):
            st.session_state.pop("chat", None)
            st.rerun()

    # ── Impact Calculator ─────────────────────────────────────────────────────
    st.divider()
    st.subheader("🌱 Sustainability Impact Calculator")
    st.caption("Estimate the environmental benefit of reducing campus waste.")
    st.info(
        "⚠️ All results are **rough estimates** based on published studies "
        "(WRAP UK, US EPA WARM, IPCC AR6). Not for certified reporting."
    )

    ic1, ic2 = st.columns(2)
    with ic1:
        wtype = st.selectbox(
            "Waste type",
            list(IMPACT_FACTORS.keys()),
            format_func=lambda k: k.capitalize(),
            key="ic_wtype",
        )
        qty = st.number_input(
            "Weekly waste quantity (kg)",
            min_value=0.0, max_value=10000.0, value=10.0, step=0.5,
            key="ic_qty",
        )
    with ic2:
        pct = st.slider("Target reduction (%)", 0, 100, 20, step=5, key="ic_pct")
        weeks = st.number_input(
            "Over how many weeks?",
            min_value=1, max_value=52, value=4, step=1,
            key="ic_weeks",
        )

    if qty > 0:
        f       = IMPACT_FACTORS[wtype]
        avoided = round(qty * weeks * pct / 100, 2)
        co2     = round(avoided * f["co2"], 2)
        water   = round(avoided * f["water"], 1)
        trees   = round(co2 / 21.0, 2) if co2 > 0 else 0

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Waste Avoided",        f"{avoided} kg")
        r2.metric("CO₂e Saved (est.)",    f"{co2} kg"    if f["co2"] > 0   else "N/A")
        r3.metric("Water Saved (est.)",   f"{water} L"   if f["water"] > 0 else "N/A")
        r4.metric("Tree-Years Equiv.",    str(trees)      if trees > 0      else "N/A")

        if f["co2"] == 0:
            st.warning(f"No CO₂ estimate for **{wtype}**. {f['source']}")
        else:
            st.caption(f"Source: {f['source']}")

        st.warning(
            "These are estimates only. Actual impact varies by local "
            "recycling infrastructure and waste quality."
        )
    else:
        st.markdown("Enter a waste quantity above to see results.")

    # ── Responsible AI ────────────────────────────────────────────────────────
    st.divider()
    with st.expander("⚖️ Responsible AI"):
        st.markdown("""
**Fairness** — Plain language used throughout. No assumptions about user background. English-only limitation noted.

**Transparency** — Every AI response shows the model name. Demo Mode is always clearly labelled as non-AI.

**Ethics** — The AI is instructed not to invent statistics. Impact factors are estimates with cited sources. No data is stored or shared.

**Privacy** — No login required. Uploaded images are processed in memory only and never saved to disk. Session data is cleared when you close the browser.

**Limitations** — AI can be wrong. Waste classification may fail on unusual items. Always check with campus facilities staff before acting on suggestions.

---
*1M1B AI for Sustainability Virtual Internship | IBM SkillsBuild × AICTE | SDG 12*
        """)
