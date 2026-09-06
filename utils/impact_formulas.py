# utils/impact_formulas.py
#
# Calculates estimated sustainability impact for the Impact Calculator (Tab 4).
#
# IMPORTANT – READ BEFORE MODIFYING:
# All conversion factors in this file are estimates derived from published
# third-party studies. Actual values depend on local conditions, waste quality,
# recycling infrastructure, and collection methods.
#
# The UI always shows a disclaimer to this effect. Do not present these numbers
# as precise measurements.
#
# Sources:
#   WRAP UK (2022) – "Plastic: Material Overview"
#       https://wrap.org.uk/resources/report/plastics-market-situation-report
#   US EPA (2021) – "Waste Reduction Model (WARM) v16"
#       https://www.epa.gov/warm
#   IPCC AR6 WG3 (2022) – Chapter 7: Agriculture, Forestry, Land Use
#       https://www.ipcc.ch/report/ar6/wg3/
#
# Any factor can be changed here without touching other files.

# ---------------------------------------------------------------------------
# CONVERSION FACTORS
# Units: kg CO2-equivalent saved per kg of waste correctly managed
# ---------------------------------------------------------------------------

FACTORS = {
    "plastic": {
        "co2_per_kg": 1.5,      # kg CO2e saved per kg plastic recycled vs landfill
        "water_litres_per_kg": 0.0,   # No reliable water-saving figure cited
        "source": "WRAP UK (2022) – estimated range 1.0–2.0 kg CO2e/kg",
    },
    "paper": {
        "co2_per_kg": 0.9,      # kg CO2e saved per kg paper recycled vs landfill
        "water_litres_per_kg": 13.0,  # Litres saved per kg paper recycled
        "source": "US EPA WARM v16 (2021) – mixed paper category",
    },
    "food": {
        "co2_per_kg": 0.5,      # kg CO2e avoided per kg food composted vs landfill
        "water_litres_per_kg": 0.0,   # Composting water savings not reliably quantified
        "source": "IPCC AR6 WG3 Ch.7 (2022) – food waste methane avoidance estimate",
    },
    "e-waste": {
        "co2_per_kg": 0.0,      # Benefit is hazardous material diversion, not CO2e
        "water_litres_per_kg": 0.0,
        "source": (
            "No simple CO2e factor applies. E-waste value is in preventing "
            "toxic leachate, not carbon savings. Impact not estimated here."
        ),
    },
    "general": {
        "co2_per_kg": 0.0,
        "water_litres_per_kg": 0.0,
        "source": "Mixed general waste: insufficient data for a reliable estimate.",
    },
}

# Trees absorb approximately 21 kg CO2 per year on average.
# Source: US Forest Service (rough urban tree average; varies widely by species)
KG_CO2_PER_TREE_PER_YEAR = 21.0

# ---------------------------------------------------------------------------
# CALCULATION FUNCTION
# ---------------------------------------------------------------------------

def calculate_impact(waste_type: str, total_kg: float, reduction_pct: float) -> dict:
    """
    Estimate the sustainability impact of reducing waste of a given type.

    Parameters
    ----------
    waste_type    : str   – one of the keys in FACTORS (e.g. "plastic")
    total_kg      : float – current total waste quantity in kilograms
    reduction_pct : float – target reduction percentage (0–100)

    Returns
    -------
    dict with keys:
        kg_avoided        – kilograms of waste avoided
        co2_saved_kg      – estimated kg CO2e saved
        water_saved_litres– estimated litres of water saved
        trees_equivalent  – rough tree-year equivalent for CO2 saved
        source            – citation string
        has_estimate      – True if a numeric estimate is available
        disclaimer        – standard disclaimer text
    """
    # Clamp inputs to sensible ranges
    total_kg = max(0.0, total_kg)
    reduction_pct = max(0.0, min(100.0, reduction_pct))

    factor = FACTORS.get(waste_type, FACTORS["general"])

    kg_avoided = total_kg * (reduction_pct / 100.0)
    co2_saved = kg_avoided * factor["co2_per_kg"]
    water_saved = kg_avoided * factor["water_litres_per_kg"]

    # Only show tree equivalent if there is a non-zero CO2 estimate
    trees_equivalent = (
        co2_saved / KG_CO2_PER_TREE_PER_YEAR if co2_saved > 0 else 0.0
    )

    has_estimate = factor["co2_per_kg"] > 0 or factor["water_litres_per_kg"] > 0

    disclaimer = (
        "⚠️ These are rough estimates based on published third-party studies. "
        "Actual impact depends on local recycling infrastructure, waste quality, "
        "and collection methods. Do not use these numbers as certified measurements."
    )

    return {
        "kg_avoided": round(kg_avoided, 2),
        "co2_saved_kg": round(co2_saved, 2),
        "water_saved_litres": round(water_saved, 1),
        "trees_equivalent": round(trees_equivalent, 2),
        "source": factor["source"],
        "has_estimate": has_estimate,
        "disclaimer": disclaimer,
    }
