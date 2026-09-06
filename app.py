"""
EcoTrack AI – AI-Powered Campus Waste & Sustainability Assistant
================================================================
1M1B AI for Sustainability Virtual Internship
IBM SkillsBuild × AICTE  |  SDG 12 – Responsible Consumption and Production

Run this app:
    streamlit run app.py

Three tabs:
    Tab 1 – Waste Image Analyzer  (Demo Mode if no vision AI configured)
    Tab 2 – Waste Analytics       (upload CSV or use sample data)
    Tab 3 – AI Assistant          (IBM Granite chat + impact calculator)
"""

import os
import base64
import logging

import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from dotenv import load_dotenv

# ── Load credentials ──────────────────────────────────────────────────────────
# Works locally (.env file) and on Streamlit Cloud (Secrets UI).
load_dotenv()

def _secret(key, default=""):
    """Read from Streamlit secrets first, then .env / environment."""
    try:
        v = st.secrets.get(key, "")
        if v:
            return str(v)
    except Exception:
        pass
    return os.getenv(key, default)

API_KEY     = _secret("WATSONX_API_KEY")
PROJECT_ID  = _secret("WATSONX_PROJECT_ID")
REGION      = _secret("WATSONX_REGION", "us-south")
VISION_ID   = _secret("WATSONX_VISION_DEPLOYMENT_ID")
BASE_URL    = f"https://{REGION}.ml.cloud.ibm.com"
TEXT_MODEL  = "ibm/granite-3-3-8b-instruct"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EcoTrack AI",
    page_icon="♻️",
    layout="wide",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("♻️ EcoTrack AI")
    st.caption("AI-Powered Campus Waste & Sustainability Assistant")
    st.divider()
    st.markdown(
        "**1M1B AI for Sustainability Internship**  \n"
        "IBM SkillsBuild × AICTE  \n"
        "**SDG 12** – Responsible Consumption & Production"
    )
    st.divider()
    st.markdown("**AI Status**")
    if API_KEY and PROJECT_ID:
        st.success("✅ AI Assistant – ready")
    else:
        st.warning("⚠️ AI Assistant – add credentials to `.env`")
    if API_KEY and VISION_ID:
        st.success("✅ Vision AI – ready")
    else:
        st.info("ℹ️ Vision AI – Demo Mode active")
    st.divider()
    st.caption("Built with IBM Granite · Streamlit · Pandas · Plotly")

st.title("♻️ EcoTrack AI — Campus Sustainability Assistant")
st.caption("SDG 12 – Responsible Consumption and Production")

tab1, tab2, tab3 = st.tabs(["📷 Waste Analyzer", "📊 Analytics", "🤖 AI Assistant"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – WASTE IMAGE ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════

WASTE_INFO = {
    "plastic":  {"label": "Plastic",           "colour": "#2563EB", "tip": "Rinse and place in the blue dry-recycling bin. Remove non-plastic parts like metal caps."},
    "paper":    {"label": "Paper / Cardboard",  "colour": "#D97706", "tip": "Flatten boxes. Soiled or greasy paper goes in general waste, not recycling."},
    "food":     {"label": "Food / Organic",     "colour": "#16A34A", "tip": "Place in the green/organic bin or compost area. Drain excess liquid first."},
    "e-waste":  {"label": "E-Waste",            "colour": "#DC2626", "tip": "Do NOT use regular bins. Drop off at campus e-waste point or authorised recycler."},
    "general":  {"label": "General Waste",      "colour": "#6B7280", "tip": "Use the general waste bin. Consider if the item could be reused or repaired first."},
}

DEMO_EXAMPLES = [
    {"desc": "Plastic water bottle",  "category": "plastic"},
    {"desc": "Crumpled newspaper",    "category": "paper"},
    {"desc": "Banana peel",           "category": "food"},
    {"desc": "Old mobile phone",      "category": "e-waste"},
    {"desc": "Torn rubber sole",      "category": "general"},
]

VISION_PROMPT = """You are a campus waste assistant. Look at the image and identify the waste type.
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
        f"<span style='background:{info['colour']};color:white;padding:5px 16px;"
        f"border-radius:12px;font-weight:bold;font-size:1.1em'>🗑️ {info['label']}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.info(tip_override if tip_override else info["tip"])

with tab1:
    st.subheader("📷 Waste Image Analyzer")
    st.markdown("Upload a photo of any waste item to get its category and disposal guidance.")

    if API_KEY and VISION_ID:
        st.success("✅ **AI Mode** – image will be sent to IBM Granite Vision for analysis.")
    else:
        st.warning(
            "⚠️ **Demo Mode** – Vision AI is not configured.  \n"
            "The examples below are **pre-written demonstrations, not real AI**.  \n"
            "_To enable AI Mode, set `WATSONX_VISION_DEPLOYMENT_ID` in your credentials._"
        )

    uploaded = st.file_uploader("Choose a waste image", type=["jpg", "jpeg", "png"])

    if uploaded:
        col_a, col_b = st.columns([1, 2])
        with col_a:
            st.image(Image.open(uploaded), caption="Your uploaded image", use_container_width=True)
        with col_b:
            if API_KEY and VISION_ID:
                # ── AI Mode ──
                with st.spinner("Analysing with IBM Granite Vision..."):
                    try:
                        import requests
                        # Get IAM token
                        tok_resp = requests.post(
                            "https://iam.cloud.ibm.com/identity/token",
                            headers={"Content-Type": "application/x-www-form-urlencoded"},
                            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": API_KEY},
                            timeout=15,
                        )
                        tok_resp.raise_for_status()
                        token = tok_resp.json()["access_token"]

                        uploaded.seek(0)
                        img_b64 = base64.b64encode(uploaded.read()).decode()
                        mime = "image/png" if uploaded.name.lower().endswith(".png") else "image/jpeg"

                        resp = requests.post(
                            f"{BASE_URL}/ml/v1/deployments/{VISION_ID}/text/generation?version=2024-05-01",
                            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
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
                        parsed = parse_vision(raw)

                        conf_icon = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(parsed["confidence"], "🔴")
                        st.markdown(f"**Confidence:** {conf_icon} {parsed['confidence'].capitalize()}")
                        if parsed["reasoning"]:
                            st.markdown(f"*{parsed['reasoning']}*")
                        show_category(parsed["category"], parsed["tip"])
                        st.caption("🤖 Generated by IBM Granite Vision via watsonx.ai. AI can be wrong — verify with campus facilities.")

                    except Exception as e:
                        logging.error("Vision API error: %s", e)
                        st.error(f"AI classification failed: {e}")
            else:
                # ── Demo Mode ──
                st.markdown("#### Demo Mode – Select an example")
                st.markdown("Choose a pre-written example to see how results look:")
                idx = st.selectbox(
                    "Demo example:",
                    range(len(DEMO_EXAMPLES)),
                    format_func=lambda i: DEMO_EXAMPLES[i]["desc"],
                )
                st.error(
                    "⚠️ **This is a Demo Mode result.**  \n"
                    "It is NOT based on your image. It is a fixed example only."
                )
                show_category(DEMO_EXAMPLES[idx]["category"])
                st.caption("Demo result — not real AI inference.")
    else:
        st.markdown("👆 Upload an image to get started.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – WASTE ANALYTICS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

SAMPLE_CSV = "data/sample_campus_waste.csv"
REQUIRED_COLS = {"date", "location", "waste_type", "weight_kg", "disposed_correctly"}

with tab2:
    st.subheader("📊 Waste Analytics Dashboard")
    st.markdown("Upload your campus waste CSV or use the bundled sample data.")

    col_up, col_btn = st.columns([3, 1])
    with col_up:
        csv_file = st.file_uploader("Upload campus waste CSV", type=["csv"])
    with col_btn:
        st.markdown(" ")
        if st.button("📂 Load sample data"):
            st.session_state["use_sample"] = True

    source = None
    if csv_file:
        source = csv_file
        st.session_state.pop("use_sample", None)
    elif st.session_state.get("use_sample"):
        source = SAMPLE_CSV

    if source is None:
        st.markdown(
            "👆 Upload a CSV or click **Load sample data**.  \n"
            "**Required columns:** `date`, `location`, `waste_type`, `weight_kg`, `disposed_correctly`"
        )
    else:
        try:
            df = pd.read_csv(source)
            df.columns = df.columns.str.lower()
            missing = REQUIRED_COLS - set(df.columns)
            if missing:
                st.error(f"CSV is missing columns: {', '.join(sorted(missing))}")
                st.stop()

            df["date"] = pd.to_datetime(df["date"], format="mixed", errors="coerce")
            df = df.dropna(subset=["date"])
            df["waste_type"] = df["waste_type"].str.lower().str.strip()
            df["disposed_correctly"] = df["disposed_correctly"].apply(
                lambda v: str(v).strip().lower() in ("true", "1", "yes")
            )

            st.caption(f"Loaded {len(df):,} records from {df['date'].min().date()} to {df['date'].max().date()}")

            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Total Waste", f"{df['weight_kg'].sum():.1f} kg")
            k2.metric("Records", f"{len(df):,}")
            k3.metric("Correctly Disposed", f"{df['disposed_correctly'].mean()*100:.1f}%")
            k4.metric("Top Category", df.groupby("waste_type")["weight_kg"].sum().idxmax().capitalize())

            st.divider()

            c1, c2 = st.columns(2)
            with c1:
                by_type = df.groupby("waste_type")["weight_kg"].sum().reset_index().sort_values("weight_kg", ascending=False)
                st.plotly_chart(
                    px.bar(by_type, x="waste_type", y="weight_kg", title="Waste by Category",
                           color="waste_type", text_auto=".1f", labels={"waste_type": "", "weight_kg": "kg"}),
                    use_container_width=True,
                )
            with c2:
                disp = df["disposed_correctly"].map({True: "Correct", False: "Incorrect"}).value_counts().reset_index()
                disp.columns = ["Disposal", "Count"]
                st.plotly_chart(
                    px.pie(disp, names="Disposal", values="Count", title="Disposal Behaviour",
                           color="Disposal", color_discrete_map={"Correct": "#16A34A", "Incorrect": "#DC2626"}),
                    use_container_width=True,
                )

            c3, c4 = st.columns(2)
            with c3:
                df["week"] = df["date"].dt.to_period("W").apply(lambda r: r.start_time)
                weekly = df.groupby(["week", "waste_type"])["weight_kg"].sum().reset_index()
                st.plotly_chart(
                    px.line(weekly, x="week", y="weight_kg", color="waste_type",
                            title="Weekly Trend", markers=True, labels={"week": "", "weight_kg": "kg"}),
                    use_container_width=True,
                )
            with c4:
                by_loc = df.groupby("location")["weight_kg"].sum().reset_index().sort_values("weight_kg")
                st.plotly_chart(
                    px.bar(by_loc, x="weight_kg", y="location", orientation="h",
                           title="Waste by Location", text_auto=".1f", labels={"location": "", "weight_kg": "kg"}),
                    use_container_width=True,
                )

        except Exception as e:
            st.error(f"Could not load the CSV file: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – AI ASSISTANT + IMPACT CALCULATOR + RESPONSIBLE AI
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = (
    "You are EcoTrack AI, a campus sustainability assistant. "
    "Help students understand waste management, recycling, and SDG 12. "
    "Give concise, practical, encouraging answers. "
    "Do not fabricate statistics. Say so if you are unsure."
)

IMPACT_FACTORS = {
    "plastic": {"co2": 1.5, "water": 0.0,  "source": "WRAP UK (2022)"},
    "paper":   {"co2": 0.9, "water": 13.0, "source": "US EPA WARM v16 (2021)"},
    "food":    {"co2": 0.5, "water": 0.0,  "source": "IPCC AR6 WG3 (2022)"},
    "e-waste": {"co2": 0.0, "water": 0.0,  "source": "No CO₂ estimate — value is in hazardous waste diversion"},
    "general": {"co2": 0.0, "water": 0.0,  "source": "No reliable estimate for mixed waste"},
}

STARTERS = [
    "How do I dispose of a plastic bottle?",
    "What is SDG 12?",
    "How can we reduce food waste on campus?",
    "Why is e-waste dangerous in regular bins?",
]

with tab3:
    st.subheader("🤖 AI Sustainability Assistant")

    # ── AI Chat ──────────────────────────────────────────────────────────────
    if not (API_KEY and PROJECT_ID):
        st.warning(
            "**AI Assistant is not configured.**  \n"
            "Add `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` to your `.env` file or Streamlit secrets.  \n"
            "See `README.md` for instructions."
        )
    else:
        st.markdown("Ask anything about campus waste, recycling, or sustainability:")

        st.markdown("**💡 Try:**")
        cols = st.columns(len(STARTERS))
        for i, q in enumerate(STARTERS):
            with cols[i]:
                if st.button(q, key=f"q{i}", use_container_width=True):
                    st.session_state["pending"] = q

        st.divider()

        if "chat" not in st.session_state:
            st.session_state["chat"] = [
                {"role": "assistant", "content":
                 "Hi! I'm EcoTrack AI. Ask me anything about waste management or sustainability."}
            ]

        for msg in st.session_state["chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        pending = st.session_state.pop("pending", None)
        user_in = st.chat_input("Ask a sustainability question...")
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
                        full_prompt = f"[SYSTEM]\n{SYSTEM_PROMPT}\n\n[USER]\n{user_msg}"
                        reply = model.generate_text(prompt=full_prompt)
                        st.markdown(reply)
                        st.caption("🤖 IBM Granite (granite-3-3-8b-instruct) via watsonx.ai")
                        st.session_state["chat"].append({"role": "assistant", "content": reply})
                    except Exception as e:
                        err = f"Sorry, could not get a response: {e}"
                        st.error(err)
                        st.session_state["chat"].append({"role": "assistant", "content": err})

        if st.button("🗑️ Clear chat"):
            st.session_state.pop("chat", None)
            st.rerun()

    st.divider()

    # ── Impact Calculator ────────────────────────────────────────────────────
    st.subheader("🌱 Sustainability Impact Calculator")
    st.info("⚠️ All results are **rough estimates** based on published studies. Not for certified reporting.")

    col_l, col_r = st.columns(2)
    with col_l:
        wtype = st.selectbox("Waste type", list(IMPACT_FACTORS.keys()),
                             format_func=lambda k: k.capitalize())
        qty   = st.number_input("Weekly waste (kg)", min_value=0.0, max_value=10000.0, value=10.0, step=0.5)
    with col_r:
        pct   = st.slider("Target reduction (%)", 0, 100, 20, step=5)
        weeks = st.number_input("Over how many weeks?", min_value=1, max_value=52, value=4, step=1)

    if qty > 0:
        f = IMPACT_FACTORS[wtype]
        avoided = round(qty * weeks * pct / 100, 2)
        co2     = round(avoided * f["co2"], 2)
        water   = round(avoided * f["water"], 1)
        trees   = round(co2 / 21.0, 2) if co2 > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Waste Avoided", f"{avoided} kg")
        m2.metric("CO₂e Saved (est.)", f"{co2} kg" if f["co2"] > 0 else "N/A")
        m3.metric("Water Saved (est.)", f"{water} L" if f["water"] > 0 else "N/A")
        m4.metric("Tree-Years Equivalent", str(trees) if trees > 0 else "N/A")

        if f["co2"] == 0:
            st.warning(f"No CO₂ estimate available for **{wtype}**. Reason: {f['source']}")
        else:
            st.caption(f"Source: {f['source']}")
        st.warning("These numbers are estimates only. Actual impact depends on local recycling infrastructure.")
    else:
        st.markdown("Enter a quantity above to see the estimate.")

    st.divider()

    # ── Responsible AI ───────────────────────────────────────────────────────
    with st.expander("⚖️ Responsible AI Principles"):
        st.markdown("""
**Fairness** — Plain language, no assumptions about user background. English-only limitation acknowledged.

**Transparency** — Every AI response is labelled with the model name. Demo Mode is always clearly marked. Impact factors show their sources.

**Ethics** — AI is instructed not to fabricate statistics. Results are presented as estimates, not measurements. No personal data is stored.

**Privacy** — No login required. Uploaded images are processed in memory only and never saved to disk. CSV data exists only for the current session.

**Limitations** — AI can produce incorrect or outdated information. Waste classification can be wrong for unusual items. Always verify with campus facilities staff before acting on AI suggestions.

*Project: 1M1B AI for Sustainability | IBM SkillsBuild × AICTE | SDG 12*
        """)
