♻️ EcoTrack AI

AI-Powered Campus Waste & Sustainability Assistant

EcoTrack AI is a student-focused sustainability application that uses AI to help campus communities identify waste, understand proper disposal practices, and make more sustainable decisions.

---

🎯 Problem Statement

«How might we use AI to help students and campus communities identify, segregate, and understand waste so that campus waste management can become more sustainable?»

Students often face difficulty identifying different types of waste and understanding how to dispose of them correctly. At the same time, campus waste patterns can be difficult to understand without simple digital tools.

EcoTrack AI aims to make waste awareness and sustainability guidance easier and more accessible.

---

🌱 SDG Alignment

SDG 12 — Responsible Consumption and Production

EcoTrack AI supports SDG 12 by encouraging:

- Better waste identification
- Proper waste segregation
- Responsible disposal practices
- Waste reduction awareness
- Sustainability education

---

🤖 Main Features

1. 📷 AI Waste Analyzer

The AI Waste Analyzer helps users understand what type of waste they are dealing with.

How it works:

1. Upload a waste image.
2. IBM Granite Vision analyzes the image when live AI is configured.
3. The application provides an approximate waste category.
4. It provides practical disposal guidance.
5. Confidence or uncertainty is shown when available.

Waste categories include:

- 🧴 Plastic
- 📦 Paper / Cardboard
- 🍎 Food / Organic
- 💻 E-Waste / Electronic
- 🗑️ General Waste

«Note: When live Vision AI is unavailable, the application uses a clearly labelled Demo Mode. Demo Mode is not real AI inference.»

---

2. 💬 AI Sustainability Assistant

The AI Sustainability Assistant allows users to ask questions related to sustainability and waste management.

Examples:

- How should plastic bottles be disposed of?
- How can I reduce waste in my hostel?
- What is e-waste?
- How can students reduce food waste?

When configured, IBM Granite provides concise and practical sustainability guidance.

«Note: Live AI responses require the appropriate IBM watsonx.ai configuration.»

---

🧩 Supporting Features

🌱 Sustainability Impact Calculator

The calculator provides estimated environmental impact indicators based on user inputs.

These results are estimates for educational purposes and are not measured or certified environmental results.

📊 Waste Analytics

The application can analyze sample campus waste data using data-processing and visualization tools.

The included dataset is sample/demo data and does not represent actual campus measurements.

⚖️ Responsible AI

EcoTrack AI considers:

- Fairness — Avoiding unnecessary assumptions about users.
- Transparency — Clearly identifying AI-generated results.
- Ethics — Avoiding fabricated statistics and unsupported claims.
- Privacy — Avoiding unnecessary collection of personal information.
- Limitations — Recognizing that AI-generated results may be incorrect.

---

🔄 How It Works

              User
                ↓
        ┌─────────────────┐
        │   EcoTrack AI   │
        │    Streamlit    │
        └─────────────────┘
                ↓
      ┌─────────┼─────────┐
      ↓         ↓         ↓
 Waste Image  Questions  Waste Data
      ↓         ↓         ↓
 IBM Granite  IBM Granite  Pandas
   Vision       AI         + Plotly
      ↓         ↓         ↓
      └─────────┼─────────┘
                ↓
      Sustainability Guidance

---

🛠️ Technology Stack

Technology| Purpose
Python| Application development
Streamlit| Web interface
IBM Granite| AI capabilities
IBM watsonx.ai| AI model access
Pandas| Data processing
Plotly| Data visualization
Pillow| Image processing

---

📁 Project Structure

EcoTrack-AI/
│
├── app.py
├── data/
│   └── sample_campus_waste.csv
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

---

▶️ Run Locally

Clone the repository and install the required packages:

pip install -r requirements.txt

Run the application:

streamlit run app.py

The application can be opened locally in a web browser.

---

🔐 AI Configuration

For local AI functionality:

1. Use ".env.example" as a configuration reference.
2. Add your IBM watsonx.ai credentials securely.
3. Never commit real credentials or API keys to GitHub.
4. Live AI functionality depends on the required IBM model configuration.

If live Vision AI is unavailable, the application clearly uses Demo Mode instead of pretending that an AI prediction was made.

---

📌 Limitations

- AI-generated responses may contain errors.
- Image classification is approximate.
- Demo Mode is not real AI inference.
- The included dataset is sample data.
- Environmental impact calculations are estimates.
- Official campus waste-management instructions should be followed where applicable.

---

🚀 Future Improvements

Possible future improvements include:

- Using real campus waste data
- Improving waste-image recognition
- Adding campus-specific disposal guidance
- Adding long-term waste tracking and reporting

---

🤝 IBM Bob

IBM Bob was used during the project development process for activities such as:

- Project planning
- Application design
- Implementation assistance
- Testing and refinement

The project was developed with a focus on keeping the solution simple, practical, and understandable for students.

---

📚 1M1B Relevance

EcoTrack AI addresses a real-world campus sustainability problem and aligns with SDG 12 — Responsible Consumption and Production.

The project demonstrates how AI can support waste awareness, responsible disposal, and sustainability education while considering transparency, privacy, ethics, and AI limitations.

---

📄 License

This project is developed as an educational sustainability project for the 1M1B AI for Sustainability Virtual Internship.
