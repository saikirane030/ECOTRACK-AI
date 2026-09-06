# ♻️ EcoTrack AI

**AI-Powered Campus Waste & Sustainability Assistant**

> *How might we use AI to help students and campus communities identify, segregate,
> and understand waste so that campus waste management becomes more sustainable?*

**Primary SDG:** SDG 12 – Responsible Consumption and Production
**Internship:** 1M1B AI for Sustainability Virtual Internship | IBM SkillsBuild × AICTE
**AI Platform:** IBM watsonx.ai (IBM Granite foundation models)
**UI:** Streamlit (Python) — single file, beginner-friendly

---

## Two Main AI Features

### 1. 📷 AI Waste Analyzer

The primary feature.

- User uploads a JPG or PNG photo of any waste item
- **When IBM Granite Vision is configured:** the image is sent to the
  `granite-vision-3-2-2b` deploy-on-demand model on watsonx.ai, which
  identifies the waste category, confidence level, reasoning, and a disposal tip
- **When Vision AI is not configured:** Demo Mode is shown — user selects
  from 5 predefined example items to see how results look. Demo Mode is
  clearly labelled and never claims to be real AI inference
- A colour-coded Waste Category Guide is shown below the analyzer

Waste categories recognised: **Plastic, Paper/Cardboard, Food/Organic,
E-Waste/Electronic, General Waste**

### 2. 🤖 AI Sustainability Assistant

The second main feature.

- Student types any question about campus waste, recycling, or sustainability
- Question is sent to IBM Granite (`ibm/granite-3-3-8b-instruct`) on
  watsonx.ai Runtime (Lite plan: 300,000 tokens/month free)
- Model replies with a concise, practical answer
- Every AI response is labelled with the model name
- If credentials are not configured, the tab shows a clear
  "AI not configured" message — it never pretends a response was generated

Example questions:
- How do I dispose of a plastic bottle on campus?
- How can students reduce waste on campus?
- What is SDG 12?
- How can our cafeteria reduce food waste?
- Why is e-waste dangerous in regular bins?

---

## Supporting Sections

These are not additional AI features. They support and complement the two
main features above.

### 🌱 Sustainability Impact Calculator

A simple arithmetic calculator — no AI involved.

- User selects a waste type and enters a weekly quantity and reduction target
- App calculates: waste avoided (kg), estimated CO₂ saved, estimated water saved,
  tree-years equivalent
- All results are clearly labelled as **rough estimates** based on:
  - WRAP UK (2022) for plastic
  - US EPA WARM v16 (2021) for paper
  - IPCC AR6 WG3 (2022) for food
- Results are not certified measurements and should not be used for official reporting

### ⚖️ Responsible AI

A collapsible section covering the five mandatory Responsible AI principles:

| Principle | What was done |
|---|---|
| Fairness | Plain language, no assumptions about user background |
| Transparency | AI responses labelled with model name; Demo Mode labelled as non-AI |
| Ethics | AI instructed not to fabricate stats; impact factors have cited sources |
| Privacy | No login; images processed in memory only; no data stored |
| Limitations | AI can be wrong; estimates are not measurements; verify with facilities staff |

---

## Project Structure

```
EcoTrack-AI/
├── app.py                        ← entire application in one file
├── data/
│   └── sample_campus_waste.csv   ← bundled demo dataset (not real campus data)
├── .streamlit/
│   ├── config.toml               ← Streamlit server config
│   └── secrets.toml.example      ← credential key template
├── .env.example                  ← credential template for local use
├── requirements.txt              ← Python dependencies
└── README.md                     ← this file
```

Everything is in a single `app.py` — no separate modules, no pages folder.
A beginner can read the entire app from top to bottom in one sitting.

---

## Setup Instructions

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Configure credentials

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_REGION=us-south
WATSONX_VISION_DEPLOYMENT_ID=        # optional — leave blank to use Demo Mode
```

**How to get credentials:**
1. Create a free IBM Cloud account at https://cloud.ibm.com
2. Create a watsonx.ai Studio instance (Lite plan — free)
3. Create a project → copy the **Project ID** from project settings
4. Go to Manage → Access (IAM) → API Keys → create an API key

**Free tier:** 300,000 tokens/month for text generation (watsonx.ai Runtime Lite)

### Step 3 — Run

```bash
streamlit run app.py
```

App opens at http://localhost:8501

---

## What Works Without Credentials

| Feature | Without credentials |
|---|---|
| Waste Category Guide | ✅ Always works |
| Waste Analyzer — Demo Mode | ✅ Always works (clearly labelled) |
| Impact Calculator | ✅ Always works |
| Responsible AI section | ✅ Always works |
| AI Assistant | ❌ Shows "AI not configured" message |
| Waste Analyzer — real AI | ❌ Falls back to Demo Mode |

---

## Enabling Vision AI

The Granite Vision model (`ibm/granite-vision-3-2-2b`) requires a
**deploy-on-demand** deployment in watsonx.ai Studio. It is not available
on the Lite multitenant plan and incurs an hourly charge while running.

If `WATSONX_VISION_DEPLOYMENT_ID` is not set, the app automatically uses
Demo Mode — no crash, no error.

---

## Deploying to Streamlit Community Cloud (Free)

1. Push to GitHub
2. Go to https://share.streamlit.io → sign in → Create app
3. Set: Repository = this repo, Branch = `main`, Main file = `app.py`
4. Go to Settings → Secrets and add:
   ```toml
   WATSONX_API_KEY = "your_key"
   WATSONX_PROJECT_ID = "your_project_id"
   WATSONX_REGION = "us-south"
   WATSONX_VISION_DEPLOYMENT_ID = ""
   ```
5. Click Deploy

---

## Interview Explanation

**What problem does it solve?**
Students and campus communities may not always know how to identify, segregate,
and manage waste correctly. EcoTrack AI provides a simple tool to classify waste
from photos and answer sustainability questions using IBM Granite AI.

**What are the two main features?**
1. AI Waste Analyzer — upload a photo, get the waste category and disposal tip
2. AI Sustainability Assistant — ask any sustainability question, get a practical answer

**Why AI and not just regular software?**
A rule-based system handles only a fixed list of inputs. IBM Granite can reason
about images, interpret open-ended natural language questions, and give contextual
answers — things rule-based code cannot do reliably.

**What IBM technology did you use?**
- `ibm/granite-3-3-8b-instruct` — IBM Granite 3.3, multitenant on watsonx.ai Runtime
- `ibm/granite-vision-3-2-2b` — IBM Granite Vision, deploy-on-demand
- IBM watsonx.ai REST API and Python SDK (`ibm-watsonx-ai`)

**How does it connect to SDG 12?**
SDG 12 targets responsible consumption and production. This app helps students
identify waste correctly (reduce wrong disposal), understand sustainability (behaviour
change), and estimate the impact of waste reduction choices.

**What responsible AI considerations did you include?**
Fairness, transparency, ethics, privacy, and limitations — all covered in the
Responsible AI section of the app. Demo Mode is never presented as real AI.
Impact estimates include their published sources. No data is stored.

---

## Sources for Impact Factors

- WRAP UK (2022) — Plastics Market Situation Report
- US EPA WARM v16 (2021) — Waste Reduction Model
- IPCC AR6 WG3 (2022) — Chapter 7: Agriculture, Forestry, Land Use
- US Forest Service — urban tree CO₂ absorption averages (~21 kg/tree/year)

All factors are configurable in `app.py` under `IMPACT_FACTORS`.

---

## License

Educational project for the 1M1B AI for Sustainability Virtual Internship.
Free to use, modify, and learn from.
