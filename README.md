# EcoTrack AI – README
# =====================================================================
# AI-Powered Campus Waste & Sustainability Assistant
# 1M1B AI for Sustainability Virtual Internship
# IBM SkillsBuild × AICTE  |  SDG 12 – Responsible Consumption and Production
# =====================================================================

# README.md

## EcoTrack AI 🌱

**AI-Powered Campus Waste & Sustainability Assistant**

A beginner-friendly student project built for the [1M1B AI for Sustainability
Virtual Internship](https://www.1m1b.com) in collaboration with IBM SkillsBuild
and AICTE.

**Primary SDG:** SDG 12 – Responsible Consumption and Production  
**AI Platform:** IBM watsonx.ai (IBM Granite foundation models)  
**UI Framework:** Streamlit (Python)

---

## What the App Does

| Tab | Feature | AI Used? |
|-----|---------|----------|
| 📷 Waste Analyzer | Upload an image and get a waste category + disposal tip | Yes (Granite Vision, optional) |
| 📊 Analytics Dashboard | Upload a campus waste CSV and see KPI metrics and charts | Optional (AI insight summary) |
| 🤖 AI Assistant | Ask sustainability and waste management questions | Yes (Granite text model) |
| 🌱 Impact Calculator | Estimate CO₂/water savings from waste reduction | No (formula-based) |
| ⚖️ Responsible AI | Fairness, transparency, ethics, and privacy statement | No |

---

## Project Structure

```
EcoTrack-AI/
├── app.py                       # Entry point – run this file
├── pages/
│   ├── waste_classifier.py      # Tab 1 – image classification
│   ├── csv_analytics.py         # Tab 2 – analytics dashboard
│   ├── ai_assistant.py          # Tab 3 – chat assistant
│   ├── impact_calculator.py     # Tab 4 – impact calculator
│   └── responsible_ai.py        # Tab 5 – responsible AI page
├── utils/
│   ├── watsonx_client.py        # IBM watsonx.ai API wrapper
│   ├── waste_categories.py      # Categories, tips, prompts
│   └── impact_formulas.py       # CO₂ estimate formulas (with sources)
├── data/
│   └── sample_campus_waste.csv  # 100-row demo dataset
├── .env.example                 # Credential template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Setup Instructions

### Step 1 – Clone or download the project

```bash
git clone https://github.com/your-username/EcoTrack-AI.git
cd EcoTrack-AI
```

### Step 2 – Create a Python virtual environment (recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3 – Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 – Configure IBM watsonx.ai credentials

Copy the template and fill in your real values:

```bash
cp .env.example .env
```

Then open `.env` in a text editor and fill in:

```
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_REGION=us-south
WATSONX_VISION_DEPLOYMENT_ID=   # optional – see below
```

**How to get your credentials:**

1. Create a free IBM Cloud account at https://cloud.ibm.com
2. Go to **Catalog → AI / Machine Learning → watsonx.ai Studio** and create a Lite instance
3. Inside watsonx.ai Studio, create a new **Project**
4. Copy the **Project ID** from the project settings page
5. Go to **Manage → Access (IAM) → API Keys** and create an API key
6. Paste both into your `.env` file

**Free tier limits (IBM Lite plan):**
- 300,000 tokens/month for text generation (watsonx.ai Runtime)
- 10 CUH/month on watsonx.ai Studio
- This is more than enough for a student demo project

### Step 5 – Run the app

```bash
streamlit run app.py
```

Open your browser at http://localhost:8501

---

## Enabling Vision AI (Tab 1 – AI Mode)

The Granite Vision model (`ibm/granite-vision-3-2-2b`) requires a separate
**deploy-on-demand** deployment. It is not available on the Lite multitenant plan.

If you do not configure this, **Tab 1 automatically uses Demo Mode** — clearly
labelled pre-canned examples. The rest of the app works normally.

**To enable Vision AI:**

1. In watsonx.ai Studio, go to **Deployments → New Deployment**
2. Select the `granite-vision-3-2-2b` model
3. Choose **"Deploy on demand"**
4. Copy the Deployment ID
5. Add it to your `.env` file:
   ```
   WATSONX_VISION_DEPLOYMENT_ID=your_deployment_id
   ```

Note: Deploy-on-demand models incur hourly charges while deployed.
Stop the deployment when you are not using it to avoid costs.

---

## CSV Format for Tab 2

The analytics dashboard expects a CSV with these columns:

| Column | Type | Example |
|--------|------|---------|
| `date` | YYYY-MM-DD | 2024-01-08 |
| `location` | text | Cafeteria |
| `waste_type` | text | plastic, paper, food, e-waste, general |
| `weight_kg` | number | 4.2 |
| `disposed_correctly` | True/False | True |

A sample dataset is included at `data/sample_campus_waste.csv`.
Click **"Load sample data"** in Tab 2 to use it immediately.

---

## Deployment to Streamlit Community Cloud (Free)

1. Push your code to a GitHub repository
2. Go to https://share.streamlit.io and sign in with GitHub
3. Select your repository and set the main file to `app.py`
4. Add your secrets in **Settings → Secrets** (same key-value pairs as `.env`)
5. Click **Deploy**

**Important:** Never commit your `.env` file to GitHub.
Add `.env` to `.gitignore`:
```
echo ".env" >> .gitignore
```

---

## How to Explain This Project in an Interview

**What problem does it solve?**
Campus students and staff generate different types of waste but often lack awareness
about correct segregation, waste patterns, and how to reduce consumption.
EcoTrack AI provides a simple, accessible tool to classify waste, visualise patterns,
and get practical sustainability guidance.

**Why AI and not just regular software?**
A rule-based system can only handle a fixed list of inputs. AI (IBM Granite) can
interpret open-ended questions, reason about visual content (images), and summarise
patterns in natural language — things rule-based code cannot do reliably.

**What IBM technology did you use?**
- `ibm/granite-3-3-8b-instruct` — IBM Granite 3.3 instruction-following model for
  the chat assistant and CSV insight summary
- `ibm/granite-vision-3-2-2b` — IBM Granite Vision for image-to-text classification
  (deploy-on-demand)
- IBM watsonx.ai REST API and Python SDK (`ibm-watsonx-ai`)

**How does it connect to SDG 12?**
SDG 12 targets responsible consumption and production. This app directly supports:
- Target 12.4: Responsible waste management (Waste Classifier)
- Target 12.5: Reducing waste generation (Impact Calculator)
- Target 12.6: Sustainability reporting (Analytics Dashboard)
- Target 12.8: Access to sustainability information (AI Assistant)

**What responsible AI considerations did you include?**
The app covers fairness (accessible language, stated limitations), transparency
(all AI responses are labelled), ethics (no fabricated statistics, no data storage),
and privacy (no login, images processed in-memory only, no data retained).

---

## Responsible AI Summary

| Principle | Implementation |
|-----------|---------------|
| Fairness | Plain language, stated accuracy limitations, no assumptions about user background |
| Transparency | Every AI response is labelled with model name; Demo Mode is clearly marked |
| Ethics | AI instructed not to fabricate stats; impact factors include sources |
| Privacy | No login, no storage, no tracking; images never saved to disk |
| Limitations | Listed explicitly in Tab 5 (Responsible AI) |

---

## Sources for Impact Factors

- WRAP UK (2022) – *Plastic: Material Overview* https://wrap.org.uk
- US EPA (2021) – *Waste Reduction Model (WARM) v16* https://www.epa.gov/warm
- IPCC AR6 WG3 (2022) – *Chapter 7: Agriculture, Forestry, Land Use* https://www.ipcc.ch/report/ar6/wg3/
- US Forest Service – Urban tree CO₂ absorption averages

All factors are configurable in `utils/impact_formulas.py`.

---

## License

This project is for educational purposes as part of the 1M1B AI for Sustainability
Virtual Internship. You are free to use, modify, and learn from this code.
