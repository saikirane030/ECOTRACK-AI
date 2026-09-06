# pages/responsible_ai.py
#
# Tab 5: Responsible AI
#
# This is a static information page – no AI calls, no data processing.
# It explains the ethical considerations behind this project.
#
# Why this matters:
#   Responsible AI is a mandatory consideration for any AI project, and
#   especially for a project submitted for an internship or academic assessment.
#   This page shows that the student understands the limitations and
#   ethical implications of the AI systems they are using.

import streamlit as st


def render() -> None:
    """Main render function called by app.py."""

    st.subheader("⚖️ Responsible AI")
    st.markdown(
        "EcoTrack AI is built with the following responsible AI principles in mind. "
        "These are not afterthoughts — they shaped every design decision in this project."
    )

    st.divider()

    # -----------------------------------------------------------------------
    # FAIRNESS
    # -----------------------------------------------------------------------

    st.markdown("### 🟢 Fairness")
    st.markdown(
        """
EcoTrack AI aims to be useful to all campus community members regardless of their
background, prior sustainability knowledge, or technical ability.

**What was done:**
- The language used in tips and the AI assistant prompt is kept plain and jargon-free.
- The system prompt instructs the AI to give practical advice without assuming the
  user's background or resources.
- The app works with any campus CSV format that has the required columns — not just
  data from a specific institution.

**Known limitations:**
- The app is currently English-only. Students whose first language is not English
  may find the AI responses harder to follow.
- The Granite Vision model has been tested on common waste items. Its accuracy on
  specific South Asian or regional packaging types is unknown and has not been validated.
- The impact calculation factors are based on Western studies (WRAP UK, US EPA).
  Actual values in India may differ due to different recycling infrastructure.
"""
    )

    # -----------------------------------------------------------------------
    # TRANSPARENCY
    # -----------------------------------------------------------------------

    st.markdown("### 🔵 Transparency")
    st.markdown(
        """
Users should always know when they are seeing AI-generated content and
what model produced it.

**What was done:**
- Every AI-generated response is labelled with the model name
  (`ibm/granite-3-3-8b-instruct`) and the platform (IBM watsonx.ai).
- Demo Mode is visually distinct from AI Mode and never pretends to be real inference.
- The sidebar shows live credential status so users know which features are active.
- All impact calculation factors include their published source and can be
  inspected in `utils/impact_formulas.py`.
- The project code is designed to be readable by a beginner — the logic is
  not hidden inside complex abstractions.

**Model information:**
- Text generation: `ibm/granite-3-3-8b-instruct` — IBM Granite 3.3 family,
  multitenant deployment on IBM watsonx.ai.
- Vision classification: `ibm/granite-vision-3-2-2b` — IBM Granite Vision,
  requires a dedicated deploy-on-demand endpoint.
- Source: [IBM watsonx.ai Foundation Models documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html)
"""
    )

    # -----------------------------------------------------------------------
    # ETHICS
    # -----------------------------------------------------------------------

    st.markdown("### 🟡 Ethics")
    st.markdown(
        """
The app is designed to inform and encourage — not to alarm, mislead, or manipulate.

**What was done:**
- The AI assistant system prompt explicitly prohibits fabricating statistics.
  If the model is uncertain, it is instructed to say so.
- Impact calculations are presented as rough estimates with source citations,
  not as precise measurements.
- The Granite model is an IBM-developed foundation model subject to IBM's
  AI ethics principles and responsible use guidelines.
- No user data is stored, sold, or used to train models.

**Limitations users should know:**
- Large language models can produce plausible-sounding but incorrect information
  (a property known as "hallucination"). Always verify important claims
  with a qualified source.
- The waste classifier can misidentify unusual or ambiguous items. When in doubt,
  check with your campus facilities team.
- This app is a student education project, not a certified waste management tool.
  It should not be used as the sole basis for institutional policy decisions.
"""
    )

    # -----------------------------------------------------------------------
    # PRIVACY
    # -----------------------------------------------------------------------

    st.markdown("### 🔴 Privacy")
    st.markdown(
        """
EcoTrack AI does not collect, store, or share any personal data.

**What was done:**
- No login or registration is required.
- No user tracking, cookies, or analytics are implemented.
- Uploaded images are processed in memory only. They are sent to IBM watsonx.ai
  for classification if Vision AI is configured, but they are **never saved to disk**
  and **never sent to any service other than IBM watsonx.ai**.
- Uploaded CSV files are processed in the current session only. When the browser
  tab is closed, the data is gone.
- API credentials are stored in a `.env` file that is excluded from version control
  via `.gitignore`. They are never displayed in the UI.

**IBM watsonx.ai data handling:**
- Data sent to IBM watsonx.ai is subject to IBM's Cloud Service Agreement and
  Privacy Statement. Review IBM's policies at
  [ibm.com/privacy](https://www.ibm.com/privacy) before using this app
  with real personal or sensitive campus data.
"""
    )

    # -----------------------------------------------------------------------
    # AI LIMITATIONS
    # -----------------------------------------------------------------------

    st.markdown("### 🟣 AI Limitations")
    st.markdown(
        """
Understanding what AI cannot do is as important as knowing what it can.

| Limitation | Detail |
|---|---|
| **Classification uncertainty** | The Granite Vision model returns a best-guess category. It can be wrong, especially for ambiguous items. The app shows a confidence indicator for this reason. |
| **Hallucination** | Language models can generate confident-sounding text that is factually incorrect. The assistant is instructed to signal uncertainty, but it may not always do so reliably. |
| **Context window** | Only the last 3 conversation turns are sent to the AI assistant to manage token usage. Earlier context is lost. |
| **Training data cutoff** | The model's knowledge has a training cutoff date. It may not know about the most recent recycling regulations or sustainability research. |
| **English only** | The app is optimised for English. Non-English queries may produce less accurate results. |
| **Estimation accuracy** | Impact calculations use published average factors. They are not calibrated to your specific campus, city, or waste collection system. |
| **No real-time data** | The app does not connect to any live data feed. It only knows what you upload or type. |
"""
    )

    st.divider()

    st.markdown(
        "**Project alignment:** SDG 12 – Responsible Consumption and Production  \n"
        "**Internship:** 1M1B AI for Sustainability Virtual Internship  \n"
        "**Platform partners:** IBM SkillsBuild × AICTE  \n"
        "**AI platform:** IBM watsonx.ai (Granite foundation models)  \n"
        "**Development tool:** IBM Bob"
    )
