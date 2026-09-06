# utils/waste_categories.py
#
# This file is the single source of truth for:
#   - The 5 waste categories the app recognises
#   - Disposal tips for each category
#   - The AI prompt used for image classification
#   - Pre-canned Demo Mode examples (used when vision AI is unavailable)
#
# A student can extend this file to add more categories or improve tips
# without touching any other code.

# ---------------------------------------------------------------------------
# WASTE CATEGORIES
# Each entry has:
#   "label"    – Short display name shown in the UI
#   "colour"   – Hex colour for the UI badge (matches common bin colours)
#   "tip"      – Practical disposal instruction for a campus setting
#   "examples" – Real-world items that belong to this category
# ---------------------------------------------------------------------------

WASTE_CATEGORIES = {
    "plastic": {
        "label": "Plastic",
        "colour": "#2563EB",   # blue
        "tip": (
            "Rinse the item if it held food or liquid, then place it in the "
            "blue/dry recycling bin. Remove any non-plastic parts (e.g. metal "
            "caps). Crushed plastic bottles take less bin space."
        ),
        "examples": [
            "water bottle", "plastic bag", "food wrapper",
            "styrofoam cup", "plastic straw", "takeaway container",
        ],
    },
    "paper": {
        "label": "Paper / Cardboard",
        "colour": "#D97706",   # amber
        "tip": (
            "Flatten cardboard boxes before placing them in the paper bin. "
            "Soiled or greasy paper (e.g. pizza boxes) cannot be recycled — "
            "put those in general waste. Keep paper dry."
        ),
        "examples": [
            "newspaper", "notebook page", "cardboard box",
            "paper cup", "tissue paper", "flyer",
        ],
    },
    "food": {
        "label": "Food / Organic",
        "colour": "#16A34A",   # green
        "tip": (
            "Place in the green/organic bin or compost area. "
            "Avoid putting liquids directly in the bin — drain excess liquid first. "
            "Food waste composted instead of landfilled significantly reduces "
            "methane emissions."
        ),
        "examples": [
            "banana peel", "vegetable scraps", "leftover rice",
            "fruit", "tea bag", "coffee grounds",
        ],
    },
    "e-waste": {
        "label": "E-Waste / Electronic",
        "colour": "#DC2626",   # red
        "tip": (
            "Do NOT place in regular bins. E-waste contains hazardous materials. "
            "Drop off at your campus e-waste collection point or an authorised "
            "e-waste recycler. Many manufacturers offer take-back programmes."
        ),
        "examples": [
            "old phone", "charger cable", "battery",
            "broken earphones", "USB drive", "laptop",
        ],
    },
    "general": {
        "label": "General / Mixed Waste",
        "colour": "#6B7280",   # grey
        "tip": (
            "Place in the general waste bin. Try to reduce items in this category — "
            "most general waste ends up in landfill. Consider whether the item "
            "could be repaired, reused, or swapped for a recyclable alternative."
        ),
        "examples": [
            "broken glass", "ceramic mug", "rubber band",
            "used tape", "worn-out shoe", "mixed packaging",
        ],
    },
}

# ---------------------------------------------------------------------------
# DEMO MODE EXAMPLES
# Shown in Tab 1 when the vision AI is not configured.
# Each entry represents one realistic classification result so a student can
# demonstrate the app without needing API credentials.
# The UI must always display the "⚠️ Demo Mode" warning alongside these.
# ---------------------------------------------------------------------------

DEMO_EXAMPLES = [
    {
        "image_description": "Plastic water bottle",
        "category": "plastic",
        "confidence_note": (
            "Demo result — not real AI inference. "
            "A plastic water bottle is typically categorised as dry recyclable plastic."
        ),
    },
    {
        "image_description": "Crumpled newspaper",
        "category": "paper",
        "confidence_note": (
            "Demo result — not real AI inference. "
            "Clean, dry newspaper belongs in the paper recycling stream."
        ),
    },
    {
        "image_description": "Banana peel",
        "category": "food",
        "confidence_note": (
            "Demo result — not real AI inference. "
            "Fruit peels are organic waste suitable for composting."
        ),
    },
    {
        "image_description": "Old mobile phone",
        "category": "e-waste",
        "confidence_note": (
            "Demo result — not real AI inference. "
            "Electronic devices must never go in regular bins due to hazardous components."
        ),
    },
    {
        "image_description": "Torn rubber sole",
        "category": "general",
        "confidence_note": (
            "Demo result — not real AI inference. "
            "Mixed or non-recyclable materials typically go in the general waste bin."
        ),
    },
]

# ---------------------------------------------------------------------------
# IMAGE CLASSIFICATION PROMPT
# Sent to the IBM Granite vision model together with the uploaded image.
# It asks for a structured JSON-like response so the app can parse it reliably.
# ---------------------------------------------------------------------------

VISION_CLASSIFICATION_PROMPT = """You are a campus waste management assistant.
Look at the image provided and identify the type of waste shown.

Respond in this exact format (no extra text before or after):
CATEGORY: <one of: plastic, paper, food, e-waste, general>
CONFIDENCE: <high, medium, or low>
REASONING: <one sentence explaining what you see and why you chose this category>
DISPOSAL_TIP: <one practical sentence on how to dispose of this item correctly>

If you cannot clearly identify the waste type, use CATEGORY: general and CONFIDENCE: low.
Never make up details you cannot see in the image."""

# ---------------------------------------------------------------------------
# AI ASSISTANT SYSTEM PROMPT
# Sets the persona and behavioural guardrails for the chat in Tab 3.
# ---------------------------------------------------------------------------

ASSISTANT_SYSTEM_PROMPT = """You are EcoTrack AI, a campus sustainability assistant \
helping students and staff understand waste management, recycling, and SDG 12 \
(Responsible Consumption and Production).

Guidelines:
- Give concise, practical, and encouraging advice.
- Do not fabricate statistics or make up facts.
- If you are uncertain about something, say so clearly.
- Keep answers relevant to a student or campus context.
- Do not identify or reference specific individuals.
- Do not produce harmful, offensive, or unrelated content.
- If asked something outside sustainability, politely redirect.

Your goal is to help users make better waste decisions, not to lecture them."""
