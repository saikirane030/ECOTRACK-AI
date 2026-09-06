# pages/impact_calculator.py
#
# Tab 4: Sustainability Impact Calculator
#
# What this page does:
#   1. User selects a waste type and enters their current weekly waste quantity
#   2. User sets a target reduction percentage using a slider
#   3. The app calculates estimated waste avoided and CO2/water savings
#   4. Results are clearly labelled as rough estimates with cited sources
#   5. No AI is used here – this is straightforward arithmetic
#
# IMPORTANT: All results include a visible disclaimer about estimation uncertainty.
# We do not claim these are precise or certified measurements.

import streamlit as st
from utils.impact_formulas import calculate_impact, FACTORS
from utils.waste_categories import WASTE_CATEGORIES


def render() -> None:
    """Main render function called by app.py."""

    st.subheader("🌱 Sustainability Impact Calculator")
    st.markdown(
        "Estimate the environmental benefit of reducing your campus waste. "
        "Enter your current weekly waste quantity and a reduction target."
    )

    st.info(
        "⚠️ **All results are rough estimates** based on published third-party studies "
        "(WRAP UK, US EPA WARM, IPCC AR6). Actual impact depends on local conditions. "
        "These numbers are for awareness and education, not certified reporting."
    )

    st.divider()

    # -----------------------------------------------------------------------
    # INPUT FORM
    # -----------------------------------------------------------------------

    col_left, col_right = st.columns(2)

    with col_left:
        # Waste type selector – only show types that have a meaningful estimate
        # E-waste and general are included but will show a "no estimate" note
        waste_type_labels = {
            "plastic": "Plastic",
            "paper":   "Paper / Cardboard",
            "food":    "Food / Organic",
            "e-waste": "E-Waste / Electronic",
            "general": "General / Mixed Waste",
        }
        selected_type = st.selectbox(
            "Waste type",
            options=list(waste_type_labels.keys()),
            format_func=lambda k: waste_type_labels[k],
            help="Select the waste category you want to calculate for.",
        )

        total_kg = st.number_input(
            "Current weekly waste quantity (kg)",
            min_value=0.0,
            max_value=10_000.0,
            value=10.0,
            step=0.5,
            help="Estimate how many kilograms of this waste type are generated per week.",
        )

    with col_right:
        reduction_pct = st.slider(
            "Target reduction (%)",
            min_value=0,
            max_value=100,
            value=20,
            step=5,
            help="What percentage reduction are you aiming for?",
        )

        period_weeks = st.number_input(
            "Over how many weeks?",
            min_value=1,
            max_value=52,
            value=4,
            step=1,
            help="The calculator will project the result over this many weeks.",
        )

    st.divider()

    # -----------------------------------------------------------------------
    # CALCULATE AND DISPLAY
    # -----------------------------------------------------------------------

    if total_kg == 0:
        st.markdown("Enter a non-zero waste quantity above to see the estimate.")
        return

    # Calculate for the full period (multiply weekly figure by number of weeks)
    total_kg_for_period = total_kg * period_weeks
    result = calculate_impact(
        waste_type=selected_type,
        total_kg=total_kg_for_period,
        reduction_pct=float(reduction_pct),
    )

    st.markdown(f"### Estimated impact over {period_weeks} week(s)")

    # Show the key result metrics
    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Waste Avoided",
        f"{result['kg_avoided']} kg",
        help="Kilograms of waste that would be prevented with the target reduction.",
    )

    if result["has_estimate"]:
        m2.metric(
            "CO₂e Saved (est.)",
            f"{result['co2_saved_kg']} kg",
            help="Estimated kg of CO₂-equivalent greenhouse gas avoided.",
        )
        if result["water_saved_litres"] > 0:
            m3.metric(
                "Water Saved (est.)",
                f"{result['water_saved_litres']} L",
                help="Estimated litres of water saved through recycling.",
            )
        else:
            m3.metric("Water Saved (est.)", "N/A")

        if result["trees_equivalent"] > 0:
            m4.metric(
                "Tree-Years Equivalent",
                f"{result['trees_equivalent']}",
                help=(
                    "Rough equivalent in tree-years of CO₂ absorption "
                    "(~21 kg CO₂/tree/year average, US Forest Service)."
                ),
            )
        else:
            m4.metric("Tree-Years Equivalent", "N/A")
    else:
        m2.metric("CO₂e Saved (est.)", "N/A")
        m3.metric("Water Saved (est.)", "N/A")
        m4.metric("Tree-Years Equivalent", "N/A")
        st.warning(
            f"A reliable CO₂ estimate is not available for **{waste_type_labels[selected_type]}**. "
            f"Reason: {result['source']}"
        )

    # -----------------------------------------------------------------------
    # BREAKDOWN TABLE
    # -----------------------------------------------------------------------

    st.markdown("#### How this was calculated")

    factor = FACTORS[selected_type]

    calc_data = {
        "Input": [
            "Current weekly waste",
            "Period",
            "Total waste in period",
            "Target reduction",
            "Waste avoided",
        ],
        "Value": [
            f"{total_kg} kg/week",
            f"{period_weeks} week(s)",
            f"{total_kg_for_period:.1f} kg",
            f"{reduction_pct}%",
            f"{result['kg_avoided']} kg",
        ],
    }

    import pandas as pd  # local import keeps file-level imports minimal
    st.table(pd.DataFrame(calc_data))

    if result["has_estimate"]:
        st.markdown(
            f"**CO₂ factor used:** {factor['co2_per_kg']} kg CO₂e per kg  \n"
            f"**Source:** {factor['source']}"
        )
        if factor["water_litres_per_kg"] > 0:
            st.markdown(
                f"**Water factor used:** {factor['water_litres_per_kg']} L per kg  \n"
                f"**Source:** {factor['source']}"
            )

    # -----------------------------------------------------------------------
    # DISCLAIMER – always shown
    # -----------------------------------------------------------------------

    st.markdown("")
    st.warning(result["disclaimer"])
    st.caption(
        "Source references: WRAP UK (2022), US EPA Waste Reduction Model v16 (2021), "
        "IPCC AR6 WG3 (2022). Factors can be adjusted in `utils/impact_formulas.py`."
    )
