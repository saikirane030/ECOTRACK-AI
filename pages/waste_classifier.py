# pages/waste_classifier.py
#
# Tab 1: Waste Image Analyzer
#
# What this page does:
#   1. Lets the user upload a JPG or PNG image of a waste item
#   2. If the Granite Vision deployment is configured → sends the image to
#      IBM watsonx.ai and parses the response into a category + tip
#   3. If vision AI is NOT configured → shows Demo Mode with pre-canned
#      examples and a clear "⚠️ Demo Mode" warning
#
# The Demo Mode never pretends to be real AI inference.
# The AI Mode clearly labels the result as AI-generated and shows uncertainty.

import streamlit as st
from PIL import Image
from io import BytesIO

from utils.watsonx_client import classify_image, is_vision_ai_available
from utils.waste_categories import (
    WASTE_CATEGORIES,
    DEMO_EXAMPLES,
    VISION_CLASSIFICATION_PROMPT,
)


def _parse_vision_response(raw: str) -> dict:
    """
    Parse the structured text response from the Granite vision model.

    Expected format (as specified in VISION_CLASSIFICATION_PROMPT):
        CATEGORY: plastic
        CONFIDENCE: high
        REASONING: I can see a clear plastic bottle with a blue cap.
        DISPOSAL_TIP: Rinse and place in the blue recycling bin.

    If parsing fails the function returns safe fallback values so the UI
    never crashes on an unexpected model response.
    """
    result = {
        "category": "general",
        "confidence": "low",
        "reasoning": raw,       # keep the raw text as reasoning fallback
        "disposal_tip": "",
        "parse_success": False,
    }

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("CATEGORY:"):
            cat = line.split(":", 1)[1].strip().lower()
            # Only accept known categories; default to general
            if cat in WASTE_CATEGORIES:
                result["category"] = cat
        elif line.startswith("CONFIDENCE:"):
            conf = line.split(":", 1)[1].strip().lower()
            if conf in ("high", "medium", "low"):
                result["confidence"] = conf
        elif line.startswith("REASONING:"):
            result["reasoning"] = line.split(":", 1)[1].strip()
            result["parse_success"] = True
        elif line.startswith("DISPOSAL_TIP:"):
            result["disposal_tip"] = line.split(":", 1)[1].strip()

    return result


def _show_category_result(category_key: str, extra_tip: str = "") -> None:
    """
    Display the category badge, disposal tip, and any extra info.
    Reused by both AI Mode and Demo Mode.
    """
    cat = WASTE_CATEGORIES.get(category_key, WASTE_CATEGORIES["general"])
    colour = cat["colour"]
    label  = cat["label"]
    tip    = extra_tip if extra_tip else cat["tip"]

    # Coloured category badge using HTML in markdown
    st.markdown(
        f"<span style='background:{colour};color:white;padding:4px 14px;"
        f"border-radius:12px;font-weight:600;font-size:1.1em'>"
        f"🗑️ {label}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("")  # spacer

    st.markdown("**Disposal guidance:**")
    st.info(tip)

    # Show example items for this category so the user learns more
    examples = cat["examples"]
    st.caption(f"Other examples in this category: {', '.join(examples)}")


def render() -> None:
    """Main render function called by app.py."""

    st.subheader("📷 Waste Image Analyzer")
    st.markdown(
        "Upload a photo of a waste item and the app will suggest its waste category "
        "and how to dispose of it correctly."
    )

    # -----------------------------------------------------------------------
    # MODE BANNER – always visible so the user knows what mode they are in
    # -----------------------------------------------------------------------

    if is_vision_ai_available():
        st.success(
            "✅ **AI Mode** – Images are sent to IBM Granite Vision (watsonx.ai) "
            "for classification. Results are AI-generated estimates."
        )
    else:
        st.warning(
            "⚠️ **Demo Mode** – Vision AI is not configured.  \n"
            "The examples below are **pre-written demonstrations**, "
            "**not real AI inference**. They are shown so you can explore the app "
            "without API credentials.  \n"
            "_To enable AI Mode, configure `WATSONX_VISION_DEPLOYMENT_ID` in your "
            "`.env` file. See README.md for instructions._"
        )

    st.divider()

    # -----------------------------------------------------------------------
    # FILE UPLOADER
    # -----------------------------------------------------------------------

    uploaded_file = st.file_uploader(
        "Choose a waste image",
        type=["jpg", "jpeg", "png"],
        help="Upload a JPG or PNG photo of the waste item you want to classify.",
    )

    if uploaded_file is None:
        st.markdown("👆 Upload an image to get started.")
        return

    # Display the uploaded image (resized to a reasonable preview width)
    image = Image.open(uploaded_file)
    col_img, col_result = st.columns([1, 2])

    with col_img:
        st.image(image, caption="Your uploaded image", use_container_width=True)

    with col_result:

        # -------------------------------------------------------------------
        # AI MODE – send image to Granite Vision
        # -------------------------------------------------------------------

        if is_vision_ai_available():
            with st.spinner("Analysing image with IBM Granite Vision..."):
                # Read raw bytes for the API call
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()

                # Determine MIME type from file extension
                mime = (
                    "image/png"
                    if uploaded_file.name.lower().endswith(".png")
                    else "image/jpeg"
                )

                raw_response, error = classify_image(
                    image_bytes=image_bytes,
                    image_mime_type=mime,
                    prompt=VISION_CLASSIFICATION_PROMPT,
                )

            if error:
                st.error(f"**AI classification failed:** {error}")
                st.markdown(
                    "The image could not be classified. "
                    "Please check your credentials or try again."
                )
                return

            # Parse the structured response
            parsed = _parse_vision_response(raw_response)

            # Show a confidence indicator
            confidence_colour = {
                "high": "🟢", "medium": "🟡", "low": "🔴"
            }.get(parsed["confidence"], "🔴")

            st.markdown(
                f"**Confidence:** {confidence_colour} {parsed['confidence'].capitalize()}"
            )

            if parsed["confidence"] == "low":
                st.warning(
                    "The AI is not confident about this classification. "
                    "Use this as a rough guide only."
                )

            # Show the reasoning from the model
            if parsed["reasoning"]:
                st.markdown(f"*{parsed['reasoning']}*")

            # Show the category result
            _show_category_result(
                category_key=parsed["category"],
                extra_tip=parsed.get("disposal_tip", ""),
            )

            # Responsible AI label
            st.caption(
                "🤖 Generated by IBM Granite Vision via watsonx.ai. "
                "AI classification can be wrong. When in doubt, check with your "
                "campus facilities team."
            )

        # -------------------------------------------------------------------
        # DEMO MODE – pre-canned examples, never fake AI
        # -------------------------------------------------------------------

        else:
            st.markdown("#### Demo Mode – Select an example")
            st.markdown(
                "Since Vision AI is not configured, choose one of these "
                "pre-written examples to see how the app would display a result."
            )

            # Let user pick from the pre-canned examples
            example_labels = [ex["image_description"] for ex in DEMO_EXAMPLES]
            choice_idx = st.selectbox(
                "Select a demo example:",
                range(len(example_labels)),
                format_func=lambda i: example_labels[i],
            )

            example = DEMO_EXAMPLES[choice_idx]

            st.markdown("---")
            st.error(
                "⚠️ **This is a Demo Mode result.**  \n"
                "It is **not** based on your uploaded image and **not** real AI "
                "inference. It is a fixed example for demonstration purposes only."
            )

            _show_category_result(category_key=example["category"])

            st.caption(f"*{example['confidence_note']}*")
